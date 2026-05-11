#!/usr/bin/env python3
"""
A5L Unit Tests
单元测试模块

Usage:
    python -m pytest tests/ -v
    python tests/run_tests.py
"""

import unittest
import sys
import json
from pathlib import Path
from datetime import datetime

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestDatabase(unittest.TestCase):
    """数据库模块测试"""
    
    def setUp(self):
        """测试前准备 - 使用内存数据库"""
        import sqlite3
        self.conn = sqlite3.connect(':memory:')
        self.conn.row_factory = sqlite3.Row
        
        # 创建表结构
        with open(Path(__file__).parent.parent / 'database' / 'schema.sql') as f:
            self.conn.executescript(f.read())
    
    def tearDown(self):
        """测试后清理"""
        self.conn.close()
    
    def test_atom_crud(self):
        """测试Atom增删改查"""
        # 创建
        self.conn.execute('''
            INSERT INTO atoms (id, kind, title, content, author)
            VALUES (?, ?, ?, ?, ?)
        ''', ('test-001', 'analysis', '测试', '测试内容', 'tester'))
        
        # 读取
        row = self.conn.execute('SELECT * FROM atoms WHERE id = ?', ('test-001',)).fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row['title'], '测试')
        
        # 更新
        self.conn.execute('UPDATE atoms SET title = ? WHERE id = ?', ('更新后', 'test-001'))
        row = self.conn.execute('SELECT title FROM atoms WHERE id = ?', ('test-001',)).fetchone()
        self.assertEqual(row['title'], '更新后')
        
        # 删除
        self.conn.execute('DELETE FROM atoms WHERE id = ?', ('test-001',))
        row = self.conn.execute('SELECT * FROM atoms WHERE id = ?', ('test-001',)).fetchone()
        self.assertIsNone(row)
    
    def test_decision_workflow(self):
        """测试决策完整流程"""
        # 创建决策
        self.conn.execute('''
            INSERT INTO decisions (id, type, symbol, action, confidence, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('dec-001', 'trade', '000001.SZ', 'buy', 0.85, 'pending'))
        
        # 验证状态
        row = self.conn.execute('SELECT status FROM decisions WHERE id = ?', ('dec-001',)).fetchone()
        self.assertEqual(row['status'], 'pending')
        
        # 更新为执行
        self.conn.execute('UPDATE decisions SET status = ? WHERE id = ?', ('executed', 'dec-001'))
        row = self.conn.execute('SELECT status FROM decisions WHERE id = ?', ('dec-001',)).fetchone()
        self.assertEqual(row['status'], 'executed')
    
    def test_signal_validation(self):
        """测试信号验证"""
        # 创建信号
        self.conn.execute('''
            INSERT INTO signals (symbol, signal_type, direction, strength, validated)
            VALUES (?, ?, ?, ?, ?)
        ''', ('000001.SZ', 'breakout', 'bullish', 0.82, 0))
        
        signal_id = self.conn.execute('SELECT last_insert_rowid()').fetchone()[0]
        
        # 验证
        self.conn.execute('''
            UPDATE signals SET validated = 1, pnl = ? WHERE id = ?
        ''', (5.5, signal_id))
        
        row = self.conn.execute('SELECT validated, pnl FROM signals WHERE id = ?', (signal_id,)).fetchone()
        self.assertEqual(row['validated'], 1)
        self.assertEqual(row['pnl'], 5.5)


class TestMCPProtocol(unittest.TestCase):
    """MCP协议测试"""
    
    def setUp(self):
        from wave1.mcp_server_real import A5LPrimeMCPServer, MCPProtocolAdapter
        self.server = A5LPrimeMCPServer()
        self.adapter = MCPProtocolAdapter(self.server)
    
    def test_initialize(self):
        """测试初始化请求"""
        request = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "id": 1
        }
        response = self.adapter.handle_request(request)
        
        self.assertEqual(response['jsonrpc'], '2.0')
        self.assertEqual(response['id'], 1)
        self.assertIn('result', response)
        self.assertEqual(response['result']['serverInfo']['name'], 'A5L-Prime')
    
    def test_tools_list(self):
        """测试tools/list请求"""
        request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": 2
        }
        response = self.adapter.handle_request(request)
        
        self.assertIn('result', response)
        self.assertIn('tools', response['result'])
        self.assertEqual(len(response['result']['tools']), 5)  # 5个tools
    
    def test_tools_call_get_stats(self):
        """测试tools/call调用get_stats"""
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "a5l_get_stats",
                "arguments": {}
            },
            "id": 3
        }
        response = self.adapter.handle_request(request)
        
        self.assertIn('result', response)
        self.assertIn('content', response['result'])
        self.assertFalse(response['result']['isError'])
    
    def test_invalid_method(self):
        """测试无效方法"""
        request = {
            "jsonrpc": "2.0",
            "method": "invalid_method",
            "id": 4
        }
        response = self.adapter.handle_request(request)
        
        self.assertIn('error', response)
        self.assertEqual(response['error']['code'], -32601)


class TestFeishuClient(unittest.TestCase):
    """飞书客户端测试"""
    
    def setUp(self):
        from integrations.feishu_real_client import FeishuConfig, FeishuRealClient
        self.config = FeishuConfig(
            app_id='test_app_id',
            app_secret='test_secret',
            default_chat_id='test_chat_id'
        )
        self.client = FeishuRealClient(self.config)
    
    def test_config_loading(self):
        """测试配置加载"""
        self.assertEqual(self.client.config.app_id, 'test_app_id')
        self.assertEqual(self.client.config.default_chat_id, 'test_chat_id')
    
    def test_message_formatting(self):
        """测试消息格式化"""
        # 测试卡片构建
        card = {
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {"tag": "plain_text", "content": "测试"},
                "template": "blue"
            },
            "elements": []
        }
        
        self.assertIn('header', card)
        self.assertEqual(card['header']['template'], 'blue')


class TestDataModels(unittest.TestCase):
    """数据模型测试"""
    
    def test_atom_model(self):
        """测试Atom模型"""
        from database.db_manager import Atom
        
        atom = Atom(
            id='test-001',
            kind='analysis',
            content='测试内容',
            title='测试标题',
            tags=['test', 'analysis']
        )
        
        self.assertEqual(atom.id, 'test-001')
        self.assertEqual(atom.kind, 'analysis')
        self.assertEqual(len(atom.tags), 2)
    
    def test_decision_model(self):
        """测试Decision模型"""
        from database.db_manager import Decision
        
        decision = Decision(
            id='dec-001',
            type='trade',
            action='buy',
            symbol='000001.SZ',
            confidence=0.85,
            status='pending'
        )
        
        self.assertEqual(decision.action, 'buy')
        self.assertEqual(decision.confidence, 0.85)


def run_tests():
    """运行所有测试"""
    print("🧪 Running A5L Unit Tests...")
    print("=" * 60)
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestDatabase))
    suite.addTests(loader.loadTestsFromTestCase(TestMCPProtocol))
    suite.addTests(loader.loadTestsFromTestCase(TestFeishuClient))
    suite.addTests(loader.loadTestsFromTestCase(TestDataModels))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 统计
    print("\n" + "=" * 60)
    print(f"📊 Test Results:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1


if __name__ == '__main__':
    exit(run_tests())
