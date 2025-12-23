#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import signal
import sys

from app import create_app
from app.extensions import socketio
from app.tasks.scheduler import start_market_refresh_task

# 创建 Flask 应用实例
app = create_app(os.getenv("FLASK_ENV", "default"))


def signal_handler(sig, frame):
    """处理 Ctrl+C 信号，优雅退出"""
    print("\n" + "=" * 60)
    print("[INFO] 正在关闭服务...")
    print("=" * 60)
    sys.exit(0)


if __name__ == "__main__":
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)

    print("=" * 60)
    print("[INFO] 启动 Flask API 服务中...")
    print("[INFO] API地址: http://127.0.0.1:5000/api")
    print("[INFO] WebSocket地址: ws://127.0.0.1:5000")
    print("[INFO] 允许CORS来源: http://localhost:5173")
    print("[INFO] 提示: 按 Ctrl+C 停止服务")
    print("=" * 60)

    # 启动行情定时刷新任务
    start_market_refresh_task(app)

    try:
        socketio.run(
            app,
            host="0.0.0.0",
            port=5000,
            debug=True,
            use_reloader=False,  # 防止重复启动
            allow_unsafe_werkzeug=True,
            log_output=False,
        )
    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("⏹️  服务器已停止")
        print("=" * 60)
