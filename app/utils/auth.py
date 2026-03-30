"""
认证辅助函数
"""

from flask import request

from app.services.auth_service import AuthService


def get_request_user():
    """从Authorization头解析当前用户，失败时返回None"""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None

    token = auth_header.split(' ', 1)[1] if ' ' in auth_header else auth_header
    result = AuthService.verify_token(token)
    if result.get('success'):
        return result.get('user')
    return None
