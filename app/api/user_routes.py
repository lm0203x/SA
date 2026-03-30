"""
用户管理接口
"""

from flask import jsonify, request
from loguru import logger

from app.api import api_bp
from app.extensions import db
from app.models.user import User
from app.services.auth_service import AuthService
from app.services.operation_log_service import OperationLogService
from app.utils.auth import get_request_user


@api_bp.route('/users', methods=['POST'])
def create_user():
    try:
        data = request.get_json() or {}
        username = (data.get('username') or '').strip()
        password = data.get('password') or ''

        if not username or not password:
            return jsonify({'success': False, 'message': '请输入用户名和密码'}), 400

        result = AuthService.register(username, password)
        if result.get('success'):
            OperationLogService.record(
                module='user',
                action_type='create',
                action_name='创建用户',
                user=get_request_user(),
                target_type='user',
                target_id=result['user']['id'],
                target_name=result['user']['username'],
                message='用户创建成功',
            )
            return jsonify(result), 201

        OperationLogService.record(
            module='user',
            action_type='create',
            action_name='创建用户',
            status='failed',
            user=get_request_user(),
            target_type='user',
            target_name=username,
            message=result.get('message'),
        )
        return jsonify(result), 400
    except Exception as exc:
        logger.error(f"创建用户失败: {exc}")
        return jsonify({'success': False, 'message': str(exc)}), 500


@api_bp.route('/users', methods=['GET'])
def get_users():
    try:
        users = User.query.order_by(User.created_at.desc(), User.id.desc()).all()
        current_user = get_request_user()
        OperationLogService.record(
            module='user',
            action_type='view',
            action_name='查看用户列表',
            user=current_user,
            message=f'共返回 {len(users)} 个用户',
        )
        return jsonify({
            'success': True,
            'data': [user.to_dict() for user in users],
        })
    except Exception as exc:
        logger.error(f"获取用户列表失败: {exc}")
        return jsonify({'success': False, 'message': str(exc)}), 500


@api_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404

        data = request.get_json() or {}
        if 'username' in data:
            username = (data.get('username') or '').strip()
            if len(username) < 3:
                return jsonify({'success': False, 'message': '用户名至少3个字符'}), 400
            existing = User.query.filter(User.username == username, User.id != user_id).first()
            if existing:
                return jsonify({'success': False, 'message': '用户名已存在'}), 400
            user.username = username

        if 'password' in data and data.get('password'):
            if len(data['password']) < 6:
                return jsonify({'success': False, 'message': '密码至少6个字符'}), 400
            user.set_password(data['password'])

        if 'is_active' in data:
            user.is_active = bool(data['is_active'])

        db.session.commit()
        OperationLogService.record(
            module='user',
            action_type='update',
            action_name='更新用户',
            user=get_request_user(),
            target_type='user',
            target_id=user.id,
            target_name=user.username,
            message='用户信息更新成功',
            detail={'updated_fields': sorted(list(data.keys()))},
        )
        return jsonify({
            'success': True,
            'message': '更新成功',
            'data': user.to_dict(),
        })
    except Exception as exc:
        db.session.rollback()
        logger.error(f"更新用户失败: {exc}")
        return jsonify({'success': False, 'message': str(exc)}), 500


@api_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404

        if user.username == 'admin':
            return jsonify({'success': False, 'message': '不能删除admin用户'}), 400

        username = user.username
        db.session.delete(user)
        db.session.commit()
        OperationLogService.record(
            module='user',
            action_type='delete',
            action_name='删除用户',
            user=get_request_user(),
            target_type='user',
            target_id=user_id,
            target_name=username,
            message='用户删除成功',
        )
        return jsonify({'success': True, 'message': '删除成功'})
    except Exception as exc:
        db.session.rollback()
        logger.error(f"删除用户失败: {exc}")
        return jsonify({'success': False, 'message': str(exc)}), 500
