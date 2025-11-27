"""
AI配置API路由
提供AI服务提供商的配置、测试、管理功能
参考数据源配置的实现模式
"""

from flask import request, jsonify
from loguru import logger
from app.api import api_bp
from app.extensions import db
from app.models.ai_config import AIConfig
from app.services.ai_stock_analyzer import AIStockAnalyzer


@api_bp.route('/ai-configs', methods=['GET'])
def get_ai_configs():
    """获取所有AI配置"""
    try:
        configs = AIConfig.query.all()
        return jsonify({
            'success': True,
            'data': [config.to_dict(include_sensitive=False) for config in configs]
        })
    except Exception as e:
        logger.error(f"获取AI配置失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/ai-configs', methods=['POST'])
def create_ai_config():
    """创建AI配置"""
    try:
        data = request.get_json()

        # 验证必需字段
        if not data.get('provider_type') or not data.get('provider_name'):
            return jsonify({
                'success': False,
                'message': '缺少必需字段：provider_type 或 provider_name'
            }), 400

        # 验证AI提供者类型
        valid_providers = ['tongyi', 'openai', 'zhipu', 'ollama', 'custom']
        if data['provider_type'] not in valid_providers:
            return jsonify({
                'success': False,
                'message': f'不支持的AI提供者类型: {data["provider_type"]}'
            }), 400


        # 创建新配置
        config = AIConfig(
            provider_type=data['provider_type'],
            provider_name=data['provider_name'],
            config_data=data.get('config_data', {}),
            is_active=data.get('is_active', False),
            is_default=data.get('is_default', False)
        )

        # 如果设置为默认，取消其他AI配置的默认状态
        if config.is_default:
            AIConfig.query.update({'is_default': False})

        db.session.add(config)
        db.session.commit()

        logger.info(f"创建AI配置成功: {config.provider_name}")
        return jsonify({
            'success': True,
            'message': '创建成功',
            'data': config.to_dict(include_sensitive=False)
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"创建AI配置失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/ai-configs/<int:config_id>', methods=['PUT'])
def update_ai_config(config_id):
    """更新AI配置"""
    try:
        config = AIConfig.query.get(config_id)
        if not config:
            return jsonify({'success': False, 'message': '配置不存在'}), 404

        data = request.get_json()

        # 更新字段
        if 'provider_name' in data:
            config.provider_name = data['provider_name']
        if 'config_data' in data:
            new_config_data = data['config_data']
            
            # 处理API密钥掩码问题
            # 如果前端传回的是掩码后的密钥（包含*），则保留原有的密钥
            if 'api_key' in new_config_data and config.config_data and 'api_key' in config.config_data:
                new_key = new_config_data['api_key']
                old_key = config.config_data['api_key']
                
                # 如果新密钥包含*，可能是掩码
                if '*' in new_key:
                    # 生成旧密钥的掩码形式进行比对
                    masked_old_key = old_key
                    if len(old_key) > 8:
                        masked_old_key = old_key[:4] + '*' * (len(old_key) - 8) + old_key[-4:]
                    else:
                        masked_old_key = '*' * len(old_key)
                    
                    # 如果新密钥与掩码后的旧密钥一致，说明用户没有修改密钥，恢复旧密钥
                    if new_key == masked_old_key:
                        new_config_data['api_key'] = old_key
            
            config.config_data = new_config_data

        if 'is_active' in data:
            config.is_active = data['is_active']
        if 'is_default' in data:
            config.is_default = data['is_default']
            # 如果设置为默认，取消其他AI配置的默认状态
            if config.is_default:
                AIConfig.query.filter(
                    AIConfig.id != config_id
                ).update({'is_default': False})

        db.session.commit()

        logger.info(f"更新AI配置成功: {config.provider_name}")
        return jsonify({
            'success': True,
            'message': '更新成功',
            'data': config.to_dict(include_sensitive=False)
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"更新AI配置失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/ai-configs/<int:config_id>', methods=['DELETE'])
def delete_ai_config(config_id):
    """删除AI配置"""
    try:
        config = AIConfig.query.get(config_id)
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

        logger.info(f"删除AI配置成功: {config.provider_name}")
        return jsonify({'success': True, 'message': '删除成功'})

    except Exception as e:
        db.session.rollback()
        logger.error(f"删除AI配置失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/ai-configs/<int:config_id>/test', methods=['POST'])
def test_ai_config(config_id):
    """测试AI配置连接"""
    try:
        config = AIConfig.query.get(config_id)
        if not config:
            return jsonify({'success': False, 'message': '配置不存在'}), 404

        # 验证配置数据
        if not config.config_data:
            return jsonify({
                'success': False,
                'message': '配置数据为空'
            }), 400

        # 根据提供者类型验证必需配置
        if config.provider_type in ['tongyi', 'openai']:
            if not config.config_data.get('api_key'):
                return jsonify({
                    'success': False,
                    'message': f'{config.provider_type} API密钥未配置'
                }), 400

        try:
            # 创建AI分析器进行测试
            analyzer = AIStockAnalyzer()

            # 临时配置用于测试
            test_config = AIConfig.get_config_dict()
            test_config['provider'] = config.provider_type
            test_config[config.provider_type] = config.config_data

            analyzer.config = test_config
            analyzer.provider = config.provider_type

            # 测试简单的API调用
            test_prompt = "请简单回复'测试成功'"
            response_text = analyzer._call_ai_api(test_prompt)

            # 更新配置状态
            from datetime import datetime
            config.status = '成功'
            config.last_test_time = datetime.now()
            config.error_message = None
            db.session.commit()

            logger.info(f"AI配置测试成功: {config.provider_name}")
            return jsonify({
                'success': True,
                'message': '连接测试成功',
                'data': {
                    'test_response': response_text[:100] + '...' if len(response_text) > 100 else response_text,
                    'test_time': config.last_test_time.isoformat()
                }
            })

        except Exception as test_error:
            # 更新配置状态
            from datetime import datetime
            config.status = '失败'
            config.last_test_time = datetime.now()
            config.error_message = str(test_error)
            db.session.commit()

            logger.error(f"AI配置测试失败: {config.provider_name} - {test_error}")
            return jsonify({
                'success': False,
                'message': f'连接测试失败: {str(test_error)}'
            }), 500

    except Exception as e:
        logger.error(f"测试AI配置失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/ai-configs/active', methods=['GET'])
def get_active_ai_config():
    """获取当前激活的AI配置"""
    try:
        config = AIConfig.get_active_config()

        if config:
            return jsonify({
                'success': True,
                'data': config.to_dict(include_sensitive=False)
            })
        else:
            return jsonify({
                'success': False,
                'message': '没有激活的AI配置'
            }), 404

    except Exception as e:
        logger.error(f"获取激活AI配置失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/ai-configs/current', methods=['GET'])
def get_current_ai_config():
    """获取当前AI配置（兼容原有接口）"""
    try:
        config_dict = AIConfig.get_config_dict()

        # 检查配置是否完整
        provider = config_dict.get('provider', 'tongyi')
        provider_config = config_dict.get(provider, {})
        is_configured = bool(provider_config.get('api_key'))

        return jsonify({
            'success': True,
            'data': {
                'ai_config': config_dict,
                'is_configured': is_configured,
                'current_provider': provider,
                'supported_providers': ['tongyi', 'openai', 'ollama']
            },
            'message': '获取AI配置成功'
        })

    except Exception as e:
        logger.error(f"获取AI配置失败: {e}")
        return jsonify({
            'success': False,
            'message': f'获取AI配置失败: {str(e)}'
        }), 500


@api_bp.route('/ai-configs/<int:config_id>/set-default', methods=['POST'])
def set_default_ai_config(config_id):
    """设置默认AI配置"""
    try:
        config = AIConfig.query.get(config_id)
        if not config:
            return jsonify({'success': False, 'message': '配置不存在'}), 404

        # 设置为默认
        config.set_as_default()

        logger.info(f"设置默认AI配置: {config.provider_name}")
        return jsonify({
            'success': True,
            'message': f'已设置 {config.provider_name} 为默认配置',
            'data': config.to_dict(include_sensitive=False)
        })

    except Exception as e:
        logger.error(f"设置默认AI配置失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/ai-configs/types', methods=['GET'])
def get_ai_config_types():
    """获取支持的AI配置类型"""
    try:
        types = [
            {
                'type': 'tongyi',
                'name': '通义千问',
                'description': '阿里云通义千问大语言模型',
                'required_fields': ['api_key', 'model'],
                'optional_fields': ['base_url', 'timeout'],
                'default_config': {
                    'model': 'qwen-plus',
                    'base_url': 'https://dashscope.aliyuncs.com/api/v1',
                    'timeout': 30
                }
            },
            {
                'type': 'openai',
                'name': 'OpenAI',
                'description': 'OpenAI GPT系列模型',
                'required_fields': ['api_key', 'model'],
                'optional_fields': ['base_url', 'timeout'],
                'default_config': {
                    'model': 'gpt-3.5-turbo',
                    'base_url': 'https://api.openai.com/v1',
                    'timeout': 30
                }
            },
            {
                'type': 'zhipu',
                'name': '智谱GLM',
                'description': '智谱AI GLM系列模型',
                'required_fields': ['api_key', 'model'],
                'optional_fields': ['base_url', 'timeout'],
                'default_config': {
                    'model': 'glm-4',
                    'base_url': 'https://open.bigmodel.cn/api/paas/v4',
                    'timeout': 30
                }
            },
            {
                'type': 'ollama',
                'name': 'Ollama',
                'description': '本地部署的Ollama服务',
                'required_fields': [],
                'optional_fields': ['base_url', 'model', 'timeout'],
                'default_config': {
                    'base_url': 'http://localhost:11434',
                    'model': 'qwen2.5-coder',
                    'timeout': 30
                }
            },
            {
                'type': 'custom',
                'name': '自定义',
                'description': '自定义AI服务（兼容OpenAI格式）',
                'required_fields': ['api_key', 'model', 'base_url'],
                'optional_fields': ['timeout'],
                'default_config': {
                    'model': 'custom-model',
                    'base_url': 'https://your-api-endpoint.com/v1',
                    'timeout': 30
                }
            }
        ]

        return jsonify({
            'success': True,
            'data': types,
            'message': '获取AI配置类型成功'
        })

    except Exception as e:
        logger.error(f"获取AI配置类型失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500