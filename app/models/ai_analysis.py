"""
AI分析记录模型
用于存储AI股票分析的历史记录
"""

from app.extensions import db
from datetime import datetime
from sqlalchemy import Index


class AIAnalysisRecord(db.Model):
    """AI分析记录模型"""
    __tablename__ = 'ai_analysis_records'

    # ==================== 基础字段 ====================
    id = db.Column(db.Integer, primary_key=True, comment='记录ID')
    ts_code = db.Column(db.String(20), nullable=False, comment='股票代码')
    stock_name = db.Column(db.String(100), nullable=False, comment='股票名称')

    # ==================== 分析结果 ====================
    recommendation = db.Column(db.Enum('buy', 'sell', 'hold'), nullable=False, comment='推荐操作')
    confidence = db.Column(db.Float, nullable=False, comment='置信度(0-1)')
    target_price = db.Column(db.Float, comment='目标价格')
    risk_level = db.Column(db.Enum('low', 'medium', 'high'), nullable=False, comment='风险等级')
    reasons = db.Column(db.Text, comment='推荐理由JSON')

    # ==================== 分析配置 ====================
    ai_provider = db.Column(db.String(50), comment='AI提供者')
    model_name = db.Column(db.String(100), comment='使用的模型名称')
    analysis_data = db.Column(db.Text, comment='分析用的数据JSON')

    # ==================== 状态和结果 ====================
    success = db.Column(db.Boolean, default=True, comment='分析是否成功')
    error_message = db.Column(db.Text, comment='错误信息')
    response_time = db.Column(db.Float, comment='响应时间(秒)')

    # ==================== 时间戳 ====================
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')

    # ==================== 数据库索引 ====================
    __table_args__ = (
        Index('idx_ai_analysis_ts_code_created', 'ts_code', 'created_at'),
        Index('idx_ai_analysis_provider', 'ai_provider'),
        Index('idx_ai_analysis_recommendation', 'recommendation'),
        Index('idx_ai_analysis_created_at', 'created_at'),
    )

    # ==================== 推荐类型常量 ====================
    RECOMMENDATIONS = {
        'buy': '买入',
        'sell': '卖出',
        'hold': '持有'
    }

    RISK_LEVELS = {
        'low': '低风险',
        'medium': '中等风险',
        'high': '高风险'
    }

    def to_dict(self):
        """转换为字典格式"""
        result = {
            'id': self.id,
            'ts_code': self.ts_code,
            'stock_name': self.stock_name,
            'recommendation': self.recommendation,
            'recommendation_name': self.RECOMMENDATIONS.get(self.recommendation, self.recommendation),
            'confidence': self.confidence,
            'target_price': self.target_price,
            'risk_level': self.risk_level,
            'risk_level_name': self.RISK_LEVELS.get(self.risk_level, self.risk_level),
            'ai_provider': self.ai_provider,
            'model_name': self.model_name,
            'success': self.success,
            'error_message': self.error_message,
            'response_time': self.response_time,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

        # 解析JSON字段
        try:
            import json
            if self.reasons:
                result['reasons'] = json.loads(self.reasons)
            if self.analysis_data:
                result['analysis_data'] = json.loads(self.analysis_data)
        except (json.JSONDecodeError, TypeError):
            result['reasons'] = []
            result['analysis_data'] = {}

        return result

    @classmethod
    def create_record(cls, ts_code, stock_name, recommendation, confidence,
                       target_price=None, risk_level='medium', reasons=None,
                       ai_provider=None, model_name=None, analysis_data=None,
                       success=True, error_message=None, response_time=None):
        """创建AI分析记录"""
        import json

        record = cls(
            ts_code=ts_code,
            stock_name=stock_name,
            recommendation=recommendation,
            confidence=confidence,
            target_price=target_price,
            risk_level=risk_level,
            reasons=json.dumps(reasons, ensure_ascii=False) if reasons else None,
            ai_provider=ai_provider,
            model_name=model_name,
            analysis_data=json.dumps(analysis_data, ensure_ascii=False) if analysis_data else None,
            success=success,
            error_message=error_message,
            response_time=response_time
        )

        db.session.add(record)
        db.session.commit()
        return record

    @classmethod
    def get_latest_analysis(cls, ts_code):
        """获取股票的最新分析记录"""
        return cls.query.filter_by(ts_code=ts_code).order_by(cls.created_at.desc()).first()

    @classmethod
    def get_analysis_history(cls, ts_code, days=30, limit=10):
        """获取股票的历史分析记录"""
        from datetime import timedelta

        start_date = datetime.utcnow() - timedelta(days=days)

        return cls.query.filter(
            cls.ts_code == ts_code,
            cls.created_at >= start_date
        ).order_by(cls.created_at.desc()).limit(limit).all()

    @classmethod
    def get_analysis_stats(cls, days=30):
        """获取分析统计信息"""
        from sqlalchemy import func
        from datetime import timedelta

        start_date = datetime.utcnow() - timedelta(days=days)

        # 总体统计
        total_analyses = cls.query.filter(cls.created_at >= start_date).count()
        successful_analyses = cls.query.filter(
            cls.created_at >= start_date,
            cls.success == True
        ).count()

        # 按推荐类型统计
        recommendation_stats = db.session.query(
            cls.recommendation,
            func.count(cls.id).label('count')
        ).filter(
            cls.created_at >= start_date,
            cls.success == True
        ).group_by(cls.recommendation).all()

        # 按风险等级统计
        risk_stats = db.session.query(
            cls.risk_level,
            func.count(cls.id).label('count')
        ).filter(
            cls.created_at >= start_date,
            cls.success == True
        ).group_by(cls.risk_level).all()

        # 按AI提供者统计
        provider_stats = db.session.query(
            cls.ai_provider,
            func.count(cls.id).label('count')
        ).filter(
            cls.created_at >= start_date
        ).group_by(cls.ai_provider).all()

        # 平均置信度
        avg_confidence = db.session.query(
            func.avg(cls.confidence)
        ).filter(
            cls.created_at >= start_date,
            cls.success == True
        ).scalar() or 0.0

        return {
            'period_days': days,
            'total_analyses': total_analyses,
            'successful_analyses': successful_analyses,
            'success_rate': (successful_analyses / total_analyses * 100) if total_analyses > 0 else 0,
            'by_recommendation': {rec: count for rec, count in recommendation_stats},
            'by_risk_level': {level: count for level, count in risk_stats},
            'by_provider': {provider: count for provider, count in provider_stats},
            'average_confidence': round(avg_confidence, 3)
        }

    @classmethod
    def get_stock_analysis_summary(cls, ts_code, days=30):
        """获取单只股票的分析摘要"""
        from datetime import timedelta

        start_date = datetime.utcnow() - timedelta(days=days)

        records = cls.query.filter(
            cls.ts_code == ts_code,
            cls.created_at >= start_date,
            cls.success == True
        ).order_by(cls.created_at.desc()).all()

        if not records:
            return None

        latest = records[0]

        # 计算统计
        total_count = len(records)
        recommendation_counts = {}
        for rec in records:
            recommendation_counts[rec.recommendation] = recommendation_counts.get(rec.recommendation, 0) + 1

        # 计算平均置信度
        avg_confidence = sum(rec.confidence for rec in records) / total_count if total_count > 0 else 0

        return {
            'latest_analysis': latest.to_dict(),
            'total_analyses': total_count,
            'recommendation_distribution': recommendation_counts,
            'average_confidence': round(avg_confidence, 3),
            'analysis_period': {
                'start_date': start_date.isoformat(),
                'end_date': datetime.utcnow().isoformat()
            }
        }