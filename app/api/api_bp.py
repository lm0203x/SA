"""
API蓝图定义
统一管理所有API路由的注册
"""

from flask import Blueprint

# 创建API蓝图
api_bp = Blueprint('api', __name__, url_prefix='/api')

# 延迟导入路由模块以避免循环导入
def register_routes():
    """注册所有路由到API蓝图"""
    from . import datasource_routes, stock_routes, alert_routes, watchlist_routes, webhook_routes

# 延迟导入 - 在实际使用时再导入路由模块
_routes_registered = False