"""
预警规则模型
用于存储用户自定义的预警规则配置
"""

from app.extensions import db
from datetime import datetime
from sqlalchemy import Index
import json


class AlertRule(db.Model):
    """预警规则模型"""
    __tablename__ = 'alert_rules'
    
    # ==================== 基础字段 ====================
    id = db.Column(db.Integer, primary_key=True, comment='规则ID')
    rule_name = db.Column(db.String(100), nullable=False, comment='规则名称')
    ts_code = db.Column(db.String(20), nullable=False, comment='股票代码')
    
    # ==================== 规则配置 ====================
    rule_type = db.Column(db.String(50), nullable=False, comment='规则类型')
    condition_type = db.Column(db.String(20), nullable=False, comment='条件类型')
    threshold_value = db.Column(db.Float, nullable=False, comment='阈值')
    comparison_operator = db.Column(db.String(10), nullable=False, comment='比较运算符')
    
    # ==================== 预警设置 ====================
    alert_level = db.Column(db.String(20), default='medium', comment='预警级别')
    alert_message_template = db.Column(db.Text, comment='预警消息模板')
    
    # ==================== 状态管理 ====================
    is_enabled = db.Column(db.Boolean, default=True, comment='是否启用')
    is_active = db.Column(db.Boolean, default=True, comment='是否活跃')
    
    # ==================== 统计信息 ====================
    trigger_count = db.Column(db.Integer, default=0, comment='触发次数')
    last_triggered_at = db.Column(db.DateTime, comment='最后触发时间')
    
    # ==================== 时间戳 ====================
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # ==================== 扩展配置 ====================
    extra_config = db.Column(db.Text, comment='扩展配置JSON')
    
    # ==================== 数据库索引 ====================
    __table_args__ = (
        Index('idx_alert_rules_ts_code', 'ts_code'),
        Index('idx_alert_rules_type_enabled', 'rule_type', 'is_enabled'),
        Index('idx_alert_rules_active', 'is_active'),
        Index('idx_alert_rules_created_at', 'created_at'),
    )
    
    # ==================== 规则类型常量 ====================
    RULE_TYPES = {
        'price_threshold': '价格阈值',
        'price_change_pct': '涨跌幅',
        'volume_ratio': '成交量比率',
        'turnover_rate': '换手率',
        'market_value': '市值变化',
        'technical_indicator': '技术指标',
        'money_flow': '资金流向'
    }
    
    # ==================== 比较运算符常量 ====================
    OPERATORS = {
        'gt': '大于',
        'gte': '大于等于', 
        'lt': '小于',
        'lte': '小于等于',
        'eq': '等于',
        'ne': '不等于'
    }
    
    # ==================== 预警级别常量 ====================
    ALERT_LEVELS = {
        'low': '低级预警',
        'medium': '中级预警',
        'high': '高级预警',
        'critical': '严重预警'
    }
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'rule_name': self.rule_name,
            'ts_code': self.ts_code,
            'rule_type': self.rule_type,
            'rule_type_name': self.RULE_TYPES.get(self.rule_type, self.rule_type),
            'condition_type': self.condition_type,
            'threshold_value': self.threshold_value,
            'comparison_operator': self.comparison_operator,
            'operator_name': self.OPERATORS.get(self.comparison_operator, self.comparison_operator),
            'alert_level': self.alert_level,
            'alert_level_name': self.ALERT_LEVELS.get(self.alert_level, self.alert_level),
            'alert_message_template': self.alert_message_template,
            'is_enabled': self.is_enabled,
            'is_active': self.is_active,
            'trigger_count': self.trigger_count,
            'last_triggered_at': self.last_triggered_at.isoformat() if self.last_triggered_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'extra_config': json.loads(self.extra_config) if self.extra_config else {}
        }
    
    @classmethod
    def create_rule(cls, rule_name, ts_code, rule_type, condition_type, 
                   threshold_value, comparison_operator, alert_level='medium',
                   alert_message_template=None, extra_config=None):
        """创建预警规则"""
        
        # 生成默认消息模板
        if not alert_message_template:
            alert_message_template = cls._generate_default_message_template(
                rule_type, comparison_operator, threshold_value
            )
        
        rule = cls(
            rule_name=rule_name,
            ts_code=ts_code,
            rule_type=rule_type,
            condition_type=condition_type,
            threshold_value=threshold_value,
            comparison_operator=comparison_operator,
            alert_level=alert_level,
            alert_message_template=alert_message_template,
            extra_config=json.dumps(extra_config) if extra_config else None
        )
        
        db.session.add(rule)
        db.session.commit()
        return rule
    
    @classmethod
    def _generate_default_message_template(cls, rule_type, operator, threshold):
        """生成默认消息模板"""
        rule_name = cls.RULE_TYPES.get(rule_type, rule_type)
        operator_name = cls.OPERATORS.get(operator, operator)
        
        return f"{rule_name}{operator_name}{threshold}，当前值：{{current_value}}"
    
    def update_rule(self, **kwargs):
        """更新规则"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def enable_rule(self):
        """启用规则"""
        self.is_enabled = True
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def disable_rule(self):
        """禁用规则"""
        self.is_enabled = False
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def record_trigger(self):
        """记录触发"""
        self.trigger_count += 1
        self.last_triggered_at = datetime.utcnow()
        db.session.commit()
    
    def check_condition(self, current_value):
        """检查条件是否满足"""
        if not self.is_enabled or not self.is_active:
            return False
        
        operator = self.comparison_operator
        threshold = self.threshold_value
        
        if operator == 'gt':
            return current_value > threshold
        elif operator == 'gte':
            return current_value >= threshold
        elif operator == 'lt':
            return current_value < threshold
        elif operator == 'lte':
            return current_value <= threshold
        elif operator == 'eq':
            return abs(current_value - threshold) < 0.0001  # 浮点数比较
        elif operator == 'ne':
            return abs(current_value - threshold) >= 0.0001
        
        return False
    
    def generate_alert_message(self, current_value, stock_name=None):
        """生成预警消息"""
        template = self.alert_message_template or self._generate_default_message_template(
            self.rule_type, self.comparison_operator, self.threshold_value
        )
        
        stock_info = f"{stock_name}({self.ts_code})" if stock_name else self.ts_code
        
        return f"【{self.ALERT_LEVELS.get(self.alert_level, '预警')}】{stock_info} {template.format(current_value=current_value)}"
    
    @classmethod
    def get_enabled_rules(cls, ts_code=None, rule_type=None):
        """获取启用的规则"""
        query = cls.query.filter_by(is_enabled=True, is_active=True)
        
        if ts_code:
            query = query.filter_by(ts_code=ts_code)
        if rule_type:
            query = query.filter_by(rule_type=rule_type)
        
        return query.order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_rule_stats(cls):
        """获取规则统计"""
        from sqlalchemy import func
        
        # 按类型统计
        type_stats = db.session.query(
            cls.rule_type,
            func.count(cls.id).label('count')
        ).filter_by(is_active=True).group_by(cls.rule_type).all()
        
        # 按级别统计
        level_stats = db.session.query(
            cls.alert_level,
            func.count(cls.id).label('count')
        ).filter_by(is_active=True, is_enabled=True).group_by(cls.alert_level).all()
        
        return {
            'by_type': {rule_type: count for rule_type, count in type_stats},
            'by_level': {level: count for level, count in level_stats},
            'total_enabled': cls.query.filter_by(is_enabled=True, is_active=True).count(),
            'total_rules': cls.query.filter_by(is_active=True).count()
        }
