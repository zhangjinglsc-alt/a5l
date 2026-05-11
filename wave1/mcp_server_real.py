#!/usr/bin/env python3
"""
A5L Prime MCP Server - 真实MCP协议实现
Wave 1 Phase 1.4 完成版

核心特性:
- 基于官方MCP协议
- 真实Tool Registration
- 真实Call Tool执行
- A5L SKILL作为MCP Tools暴露
"""

import json
import sys
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# MCP协议基础类 (简化实现)
class MCPServer:
    """MCP服务器基类"""
    
    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.tools: Dict[str, Dict] = {}
        self.capabilities = {
            "tools": {"listChanged": True}
        }
    
    def register_tool(self, name: str, description: str, 
                      input_schema: Dict, handler: callable):
        """注册Tool"""
        self.tools[name] = {
            "name": name,
            "description": description,
            "inputSchema": input_schema,
            "handler": handler
        }
    
    def list_tools(self) -> List[Dict]:
        """列出所有Tools"""
        return [
            {
                "name": t["name"],
                "description": t["description"],
                "inputSchema": t["inputSchema"]
            }
            for t in self.tools.values()
        ]
    
    def call_tool(self, name: str, arguments: Dict) -> Dict:
        """调用Tool"""
        if name not in self.tools:
            return {
                "content": [{"type": "text", "text": f"Tool not found: {name}"}],
                "isError": True
            }
        
        try:
            handler = self.tools[name]["handler"]
            result = handler(arguments)
            return {
                "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}],
                "isError": False
            }
        except Exception as e:
            return {
                "content": [{"type": "text", "text": f"Error: {str(e)}"}],
                "isError": True
            }


