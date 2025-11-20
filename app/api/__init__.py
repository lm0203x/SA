"""
API模块初始化
"""

# 导入API蓝图
from .api_bp import api_bp

# 导出API蓝图供其他模块使用
__all__ = ['api_bp']