#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import signal
import sys
from app import create_app
from app.extensions import socketio

# 创建Flask应用实例
app = create_app(os.getenv('FLASK_ENV', 'default'))

def signal_handler(sig, frame):
    """处理Ctrl+C信号，优雅退出"""
    print("\n" + "=" * 60)
    print("[INFO] 正在关闭服务器...")
    print("=" * 60)
    sys.exit(0)

if __name__ == '__main__':
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)

    # 开发环境下运行，使用SocketIO
    print("=" * 60)
    print("[INFO] 启动 Flask API 服务器...")
    print(f"[INFO] API地址: http://127.0.0.1:5000/api")
    print(f"[INFO] WebSocket地址: ws://127.0.0.1:5000")
    print(f"[INFO] 允许CORS来源: http://localhost:5173")
    print(f"[INFO] 提示: 按 Ctrl+C 停止服务器")
    print("=" * 60)
    
    try:
        socketio.run(
            app,
            host='0.0.0.0',  # 改为0.0.0.0以便前端访问
            port=5000,
            debug=True,  # 开启debug模式，显示日志
            use_reloader=False,  # 关闭自动重载（避免重复启动）
            allow_unsafe_werkzeug=True,
            log_output=False  # 减少eventlet日志输出
        )
    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("⏹️  服务器已停止")
        print("=" * 60) 