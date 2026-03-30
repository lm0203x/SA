"""
认证路由
提供用户注册、登录接口
"""

from flask import request, jsonify
from app.api import api_bp
from app.services.auth_service import AuthService
from app.services.operation_log_service import OperationLogService
from app.utils.auth import get_request_user


@api_bp.route('/auth/register', methods=['POST'])
def register():
    """
    用户注册接口

    请求体:
        {
            "username": "用户名",
            "password": "密码"
        }

    响应:
        {
            "success": true/false,
            "message": "错误信息",
            "user": {用户信息}
        }
    """
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '请求体不能为空'})

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'success': False, 'message': '请输入用户名和密码'})

    if len(username) < 3:
        return jsonify({'success': False, 'message': '用户名至少3个字符'})

    if len(password) < 6:
        return jsonify({'success': False, 'message': '密码至少6个字符'})

    result = AuthService.register(username, password)
    OperationLogService.record(
        module='auth',
        action_type='register',
        action_name='用户注册',
        status='success' if result.get('success') else 'failed',
        user=get_request_user(),
        target_type='user',
        target_name=username,
        message=result.get('message') or ('注册成功' if result.get('success') else '注册失败'),
    )
    return jsonify(result)


@api_bp.route('/auth/login', methods=['POST'])
def login():
    """
    用户登录接口

    请求体:
        {
            "username": "用户名",
            "password": "密码"
        }

    响应:
        {
            "success": true/false,
            "message": "错误信息",
            "token": "JWT token",
            "user": {用户信息}
        }
    """
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '请求体不能为空'})

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'success': False, 'message': '请输入用户名和密码'})

    result = AuthService.login(username, password)
    OperationLogService.record(
        module='auth',
        action_type='login',
        action_name='用户登录',
        status='success' if result.get('success') else 'failed',
        user_id=result.get('user', {}).get('id') if result.get('success') else None,
        username=username,
        target_type='user',
        target_name=username,
        message=result.get('message') or ('登录成功' if result.get('success') else '登录失败'),
    )
    return jsonify(result)


@api_bp.route('/auth/me', methods=['GET'])
def get_current_user():
    """
    获取当前用户信息

    请求头:
        Authorization: Bearer <token>

    响应:
        {
            "success": true/false,
            "message": "错误信息",
            "user": {用户信息}
        }
    """
    # 从 header 获取 token
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({'success': False, 'message': '未提供认证令牌'})

    try:
        # 解析 Bearer token
        token = auth_header.split(' ')[1] if ' ' in auth_header else auth_header
    except IndexError:
        return jsonify({'success': False, 'message': '令牌格式错误'})

    result = AuthService.verify_token(token)
    if result['success']:
        return jsonify({'success': True, 'user': result['user'].to_dict()})
    return jsonify(result)


@api_bp.route('/auth/logout', methods=['POST'])
def logout():
    """
    用户登出接口

    客户端需要删除本地存储的 token
    """
    return jsonify({'success': True, 'message': '登出成功'})
