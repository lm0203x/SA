"""
AI配置模型
用于存储和管理各种AI服务提供商的配置信息
"""

from datetime import datetime
from app.extensions import db


class AIConfig(db.Model):
    """AI配置模型"""
    __tablename__ = 'ai_config'

    id = db.Column(db.Integer, primary_key=True)
    provider_type = db.Column(db.String(50), nullable=False)  # tongyi, openai, ollama
    provider_name = db.Column(db.String(100), nullable=False)  # AI服务名称
    config_data = db.Column(db.JSON)  # 配置数据（API密钥、模型、地址等）
    is_active = db.Column(db.Boolean, default=False)  # 是否激活
    is_default = db.Column(db.Boolean, default=False)  # 是否为默认AI服务
    status = db.Column(db.String(20), default='未测试')  # 连接状态：成功、失败、未测试
    last_test_time = db.Column(db.DateTime)  # 最后测试时间
    error_message = db.Column(db.Text)  # 错误信息
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    @classmethod
    def get_active_config(cls):
        """获取当前激活的AI配置"""
        # 获取默认配置
        config = cls.query.filter_by(
            is_active=True,
            is_default=True
        ).first()

        if not config:
            # 如果没有默认配置，获取第一个激活的
            config = cls.query.filter_by(is_active=True).first()

        return config

    @classmethod
    def get_default_config(cls):
        """获取默认AI配置"""
        return cls.query.filter_by(is_active=True, is_default=True).first()

    def set_as_default(self):
        """设置为默认配置"""
        # 取消其他同类型配置的默认状态
        AIConfig.query.filter(
            AIConfig.provider_type == self.provider_type,
            AIConfig.id != self.id
        ).update({'is_default': False})

        self.is_default = True
        db.session.commit()

    def get_api_key(self):
        """获取API密钥（安全处理）"""
        if self.config_data and 'api_key' in self.config_data:
            # 返回掩码后的API密钥
            api_key = self.config_data['api_key']
            if len(api_key) > 8:
                return api_key[:4] + '*' * (len(api_key) - 8) + api_key[-4:]
            return '*' * len(api_key)
        return None

    def get_safe_config_data(self):
        """获取安全的配置数据（隐藏敏感信息）"""
        if not self.config_data:
            return {}

        safe_data = self.config_data.copy()
        if 'api_key' in safe_data:
            api_key = safe_data['api_key']
            if len(api_key) > 8:
                safe_data['api_key'] = api_key[:4] + '*' * (len(api_key) - 8) + api_key[-4:]
            else:
                safe_data['api_key'] = '*' * len(api_key)

        return safe_data

    def to_dict(self, include_sensitive=False):
        """转换为字典"""
        config_data = self.config_data if include_sensitive else self.get_safe_config_data()

        return {
            'id': self.id,
            'provider_type': self.provider_type,
            'provider_name': self.provider_name,
            'config_data': config_data,
            'is_active': self.is_active,
            'is_default': self.is_default,
            'status': self.status,
            'last_test_time': self.last_test_time.isoformat() if self.last_test_time else None,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def get_config_dict(cls):
        """获取配置字典格式（兼容原有AI服务）"""
        config = cls.get_active_config()
        if not config:
            return {
                'provider': 'tongyi',
                'tongyi': {
                    'api_key': '',
                    'model': 'qwen-plus',
                    'base_url': 'https://dashscope.aliyuncs.com/api/v1',
                    'timeout': 600
                },
                'openai': {
                    'api_key': '',
                    'model': 'gpt-3.5-turbo',
                    'base_url': 'https://api.openai.com/v1',
                    'timeout': 600
                },
                'ollama': {
                    'base_url': 'http://localhost:11434',
                    'model': 'qwen2.5-coder',
                    'timeout': 600
                }
            }

        # 构建配置字典
        result = {
            'provider': config.provider_type
        }

        # 添加当前配置
        current_config = config.config_data or {}
        result[config.provider_type] = current_config

        # 添加默认配置（确保结构完整）
        default_configs = {
            'tongyi': {
                'api_key': '',
                'model': 'qwen-plus',
                'base_url': 'https://dashscope.aliyuncs.com/api/v1',
                'timeout': 600
            },
            'openai': {
                'api_key': '',
                'model': 'gpt-3.5-turbo',
                'base_url': 'https://api.openai.com/v1',
                'timeout': 600
            },
            'ollama': {
                'base_url': 'http://localhost:11434',
                'model': 'qwen2.5-coder',
                'timeout': 600
            }
        }

        for provider, default_config in default_configs.items():
            if provider not in result:
                result[provider] = default_config

        return result

    def __repr__(self):
        return f'<AIConfig {self.provider_name} ({self.provider_type})>'