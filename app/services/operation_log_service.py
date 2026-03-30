"""
操作日志服务
"""

from flask import request
from loguru import logger

from app.extensions import db
from app.models.operation_log import OperationLog


class OperationLogService:
    """统一写入与查询操作日志"""

    @staticmethod
    def record(
        module,
        action_type,
        action_name,
        status='success',
        user=None,
        user_id=None,
        username=None,
        target_type=None,
        target_id=None,
        target_name=None,
        message=None,
        detail=None,
        commit=True,
    ):
        try:
            log_item = OperationLog(
                user_id=user_id if user_id is not None else getattr(user, 'id', None),
                username=username or getattr(user, 'username', None),
                module=module,
                action_type=action_type,
                action_name=action_name,
                target_type=target_type,
                target_id=str(target_id) if target_id is not None else None,
                target_name=target_name,
                request_path=request.path if request else None,
                request_method=request.method if request else None,
                status=status,
                message=message,
                detail_json=detail or {},
                ip=OperationLogService._resolve_ip(),
                user_agent=request.headers.get('User-Agent') if request else None,
            )
            db.session.add(log_item)
            if commit:
                db.session.commit()
            return log_item
        except Exception as exc:
            logger.error(f"记录操作日志失败: {exc}")
            if commit:
                db.session.rollback()
            return None

    @staticmethod
    def query_logs(page=1, per_page=20, module=None, action_type=None, username=None, status=None):
        query = OperationLog.query

        if module:
            query = query.filter(OperationLog.module == module)
        if action_type:
            query = query.filter(OperationLog.action_type == action_type)
        if username:
            query = query.filter(OperationLog.username.ilike(f"%{username}%"))
        if status:
            query = query.filter(OperationLog.status == status)

        return query.order_by(OperationLog.created_at.desc(), OperationLog.id.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False,
        )

    @staticmethod
    def _resolve_ip():
        if not request:
            return None
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        return request.remote_addr
