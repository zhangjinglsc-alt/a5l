#!/usr/bin/env python3
"""
SKILL隐私扫描器
在开源前自动扫描敏感信息
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple

class PrivacyScanner:
    """隐私信息扫描器"""
    
    # 敏感模式定义
    PATTERNS = {
        'api_key': [
            r'api[_-]?key\s*[=:]\s*["\']?[a-zA-Z0-9]{16,}["\']?',
            r'secret[_-]?key\s*[=:]\s*["\']?[a-zA-Z0-9]{16,}["\']?',
            r'token\s*[=:]\s*["\']?[a-zA-Z0-9]{20,}["\']?',
            r'sk-[a-zA-Z0-9]{48}',  # OpenAI API Key
            r'ghp_[a-zA-Z0-9]{36}',  # GitHub Personal Token
        ],
        'ip_address': [
            r'\b(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b',
        ],
        'email': [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        ],
        'phone': [
            r'1[3-9]\d{9}',  # 中国手机号
            r'\+86\s*1[3-9]\d{9}',
        ],
        'account_id': [
            r'ou_[a-f0-9]{24}',  # 飞书 open_id
            r'oc_[a-f0-9]{24}',  # 飞书 chat_id
        ],
        'internal_url': [
            r'https?://(?:192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+|172\.(?:1[6-9]|2\d|3[01])\.\d+\.\d+)',
            r'https?://[a-z0-9-]+\.internal\.',
            r'https?://[a-z0-9-]+\.local',
        ],
        'position_data': [
            r'持仓.*\d{4,}',  # 持仓金额
            r'盈亏.*[+-]?\d{4,}',
            r'市值.*\d{4,}',
        ]
    }
    
    # 白名单 - 允许的内容
    WHITELIST = [
        'example.com',
        'test@example.com',
        '127.0.0.1',
        'localhost',
        '0.0.0.0',
        'user@domain.com',
    ]
    
    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.findings = []
        
    def scan_file(self, file_path: Path) -> List[Tuple[str, int, str, str]]:
        """扫描单个文件"""
        findings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
        except Exception as e:
            return [(str(file_path), 0, 'ERROR', str(e))]
        
        # 检查每一行
        for line_num, line in enumerate(lines, 1):
            # 跳过白名单
            if any(w in line for w in self.WHITELIST):
                continue
                
            for category, patterns in self.PATTERNS.items():
                for pattern in patterns:
                    matches = re.finditer(pattern, line, re.IGNORECASE)
                    for match in matches:
                        finding = (
                            str(file_path.relative_to(self.skill_path)),
                            line_num,
                            category,
                            match.group()[:50]  # 截断长匹配
                        )
                        findings.append(finding)
        
        return findings
    
    def scan_directory(self) -> List[Tuple[str, int, str, str]]:
        """扫描整个目录"""
        all_findings = []
        
        # 要扫描的文件扩展名
        extensions = {'.md', '.py', '.json', '.yaml', '.yml', '.sh', '.txt'}
        
        for ext in extensions:
            for file_path in self.skill_path.rglob(f'*{ext}'):
                if file_path.is_file():
                    findings = self.scan_file(file_path)
                    all_findings.extend(findings)
        
        return all_findings
    
    def generate_report(self) -> dict:
        """生成扫描报告"""
        findings = self.scan_directory()
        
        # 按类别统计
        category_counts = {}
        for _, _, category, _ in findings:
            category_counts[category] = category_counts.get(category, 0) + 1
        
        return {
            'skill_path': str(self.skill_path),
            'total_findings': len(findings),
            'category_counts': category_counts,
            'findings': findings,
            'passed': len(findings) == 0
        }
    
    def print_report(self, report: dict):
        """打印报告"""
        print(f"🔍 隐私扫描报告: {report['skill_path']}")
        print("=" * 60)
        
        if report['passed']:
            print("✅ 通过 - 未发现敏感信息")
            return True
        
        print(f"⚠️ 发现 {report['total_findings']} 处潜在敏感信息:\n")
        
        # 按类别分组
        for category, count in report['category_counts'].items():
            print(f"  {category}: {count} 处")
        
        print("\n📋 详细信息:")
        for file, line, category, match in report['findings'][:10]:  # 只显示前10个
            print(f"  - {file}:{line} [{category}] {match}")
        
        if len(report['findings']) > 10:
            print(f"  ... 还有 {len(report['findings']) - 10} 处")
        
        print("\n❌ 未通过隐私扫描")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 privacy_scanner.py <skill_path>")
        sys.exit(1)
    
    skill_path = sys.argv[1]
    
    if not os.path.exists(skill_path):
        print(f"❌ 路径不存在: {skill_path}")
        sys.exit(1)
    
    scanner = PrivacyScanner(skill_path)
    report = scanner.generate_report()
    passed = scanner.print_report(report)
    
    sys.exit(0 if passed else 1)

if __name__ == "__main__":
    main()
