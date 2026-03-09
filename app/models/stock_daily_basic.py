from app.extensions import db
from sqlalchemy import Column, String, Date, DECIMAL

class StockDailyBasic(db.Model):
    """股票日线基本数据表"""
    __tablename__ = 'stock_daily_basic'
    
    ts_code = Column(String(20), primary_key=True, comment='TS股票代码')
    trade_date = Column(Date, primary_key=True, comment='交易日期')
    close = Column(DECIMAL(10, 2), comment='当日收盘价')
    turnover_rate = Column(DECIMAL(10, 2), comment='换手率（%）')
    turnover_rate_f = Column(DECIMAL(10, 2), comment='换手率（自由流通股）')
    volume_ratio = Column(DECIMAL(10, 2), comment='量比')
    pe = Column(DECIMAL(10, 2), comment='市盈率')
    pe_ttm = Column(DECIMAL(10, 2), comment='市盈率（TTM）')
    pb = Column(DECIMAL(10, 2), comment='市净率')
    ps = Column(DECIMAL(10, 2), comment='市销率')
    ps_ttm = Column(DECIMAL(10, 2), comment='市销率（TTM）')
    dv_ratio = Column(DECIMAL(10, 2), comment='股息率（%）')
    dv_ttm = Column(DECIMAL(10, 2), comment='股息率（TTM）（%）')
    total_share = Column(DECIMAL(20, 2), comment='总股本（万股）')
    float_share = Column(DECIMAL(20, 2), comment='流通股本（万股）')
    free_share = Column(DECIMAL(20, 2), comment='自由流通股本（万）')
    total_mv = Column(DECIMAL(20, 2), comment='总市值（万元）')
    circ_mv = Column(DECIMAL(20, 2), comment='流通市值（万元）')

    @staticmethod
    def _to_float_or_none(value):
        return float(value) if value is not None else None
    
    def to_dict(self):
        """转换为字典"""
        return {
            'ts_code': self.ts_code,
            'trade_date': self.trade_date.isoformat() if self.trade_date else None,
            'close': self._to_float_or_none(self.close),
            'turnover_rate': self._to_float_or_none(self.turnover_rate),
            'turnover_rate_f': self._to_float_or_none(self.turnover_rate_f),
            'volume_ratio': self._to_float_or_none(self.volume_ratio),
            'pe': self._to_float_or_none(self.pe),
            'pe_ttm': self._to_float_or_none(self.pe_ttm),
            'pb': self._to_float_or_none(self.pb),
            'ps': self._to_float_or_none(self.ps),
            'ps_ttm': self._to_float_or_none(self.ps_ttm),
            'dv_ratio': self._to_float_or_none(self.dv_ratio),
            'dv_ttm': self._to_float_or_none(self.dv_ttm),
            'total_share': self._to_float_or_none(self.total_share),
            'float_share': self._to_float_or_none(self.float_share),
            'free_share': self._to_float_or_none(self.free_share),
            'total_mv': self._to_float_or_none(self.total_mv),
            'circ_mv': self._to_float_or_none(self.circ_mv)
        }
    
    def __repr__(self):
        return f'<StockDailyBasic {self.ts_code} {self.trade_date}>' 