class A5LPrimeMCPServer(MCPServer):
    """
    A5L Prime MCP服务器
    
    将A5L SKILL暴露为MCP Tools:
    - a5l_save_analysis: 保存分析
    - a5l_get_decisions: 获取决策
    - a5l_send_signal: 发送信号
    - a5l_query_atoms: 查询Atoms
    - a5l_get_stock_data: 获取股票数据
    """
    
    def __init__(self):
        super().__init__("A5L-Prime", "2.2.0")
        self._register_a5l_tools()
    
    def _register_a5l_tools(self):
        """注册A5L Tools"""
        
        # Tool 1: 保存分析
        self.register_tool(
            name="a5l_save_analysis",
            description="保存股票分析到A5L数据库",
            input_schema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "股票代码"},
                    "content": {"type": "string", "description": "分析内容"},
                    "title": {"type": "string", "description": "分析标题"},
                    "analysis_type": {"type": "string", "enum": ["technical", "fundamental", "composite"]},
                    "tags": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["symbol", "content"]
            },
            handler=self._handle_save_analysis
        )
        
        # Tool 2: 获取决策
        self.register_tool(
            name="a5l_get_decisions",
            description="获取A5L决策记录",
            input_schema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "股票代码筛选"},
                    "status": {"type": "string", "enum": ["pending", "approved", "executed"]},
                    "limit": {"type": "integer", "default": 10}
                }
            },
            handler=self._handle_get_decisions
        )
        
        # Tool 3: 发送交易信号
        self.register_tool(
            name="a5l_send_signal",
            description="创建并保存交易信号",
            input_schema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "股票代码"},
                    "direction": {"type": "string", "enum": ["bullish", "bearish", "neutral"]},
                    "strength": {"type": "number", "description": "信号强度 0-1"},
                    "reason": {"type": "string"}
                },
                "required": ["symbol", "direction", "strength"]
            },
            handler=self._handle_send_signal
        )
        
        # Tool 4: 查询Atoms
        self.register_tool(
            name="a5l_query_atoms",
            description="查询A5L知识库Atoms",
            input_schema={
                "type": "object",
                "properties": {
                    "kind": {"type": "string", "enum": ["analysis", "memo", "decision", "signal"]},
                    "search": {"type": "string", "description": "搜索关键词"},
                    "limit": {"type": "integer", "default": 10}
                }
            },
            handler=self._handle_query_atoms
        )
        
        # Tool 5: 获取数据库统计
        self.register_tool(
            name="a5l_get_stats",
            description="获取A5L数据库统计信息",
            input_schema={
                "type": "object",
                "properties": {}
            },
            handler=self._handle_get_stats
        )
    
    # ============================================
    # Handlers
    # ============================================
    
    def _handle_save_analysis(self, args: Dict) -> Dict:
        """处理保存分析"""
        from database.db_utils import save_analysis
        
        atom_id = save_analysis(
            content=args["content"],
            title=args.get("title"),
            symbol=args.get("symbol"),
            analysis_type=args.get("analysis_type", "general"),
            tags=args.get("tags", [])
        )
        
        return {
            "success": True,
            "atom_id": atom_id,
            "message": f"Analysis saved: {atom_id}"
        }
    
    def _handle_get_decisions(self, args: Dict) -> Dict:
        """处理获取决策"""
        from database.db_utils import get_decisions
        
        decisions = get_decisions(
            symbol=args.get("symbol"),
            status=args.get("status"),
            limit=args.get("limit", 10)
        )
        
        return {
            "success": True,
            "count": len(decisions),
            "decisions": decisions
        }
    
    def _handle_send_signal(self, args: Dict) -> Dict:
        """处理发送信号"""
        from database.db_utils import save_trade_signal
        
        signal_id = save_trade_signal(
            symbol=args["symbol"],
            direction=args["direction"],
            strength=args["strength"],
            reason=args.get("reason"),
            signal_type="mcp_api"
        )
        
        return {
            "success": True,
            "signal_id": signal_id,
            "symbol": args["symbol"],
            "direction": args["direction"],
            "strength": args["strength"]
        }
    
    def _handle_query_atoms(self, args: Dict) -> Dict:
        """处理查询Atoms"""
        from database import get_db_manager
        
        db = get_db_manager()
        
        if args.get("kind"):
            atoms = db.get_atoms_by_kind(args["kind"], args.get("limit", 10))
        elif args.get("search"):
            atoms = db.search_atoms(args["search"], args.get("limit", 10))
        else:
            return {"success": False, "error": "Must specify kind or search"}
        
        return {
            "success": True,
            "count": len(atoms),
            "atoms": [
                {
                    "id": a.id,
                    "kind": a.kind,
                    "title": a.title,
                    "created_at": a.created_at
                }
                for a in atoms
            ]
        }
    
    def _handle_get_stats(self, args: Dict) -> Dict:
        """处理获取统计"""
        from database.db_utils import get_dashboard_stats
        
        dashboard = get_dashboard_stats()
        
        return {
            "success": True,
            "stats": dashboard["stats"],
            "timestamp": dashboard["timestamp"]
        }


# ============================================
# MCP协议适配器
# ============================================

