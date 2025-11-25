"""
系统配置API路由
提供AI配置、Tushare配置等系统参数管理接口
"""

from flask import request, jsonify
from loguru import logger
from datetime import datetime
from app.api import api_bp
from app.extensions import db
from app.models.system_config import SystemConfig
from app.services.ai_stock_analyzer import AIStockAnalyzer


@api_bp.route('/config/ai', methods=['GET'])
def get_ai_config_old():
    """获取AI配置信息"""
    try:
        ai_config = SystemConfig.get_ai_config()

        # 检查配置是否完整
        provider = ai_config.get('provider', 'tongyi')
        provider_config = ai_config.get(provider, {})
        is_configured = bool(provider_config.get('api_key'))

        return jsonify({
            'success': True,
            'data': {
                'ai_config': ai_config,
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


@api_bp.route('/config/ai', methods=['PUT'])
def update_ai_config_old():
    """更新AI配置信息"""
    try:
        data = request.get_json()
        ai_config = data.get('ai_config', {})

        # 验证提供者
        provider = ai_config.get('provider')
        if provider not in ['tongyi', 'openai', 'ollama']:
            return jsonify({
                'success': False,
                'message': '不支持的AI提供者'
            }), 400

        # 验证必要配置
        if provider != 'ollama':  # Ollama不需要API Key
            provider_config = ai_config.get(provider, {})
            if not provider_config.get('api_key'):
                return jsonify({
                    'success': False,
                    'message': f'{provider} API密钥不能为空'
                }), 400

        # 保存配置
        SystemConfig.set_ai_config(ai_config)

        logger.info(f"AI配置更新成功: provider={provider}")

        return jsonify({
            'success': True,
            'data': {
                'updated_provider': provider,
                'updated_at': datetime.now().isoformat()
            },
            'message': 'AI配置更新成功'
        })

    except Exception as e:
        logger.error(f"更新AI配置失败: {e}")
        return jsonify({
            'success': False,
            'message': f'更新AI配置失败: {str(e)}'
        }), 500


@api_bp.route('/config/ai/test', methods=['POST'])
def test_ai_config_old():
    """测试AI配置连通性"""
    try:
        data = request.get_json()
        provider = data.get('provider', 'tongyi')

        # 获取当前配置
        ai_config = SystemConfig.get_ai_config()

        # 如果提供了临时测试配置，使用临时配置
        if 'test_config' in data:
            test_config = data.get('test_config', {})
            ai_config.update(test_config)

        # 创建AI分析器进行测试
        analyzer = AIStockAnalyzer()
        analyzer.config = ai_config
        analyzer.provider = provider

        # 测试简单的API调用
        test_prompt = "请简单回复'测试成功'"
        response_text = analyzer._call_ai_api(test_prompt)

        logger.info(f"AI配置测试成功: provider={provider}")

        return jsonify({
            'success': True,
            'data': {
                'provider': provider,
                'test_response': response_text[:100] + '...' if len(response_text) > 100 else response_text,
                'test_time': datetime.now().isoformat()
            },
            'message': f'{provider} API连接测试成功'
        })

    except Exception as e:
        logger.error(f"AI配置测试失败: {e}")
        return jsonify({
            'success': False,
            'message': f'API连接测试失败: {str(e)}',
            'provider': provider
        }), 500


@api_bp.route('/config/all', methods=['GET'])
def get_all_configs():
    """获取所有系统配置"""
    try:
        configs = SystemConfig.get_all_configs()

        # 隐藏敏感信息
        safe_configs = {}
        for key, value in configs.items():
            safe_configs[key] = {
                'type': value['type'],
                'description': value['description'],
                'is_encrypted': value['is_encrypted'],
                'updated_at': value['updated_at'],
                'has_value': bool(value['value']) if not value['is_encrypted'] else '***'
            }

        return jsonify({
            'success': True,
            'data': {
                'configs': safe_configs,
                'total_count': len(configs)
            },
            'message': f'获取到 {len(configs)} 个配置项'
        })

    except Exception as e:
        logger.error(f"获取系统配置失败: {e}")
        return jsonify({
            'success': False,
            'message': f'获取系统配置失败: {str(e)}'
        }), 500


@api_bp.route('/config/<string:config_key>', methods=['PUT'])
def update_config(config_key):
    """更新单个配置项"""
    try:
        data = request.get_json()
        config_value = data.get('config_value')
        config_type = data.get('config_type', 'string')
        description = data.get('description', '')
        is_encrypted = data.get('is_encrypted', False)

        # 检查是否为敏感配置
        sensitive_keys = ['api_key', 'secret', 'password', 'token']
        auto_encrypt = any(key in config_key.lower() for key in sensitive_keys)
        if auto_encrypt and not is_encrypted:
            is_encrypted = True

        config = SystemConfig.set_config(
            config_key=config_key,
            config_value=config_value,
            config_type=config_type,
            description=description,
            is_encrypted=is_encrypted
        )

        logger.info(f"配置更新成功: {config_key}")

        return jsonify({
            'success': True,
            'data': {
                'config_key': config_key,
                'updated_at': config.updated_at.isoformat() if config.updated_at else None
            },
            'message': '配置更新成功'
        })

    except Exception as e:
        logger.error(f"更新配置失败: {e}")
        return jsonify({
            'success': False,
            'message': f'更新配置失败: {str(e)}'
        }), 500


@api_bp.route('/config/tushare', methods=['GET'])
def get_tushare_config():
    """获取Tushare配置"""
    try:
        tushare_config = {
            'token': SystemConfig.get_config('tushare_token', ''),
            'api_url': SystemConfig.get_config('tushare_api_url', 'http://api.tushare.pro'),
            'timeout': int(SystemConfig.get_config('tushare_timeout', 30))
        }

        return jsonify({
            'success': True,
            'data': {
                'tushare_config': tushare_config,
                'has_token': bool(tushare_config['token'])
            },
            'message': '获取Tushare配置成功'
        })

    except Exception as e:
        logger.error(f"获取Tushare配置失败: {e}")
        return jsonify({
            'success': False,
            'message': f'获取Tushare配置失败: {str(e)}'
        }), 500


@api_bp.route('/config/tushare', methods=['PUT'])
def update_tushare_config():
    """更新Tushare配置"""
    try:
        data = request.get_json()
        tushare_config = data.get('tushare_config', {})

        # 验证token
        if not tushare_config.get('token'):
            return jsonify({
                'success': False,
                'message': 'Tushare Token不能为空'
            }), 400

        # 保存配置
        SystemConfig.set_config('tushare_token', tushare_config.get('token', ''), 'string', 'Tushare API Token', True)
        SystemConfig.set_config('tushare_api_url', tushare_config.get('api_url', 'http://api.tushare.pro'), 'string', 'Tushare API地址')
        SystemConfig.set_config('tushare_timeout', tushare_config.get('timeout', 30), 'string', 'Tushare请求超时时间')

        logger.info("Tushare配置更新成功")

        return jsonify({
            'success': True,
            'data': {
                'updated_at': datetime.now().isoformat()
            },
            'message': 'Tushare配置更新成功'
        })

    except Exception as e:
        logger.error(f"更新Tushare配置失败: {e}")
        return jsonify({
            'success': False,
            'message': f'更新Tushare配置失败: {str(e)}'
        }), 500