"""
API模块初始化
"""

from flask import Blueprint

# 创建API蓝图（如果还没有创建的话）
try:
    from app.api import api_bp
except ImportError:
    api_bp = Blueprint('api', __name__)

# 导入路由
from app.api import datasource_routes, stock_routes, alert_routes, watchlist_routes