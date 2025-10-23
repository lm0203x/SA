from flask import Flask
from flask_cors import CORS
from config import config
from app.extensions import db, socketio
from app.utils.logger import setup_logger

def create_app(config_name='default'):
    """应用工厂函数 - 前后端分离架构"""
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    db.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*", async_mode='eventlet')
    
    # 配置CORS - 允许React开发服务器和生产环境访问
    # Vite默认端口是5173，如果需要其他端口请在这里添加
    allowed_origins = [
        "http://localhost:5173",  # Vite开发服务器
        "http://localhost:3000",  # 备用端口
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]
    
    # 如果在生产环境，可以添加生产域名
    if not app.config['DEBUG']:
        # allowed_origins.append("https://your-production-domain.com")
        pass
    
    CORS(app, 
         origins=allowed_origins,
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    
    # 设置日志
    setup_logger(app.config['LOG_LEVEL'], app.config['LOG_FILE'])
    
    # ==================== 注册API蓝图 ====================
    # 核心API - 为前端React应用提供数据
    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # 可选的高级API（如果需要可以启用）
    # 注意：这些模块已被删除，如需使用请先恢复对应文件
    # from app.api.realtime_analysis import realtime_analysis_bp
    # from app.api.realtime_indicators import realtime_indicators_bp
    # from app.api.realtime_signals import realtime_signals_bp
    # from app.api.realtime_monitor import realtime_monitor_bp
    # from app.api.realtime_risk import realtime_risk_bp
    # from app.api.realtime_report import realtime_report_bp
    # from app.api.websocket_api import websocket_api_bp
    # from app.api.ml_factor_api import ml_factor_bp
    # from app.api.test_api import test_bp
    
    # ==================== 旧版模板路由（已禁用）====================
    # 旧版HTML模板路由已被删除，系统现在使用纯API模式
    # 如需恢复旧版功能，请先恢复对应的路由文件
    if app.config.get('ENABLE_LEGACY_TEMPLATES', False):
        app.logger.warning("旧版模板路由已被禁用，请使用前端React应用访问系统")
    
    # ==================== WebSocket事件处理器 ====================
    from app.websocket import websocket_events
    
    return app 