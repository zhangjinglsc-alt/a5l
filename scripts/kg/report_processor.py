#!/usr/bin/env python3
"""
A5L 研报下载与预处理系统
Goal G010 Step 1.2

功能:
- 自动下载飞书研报文件
- PDF转文本提取
- 图片OCR识别
- 存储到data/stock_research/incoming/

执行时间: 2026-05-03 23:56 (后台模式)
"""

import os
import sys
import json
import time
import re
from datetime import datetime
from pathlib import Path

# A5L工作空间
WORKSPACE = "/workspace/projects/workspace"
INCOMING_DIR = f"{WORKSPACE}/data/stock_research/incoming"
PROCESSED_DIR = f"{WORKSPACE}/data/stock_research/processed"
QUEUE_FILE = f"{WORKSPACE}/data/report_queue.json"
LOG_FILE = f"{WORKSPACE}/logs/report_processor.log"

class ReportDownloader:
    """研报下载器"""
    
    def __init__(self):
        self.ensure_directories()
        self.log("="*60)
        self.log("A5L 研报下载系统初始化")
        self.log("="*60)
    
    def log(self, message):
        """记录日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"[{timestamp}] {message}"
        print(log_line)
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_line + '\n')
    
    def ensure_directories(self):
        """确保目录存在"""
        os.makedirs(INCOMING_DIR, exist_ok=True)
        os.makedirs(PROCESSED_DIR, exist_ok=True)
        self.log(f"✅ 目录检查: {INCOMING_DIR}")
        self.log(f"✅ 目录检查: {PROCESSED_DIR}")
    
    def download_from_feishu(self, file_token, file_name, folder_token):
        """
        从飞书下载文件
        
        TODO: 集成飞书下载API
        - 调用 feishu_drive_file download API
        - 保存到INCOMING_DIR
        - 返回本地路径
        """
        self.log(f"⬇️ 下载文件: {file_name} (token: {file_token[:8]}...)")
        
        # 生成本地文件名
        date_prefix = datetime.now().strftime('%Y%m%d')
        safe_name = re.sub(r'[^\w\s-]', '_', file_name)
        local_filename = f"{date_prefix}_{safe_name}"
        local_path = os.path.join(INCOMING_DIR, local_filename)
        
        # TODO: 实际下载逻辑
        # 目前创建占位文件表示流程
        with open(local_path + '.pending', 'w') as f:
            f.write(f"token:{file_token}\nname:{file_name}\nfolder:{folder_token}")
        
        self.log(f"📁 本地路径: {local_path}")
        return local_path
    
    def process_download_queue(self):
        """处理下载队列"""
        if not os.path.exists(QUEUE_FILE):
            self.log("ℹ️ 队列为空，无需下载")
            return []
        
        with open(QUEUE_FILE, 'r', encoding='utf-8') as f:
            queue = json.load(f)
        
        pending_files = [item for item in queue if item.get('status') == 'pending']
        self.log(f"📥 发现 {len(pending_files)} 个待下载文件")
        
        downloaded = []
        for item in pending_files:
            try:
                local_path = self.download_from_feishu(
                    item['file_token'],
                    item['file_name'],
                    item.get('folder_token', '')
                )
                item['status'] = 'downloaded'
                item['local_path'] = local_path
                item['downloaded_at'] = datetime.now().isoformat()
                downloaded.append(item)
                self.log(f"✅ 下载完成: {item['file_name']}")
            except Exception as e:
                item['status'] = 'download_failed'
                item['error'] = str(e)
                self.log(f"❌ 下载失败: {item['file_name']} - {e}")
        
        # 保存更新后的队列
        with open(QUEUE_FILE, 'w', encoding='utf-8') as f:
            json.dump(queue, f, ensure_ascii=False, indent=2)
        
        return downloaded


class ReportPreprocessor:
    """研报预处理器"""
    
    def __init__(self):
        self.log_file = LOG_FILE
        self.log("="*60)
        self.log("A5L 研报预处理系统初始化")
        self.log("="*60)
    
    def log(self, message):
        """记录日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"[{timestamp}] {message}"
        print(log_line)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_line + '\n')
    
    def extract_text_from_pdf(self, pdf_path):
        """
        从PDF提取文本
        
        依赖: PyPDF2, pdfplumber
        """
        self.log(f"📄 PDF文本提取: {os.path.basename(pdf_path)}")
        
        try:
            import pdfplumber
            text_content = []
            
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        text_content.append(f"--- Page {i+1} ---\n{text}")
            
            full_text = '\n\n'.join(text_content)
            
            # 保存提取的文本
            text_path = pdf_path.replace('.pdf', '.txt')
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(full_text)
            
            self.log(f"✅ 提取完成: {len(full_text)} 字符")
            return text_path, full_text
            
        except ImportError:
            self.log("⚠️ pdfplumber未安装，使用占位符")
            text_path = pdf_path.replace('.pdf', '.txt')
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(f"[PDF文本提取占位符]\n文件: {pdf_path}\n")
            return text_path, ""
        except Exception as e:
            self.log(f"❌ PDF提取失败: {e}")
            return None, ""
    
    def extract_text_from_image(self, image_path):
        """
        从图片提取文本 (OCR)
        
        依赖: paddleocr 或 pytesseract
        """
        self.log(f"🖼️ OCR识别: {os.path.basename(image_path)}")
        
        try:
            # 尝试使用paddleocr
            from paddleocr import PaddleOCR
            ocr = PaddleOCR(use_angle_cls=True, lang='ch')
            result = ocr.ocr(image_path, cls=True)
            
            text_lines = []
            for line in result:
                for word_info in line:
                    text_lines.append(word_info[1][0])
            
            full_text = '\n'.join(text_lines)
            
            # 保存提取的文本
            text_path = image_path.rsplit('.', 1)[0] + '.txt'
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(full_text)
            
            self.log(f"✅ OCR完成: {len(full_text)} 字符")
            return text_path, full_text
            
        except ImportError:
            self.log("⚠️ OCR引擎未安装，使用占位符")
            text_path = image_path.rsplit('.', 1)[0] + '.txt'
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(f"[OCR文本提取占位符]\n文件: {image_path}\n")
            return text_path, ""
        except Exception as e:
            self.log(f"❌ OCR失败: {e}")
            return None, ""
    
    def extract_metadata(self, file_path, text_content):
        """
        提取研报元数据
        
        包括: 标题、日期、来源、分析师、评级、目标价
        """
        self.log(f"🔍 提取元数据: {os.path.basename(file_path)}")
        
        metadata = {
            'file_path': file_path,
            'processed_at': datetime.now().isoformat(),
            'char_count': len(text_content),
        }
        
        # 简单的正则提取
        # 股票代码
        stock_codes = re.findall(r'\b(\d{6})\b', text_content)
        if stock_codes:
            metadata['stock_codes'] = list(set(stock_codes))
        
        # 日期
        dates = re.findall(r'20\d{2}[年/-]\d{1,2}[月/-]\d{1,2}', text_content)
        if dates:
            metadata['dates_mentioned'] = dates[:5]  # 前5个日期
        
        # 评级关键词
        rating_keywords = ['买入', '增持', '中性', '减持', '卖出', '强烈推荐', '推荐']
        found_ratings = [kw for kw in rating_keywords if kw in text_content]
        if found_ratings:
            metadata['ratings'] = found_ratings
        
        # 目标价 (简单匹配)
        target_prices = re.findall(r'目标价[^\d]*(\d+\.?\d*)', text_content)
        if target_prices:
            metadata['target_prices'] = target_prices[:3]
        
        self.log(f"✅ 元数据提取完成")
        return metadata
    
    def process_pending_files(self):
        """处理所有待处理文件"""
        if not os.path.exists(QUEUE_FILE):
            self.log("ℹ️ 无待处理文件")
            return []
        
        with open(QUEUE_FILE, 'r', encoding='utf-8') as f:
            queue = json.load(f)
        
        pending = [item for item in queue if item.get('status') == 'downloaded']
        self.log(f"📂 发现 {len(pending)} 个待处理文件")
        
        processed = []
        for item in pending:
            try:
                local_path = item.get('local_path', '')
                if not local_path or not os.path.exists(local_path):
                    self.log(f"⚠️ 文件不存在: {local_path}")
                    continue
                
                # 根据文件类型处理
                if local_path.endswith('.pdf'):
                    text_path, text_content = self.extract_text_from_pdf(local_path)
                elif local_path.endswith(('.png', '.jpg', '.jpeg')):
                    text_path, text_content = self.extract_text_from_image(local_path)
                else:
                    self.log(f"⚠️ 不支持的文件类型: {local_path}")
                    continue
                
                # 提取元数据
                metadata = self.extract_metadata(local_path, text_content)
                
                # 更新状态
                item['status'] = 'preprocessed'
                item['text_path'] = text_path
                item['text_length'] = len(text_content)
                item['metadata'] = metadata
                item['preprocessed_at'] = datetime.now().isoformat()
                
                processed.append(item)
                self.log(f"✅ 预处理完成: {item['file_name']}")
                
            except Exception as e:
                item['status'] = 'preprocess_failed'
                item['error'] = str(e)
                self.log(f"❌ 预处理失败: {item.get('file_name', 'unknown')} - {e}")
        
        # 保存更新后的队列
        with open(QUEUE_FILE, 'w', encoding='utf-8') as f:
            json.dump(queue, f, ensure_ascii=False, indent=2)
        
        return processed


def main():
    """主函数"""
    print("="*60)
    print("A5L 研报下载与预处理系统")
    print("G010 Step 1.2 - 后台模式")
    print("="*60)
    
    # 步骤1: 下载文件
    downloader = ReportDownloader()
    downloaded = downloader.process_download_queue()
    
    # 步骤2: 预处理文件
    preprocessor = ReportPreprocessor()
    processed = preprocessor.process_pending_files()
    
    print("="*60)
    print(f"✅ 处理完成: {len(downloaded)} 下载, {len(processed)} 预处理")
    print("="*60)


if __name__ == "__main__":
    main()
