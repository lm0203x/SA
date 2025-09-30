#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from app import create_app
from app.extensions import socketio

# 创建Flask应用实例
app = create_app(os.getenv('FLASK_ENV', 'default'))

if __name__ == '__main__':
    # 开发环境下运行，使用SocketIO
    print("=" * 60)
    print("🚀 启动 Flask API 服务器...")
    print(f"📡 API地址: http://127.0.0.1:5000/api")
    print(f"🔌 WebSocket地址: ws://127.0.0.1:5000")
    print(f"🌐 允许CORS来源: http://localhost:5173")
    print("=" * 60)
    
    socketio.run(
        app,
        host='0.0.0.0',  # 改为0.0.0.0以便前端访问
        port=5000,
        debug=True,  # 开启debug模式，显示日志
        use_reloader=False,  # 关闭自动重载（避免重复启动）
        allow_unsafe_werkzeug=True
    ) 