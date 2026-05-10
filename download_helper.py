#!/usr/bin/env python3
"""
尝试多种方式下载飞书文件
"""
import requests
import os
import json

TARGET_DIR = "/workspace/projects/workspace/A5L_v2.1_DEV/cio_awakening/data/historical"
FILE_KEY = "file_v3_0011i_6497f931-041f-45e5-8790-aaa2c0f5929g"
MESSAGE_ID = "om_x100b50c2b96c7ca4c3183b0bef0d3c7"

def try_direct_download():
    """尝试直接下载"""
    # 飞书文件下载URL格式
    url = f"https://open.feishu.cn/open-apis/im/v1/files/{FILE_KEY}"
    
    headers = {
        "Authorization": f"Bearer {os.environ.get('FEISHU_ACCESS_TOKEN', '')}"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"Direct download status: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"Direct download failed: {e}")
        return False

def check_file_exists():
    """检查目标文件是否已存在"""
    target_file = os.path.join(TARGET_DIR, "1d_price.zip")
    if os.path.exists(target_file):
        size = os.path.getsize(target_file)
        print(f"File already exists: {target_file} ({size} bytes)")
        return True
    return False

if __name__ == "__main__":
    os.makedirs(TARGET_DIR, exist_ok=True)
    
    if check_file_exists():
        print("✅ 文件已存在，无需下载")
    else:
        print("⏳ 尝试下载文件...")
        try_direct_download()
        print("\n💡 建议: 使用HTTP上传 http://14.103.87.246")
