#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化启动脚本 - 不使用SocketIO，避免卡死问题
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

def open_browser():
    """延迟打开浏览器"""
    time.sleep(2)
    webbrowser.open('http://localhost:5002/ml-factor')

def main():
    """主函数"""
    print("🚀 启动多因子选股系统（简化版）...")
    print("📱 访问地址:")
    print("   - 主页: http://localhost:5002")
    print("   - 多因子系统: http://localhost:5002/ml-factor")
    print("   - API文档: http://localhost:5002/api")
    print("\n💡 提示: 按 Ctrl+C 停止服务器")
    
    try:
        # 导入Flask应用（不使用SocketIO）
        from flask import Flask
        from flask_cors import CORS
        from config import config
        from app.extensions import db
        from app.utils.logger import setup_logger
        
        # 创建简化的Flask应用，指定模板和静态文件路径
        app = Flask(__name__, 
                   template_folder='app/templates',
                   static_folder='app/static')
        app.config.from_object(config['default'])
        
        # 初始化扩展（不包括socketio）
        db.init_app(app)
        CORS(app)
        
        # 设置日志
        setup_logger(app.config['LOG_LEVEL'], app.config['LOG_FILE'])
        
        # 注册蓝图
        from app.api import api_bp
        from app.api.ml_factor_api import ml_factor_bp
        from app.routes.ml_factor_routes import ml_factor_routes
        from app.main import main_bp
        
        app.register_blueprint(api_bp, url_prefix='/api')
        app.register_blueprint(ml_factor_bp)
        app.register_blueprint(ml_factor_routes)
        app.register_blueprint(main_bp)
        
        # 启动浏览器线程
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # 启动Flask服务器（不使用SocketIO）
        app.run(host='127.0.0.1', port=5002, debug=False, use_reloader=False)
        
    except KeyboardInterrupt:
        print("\n👋 服务器已停止，感谢使用!")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print("💡 建议使用快速启动: python quick_start_fixed.py")

if __name__ == "__main__":
    main()