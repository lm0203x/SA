"""
操作日志接口
"""

from flask import jsonify, request
from loguru import logger

from app.api import api_bp
from app.services.operation_log_service import OperationLogService
from app.utils.auth import get_request_user


@api_bp.route('/operation-logs', methods=['GET'])
def get_operation_logs():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        module = request.args.get('module')
        action_type = request.args.get('action_type')
        username = request.args.get('username')
        status = request.args.get('status')

        pagination = OperationLogService.query_logs(
            page=page,
            per_page=per_page,
            module=module,
            action_type=action_type,
            username=username,
            status=status,
        )
        current_user = get_request_user()
        OperationLogService.record(
            module='operation_log',
            action_type='view',
            action_name='查看操作日志',
            user=current_user,
            message=f'第 {page} 页操作日志查询',
        )
        return jsonify({
            'success': True,
            'data': {
                'records': [item.to_dict() for item in pagination.items],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev,
                },
            },
        })
    except Exception as exc:
        logger.error(f"获取操作日志失败: {exc}")
        return jsonify({'success': False, 'message': str(exc)}), 500
