"""
认证服务
提供用户注册、登录、token验证功能
"""

from app.models.user import User
from app.extensions import db
import jwt
from datetime import datetime, timedelta
from flask import current_app


class AuthService:
    """认证服务类"""

    @staticmethod
    def register(username, password):
        """
        用户注册

        Args:
            username: 用户名
            password: 密码

        Returns:
            dict: 包含 success 和 message/user
        """
        # 检查用户名是否存在
        if User.query.filter_by(username=username).first():
            return {'success': False, 'message': '用户名已存在'}

        # 创建用户
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        return {'success': True, 'user': user.to_dict()}

    @staticmethod
    def login(username, password):
        """
        用户登录

        Args:
            username: 用户名
            password: 密码

        Returns:
            dict: 包含 success 和 token/user 或 message
        """
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            return {'success': False, 'message': '用户名或密码错误'}

        if not user.is_active:
            return {'success': False, 'message': '账号已被禁用'}

        # 生成 token
        secret_key = current_app.config.get('SECRET_KEY', 'your-secret-key-here')
        token = jwt.encode({
            'user_id': user.id,
            'username': user.username,
            'exp': datetime.utcnow() + timedelta(days=7)
        }, secret_key, algorithm='HS256')

        return {
            'success': True,
            'token': token,
            'user': user.to_dict()
        }

    @staticmethod
    def verify_token(token):
        """
        验证 token

        Args:
            token: JWT token

        Returns:
            dict: 包含 success 和 user 或 message
        """
        try:
            secret_key = current_app.config.get('SECRET_KEY', 'your-secret-key-here')
            data = jwt.decode(token, secret_key, algorithms=['HS256'])
            user = User.query.get(data['user_id'])
            if not user or not user.is_active:
                return {'success': False, 'message': '用户不存在或已被禁用'}
            return {'success': True, 'user': user}
        except jwt.ExpiredSignatureError:
            return {'success': False, 'message': 'token已过期'}
        except jwt.InvalidTokenError:
            return {'success': False, 'message': '无效token'}
        except Exception as e:
            return {'success': False, 'message': f'验证失败: {str(e)}'}

    @staticmethod
    def get_user_by_id(user_id):
        """
        通过ID获取用户

        Args:
            user_id: 用户ID

        Returns:
            User or None
        """
        return User.query.get(user_id)
