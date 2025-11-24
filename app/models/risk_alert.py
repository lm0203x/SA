"""
风险预警记录模型
用于存储风险预警信息和历史记录
"""

from app.extensions import db
from datetime import datetime
from sqlalchemy import Index, text
import json


class RiskAlert(db.Model):
    """风险预警记录模型"""
    __tablename__ = 'risk_alerts'

    # ==================== 基础字段 ====================
    id = db.Column(db.Integer, primary_key=True, comment='预警记录ID')
    ts_code = db.Column(db.String(20), nullable=False, comment='股票代码')
    alert_type = db.Column(db.String(50), nullable=False, comment='预警类型')
    alert_level = db.Column(db.String(20), nullable=False, comment='预警级别')
    alert_message = db.Column(db.Text, nullable=False, comment='预警消息')

    # ==================== 关联字段 ====================
    rule_id = db.Column(db.Integer, db.ForeignKey('alert_rules.id'), comment='关联的预警规则ID')
    trigger_source = db.Column(db.String(20), default='auto', comment='触发源: auto/manual')

    # ==================== 数值字段 ====================
    risk_value = db.Column(db.Float, comment='风险值(当前值)')
    threshold_value = db.Column(db.Float, comment='阈值')
    current_price = db.Column(db.Float, comment='当前价格')
    position_size = db.Column(db.Float, comment='持仓数量')
    portfolio_weight = db.Column(db.Float, comment='组合权重')

    # ==================== 状态管理 ====================
    alert_status = db.Column(db.String(20), default='active', comment='预警状态: active/resolved/ignored/pending')
    is_active = db.Column(db.Boolean, default=True, comment='是否活跃')
    is_resolved = db.Column(db.Boolean, default=False, comment='是否已解决')
    is_ignored = db.Column(db.Boolean, default=False, comment='是否已忽略')

    # ==================== 时间戳 ====================
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    resolved_at = db.Column(db.DateTime, comment='解决时间')
    ignored_at = db.Column(db.DateTime, comment='忽略时间')

    # ==================== 扩展字段 ====================
    extra_data = db.Column(db.Text, comment='扩展数据JSON')
    resolution_note = db.Column(db.Text, comment='解决备注')

    # ==================== 外键关系 ====================
    rule = db.relationship('AlertRule', backref='alerts', lazy='select')

    # ==================== 数据库索引 ====================
    __table_args__ = (
        Index('idx_risk_alerts_ts_code_type', 'ts_code', 'alert_type'),
        Index('idx_risk_alerts_level_status', 'alert_level', 'alert_status'),
        Index('idx_risk_alerts_active', 'is_active'),
        Index('idx_risk_alerts_resolved', 'is_resolved'),
        Index('idx_risk_alerts_created_at', 'created_at'),
        Index('idx_risk_alerts_rule_id', 'rule_id'),
        Index('idx_risk_alerts_source', 'trigger_source'),
    )

    # ==================== 状态常量 ====================
    ALERT_STATUS = {
        'active': '活跃',
        'resolved': '已解决',
        'ignored': '已忽略',
        'pending': '待处理'
    }

    TRIGGER_SOURCE = {
        'auto': '自动触发',
        'manual': '手动创建',
        'api': 'API调用',
        'system': '系统生成'
    }

    ALERT_TYPES = {
        'price_threshold': '价格阈值',
        'price_change_pct': '涨跌幅',
        'volume_ratio': '成交量比率',
        'turnover_rate': '换手率',
        'market_value': '市值变化',
        'technical_indicator': '技术指标',
        'money_flow': '资金流向',
        'custom': '自定义'
    }

    ALERT_LEVELS = {
        'low': '低级预警',
        'medium': '中级预警',
        'high': '高级预警',
        'critical': '严重预警'
    }
    
    def to_dict(self, include_rule=False):
        """转换为字典"""
        result = {
            'id': self.id,
            'ts_code': self.ts_code,
            'alert_type': self.alert_type,
            'alert_type_name': self.ALERT_TYPES.get(self.alert_type, self.alert_type),
            'alert_level': self.alert_level,
            'alert_level_name': self.ALERT_LEVELS.get(self.alert_level, self.alert_level),
            'alert_message': self.alert_message,
            'alert_status': self.alert_status,
            'alert_status_name': self.ALERT_STATUS.get(self.alert_status, self.alert_status),

            # 关联信息
            'rule_id': self.rule_id,
            'trigger_source': self.trigger_source,
            'trigger_source_name': self.TRIGGER_SOURCE.get(self.trigger_source, self.trigger_source),

            # 数值信息
            'risk_value': self.risk_value,
            'threshold_value': self.threshold_value,
            'current_price': self.current_price,
            'position_size': self.position_size,
            'portfolio_weight': self.portfolio_weight,

            # 状态信息
            'is_active': self.is_active,
            'is_resolved': self.is_resolved,
            'is_ignored': self.is_ignored,

            # 时间信息
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'ignored_at': self.ignored_at.isoformat() if self.ignored_at else None,

            # 扩展信息
            'resolution_note': self.resolution_note,
            'extra_data': json.loads(self.extra_data) if self.extra_data else {}
        }

        # 包含关联的预警规则信息
        if include_rule and self.rule:
            result['rule'] = {
                'id': self.rule.id,
                'rule_name': self.rule.rule_name,
                'rule_type': self.rule.rule_type,
                'threshold_value': self.rule.threshold_value,
                'comparison_operator': self.rule.comparison_operator
            }

        return result
    
    @classmethod
    def create_alert(cls, ts_code, alert_type, alert_level, alert_message,
                    rule_id=None, risk_value=None, threshold_value=None,
                    current_price=None, position_size=None, portfolio_weight=None,
                    trigger_source='auto', extra_data=None):
        """创建风险预警"""
        alert = cls(
            ts_code=ts_code,
            alert_type=alert_type,
            alert_level=alert_level,
            alert_message=alert_message,
            rule_id=rule_id,
            risk_value=risk_value,
            threshold_value=threshold_value,
            current_price=current_price,
            position_size=position_size,
            portfolio_weight=portfolio_weight,
            trigger_source=trigger_source,
            extra_data=json.dumps(extra_data) if extra_data else None
        )
        db.session.add(alert)
        db.session.commit()
        return alert

    def resolve_alert(self, resolution_note=None):
        """解决预警"""
        self.is_resolved = True
        self.is_active = False
        self.alert_status = 'resolved'
        self.resolved_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.resolution_note = resolution_note
        db.session.commit()

    def ignore_alert(self, ignore_note=None):
        """忽略预警"""
        self.is_ignored = True
        self.is_active = False
        self.alert_status = 'ignored'
        self.ignored_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.resolution_note = ignore_note
        db.session.commit()

    def reactivate_alert(self):
        """重新激活预警"""
        self.is_active = True
        self.is_resolved = False
        self.is_ignored = False
        self.alert_status = 'active'
        self.updated_at = datetime.utcnow()
        db.session.commit()

    def update_alert(self, **kwargs):
        """更新预警信息"""
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ['id', 'created_at']:
                setattr(self, key, value)

        self.updated_at = datetime.utcnow()
        db.session.commit()

    @classmethod
    def get_alerts(cls, ts_code=None, alert_type=None, alert_level=None,
                   alert_status=None, trigger_source=None, rule_id=None,
                   start_date=None, end_date=None, page=1, per_page=20,
                   order_by='created_at', order_dir='desc'):
        """
        获取预警记录列表（支持多种过滤条件）

        Args:
            ts_code: 股票代码过滤
            alert_type: 预警类型过滤
            alert_level: 预警级别过滤
            alert_status: 预警状态过滤
            trigger_source: 触发源过滤
            rule_id: 预警规则ID过滤
            start_date: 开始日期过滤
            end_date: 结束日期过滤
            page: 页码
            per_page: 每页条数
            order_by: 排序字段
            order_dir: 排序方向

        Returns:
            分页的预警记录列表
        """
        query = cls.query

        # 应用过滤条件
        if ts_code:
            query = query.filter(cls.ts_code == ts_code)
        if alert_type:
            query = query.filter(cls.alert_type == alert_type)
        if alert_level:
            query = query.filter(cls.alert_level == alert_level)
        if alert_status:
            query = query.filter(cls.alert_status == alert_status)
        if trigger_source:
            query = query.filter(cls.trigger_source == trigger_source)
        if rule_id:
            query = query.filter(cls.rule_id == rule_id)
        if start_date:
            query = query.filter(cls.created_at >= start_date)
        if end_date:
            query = query.filter(cls.created_at <= end_date)

        # 应用排序
        if hasattr(cls, order_by):
            order_column = getattr(cls, order_by)
            if order_dir.lower() == 'desc':
                query = query.order_by(order_column.desc())
            else:
                query = query.order_by(order_column.asc())

        # 分页
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )

        return pagination

    @classmethod
    def get_active_alerts(cls, ts_code=None, alert_type=None, alert_level=None):
        """获取活跃预警"""
        return cls.get_alerts(
            ts_code=ts_code,
            alert_type=alert_type,
            alert_level=alert_level,
            alert_status='active'
        ).items

    @classmethod
    def get_alert_by_id(cls, alert_id):
        """根据ID获取预警记录"""
        return cls.query.filter_by(id=alert_id).first()

    @classmethod
    def get_alert_stats(cls, days=30, ts_code=None):
        """
        获取预警统计信息

        Args:
            days: 统计天数
            ts_code: 股票代码过滤

        Returns:
            统计信息字典
        """
        from sqlalchemy import func
        from datetime import datetime, timedelta

        # 计算时间范围
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days)

        # 基础查询
        base_query = cls.query.filter(cls.created_at >= start_time)
        if ts_code:
            base_query = base_query.filter(cls.ts_code == ts_code)

        # 总体统计
        total_alerts = base_query.count()
        active_alerts = base_query.filter_by(is_active=True).count()
        resolved_alerts = base_query.filter_by(is_resolved=True).count()
        ignored_alerts = base_query.filter_by(is_ignored=True).count()

        # 按级别统计
        level_stats = base_query.with_entities(
            cls.alert_level,
            func.count(cls.id).label('count')
        ).group_by(cls.alert_level).all()

        # 按类型统计
        type_stats = base_query.with_entities(
            cls.alert_type,
            func.count(cls.id).label('count')
        ).group_by(cls.alert_type).all()

        # 按状态统计
        status_stats = base_query.with_entities(
            cls.alert_status,
            func.count(cls.id).label('count')
        ).group_by(cls.alert_status).all()

        # 按触发源统计
        source_stats = base_query.with_entities(
            cls.trigger_source,
            func.count(cls.id).label('count')
        ).group_by(cls.trigger_source).all()

        # 时间趋势统计（按天）
        trend_stats = base_query.with_entities(
            func.date(cls.created_at).label('date'),
            func.count(cls.id).label('count')
        ).group_by(func.date(cls.created_at)).order_by(func.date(cls.created_at)).all()

        return {
            'period_days': days,
            'total_alerts': total_alerts,
            'active_alerts': active_alerts,
            'resolved_alerts': resolved_alerts,
            'ignored_alerts': ignored_alerts,
            'by_level': {level: count for level, count in level_stats},
            'by_type': {alert_type: count for alert_type, count in type_stats},
            'by_status': {status: count for status, count in status_stats},
            'by_source': {source: count for source, count in source_stats},
            'trend': [{'date': str(date), 'count': count} for date, count in trend_stats]
        }

    @classmethod
    def delete_alert(cls, alert_id):
        """删除预警记录"""
        alert = cls.query.filter_by(id=alert_id).first()
        if alert:
            db.session.delete(alert)
            db.session.commit()
            return True
        return False

    @classmethod
    def bulk_resolve_alerts(cls, alert_ids, resolution_note=None):
        """批量解决预警"""
        alerts = cls.query.filter(cls.id.in_(alert_ids)).all()
        for alert in alerts:
            alert.resolve_alert(resolution_note)
        return len(alerts)

    @classmethod
    def bulk_ignore_alerts(cls, alert_ids, ignore_note=None):
        """批量忽略预警"""
        alerts = cls.query.filter(cls.id.in_(alert_ids)).all()
        for alert in alerts:
            alert.ignore_alert(ignore_note)
        return len(alerts) 