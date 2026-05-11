#!/usr/bin/env python3
"""
A5L Prime MCP Server Runner
MCP服务器启动器

Usage:
    python run_mcp_server.py [--port 8080]
"""

import sys
import time
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from wave1.mcp_server_real import start_mcp_server


def main():
    parser = argparse.ArgumentParser(description='A5L Prime MCP Server')
    parser.add_argument('--port', type=int, default=8080, help='Server port')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon')
    args = parser.parse_args()
    
    print("=" * 60)
    print("🚀 A5L Prime MCP Server")
    print("=" * 60)
    
    # 启动服务器
    httpd, server = start_mcp_server(args.port)
    
    print("\n✅ Server is running!")
    print(f"   Port: {args.port}")
    print(f"   Health: http://localhost:{args.port}/health")
    print(f"   MCP: http://localhost:{args.port}/mcp")
    print()
    
    if args.daemon:
        print("Running in daemon mode...")
        while True:
            time.sleep(60)
    else:
        print("Press Ctrl+C to stop...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 Shutting down...")
            httpd.shutdown()
            print("✅ Server stopped")


if __name__ == '__main__':
    main()
