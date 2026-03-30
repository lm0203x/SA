"""
API模块初始化
"""

from flask import Blueprint

# 创建API蓝图
api_bp = Blueprint('api', __name__)

# 导入路由
from app.api import datasource_routes, stock_routes, alert_routes, watchlist_routes, ai_routes, config_routes, ai_config_routes, webhook_routes, auth_routes, user_routes, operation_log_routes
