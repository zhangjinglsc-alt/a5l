#!/usr/bin/env python3
"""
A5L Test Runner
测试运行器

Usage:
    python tests/run_tests.py
    python tests/run_tests.py --verbose
    python tests/run_tests.py --coverage
"""

import sys
import argparse
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))


def main():
    parser = argparse.ArgumentParser(description='A5L Test Runner')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--coverage', '-c', action='store_true', help='Run with coverage')
    parser.add_argument('--module', '-m', help='Test specific module (database/mcp/feishu)')
    
    args = parser.parse_args()
    
    print("🚀 A5L Test Runner")
    print("=" * 60)
    
    if args.coverage:
        try:
            import coverage
            cov = coverage.Coverage()
            cov.start()
        except ImportError:
            print("⚠️ Coverage not installed. Install with: pip install coverage")
            args.coverage = False
    
    # 运行测试
    import importlib.util
    spec = importlib.util.spec_from_file_location("test_a5l", str(Path(__file__).parent / "test_a5l.py"))
    test_module = importlib.util.module_from_spec(spec)
    sys.modules["test_a5l"] = test_module
    spec.loader.exec_module(test_module)
    exit_code = test_module.run_tests()
    
    if args.coverage:
        cov.stop()
        cov.save()
        print("\n📊 Coverage Report:")
        cov.report()
    
    return exit_code


if __name__ == '__main__':
    exit(main())
