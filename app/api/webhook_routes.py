"""
Webhook配置API路由
提供Webhook配置的创建、查询、更新、删除、测试功能
"""

from flask import request, jsonify
from loguru import logger
from datetime import datetime
from app.extensions import db
from app.models.webhook_config import WebhookConfig
from app.services.webhook_service import send_webhook_notification


def register_webhook_routes(api_bp):
    """注册Webhook路由到API蓝图"""

    @api_bp.route('/webhooks', methods=['GET'])
    def get_webhooks():
        """获取Webhook配置列表"""
        try:
            # 获取查询参数
            webhook_type = request.args.get('type')
            is_enabled = request.args.get('is_enabled')
            page = int(request.args.get('page', 1))
            per_page = min(int(request.args.get('per_page', 20)), 100)

            # 构建查询
            query = WebhookConfig.query.filter_by(is_active=True)

            if webhook_type:
                query = query.filter_by(type=webhook_type)
            if is_enabled is not None:
                enabled = is_enabled.lower() == 'true'
                query = query.filter_by(is_enabled=enabled)

            # 分页查询
            pagination = query.order_by(WebhookConfig.created_at.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )

            webhooks = [webhook.to_dict() for webhook in pagination.items]

            return jsonify({
                'success': True,
                'data': {
                    'webhooks': webhooks,
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': pagination.total,
                        'pages': pagination.pages,
                        'has_next': pagination.has_next,
                        'has_prev': pagination.has_prev
                    }
                },
                'message': f'获取到 {len(webhooks)} 个Webhook配置'
            })

        except Exception as e:
            logger.error(f"获取Webhook配置失败: {e}")
            return jsonify({'success': False, 'message': str(e)}), 500

    @api_bp.route('/webhooks', methods=['POST'])
    def create_webhook():
        """创建Webhook配置"""
        try:
            data = request.get_json()

            # 验证必需字段
            required_fields = ['name', 'type', 'url']
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        'success': False,
                        'message': f'缺少必需字段: {field}'
                    }), 400

            # 验证Webhook类型
            if data['type'] not in WebhookConfig.WEBHOOK_TYPES:
                return jsonify({
                    'success': False,
                    'message': f'无效的Webhook类型: {data["type"]}'
                }), 400

            # 验证HTTP方法
            method = data.get('method', 'POST')
            if method not in WebhookConfig.HTTP_METHODS:
                return jsonify({
                    'success': False,
                    'message': f'无效的HTTP方法: {method}'
                }), 400

            # 检查URL格式
            url = data['url'].strip()
            if not url.startswith(('http://', 'https://')):
                return jsonify({
                    'success': False,
                    'message': 'URL必须以http://或https://开头'
                }), 400

            # 创建Webhook配置
            webhook = WebhookConfig.create_config(
                name=data['name'].strip(),
                webhook_type=data['type'],
                url=url,
                description=data.get('description', ''),
                method=method,
                headers=data.get('headers', {}),
                timeout=data.get('timeout', 30),
                retry_count=data.get('retry_count', 3),
                message_template=data.get('message_template', ''),
                content_type=data.get('content_type', 'application/json'),
                secret=data.get('secret'),
                app_key=data.get('app_key'),
                app_secret=data.get('app_secret'),
                extra_config=data.get('extra_config', {})
            )

            logger.info(f"创建Webhook配置成功: {webhook.name} ({webhook.id})")

            return jsonify({
                'success': True,
                'data': webhook.to_dict(),
                'message': f'Webhook配置 "{webhook.name}" 创建成功'
            }), 201

        except Exception as e:
            logger.error(f"创建Webhook配置失败: {e}")
            return jsonify({'success': False, 'message': str(e)}), 500

    @api_bp.route('/webhooks/<int:webhook_id>', methods=['GET'])
    def get_webhook(webhook_id):
        """获取单个Webhook配置详情"""
        try:
            webhook = WebhookConfig.query.filter_by(id=webhook_id, is_active=True).first()
            if not webhook:
                return jsonify({
                    'success': False,
                    'message': f'Webhook配置 {webhook_id} 不存在'
                }), 404

            return jsonify({
                'success': True,
                'data': webhook.to_dict(),
                'message': '获取Webhook配置详情成功'
            })

        except Exception as e:
            logger.error(f"获取Webhook配置详情失败: {e}")
            return jsonify({'success': False, 'message': str(e)}), 500

    @api_bp.route('/webhooks/<int:webhook_id>', methods=['PUT'])
    def update_webhook(webhook_id):
        """更新Webhook配置"""
        try:
            webhook = WebhookConfig.query.filter_by(id=webhook_id, is_active=True).first()
            if not webhook:
                return jsonify({
                    'success': False,
                    'message': f'Webhook配置 {webhook_id} 不存在'
                }), 404

            data = request.get_json()

            # 验证HTTP方法
            method = data.get('method', webhook.method)
            if method not in WebhookConfig.HTTP_METHODS:
                return jsonify({
                    'success': False,
                    'message': f'无效的HTTP方法: {method}'
                }), 400

            # 可更新的字段
            updatable_fields = [
                'name', 'url', 'description', 'method', 'headers', 'timeout',
                'retry_count', 'message_template', 'content_type', 'secret',
                'app_key', 'app_secret', 'extra_config'
            ]

            update_data = {}
            for field in updatable_fields:
                if field in data:
                    update_data[field] = data[field]

            if update_data:
                webhook.update_config(**update_data)
                logger.info(f"更新Webhook配置成功: {webhook.name} ({webhook.id})")

            return jsonify({
                'success': True,
                'data': webhook.to_dict(),
                'message': f'Webhook配置 "{webhook.name}" 更新成功'
            })

        except Exception as e:
            logger.error(f"更新Webhook配置失败: {e}")
            return jsonify({'success': False, 'message': str(e)}), 500

    @api_bp.route('/webhooks/<int:webhook_id>', methods=['DELETE'])
    def delete_webhook(webhook_id):
        """删除Webhook配置（软删除）"""
        try:
            webhook = WebhookConfig.query.filter_by(id=webhook_id, is_active=True).first()
            if not webhook:
                return jsonify({
                    'success': False,
                    'message': f'Webhook配置 {webhook_id} 不存在'
                }), 404

            # 软删除
            webhook.delete_config()

            logger.info(f"删除Webhook配置成功: {webhook.name} ({webhook.id})")

            return jsonify({
                'success': True,
                'message': f'Webhook配置 "{webhook.name}" 删除成功'
            })

        except Exception as e:
            logger.error(f"删除Webhook配置失败: {e}")
            return jsonify({'success': False, 'message': str(e)}), 500

    @api_bp.route('/webhooks/<int:webhook_id>/toggle', methods=['POST'])
    def toggle_webhook(webhook_id):
        """切换Webhook配置启用状态"""
        try:
            webhook = WebhookConfig.query.filter_by(id=webhook_id, is_active=True).first()
            if not webhook:
                return jsonify({
                    'success': False,
                    'message': f'Webhook配置 {webhook_id} 不存在'
                }), 404

            # 切换启用状态
            if webhook.is_enabled:
                webhook.disable()
                action = '禁用'
            else:
                webhook.enable()
                action = '启用'

            logger.info(f"{action}Webhook配置成功: {webhook.name} ({webhook.id})")

            return jsonify({
                'success': True,
                'data': webhook.to_dict(),
                'message': f'Webhook配置 "{webhook.name}" {action}成功'
            })

        except Exception as e:
            logger.error(f"切换Webhook配置状态失败: {e}")
            return jsonify({'success': False, 'message': str(e)}), 500

    @api_bp.route('/webhooks/<int:webhook_id>/test', methods=['POST'])
    def test_webhook(webhook_id):
        """测试Webhook配置"""
        try:
            webhook = WebhookConfig.query.filter_by(id=webhook_id, is_active=True).first()
            if not webhook:
                return jsonify({
                    'success': False,
                    'message': f'Webhook配置 {webhook_id} 不存在'
                }), 404

            # 获取测试数据
            test_data = request.get_json() or {
                'ts_code': '000001.SZ',
                'stock_name': '平安银行',
                'alert_level': 'medium',
                'alert_type': 'price_change_pct',
                'alert_message': '这是一条测试预警消息：涨跌幅超过5%阈值',
                'current_price': 15.68,
                'threshold_value': 5.0,
                'risk_value': 6.5,
                'created_at': datetime.now().isoformat()
            }

            # 发送测试消息
            result = send_webhook_notification(webhook.to_dict(), test_data)

            if result.get('success'):
                webhook.record_success()
                logger.info(f"Webhook测试成功: {webhook.name}")
                return jsonify({
                    'success': True,
                    'message': f'Webhook "{webhook.name}" 测试成功',
                    'response': result
                })
            else:
                webhook.record_failure()
                logger.error(f"Webhook测试失败: {webhook.name} - {result.get('message')}")
                return jsonify({
                    'success': False,
                    'message': f'Webhook测试失败: {result.get("message")}',
                    'error': result
                }), 500

        except Exception as e:
            logger.error(f"测试Webhook配置失败: {e}")
            return jsonify({
                'success': False,
                'message': f'测试Webhook失败: {str(e)}'
            }), 500

    @api_bp.route('/webhooks/stats', methods=['GET'])
    def get_webhook_stats():
        """获取Webhook统计信息"""
        try:
            # 获取统计信息
            stats = WebhookConfig.get_stats()

            # 获取总体统计
            total_configs = WebhookConfig.query.filter_by(is_active=True).count()
            enabled_configs = WebhookConfig.query.filter_by(is_active=True, is_enabled=True).count()

            return jsonify({
                'success': True,
                'data': {
                    'total_configs': total_configs,
                    'enabled_configs': enabled_configs,
                    'disabled_configs': total_configs - enabled_configs,
                    'by_type': stats
                },
                'message': '获取Webhook统计信息成功'
            })

        except Exception as e:
            logger.error(f"获取Webhook统计信息失败: {e}")
            return jsonify({'success': False, 'message': str(e)}), 500

    @api_bp.route('/webhooks/options', methods=['GET'])
    def get_webhook_options():
        """获取Webhook配置选项"""
        try:
            return jsonify({
                'success': True,
                'data': {
                    'webhook_types': WebhookConfig.WEBHOOK_TYPES,
                    'http_methods': WebhookConfig.HTTP_METHODS
                },
                'message': '获取Webhook配置选项成功'
            })

        except Exception as e:
            logger.error(f"获取Webhook配置选项失败: {e}")
            return jsonify({'success': False, 'message': str(e)}), 500

    # 返回注册的函数
    return register_webhook_routes