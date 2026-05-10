#!/usr/bin/env python3
"""
Download all parquet files from Feishu 1d_price folder
"""
import json
import subprocess
import os
import sys

# File list (from API responses)
files_batch_1 = [
    ("20130307.parquet", "FGxCbv9pFow1B8xQWO4cnWy0n0c"),
    ("20130306.parquet", "HK5wbt1IVowuz7x6azJc1LmInRg"),
    ("20130305.parquet", "VSn6bRR9SoNBfVx10Tzclye4nPc"),
    ("20130304.parquet", "Kx9JbKCf1o574zxizpPcjBQunJg"),
    ("20130301.parquet", "E7rCbSt5EokLdhxryjjcMcxvnvg"),
    ("20130228.parquet", "YG8FbC9O2ocyEAx8gvyc9ZW0nYg"),
    ("20130227.parquet", "YZGTbGvkGoE9h7xpPUdcjrHcnQd"),
    ("20130226.parquet", "Q3bqb0uRroHWo4xTeuhckT1XnNg"),
    ("20130225.parquet", "OyrXbq09Boo55gxGdUacFucYnkb"),
    ("20130222.parquet", "Fa8gbZQGjoaiiCxPOQacMccenOg"),
]

# Create target directory
os.makedirs("1d_price", exist_ok=True)

print("=" * 60)
print("Feishu 1d_price Data Download Script")
print("=" * 60)
print(f"Files to download: {len(files_batch_1)}")
print()

# Download each file
for filename, file_token in files_batch_1:
    output_path = f"1d_price/{filename}"
    
    if os.path.exists(output_path):
        print(f"✓ {filename} - already exists")
        continue
    
    print(f"Downloading {filename}...")
    
    # Use feishu_drive_file download
    result = subprocess.run([
        "python3", "-c",
        f"""
import sys
sys.path.insert(0, '/workspace/projects/workspace')
from tools.feishu_drive_file import feishu_drive_file_download
try:
    feishu_drive_file_download('{file_token}', '{output_path}')
    print('SUCCESS')
except Exception as e:
    print(f'ERROR: {{e}}')
"""
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"  ✓ Downloaded successfully")
    else:
        print(f"  ✗ Error: {result.stderr}")

print()
print("=" * 60)
print("Download batch complete!")
print("=" * 60)
