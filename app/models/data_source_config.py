"""
数据源配置模型
用于存储和管理各种数据源的配置信息
"""

from datetime import datetime
from app.extensions import db


class DataSourceConfig(db.Model):
    """数据源配置模型"""
    __tablename__ = 'data_source_config'
    
    id = db.Column(db.Integer, primary_key=True)
    source_type = db.Column(db.String(50), nullable=False)  # tushare, yahoo, custom
    source_name = db.Column(db.String(100), nullable=False)  # 数据源名称
    config_data = db.Column(db.JSON)  # 配置数据（如API Token等）
    is_active = db.Column(db.Boolean, default=False)  # 是否激活
    is_default = db.Column(db.Boolean, default=False)  # 是否为默认数据源
    status = db.Column(db.String(20), default='未测试')  # 连接状态：成功、失败、未测试
    last_test_time = db.Column(db.DateTime)  # 最后测试时间
    error_message = db.Column(db.Text)  # 错误信息
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'source_type': self.source_type,
            'source_name': self.source_name,
            'config_data': self.config_data,
            'is_active': self.is_active,
            'is_default': self.is_default,
            'status': self.status,
            'last_test_time': self.last_test_time.isoformat() if self.last_test_time else None,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<DataSourceConfig {self.source_name} ({self.source_type})>'
