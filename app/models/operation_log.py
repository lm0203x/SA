"""
操作日志模型
"""

from datetime import datetime

from app.extensions import db


class OperationLog(db.Model):
    """持久化记录后台关键操作"""

    __tablename__ = 'operation_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True, comment='用户ID')
    username = db.Column(db.String(80), nullable=True, index=True, comment='用户名')
    module = db.Column(db.String(50), nullable=False, index=True, comment='模块')
    action_type = db.Column(db.String(50), nullable=False, index=True, comment='操作类型')
    action_name = db.Column(db.String(100), nullable=False, comment='操作名称')
    target_type = db.Column(db.String(50), nullable=True, comment='操作对象类型')
    target_id = db.Column(db.String(100), nullable=True, comment='操作对象ID')
    target_name = db.Column(db.String(255), nullable=True, comment='操作对象名称')
    request_path = db.Column(db.String(255), nullable=True, comment='请求路径')
    request_method = db.Column(db.String(10), nullable=True, comment='请求方法')
    status = db.Column(db.String(20), nullable=False, default='success', index=True, comment='结果状态')
    message = db.Column(db.String(255), nullable=True, comment='摘要信息')
    detail_json = db.Column(db.JSON, nullable=True, comment='详细信息')
    ip = db.Column(db.String(45), nullable=True, comment='请求IP')
    user_agent = db.Column(db.String(500), nullable=True, comment='用户代理')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True, comment='创建时间')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.username,
            'module': self.module,
            'action_type': self.action_type,
            'action_name': self.action_name,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'target_name': self.target_name,
            'request_path': self.request_path,
            'request_method': self.request_method,
            'status': self.status,
            'message': self.message,
            'detail_json': self.detail_json or {},
            'ip': self.ip,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
