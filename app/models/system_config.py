"""
系统配置模型
支持AI配置、Tushare配置等系统参数管理
"""

from datetime import datetime
from app.extensions import db
import json
from cryptography.fernet import Fernet
import base64


class SystemConfig(db.Model):
    """系统配置模型"""

    __tablename__ = 'system_configs'

    id = db.Column(db.Integer, primary_key=True)
    config_key = db.Column(db.String(100), unique=True, nullable=False, comment='配置键')
    config_value = db.Column(db.Text, comment='配置值(加密存储)')
    config_type = db.Column(db.String(20), default='string', comment='配置类型:string/json/encrypted')
    description = db.Column(db.String(200), comment='配置描述')
    is_encrypted = db.Column(db.Boolean, default=False, comment='是否加密存储')
    is_active = db.Column(db.Boolean, default=True, comment='是否启用')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')

    # 加密密钥（应该从环境变量获取）
    _cipher = None

    @classmethod
    def get_cipher(cls):
        """获取加密器"""
        if cls._cipher is None:
            # 从环境变量获取密钥，如果没有则使用默认密钥
            secret_key = db.app.config.get('CONFIG_SECRET_KEY', 'default-secret-key-32-chars!')
            # 确保密钥长度为32字节
            if len(secret_key) < 32:
                secret_key = secret_key.ljust(32, '0')
            else:
                secret_key = secret_key[:32]
            key = base64.urlsafe_b64encode(secret_key.encode())
            cls._cipher = Fernet(key)
        return cls._cipher

    @classmethod
    def get_config(cls, config_key, default_value=None):
        """获取配置值"""
        config = cls.query.filter_by(config_key=config_key, is_active=True).first()
        if not config:
            return default_value

        if config.is_encrypted:
            try:
                cipher = cls.get_cipher()
                decrypted_value = cipher.decrypt(config.config_value.encode()).decode()
                if config.config_type == 'json':
                    return json.loads(decrypted_value)
                return decrypted_value
            except Exception:
                return default_value
        else:
            if config.config_type == 'json':
                return json.loads(config.config_value) if config.config_value else {}
            return config.config_value

    @classmethod
    def set_config(cls, config_key, config_value, config_type='string',
                   description='', is_encrypted=False):
        """设置配置值"""
        config = cls.query.filter_by(config_key=config_key).first()

        if is_encrypted:
            try:
                cipher = cls.get_cipher()
                if config_type == 'json':
                    value_str = json.dumps(config_value, ensure_ascii=False)
                else:
                    value_str = str(config_value)
                encrypted_value = cipher.encrypt(value_str.encode()).decode()
            except Exception:
                encrypted_value = str(config_value)
        else:
            if config_type == 'json':
                encrypted_value = json.dumps(config_value, ensure_ascii=False)
            else:
                encrypted_value = str(config_value)

        if config:
            config.config_value = encrypted_value
            config.config_type = config_type
            config.description = description
            config.is_encrypted = is_encrypted
            config.updated_at = datetime.utcnow()
        else:
            config = cls(
                config_key=config_key,
                config_value=encrypted_value,
                config_type=config_type,
                description=description,
                is_encrypted=is_encrypted
            )
            db.session.add(config)

        db.session.commit()
        return config

    @classmethod
    def get_ai_config(cls):
        """获取AI配置"""
        return {
            'provider': cls.get_config('ai_provider', 'tongyi'),
            'tongyi': {
                'api_key': cls.get_config('tongyi_api_key', ''),
                'model': cls.get_config('tongyi_model', 'qwen-plus'),
                'base_url': cls.get_config('tongyi_base_url', 'https://dashscope.aliyuncs.com/api/v1'),
                'timeout': int(cls.get_config('tongyi_timeout', 30))
            },
            'openai': {
                'api_key': cls.get_config('openai_api_key', ''),
                'model': cls.get_config('openai_model', 'gpt-3.5-turbo'),
                'base_url': cls.get_config('openai_base_url', 'https://api.openai.com/v1'),
                'timeout': int(cls.get_config('openai_timeout', 30))
            },
            'ollama': {
                'base_url': cls.get_config('ollama_base_url', 'http://localhost:11434'),
                'model': cls.get_config('ollama_model', 'qwen2.5-coder'),
                'timeout': int(cls.get_config('ollama_timeout', 30))
            }
        }

    @classmethod
    def set_ai_config(cls, ai_config):
        """设置AI配置"""
        # 设置提供者
        cls.set_config('ai_provider', ai_config.get('provider', 'tongyi'))

        # 设置通义千问配置
        tongyi_config = ai_config.get('tongyi', {})
        cls.set_config('tongyi_api_key', tongyi_config.get('api_key', ''), 'string', '通义千问API密钥', True)
        cls.set_config('tongyi_model', tongyi_config.get('model', 'qwen-plus'), 'string', '通义千问模型')
        cls.set_config('tongyi_base_url', tongyi_config.get('base_url', 'https://dashscope.aliyuncs.com/api/v1'), 'string', '通义千问API地址')
        cls.set_config('tongyi_timeout', tongyi_config.get('timeout', 30), 'string', '通义千问超时时间')

        # 设置OpenAI配置
        openai_config = ai_config.get('openai', {})
        cls.set_config('openai_api_key', openai_config.get('api_key', ''), 'string', 'OpenAI API密钥', True)
        cls.set_config('openai_model', openai_config.get('model', 'gpt-3.5-turbo'), 'string', 'OpenAI模型')
        cls.set_config('openai_base_url', openai_config.get('base_url', 'https://api.openai.com/v1'), 'string', 'OpenAI API地址')
        cls.set_config('openai_timeout', openai_config.get('timeout', 30), 'string', 'OpenAI超时时间')

        # 设置Ollama配置
        ollama_config = ai_config.get('ollama', {})
        cls.set_config('ollama_base_url', ollama_config.get('base_url', 'http://localhost:11434'), 'string', 'Ollama API地址')
        cls.set_config('ollama_model', ollama_config.get('model', 'qwen2.5-coder'), 'string', 'Ollama模型')
        cls.set_config('ollama_timeout', ollama_config.get('timeout', 30), 'string', 'Ollama超时时间')

    @classmethod
    def get_all_configs(cls):
        """获取所有配置"""
        configs = cls.query.filter_by(is_active=True).all()
        result = {}
        for config in configs:
            result[config.config_key] = {
                'value': cls.get_config(config.config_key),
                'type': config.config_type,
                'description': config.description,
                'is_encrypted': config.is_encrypted,
                'updated_at': config.updated_at.isoformat() if config.updated_at else None
            }
        return result

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'config_key': self.config_key,
            'config_value': '***ENCRYPTED***' if self.is_encrypted else self.config_value,
            'config_type': self.config_type,
            'description': self.description,
            'is_encrypted': self.is_encrypted,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }