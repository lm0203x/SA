import json
from datetime import datetime

from app.extensions import db


class AnalysisStrategy(db.Model):
    __tablename__ = "analysis_strategies"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, comment="策略名称")
    code = db.Column(db.String(50), nullable=False, unique=True, comment="策略编码")
    strategy_type = db.Column(db.String(50), nullable=False, comment="策略类型")
    description = db.Column(db.Text, comment="策略描述")
    conditions_json = db.Column(db.Text, comment="策略条件JSON")
    prompt_template = db.Column(db.Text, comment="AI提示模板")
    is_active = db.Column(db.Boolean, default=True, comment="是否启用")
    schedule_type = db.Column(db.String(30), default="manual", comment="调度类型")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="更新时间",
    )

    tasks = db.relationship("AnalysisTask", backref="strategy", lazy=True)

    @staticmethod
    def parse_json(raw_value, default=None):
        if default is None:
            default = {}
        if not raw_value:
            return default
        try:
            return json.loads(raw_value)
        except (TypeError, json.JSONDecodeError):
            return default

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "strategy_type": self.strategy_type,
            "description": self.description,
            "conditions": self.parse_json(self.conditions_json, {}),
            "prompt_template": self.prompt_template,
            "is_active": self.is_active,
            "schedule_type": self.schedule_type,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class AnalysisTask(db.Model):
    __tablename__ = "analysis_tasks"

    id = db.Column(db.Integer, primary_key=True)
    strategy_id = db.Column(
        db.Integer, db.ForeignKey("analysis_strategies.id"), nullable=False, index=True
    )
    task_date = db.Column(db.Date, nullable=False, comment="任务日期")
    status = db.Column(db.String(20), default="pending", comment="任务状态")
    started_at = db.Column(db.DateTime, comment="开始时间")
    finished_at = db.Column(db.DateTime, comment="结束时间")
    stock_scope_type = db.Column(db.String(30), default="watchlist", comment="股票范围类型")
    stock_scope_json = db.Column(db.Text, comment="股票范围JSON")
    summary_json = db.Column(db.Text, comment="汇总结果JSON")
    error_message = db.Column(db.Text, comment="错误信息")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="更新时间",
    )

    results = db.relationship("AnalysisResult", backref="task", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "strategy_id": self.strategy_id,
            "task_date": self.task_date.isoformat() if self.task_date else None,
            "status": self.status,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "stock_scope_type": self.stock_scope_type,
            "stock_scope": AnalysisStrategy.parse_json(self.stock_scope_json, {}),
            "summary": AnalysisStrategy.parse_json(self.summary_json, {}),
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class AnalysisResult(db.Model):
    __tablename__ = "analysis_results"

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(
        db.Integer, db.ForeignKey("analysis_tasks.id"), nullable=False, index=True
    )
    ts_code = db.Column(db.String(20), nullable=False, index=True, comment="股票代码")
    stock_name = db.Column(db.String(100), comment="股票名称")
    score = db.Column(db.Float, default=0.0, comment="评分")
    signal = db.Column(db.String(20), nullable=False, comment="信号")
    risk_level = db.Column(db.String(20), default="medium", comment="风险等级")
    reason_json = db.Column(db.Text, comment="原因JSON")
    metrics_json = db.Column(db.Text, comment="指标JSON")
    ai_summary = db.Column(db.Text, comment="AI总结")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment="创建时间")

    def to_dict(self):
        return {
            "id": self.id,
            "task_id": self.task_id,
            "ts_code": self.ts_code,
            "stock_name": self.stock_name,
            "score": self.score,
            "signal": self.signal,
            "risk_level": self.risk_level,
            "reasons": AnalysisStrategy.parse_json(self.reason_json, []),
            "metrics": AnalysisStrategy.parse_json(self.metrics_json, {}),
            "ai_summary": self.ai_summary,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
