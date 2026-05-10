#!/usr/bin/env python3
"""
Simple HTTP file upload server for large files
"""
import http.server
import socketserver
import os
import cgi
import shutil
from pathlib import Path

PORT = 8080
UPLOAD_DIR = "/workspace/projects/workspace/A5L_v2.1_DEV/cio_awakening/data/historical"

class UploadHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>A5L数据文件上传</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }}
        .upload-box {{ border: 3px dashed #ccc; padding: 40px; text-align: center; border-radius: 10px; }}
        .upload-box:hover {{ border-color: #007bff; background: #f8f9fa; }}
        button {{ background: #007bff; color: white; padding: 15px 30px; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; }}
        button:hover {{ background: #0056b3; }}
        #status {{ margin-top: 20px; padding: 15px; border-radius: 5px; display: none; }}
        .success {{ background: #d4edda; color: #155724; }}
        .error {{ background: #f8d7da; color: #721c24; }}
        .progress {{ margin-top: 20px; }}
        progress {{ width: 100%; height: 30px; }}
    </style>
</head>
<body>
    <h1>🚀 A5L v2.1 数据文件上传</h1>
    <div class="upload-box">
        <h2>拖拽文件到这里上传</h2>
        <p>或点击选择文件</p>
        <input type="file" id="fileInput" style="display:none">
        <button onclick="document.getElementById('fileInput').click()">选择文件</button>
        <div class="progress" id="progressDiv" style="display:none">
            <progress id="progressBar" value="0" max="100"></progress>
            <p id="progressText">0%</p>
        </div>
    </div>
    <div id="status"></div>
    
    <script>
        const uploadBox = document.querySelector('.upload-box');
        const fileInput = document.getElementById('fileInput');
        const status = document.getElementById('status');
        const progressDiv = document.getElementById('progressDiv');
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');
        
        uploadBox.addEventListener('dragover', (e) => {{ e.preventDefault(); uploadBox.style.borderColor = '#007bff'; }});
        uploadBox.addEventListener('dragleave', (e) => {{ e.preventDefault(); uploadBox.style.borderColor = '#ccc'; }});
        uploadBox.addEventListener('drop', (e) => {{
            e.preventDefault();
            uploadBox.style.borderColor = '#ccc';
            handleFile(e.dataTransfer.files[0]);
        }});
        
        fileInput.addEventListener('change', (e) => {{ handleFile(e.target.files[0]); }});
        
        function handleFile(file) {{
            if (!file) return;
            if (file.name !== '1d_price.zip') {{
                showStatus('请上传名为 1d_price.zip 的文件', 'error');
                return;
            }}
            
            const formData = new FormData();
            formData.append('file', file);
            
            progressDiv.style.display = 'block';
            status.style.display = 'none';
            
            const xhr = new XMLHttpRequest();
            xhr.upload.addEventListener('progress', (e) => {{
                if (e.lengthComputable) {{
                    const percent = Math.round((e.loaded / e.total) * 100);
                    progressBar.value = percent;
                    progressText.textContent = percent + '% (' + formatBytes(e.loaded) + ' / ' + formatBytes(e.total) + ')';
                }}
            }});
            
            xhr.addEventListener('load', () => {{
                progressDiv.style.display = 'none';
                if (xhr.status === 200) {{
                    showStatus('✅ 上传成功！系统已开始自动升级...', 'success');
                }} else {{
                    showStatus('❌ 上传失败: ' + xhr.responseText, 'error');
                }}
            }});
            
            xhr.addEventListener('error', () => {{
                progressDiv.style.display = 'none';
                showStatus('❌ 上传出错，请重试', 'error');
            }});
            
            xhr.open('POST', '/upload');
            xhr.send(formData);
        }}
        
        function showStatus(msg, type) {{
            status.textContent = msg;
            status.className = type;
            status.style.display = 'block';
        }}
        
        function formatBytes(bytes) {{
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }}
    </script>
</body>
</html>
"""
        self.wfile.write(html.encode())
    
    def do_POST(self):
        if self.path == '/upload':
            content_type = self.headers.get('Content-Type', '')
            if 'multipart/form-data' in content_type:
                boundary = content_type.split('boundary=')[1].split(';')[0].strip()
                
                # Read the entire request body
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)
                
                # Parse multipart form data
                boundary_bytes = ('--' + boundary).encode()
                parts = body.split(boundary_bytes)
                
                for part in parts:
                    if b'filename="' in part and b'Content-Type:' in part:
                        # Extract filename
                        filename_start = part.find(b'filename="') + 10
                        filename_end = part.find(b'"', filename_start)
                        filename = part[filename_start:filename_end].decode()
                        
                        # Extract file content
                        header_end = part.find(b'\r\n\r\n') + 4
                        file_content = part[header_end:].rstrip(b'\r\n--')
                        
                        # Save file
                        os.makedirs(UPLOAD_DIR, exist_ok=True)
                        filepath = os.path.join(UPLOAD_DIR, filename)
                        with open(filepath, 'wb') as f:
                            f.write(file_content)
                        
                        self.send_response(200)
                        self.end_headers()
                        self.wfile.write(b'Upload successful')
                        print(f"File uploaded: {filepath} ({len(file_content)} bytes)")
                        return
                
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'No file found')
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'Invalid content type')
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == '__main__':
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    with socketserver.TCPServer(("0.0.0.0", PORT), UploadHandler) as httpd:
        print(f"Upload server running at http://0.0.0.0:{PORT}")
        print(f"Files will be saved to: {UPLOAD_DIR}")
        httpd.serve_forever()
