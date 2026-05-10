#!/usr/bin/env python3
"""
Batch download all parquet files from Feishu
"""
import subprocess
import os
import time

# Complete file list from Feishu (first batch)
files_to_download = [
    # 2013-03
    ("20130307.parquet", "FGxCbv9pFow1B8xQWO4cnWy0n0c"),
    ("20130306.parquet", "HK5wbt1IVowuz7x6azJc1LmInRg"),
    ("20130305.parquet", "VSn6bRR9SoNBfVx10Tzclye4nPc"),
    ("20130304.parquet", "Kx9JbKCf1o574zxizpPcjBQunJg"),
    ("20130301.parquet", "E7rCbSt5EokLdhxryjjcMcxvnvg"),
    # 2013-02
    ("20130228.parquet", "YG8FbC9O2ocyEAx8gvyc9ZW0nYg"),
    ("20130227.parquet", "YZGTbGvkGoE9h7xpPUdcjrHcnQd"),
    ("20130226.parquet", "Q3bqb0uRroHWo4xTeuhckT1XnNg"),
    ("20130225.parquet", "OyrXbq09Boo55gxGdUacFucYnkb"),
    ("20130222.parquet", "Fa8gbZQGjoaiiCxPOQacMccenOg"),
    ("20130221.parquet", "Cur5bN1IaodljLxesAWcatHtnzb"),
    ("20130220.parquet", "J3tZbXmpHoXoB5xioFmcfuTKnbb"),
    ("20130219.parquet", "NBEEbgChNol027xA3IocVqU3nde"),
    ("20130218.parquet", "Ai6hbdqQYo7tGjx2XwdcZLLrn6A"),
    ("20130208.parquet", "LannbWoUqoCuXyxx1O9cRpU6nLy"),
    ("20130207.parquet", "RRcQbwGGGoHepHxRwDNcfy1Jngh"),
    ("20130206.parquet", "TEZQb7basohO8vxnXgkcxHQkn6e"),
    ("20130205.parquet", "Cv1ybFIpvoK86Tx6PhncnwOcnUh"),
    ("20130204.parquet", "SJ0gbfjTWohhqdxKEQlcCEFanMf"),
    ("20130201.parquet", "AeyvbvZqWobWkNx9758cWmiGn3b"),
    # 2013-01
    ("20130131.parquet", "Hdfybduobo8Gr0xwSTycq5THnth"),
    ("20130130.parquet", "DC3vbnZVJoS0vnxPZOLctlhunrd"),
    ("20130129.parquet", "C007bvKrXo7pgqxazo8cNL2onag"),
    ("20130128.parquet", "LXlhbqJg5o8zL6xcqq7ccsZQnUd"),
    ("20130125.parquet", "Xz6wbYdN9odZSxxrmgvcFfKPnVh"),
    ("20130124.parquet", "FJ3HbReYWomzb6xxRPJcid1knaf"),
    ("20130123.parquet", "A4dhbMtjQo2nPKx30SzcwAN1nZr"),
    ("20130122.parquet", "OLOLbFrseo19XTxojdDccJ94nxf"),
    ("20130121.parquet", "S5JZbGkmooav38xVajVcBoGvnph"),
    ("20130118.parquet", "AtXKbx8q8odyFZxbfHZcQRPAnah"),
    ("20130117.parquet", "RoYBbHA3MobUZ4x4hblcSha2nTg"),
    ("20130116.parquet", "CyuQbmLC7o9A5exynjRcTDOKnVe"),
    ("20130115.parquet", "EjCgbdc5CosHmLx2xOwcwD8Nnce"),
    ("20130114.parquet", "RJusbV9T7oYXxFxBPnOcQSdinIc"),
    ("20130111.parquet", "N87qbVSHYoU1eUxOH49clLVGnXd"),
    ("20130110.parquet", "ZB1Ibj5swo7mdTxFMIfcKEwqnwe"),
    ("20130109.parquet", "VdlGbYKd3oMOg5xIyg3cPrmVnGe"),
    ("20130108.parquet", "XJS0b1NNgovHeFxUp79cLf1znnu"),
    ("20130107.parquet", "WdA1b0PPkoeFIYxpERgc3PCJnmg"),
    ("20130104.parquet", "Na2Cbo8U6o3zA9xrW1JctxP1nwh"),
]

print("=" * 70)
print("A5L CIO Historical Data - Batch Download")
print("=" * 70)
print(f"Total files to download: {len(files_to_download)}")
print()

success_count = 0
error_count = 0

for i, (filename, file_token) in enumerate(files_to_download, 1):
    output_path = f"1d_price/{filename}"
    
    # Check if already exists
    if os.path.exists(output_path):
        size = os.path.getsize(output_path)
        print(f"[{i}/{len(files_to_download)}] ✓ {filename} - already exists ({size} bytes)")
        success_count += 1
        continue
    
    print(f"[{i}/{len(files_to_download)}] Downloading {filename}...", end=" ")
    
    try:
        # Use feishu_drive_file tool via subprocess
        result = subprocess.run(
            ["openclaw", "tools", "feishu_drive_file", "download", 
             "--file_token", file_token, 
             "--type", "file",
             "--output_path", output_path],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0 or "saved_path" in result.stdout:
            print(f"✓ Success")
            success_count += 1
        else:
            print(f"✗ Failed: {result.stderr}")
            error_count += 1
            
    except Exception as e:
        print(f"✗ Error: {e}")
        error_count += 1
    
    # Small delay to avoid rate limiting
    time.sleep(0.5)

print()
print("=" * 70)
print(f"Download Summary: {success_count} success, {error_count} errors")
print("=" * 70)
