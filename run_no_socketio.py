#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整系统启动脚本 - 不使用SocketIO版本
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
    webbrowser.open('http://localhost:5004/ml-factor')

def create_app_no_socketio(config_name='default'):
    """创建不使用SocketIO的Flask应用"""
    from flask import Flask
    from flask_cors import CORS
    from config import config
    from app.extensions import db
    from app.utils.logger import setup_logger
    
    # 指定正确的模板和静态文件路径
    app = Flask(__name__, 
                template_folder='app/templates',
                static_folder='app/static')
    
    # 加载配置
    app.config.from_object(config[config_name])
    
    # 初始化扩展（不包括socketio）
    db.init_app(app)
    CORS(app)
    
    # 设置日志
    setup_logger(app.config['LOG_LEVEL'], app.config['LOG_FILE'])
    
    # 注册蓝图（只注册核心功能，避免复杂依赖）
    try:
        from app.api import api_bp
        app.register_blueprint(api_bp, url_prefix='/api')
        print("✅ 注册API蓝图")
    except Exception as e:
        print(f"⚠️ API蓝图注册失败: {e}")
    
    try:
        from app.api.ml_factor_api import ml_factor_bp
        app.register_blueprint(ml_factor_bp)
        print("✅ 注册多因子API蓝图")
    except Exception as e:
        print(f"⚠️ 多因子API蓝图注册失败: {e}")
    
    try:
        from app.routes.ml_factor_routes import ml_factor_routes
        app.register_blueprint(ml_factor_routes)
        print("✅ 注册多因子路由蓝图")
    except Exception as e:
        print(f"⚠️ 多因子路由蓝图注册失败: {e}")
    
    try:
        from app.main import main_bp
        app.register_blueprint(main_bp)
        print("✅ 注册主蓝图")
    except Exception as e:
        print(f"⚠️ 主蓝图注册失败: {e}")
    
    # 注册实时分析相关API蓝图
    try:
        from app.api.realtime_analysis import realtime_analysis_bp
        app.register_blueprint(realtime_analysis_bp)
        print("✅ 注册实时分析API蓝图")
    except Exception as e:
        print(f"⚠️ 实时分析API蓝图注册失败: {e}")
    
    try:
        from app.api.realtime_indicators import realtime_indicators_bp
        app.register_blueprint(realtime_indicators_bp, url_prefix='/api/realtime-analysis/indicators')
        print("✅ 注册实时指标API蓝图")
    except Exception as e:
        print(f"⚠️ 实时指标API蓝图注册失败: {e}")
    
    try:
        from app.api.realtime_signals import realtime_signals_bp
        app.register_blueprint(realtime_signals_bp, url_prefix='/api/realtime-analysis/signals')
        print("✅ 注册实时信号API蓝图")
    except Exception as e:
        print(f"⚠️ 实时信号API蓝图注册失败: {e}")
    
    try:
        from app.api.realtime_monitor import realtime_monitor_bp
        app.register_blueprint(realtime_monitor_bp, url_prefix='/api/realtime-analysis/monitor')
        print("✅ 注册实时监控API蓝图")
    except Exception as e:
        print(f"⚠️ 实时监控API蓝图注册失败: {e}")
    
    try:
        from app.routes.realtime_analysis_routes import realtime_analysis_routes
        app.register_blueprint(realtime_analysis_routes)
        print("✅ 注册实时分析路由蓝图")
    except Exception as e:
        print(f"⚠️ 实时分析路由蓝图注册失败: {e}")
    
    # 不注册WebSocket相关的内容
    
    return app

def main():
    """主函数"""
    print("🚀 启动多因子选股系统（完整版-无SocketIO）...")
    print("📱 访问地址:")
    print("   - 主页: http://localhost:5004")
    print("   - 多因子系统: http://localhost:5004/ml-factor")
    print("   - API文档: http://localhost:5004/api")
    print("\n💡 提示: 按 Ctrl+C 停止服务器")
    
    try:
        # 创建应用
        app = create_app_no_socketio('development')
        
        # 启动浏览器线程
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # 启动Flask服务器
        app.run(host='127.0.0.1', port=5004, debug=False, use_reloader=False)
        
    except KeyboardInterrupt:
        print("\n👋 服务器已停止，感谢使用!")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()