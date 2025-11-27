"""
Webhook配置模型
存储各种Webhook通知的配置信息
"""

from app.extensions import db
from datetime import datetime
from sqlalchemy import Index
import json


class WebhookConfig(db.Model):
    """Webhook配置模型"""
    __tablename__ = 'webhook_configs'

    # ==================== 基础字段 ====================
    id = db.Column(db.Integer, primary_key=True, comment='配置ID')
    name = db.Column(db.String(100), nullable=False, comment='Webhook名称')
    type = db.Column(db.String(50), nullable=False, comment='Webhook类型')
    url = db.Column(db.Text, nullable=False, comment='Webhook URL')
    description = db.Column(db.Text, comment='描述')

    # ==================== 认证配置 ====================
    secret = db.Column(db.String(255), comment='签名密钥')
    app_key = db.Column(db.String(100), comment='应用密钥')
    app_secret = db.Column(db.String(255), comment='应用密钥')

    # ==================== 请求配置 ====================
    method = db.Column(db.String(10), default='POST', comment='HTTP方法')
    headers = db.Column(db.Text, comment='HTTP头信息JSON')
    timeout = db.Column(db.Integer, default=30, comment='超时时间(秒)')
    retry_count = db.Column(db.Integer, default=3, comment='重试次数')

    # ==================== 消息配置 ====================
    message_template = db.Column(db.Text, comment='消息模板')
    content_type = db.Column(db.String(50), default='application/json', comment='内容类型')

    # ==================== 状态管理 ====================
    is_enabled = db.Column(db.Boolean, default=True, comment='是否启用')
    is_active = db.Column(db.Boolean, default=True, comment='是否活跃')

    # ==================== 统计信息 ====================
    success_count = db.Column(db.Integer, default=0, comment='成功次数')
    failure_count = db.Column(db.Integer, default=0, comment='失败次数')
    last_sent_at = db.Column(db.DateTime, comment='最后发送时间')
    last_status = db.Column(db.String(20), comment='最后状态')

    # ==================== 时间戳 ====================
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')

    # ==================== 扩展配置 ====================
    extra_config = db.Column(db.Text, comment='扩展配置JSON')

    # ==================== 数据库索引 ====================
    __table_args__ = (
        Index('idx_webhook_configs_type_enabled', 'type', 'is_enabled'),
        Index('idx_webhook_configs_active', 'is_active'),
        Index('idx_webhook_configs_created_at', 'created_at'),
    )

    # ==================== Webhook类型常量 ====================
    WEBHOOK_TYPES = {
        'feishu': '飞书',
        'dingtalk': '钉钉',
        'wechat_work': '企业微信',
        'slack': 'Slack',
        'telegram': 'Telegram',
        'email': '邮件',
        'generic': '通用HTTP'
    }

    # ==================== HTTP方法常量 ====================
    HTTP_METHODS = {
        'GET': 'GET',
        'POST': 'POST',
        'PUT': 'PUT',
        'PATCH': 'PATCH'
    }

    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'type_name': self.WEBHOOK_TYPES.get(self.type, self.type),
            'url': self.url,
            'description': self.description,
            'method': self.method,
            'headers': json.loads(self.headers) if self.headers else {},
            'timeout': self.timeout,
            'retry_count': self.retry_count,
            'message_template': self.message_template,
            'content_type': self.content_type,
            'is_enabled': self.is_enabled,
            'is_active': self.is_active,
            'success_count': self.success_count,
            'failure_count': self.failure_count,
            'last_sent_at': self.last_sent_at.isoformat() if self.last_sent_at else None,
            'last_status': self.last_status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'extra_config': json.loads(self.extra_config) if self.extra_config else {}
        }

    @classmethod
    def create_config(cls, name: str, webhook_type: str, url: str,
                      description: str = None, **kwargs) -> 'WebhookConfig':
        """创建Webhook配置"""

        config = cls(
            name=name,
            type=webhook_type,
            url=url,
            description=description,
            method=kwargs.get('method', 'POST'),
            headers=json.dumps(kwargs.get('headers', {})) if kwargs.get('headers') else None,
            timeout=kwargs.get('timeout', 30),
            retry_count=kwargs.get('retry_count', 3),
            message_template=kwargs.get('message_template'),
            content_type=kwargs.get('content_type', 'application/json'),
            secret=kwargs.get('secret'),
            app_key=kwargs.get('app_key'),
            app_secret=kwargs.get('app_secret'),
            extra_config=json.dumps(kwargs.get('extra_config')) if kwargs.get('extra_config') else None
        )

        db.session.add(config)
        db.session.commit()
        return config

    def update_config(self, **kwargs):
        """更新配置"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                if key in ['headers', 'extra_config'] and value:
                    setattr(self, key, json.dumps(value))
                else:
                    setattr(self, key, value)

        self.updated_at = datetime.utcnow()
        db.session.commit()

    def enable(self):
        """启用配置"""
        self.is_enabled = True
        self.updated_at = datetime.utcnow()
        db.session.commit()

    def disable(self):
        """禁用配置"""
        self.is_enabled = False
        self.updated_at = datetime.utcnow()
        db.session.commit()

    def record_success(self):
        """记录成功发送"""
        self.success_count += 1
        self.last_sent_at = datetime.utcnow()
        self.last_status = 'success'
        db.session.commit()

    def record_failure(self):
        """记录发送失败"""
        self.failure_count += 1
        self.last_sent_at = datetime.utcnow()
        self.last_status = 'failure'
        db.session.commit()

    def delete_config(self):
        """软删除配置"""
        self.is_active = False
        self.updated_at = datetime.utcnow()
        db.session.commit()

    def get_headers_dict(self) -> dict:
        """获取HTTP头信息字典"""
        if self.headers:
            try:
                return json.loads(self.headers)
            except:
                return {}
        return {}

    def get_extra_config_dict(self) -> dict:
        """获取扩展配置字典"""
        if self.extra_config:
            try:
                return json.loads(self.extra_config)
            except:
                return {}
        return {}

    def get_success_rate(self) -> float:
        """获取成功率"""
        total = self.success_count + self.failure_count
        if total == 0:
            return 0.0
        return (self.success_count / total) * 100

    @classmethod
    def get_enabled_configs(cls, webhook_type: str = None) -> list:
        """获取启用的配置"""
        query = cls.query.filter_by(is_enabled=True, is_active=True)

        if webhook_type:
            query = query.filter_by(type=webhook_type)

        return query.order_by(cls.created_at.desc()).all()

    @classmethod
    def get_by_type(cls, webhook_type: str) -> list:
        """根据类型获取配置"""
        return cls.query.filter_by(
            type=webhook_type,
            is_enabled=True,
            is_active=True
        ).order_by(cls.created_at.desc()).all()

    @classmethod
    def get_stats(cls) -> dict:
        """获取统计信息"""
        from sqlalchemy import func

        # 按类型统计
        type_stats = db.session.query(
            cls.type,
            func.count(cls.id).label('count'),
            func.sum(cls.success_count).label('success_count'),
            func.sum(cls.failure_count).label('failure_count')
        ).filter_by(is_active=True).group_by(cls.type).all()

        stats = {}
        for stat in type_stats:
            stats[stat.type] = {
                'config_count': stat.count,
                'success_count': stat.success_count or 0,
                'failure_count': stat.failure_count or 0,
                'success_rate': (stat.success_count or 0) / max((stat.success_count or 0) + (stat.failure_count or 0), 1) * 100
            }

        return stats