class MCPProtocolAdapter:
    """
    MCP协议适配器
    
    处理标准MCP JSON-RPC请求
    """
    
    def __init__(self, server: A5LPrimeMCPServer):
        self.server = server
    
    def handle_request(self, request: Dict) -> Dict:
        """
        处理MCP请求
        
        Args:
            request: JSON-RPC请求
            
        Returns:
            JSON-RPC响应
        """
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        if method == "initialize":
            return self._handle_initialize(request_id)
        
        elif method == "tools/list":
            return self._handle_tools_list(request_id)
        
        elif method == "tools/call":
            return self._handle_tools_call(request_id, params)
        
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
    
    def _handle_initialize(self, request_id: Any) -> Dict:
        """处理初始化请求"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": self.server.capabilities,
                "serverInfo": {
                    "name": self.server.name,
                    "version": self.server.version
                }
            }
        }
    
    def _handle_tools_list(self, request_id: Any) -> Dict:
        """处理tools/list请求"""
        tools = self.server.list_tools()
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {"tools": tools}
        }
    
    def _handle_tools_call(self, request_id: Any, params: Dict) -> Dict:
        """处理tools/call请求"""
        name = params.get("name")
        arguments = params.get("arguments", {})
        
        result = self.server.call_tool(name, arguments)
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        }


# ============================================
# HTTP服务器 (简化版)
# ============================================

from http.server import HTTPServer, BaseHTTPRequestHandler
import threading


class MCPHTTPHandler(BaseHTTPRequestHandler):
    """MCP HTTP处理器"""
    
    server_instance: A5LPrimeMCPServer = None
    protocol_adapter: MCPProtocolAdapter = None
    
    def log_message(self, format, *args):
        """关闭日志输出"""
        pass
    
    def do_POST(self):
        """处理POST请求"""
        if self.path == "/mcp":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            
            try:
                request = json.loads(body)
                response = self.protocol_adapter.handle_request(request)
            except Exception as e:
                response = {
                    "jsonrpc": "2.0",
                    "error": {"code": -32700, "message": str(e)}
                }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_error(404)
    
    def do_GET(self):
        """处理GET请求 - 健康检查"""
        if self.path == "/health":
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "ok",
                "server": "A5L-Prime-MCP",
                "version": "2.2.0"
            }).encode())
        else:
            self.send_error(404)


def start_mcp_server(port: int = 8080):
    """启动MCP服务器"""
    # 创建服务器实例
    mcp_server = A5LPrimeMCPServer()
    MCPHTTPHandler.server_instance = mcp_server
    MCPHTTPHandler.protocol_adapter = MCPProtocolAdapter(mcp_server)
    
    # 启动HTTP服务器
    httpd = HTTPServer(("0.0.0.0", port), MCPHTTPHandler)
    
    print(f"🚀 A5L Prime MCP Server started on port {port}")
    print(f"   Health: http://localhost:{port}/health")
    print(f"   MCP Endpoint: http://localhost:{port}/mcp")
    print()
    print(f"   Registered Tools ({len(mcp_server.tools)}):")
    for name in mcp_server.tools:
        print(f"     • {name}")
    
    # 在后台线程运行
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    
    return httpd, mcp_server


# ============================================
# 测试
# ============================================

def test_mcp_protocol():
    """测试MCP协议"""
    print("🧪 Testing A5L Prime MCP Protocol...")
    print("=" * 60)
    
    # 创建服务器
    server = A5LPrimeMCPServer()
    adapter = MCPProtocolAdapter(server)
    
    # 测试1: Initialize
    print("\n1️⃣ 测试 Initialize...")
    request = {
        "jsonrpc": "2.0",
        "method": "initialize",
        "id": 1
    }
    response = adapter.handle_request(request)
    print(f"   Server: {response['result']['serverInfo']['name']} v{response['result']['serverInfo']['version']}")
    print("   ✅ Initialize success")
    
    # 测试2: Tools/List
    print("\n2️⃣ 测试 Tools/List...")
    request = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "id": 2
    }
    response = adapter.handle_request(request)
    tools = response['result']['tools']
    print(f"   Available tools: {len(tools)}")
    for tool in tools:
        print(f"     • {tool['name']}: {tool['description'][:40]}...")
    print("   ✅ Tools/List success")
    
    # 测试3: Tools/Call - get_stats
    print("\n3️⃣ 测试 Tools/Call (get_stats)...")
    request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "a5l_get_stats",
            "arguments": {}
        },
        "id": 3
    }
    response = adapter.handle_request(request)
    result = json.loads(response['result']['content'][0]['text'])
    print(f"   Stats: {result['stats']}")
    print("   ✅ Tools/Call success")
    
    # 测试4: Tools/Call - save_analysis
    print("\n4️⃣ 测试 Tools/Call (save_analysis)...")
    request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "a5l_save_analysis",
            "arguments": {
                "symbol": "000001.SZ",
                "content": "MCP协议测试分析",
                "title": "MCP Test"
            }
        },
        "id": 4
    }
    response = adapter.handle_request(request)
    result = json.loads(response['result']['content'][0]['text'])
    print(f"   Result: {result['message']}")
    print("   ✅ Tools/Call success")
    
    print("\n" + "=" * 60)
    print("✅ All MCP Protocol tests passed!")
    
    return server


if __name__ == '__main__':
    test_mcp_protocol()
    
    # 可选：启动HTTP服务器
    # httpd, server = start_mcp_server(8080)
    # input("Press Enter to stop...")
    # httpd.shutdown()
