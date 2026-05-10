#!/usr/bin/env python3
"""
A5L 数据文件上传客户端
在本地运行此脚本上传 1d_price.zip 到服务器
"""
import requests
import sys
import os
from pathlib import Path

def upload_file(filepath):
    """上传文件到A5L服务器"""
    
    if not os.path.exists(filepath):
        print(f"❌ 错误: 文件不存在 - {filepath}")
        return False
    
    filename = os.path.basename(filepath)
    file_size = os.path.getsize(filepath)
    
    print(f"📤 准备上传: {filename}")
    print(f"📦 文件大小: {file_size / 1024 / 1024:.2f} MB")
    print(f"🎯 目标服务器: http://14.103.87.246:8080")
    print("-" * 50)
    
    # 上传文件
    url = "http://14.103.87.246:8080/upload"
    
    with open(filepath, 'rb') as f:
        files = {'file': (filename, f, 'application/zip')}
        
        try:
            response = requests.post(url, files=files, timeout=300)
            
            if response.status_code == 200:
                print("✅ 上传成功！")
                print("🚀 A5L v2.1 升级流水线已启动！")
                print("\n⏰ 升级时间表:")
                print("  01:45 - 数据解压与验证")
                print("  03:00 - 第1次进度汇报")
                print("  05:00 - 第2次进度汇报") 
                print("  07:00 - 第3次进度汇报")
                print("  09:30 - 完整报告交付")
                return True
            else:
                print(f"❌ 上传失败: {response.text}")
                return False
                
        except requests.exceptions.ConnectionError:
            print("❌ 连接失败: 无法连接到服务器")
            print("💡 请检查网络连接或联系管理员")
            return False
        except Exception as e:
            print(f"❌ 上传出错: {e}")
            return False

def main():
    # 默认文件路径
    default_path = r"E:\BaiduNetdiskDownload\1d_price.zip"
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    elif os.path.exists(default_path):
        filepath = default_path
    else:
        print("📁 请输入文件路径:")
        filepath = input("> ").strip().strip('"')
    
    # 执行上传
    success = upload_file(filepath)
    
    if not success:
        print("\n💡 提示:")
        print("  1. 确保文件路径正确")
        print("  2. 确保网络连接正常")
        print("  3. 或使用浏览器访问: http://14.103.87.246:8080")
        sys.exit(1)

if __name__ == "__main__":
    main()
