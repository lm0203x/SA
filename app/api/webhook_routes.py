"""
Webhook配置API路由
提供Webhook通知渠道的配置、测试、管理功能
参考数据源配置的实现模式
"""

from flask import request, jsonify
from loguru import logger
from app.api import api_bp
from app.extensions import db
from app.models.webhook_config import WebhookConfig
from app.services.webhook_service import webhook_service


@api_bp.route('/webhook-configs', methods=['GET'])
def get_webhook_configs():
    """获取所有Webhook配置"""
    try:
        configs = WebhookConfig.query.all()
        return jsonify({
            'success': True,
            'data': [config.to_dict(include_sensitive=False) for config in configs]
        })
    except Exception as e:
        logger.error(f"获取Webhook配置失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/webhook-configs', methods=['POST'])
def create_webhook_config():
    """创建Webhook配置"""
    try:
        data = request.get_json()

        # 验证必需字段
        if not data.get('webhook_type') or not data.get('webhook_name'):
            return jsonify({
                'success': False,
                'message': '缺少必需字段：webhook_type 或 webhook_name'
            }), 400

        # 验证Webhook类型
        valid_types = ['dingtalk', 'wechat_work', 'feishu', 'email', 'webhook', 'custom']
        if data['webhook_type'] not in valid_types:
            return jsonify({
                'success': False,
                'message': f'不支持的Webhook类型: {data["webhook_type"]}'
            }), 400

        # 验证配置数据
        config_data = data.get('config_data', {})
        webhook_type = data['webhook_type']

        if webhook_type != 'ollama':  # Ollama不需要配置验证
            if webhook_type in ['dingtalk', 'wechat_work', 'feishu', 'webhook']:
                if not config_data.get('webhook_url'):
                    return jsonify({
                        'success': False,
                        'message': f'{webhook_type} webhook_url不能为空'
                    }), 400
            elif webhook_type == 'email':
                required_email_fields = ['smtp_host', 'smtp_port', 'email', 'password', 'to_emails']
                if not all(config_data.get(field) for field in required_email_fields):
                    return jsonify({
                        'success': False,
                        'message': f'邮件配置缺少必要字段: {required_email_fields}'
                    }), 400
            elif webhook_type == 'custom':
                if not config_data.get('api_url'):
                    return jsonify({
                        'success': False,
                        'message': '自定义API URL不能为空'
                    }), 400

        # 创建新配置
        config = WebhookConfig(
            webhook_type=data['webhook_type'],
            webhook_name=data['webhook_name'],
            config_data=config_data,
            is_enabled=data.get('is_enabled', False),
            is_default=data.get('is_default', False),
            alert_levels=data.get('alert_levels', ['low', 'medium', 'high', 'critical']),
            message_template=data.get('message_template'),
            include_stock_info=data.get('include_stock_info', True),
            include_rule_info=data.get('include_rule_info', True),
            retry_count=data.get('retry_count', 3),
            retry_interval=data.get('retry_interval', 5)
        )

        # 如果设置为默认，取消其他Webhook配置的默认状态
        if config.is_default:
            WebhookConfig.query.update({'is_default': False})

        db.session.add(config)
        db.session.commit()

        logger.info(f"创建Webhook配置成功: {config.webhook_name}")
        return jsonify({
            'success': True,
            'message': '创建成功',
            'data': config.to_dict(include_sensitive=False)
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"创建Webhook配置失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/webhook-configs/<int:config_id>', methods=['PUT'])
def update_webhook_config(config_id):
    """更新Webhook配置"""
    try:
        config = WebhookConfig.query.get(config_id)
        if not config:
            return jsonify({'success': False, 'message': '配置不存在'}), 404

        data = request.get_json()

        # 更新字段
        if 'webhook_name' in data:
            config.webhook_name = data['webhook_name']
        if 'config_data' in data:
            config.config_data = data['config_data']
        if 'is_enabled' in data:
            config.is_enabled = data['is_enabled']
        if 'is_default' in data:
            config.is_default = data['is_default']
            # 如果设置为默认，取消其他Webhook配置的默认状态
            if config.is_default:
                WebhookConfig.query.filter(
                    WebhookConfig.id != config_id
                ).update({'is_default': False})
        if 'alert_levels' in data:
            config.alert_levels = data['alert_levels']
        if 'message_template' in data:
            config.message_template = data['message_template']
        if 'include_stock_info' in data:
            config.include_stock_info = data['include_stock_info']
        if 'include_rule_info' in data:
            config.include_rule_info = data['include_rule_info']
        if 'retry_count' in data:
            config.retry_count = data['retry_count']
        if 'retry_interval' in data:
            config.retry_interval = data['retry_interval']

        db.session.commit()

        logger.info(f"更新Webhook配置成功: {config.webhook_name}")
        return jsonify({
            'success': True,
            'message': '更新成功',
            'data': config.to_dict(include_sensitive=False)
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"更新Webhook配置失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/webhook-configs/<int:config_id>', methods=['DELETE'])
def delete_webhook_config(config_id):
    """删除Webhook配置"""
    try:
        config = WebhookConfig.query.get(config_id)
        if not config:
            return jsonify({'success': False, 'message': '配置不存在'}), 404

        # 防止删除默认配置
        if config.is_default:
            return jsonify({
                'success': False,
                'message': '不能删除默认配置'
            }), 400

        db.session.delete(config)
        db.session.commit()

        logger.info(f"删除Webhook配置成功: {config.webhook_name}")
        return jsonify({'success': True, 'message': '删除成功'})

    except Exception as e:
        db.session.rollback()
        logger.error(f"删除Webhook配置失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/webhook-configs/<int:config_id>/test', methods=['POST'])
def test_webhook_config(config_id):
    """测试Webhook配置连通性"""
    try:
        config = WebhookConfig.query.get(config_id)
        if not config:
            return jsonify({'success': False, 'message': '配置不存在'}), 404

        # 测试连接
        result = config.test_connection()

        logger.info(f"Webhook配置测试完成: {config.webhook_name}")
        return jsonify(result)

    except Exception as e:
        logger.error(f"测试Webhook配置失败: {e}")
        return jsonify({
            'success': False,
            'message': f'连接测试失败: {str(e)}'
        }), 500


@api_bp.route('/webhook-configs/active', methods=['GET'])
def get_active_webhook_configs():
    """获取当前激活的Webhook配置"""
    try:
        configs = WebhookConfig.get_enabled_configs()
        return jsonify({
            'success': True,
            'data': [config.to_dict(include_sensitive=False) for config in configs]
        })
    except Exception as e:
        logger.error(f"获取激活Webhook配置失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/webhook-configs/default', methods=['GET'])
def get_default_webhook_config():
    """获取默认Webhook配置"""
    try:
        config = WebhookConfig.get_default_config()

        if config:
            return jsonify({
                'success': True,
                'data': config.to_dict(include_sensitive=False)
            })
        else:
            return jsonify({
                'success': False,
                'message': '没有默认Webhook配置'
            }), 404

    except Exception as e:
        logger.error(f"获取默认Webhook配置失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/webhook-configs/<int:config_id>/set-default', methods=['POST'])
def set_default_webhook_config(config_id):
    """设置默认Webhook配置"""
    try:
        config = WebhookConfig.query.get(config_id)
        if not config:
            return jsonify({'success': False, 'message': '配置不存在'}), 404

        # 设置为默认
        config.set_as_default()

        logger.info(f"设置默认Webhook配置: {config.webhook_name}")
        return jsonify({
            'success': True,
            'message': f'已设置 {config.webhook_name} 为默认配置',
            'data': config.to_dict(include_sensitive=False)
        })

    except Exception as e:
        logger.error(f"设置默认Webhook配置失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/webhook-configs/types', methods=['GET'])
def get_webhook_config_types():
    """获取支持的Webhook配置类型"""
    try:
        types = WebhookConfig.get_webhook_types_info()

        return jsonify({
            'success': True,
            'data': types,
            'message': '获取Webhook配置类型成功'
        })

    except Exception as e:
        logger.error(f"获取Webhook配置类型失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/webhook-configs/<int:config_id>/enable', methods=['POST'])
def enable_webhook_config(config_id):
    """启用Webhook配置"""
    try:
        config = WebhookConfig.query.get(config_id)
        if not config:
            return jsonify({'success': False, 'message': '配置不存在'}), 404

        config.is_enabled = True
        db.session.commit()

        logger.info(f"启用Webhook配置: {config.webhook_name}")
        return jsonify({
            'success': True,
            'message': '配置已启用',
            'data': config.to_dict(include_sensitive=False)
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"启用Webhook配置失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/webhook-configs/<int:config_id>/disable', methods=['POST'])
def disable_webhook_config(config_id):
    """禁用Webhook配置"""
    try:
        config = WebhookConfig.query.get(config_id)
        if not config:
            return jsonify({'success': False, 'message': '配置不存在'}), 404

        # 防止禁用默认配置
        if config.is_default:
            return jsonify({
                'success': False,
                'message': '不能禁用默认配置'
            }), 400

        config.is_enabled = False
        db.session.commit()

        logger.info(f"禁用Webhook配置: {config.webhook_name}")
        return jsonify({
            'success': True,
            'message': '配置已禁用',
            'data': config.to_dict(include_sensitive=False)
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"禁用Webhook配置失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/webhook-configs/<int:config_id>/toggle', methods=['POST'])
def toggle_webhook_config(config_id):
    """切换Webhook配置状态"""
    try:
        config = WebhookConfig.query.get(config_id)
        if not config:
            return jsonify({'success': False, 'message': '配置不存在'}), 404

        # 切换状态
        config.is_enabled = not config.is_enabled
        db.session.commit()

        status = '启用' if config.is_enabled else '禁用'
        logger.info(f"{status}Webhook配置: {config.webhook_name}")
        return jsonify({
            'success': True,
            'message': f'配置已{status}',
            'data': config.to_dict(include_sensitive=False)
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"切换Webhook配置状态失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/webhook-configs/send-test', methods=['POST'])
def send_test_alert():
    """发送测试预警消息"""
    try:
        data = request.get_json()

        # 获取测试数据
        alert_data = data.get('alert_data', {
            'ts_code': '000001.SZ',
            'stock_name': '平安银行',
            'alert_level': 'medium',
            'alert_message': '[测试] 这是一条测试预警消息',
            'current_price': 10.50,
            'threshold_value': 10.00,
            'trigger_time': datetime.now().isoformat(),
            'rule_name': '测试规则'
        })

        # 发送到所有激活的Webhook配置
        result = webhook_service.send_alert_to_webhooks(alert_data)

        return jsonify(result)

    except Exception as e:
        logger.error(f"发送测试预警消息失败: {e}")
        return jsonify({
            'success': False,
            'message': f'发送测试消息失败: {str(e)}'
        }), 500


@api_bp.route('/webhook-configs/send-to-level', methods=['POST'])
def send_alert_to_level():
    """发送预警消息到指定级别"""
    try:
        data = request.get_json()

        alert_level = data.get('alert_level', 'medium')
        alert_data = data.get('alert_data', {
            'ts_code': '000001.SZ',
            'stock_name': '平安银行',
            'alert_level': alert_level,
            'alert_message': f'[{alert_level}] 级别预警测试消息',
            'current_price': 10.50,
            'threshold_value': 10.00,
            'trigger_time': datetime.now().isoformat(),
            'rule_name': f'{alert_level}级别测试规则'
        })

        # 发送到指定级别的Webhook配置
        from app.models.webhook_config import WebhookConfig
        webhook_configs = WebhookConfig.get_configs_by_alert_level(alert_level)

        if not webhook_configs:
            return jsonify({
                'success': False,
                'message': f'没有找到支持{alert_level}级别的Webhook配置'
            }), 404

        results = []
        success_count = 0

        for webhook_config in webhook_configs:
            try:
                result = webhook_service.send_message(webhook_config, alert_data)
                results.append({
                    'webhook_name': webhook_config.webhook_name,
                    'webhook_type': webhook_config.webhook_type,
                    'result': result
                })

                if result['success']:
                    success_count += 1

            except Exception as e:
                logger.error(f"发送Webhook消息异常: {webhook_config.webhook_name} - {str(e)}")
                results.append({
                    'webhook_name': webhook_config.webhook_name,
                    'webhook_type': webhook_config.webhook_type,
                    'result': {
                        'success': False,
                        'error_message': f'发送异常: {str(e)}'
                    }
                })

        return jsonify({
            'success': success_count > 0,
            'message': f'发送完成，成功: {success_count}/{len(webhook_configs)}',
            'sent_count': len(webhook_configs),
            'success_count': success_count,
            'alert_level': alert_level,
            'results': results
        })

    except Exception as e:
        logger.error(f"发送预警消息到指定级别失败: {e}")
        return jsonify({
            'success': False,
            'message': f'发送失败: {str(e)}'
        }), 500


@api_bp.route('/webhook-configs/batch-delete', methods=['POST'])
def batch_delete_webhook_configs():
    """批量删除Webhook配置"""
    try:
        data = request.get_json()
        config_ids = data.get('config_ids', [])

        if not config_ids:
            return jsonify({
                'success': False,
                'message': '请选择要删除的配置'
            }), 400

        deleted_count = 0
        error_count = 0

        for config_id in config_ids:
            try:
                config = WebhookConfig.query.get(config_id)
                if config and not config.is_default:
                    db.session.delete(config)
                    deleted_count += 1
                elif config and config.is_default:
                    logger.warning(f"跳过默认配置: {config.webhook_name}")
                    error_count += 1
                else:
                    logger.warning(f"配置不存在: {config_id}")
                    error_count += 1

            except Exception as e:
                logger.error(f"删除配置失败: {config_id} - {str(e)}")
                error_count += 1

        if deleted_count > 0:
            db.session.commit()

        message = f'批量删除完成，成功: {deleted_count}, 失败: {error_count}'
        return jsonify({
            'success': deleted_count > 0,
            'message': message,
            'deleted_count': deleted_count,
            'error_count': error_count
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"批量删除Webhook配置失败: {e}")
        return jsonify({
            'success': False,
            'message': f'批量删除失败: {str(e)}'
        }), 500


@api_bp.route('/webhook-configs/batch-enable', methods=['POST'])
def batch_enable_webhook_configs():
    """批量启用Webhook配置"""
    try:
        data = request.get_json()
        config_ids = data.get('config_ids', [])

        if not config_ids:
            return jsonify({
                'success': False,
                'message': '请选择要启用的配置'
            }), 400

        enabled_count = 0
        error_count = 0

        for config_id in config_ids:
            try:
                config = WebhookConfig.query.get(config_id)
                if config:
                    config.is_enabled = True
                    enabled_count += 1
                else:
                    logger.warning(f"配置不存在: {config_id}")
                    error_count += 1

            except Exception as e:
                logger.error(f"启用配置失败: {config_id} - {str(e)}")
                error_count += 1

        if enabled_count > 0:
            db.session.commit()

        message = f'批量启用完成，成功: {enabled_count}, 失败: {error_count}'
        return jsonify({
            'success': enabled_count > 0,
            'message': message,
            'enabled_count': enabled_count,
            'error_count': error_count
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"批量启用Webhook配置失败: {e}")
        return jsonify({
            'success': False,
            'message': f'批量启用失败: {str(e)}'
        }), 500


@api_bp.route('/webhook-configs/batch-disable', methods=['POST'])
def batch_disable_webhook_configs():
    """批量禁用Webhook配置"""
    try:
        data = request.get_json()
        config_ids = data.get('config_ids', [])

        if not config_ids:
            return jsonify({
                'success': False,
                'message': '请选择要禁用的配置'
            }), 400

        disabled_count = 0
        error_count = 0
        default_skipped = 0

        for config_id in config_ids:
            try:
                config = WebhookConfig.query.get(config_id)
                if config and not config.is_default:
                    config.is_enabled = False
                    disabled_count += 1
                elif config and config.is_default:
                    logger.warning(f"跳过默认配置: {config.webhook_name}")
                    default_skipped += 1
                else:
                    logger.warning(f"配置不存在: {config_id}")
                    error_count += 1

            except Exception as e:
                logger.error(f"禁用配置失败: {config_id} - {str(e)}")
                error_count += 1

        if disabled_count > 0:
            db.session.commit()

        message = f'批量禁用完成，成功: {disabled_count}, 跳过默认: {default_skipped}, 失败: {error_count}'
        return jsonify({
            'success': disabled_count > 0,
            'message': message,
            'disabled_count': disabled_count,
            'default_skipped': default_skipped,
            'error_count': error_count
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"批量禁用Webhook配置失败: {e}")
        return jsonify({
            'success': False,
            'message': f'批量禁用失败: {str(e)}'
        }), 500