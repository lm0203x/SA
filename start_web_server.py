#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动Web服务器脚本
"""

import os
import sys
import webbrowser
import time
import threading
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app import create_app

def open_browser():
    """延迟打开浏览器"""
    time.sleep(2)
    webbrowser.open('http://localhost:5000/ml-factor')

def main():
    """主函数"""
    print("🚀 启动多因子选股系统...")
    print("📱 访问地址:")
    print("   - 主页: http://localhost:5000")
    print("   - 多因子系统: http://localhost:5000/ml-factor")
    print("   - API文档: http://localhost:5000/api")
    print("\n💡 提示: 按 Ctrl+C 停止服务器")
    
    try:
        # 创建Flask应用
        app = create_app('development')
        
        # 启动浏览器线程
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # 启动Flask服务器
        app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)
        
    except KeyboardInterrupt:
        print("\n👋 服务器已停止，感谢使用!")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

if __name__ == "__main__":
    main()