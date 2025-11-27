"""
自选股模型
"""

from app.extensions import db
from datetime import datetime


class Watchlist(db.Model):
    """自选股列表"""
    __tablename__ = 'watchlist'
    
    id = db.Column(db.Integer, primary_key=True)
    ts_code = db.Column(db.String(20), unique=True, nullable=False, index=True, comment='股票代码')
    symbol = db.Column(db.String(10), comment='简称')
    name = db.Column(db.String(50), comment='股票名称')
    
    # 用户备注
    note = db.Column(db.String(200), comment='用户备注')
    
    # 添加时间
    added_at = db.Column(db.DateTime, default=datetime.utcnow, comment='添加时间')
    
    # 最后更新时间
    last_sync = db.Column(db.DateTime, comment='最后同步时间')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'ts_code': self.ts_code,
            'symbol': self.symbol,
            'name': self.name,
            'note': self.note,
            'added_at': self.added_at.isoformat() if self.added_at else None,
            'last_sync': self.last_sync.isoformat() if self.last_sync else None
        }
    
    def __repr__(self):
        return f'<Watchlist {self.ts_code} {self.name}>'
