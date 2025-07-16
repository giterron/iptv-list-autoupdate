import requests
import os
import sys
from datetime import datetime
import gzip
import shutil
import json

def fetch_iptv_list():
    # 原始嗅探参数
    headers = {
        "Host": "rihou.cc:555",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        "User-Agent": "okhttp/5.0.0-alpha.14"
    }
    
    # 原始URL（不带结尾斜杠）
    base_url = "http://rihou.cc:555/gggg.nzk"
    
    # 创建会话对象以处理重定向
    session = requests.Session()
    session.max_redirects = 5
    
    # 初始请求（应收到301重定向）
    try:
        print(f"Initial request: {base_url}")
        response = session.get(
            base_url, 
            headers=headers, 
            allow_redirects=False,
            timeout=15
        )
        
        # 检查301重定向
        if response.status_code == 301:
            redirect_url = response.headers.get('Location', base_url + '/')
            print(f"Redirected to: {redirect_url}")
        else:
            redirect_url = base_url + '/'
            print(f"Unexpected status {response.status_code}, using fallback URL")
            
        # 访问重定向后的URL
        response = session.get(
            redirect_url, 
            headers=headers, 
            allow_redirects=True,  # 允许跟随重定向
            timeout=15
        )
        response.raise_for_status()
        
        # 获取最终URL（解决所有重定向后）
        final_url = response.url
        content_type = response.headers.get('Content-Type', 'text/plain')
        encoding = response.headers.get('Content-Encoding', 'identity')
        
        print(f"Success! Final URL: {final_url}")
        print(f"Content-Type: {content_type}, Encoding: {encoding}")
        
        content = response.content
        
        # 处理gzip编码
        if encoding == 'gzip':
            print("Decompressing gzip content")
            content = gzip.decompress(content)
        
        # 将内容解码为文本
        content_str = content.decode('utf-8')
        print(f"Content size: {len(content_str)} characters")
        
        # 保存文件（模拟原始文件格式）
        with open('list.nzk', 'w', encoding='utf-8') as f:
            f.write(content_str)
            
        # 输出元数据
        metadata = {
            "timestamp": datetime.utcnow().isoformat(),
            "source_url": base_url,
            "final_url": final_url,
            "content_length": len(content_str),
            "status": "success"
        }
        with open('update-meta.json', 'w', encoding='utf-8') as f:
            json.dump(metadata, f)
            
        # 为GitHub Actions设置输出
        print(f"::set-output name=final_url::{final_url}")
        
        return True
        
    except Exception as e:
        import traceback
        error_info = {
            "error": str(e),
            "traceback": traceback.format_exc(),
            "timestamp": datetime.utcnow().isoformat()
        }
        print(f"Error fetching list: {e}")
        with open('update-meta.json', 'w', encoding='utf-8') as f:
            json.dump(error_info, f)
        return False

if __name__ == "__main__":
    if fetch_iptv_list():
        sys.exit(0)
    else:
        sys.exit(1)
