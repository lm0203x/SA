"""
数据源配置API路由
提供数据源的配置、测试、管理功能
"""

from flask import request, jsonify
from loguru import logger
from app.api import api_bp
from app.extensions import db
from app.models.data_source_config import DataSourceConfig
from app.services.tushare_service import TushareService


@api_bp.route('/datasources', methods=['GET'])
def get_datasources():
    """获取所有数据源配置"""
    try:
        configs = DataSourceConfig.query.all()
        return jsonify({
            'success': True,
            'data': [config.to_dict() for config in configs]
        })
    except Exception as e:
        logger.error(f"获取数据源配置失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/datasources', methods=['POST'])
def create_datasource():
    """创建数据源配置"""
    try:
        data = request.get_json()
        
        # 验证必需字段
        if not data.get('source_type') or not data.get('source_name'):
            return jsonify({
                'success': False,
                'message': '缺少必需字段：source_type 或 source_name'
            }), 400
        
        # 创建新配置
        config = DataSourceConfig(
            source_type=data['source_type'],
            source_name=data['source_name'],
            config_data=data.get('config_data', {}),
            is_active=data.get('is_active', False),
            is_default=data.get('is_default', False)
        )
        
        # 如果设置为默认，取消其他数据源的默认状态
        if config.is_default:
            DataSourceConfig.query.filter_by(
                source_type=config.source_type,
                is_default=True
            ).update({'is_default': False})
        
        db.session.add(config)
        db.session.commit()
        
        logger.info(f"创建数据源配置成功: {config.source_name}")
        return jsonify({
            'success': True,
            'message': '创建成功',
            'data': config.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"创建数据源配置失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/datasources/<int:config_id>', methods=['PUT'])
def update_datasource(config_id):
    """更新数据源配置"""
    try:
        config = DataSourceConfig.query.get(config_id)
        if not config:
            return jsonify({'success': False, 'message': '配置不存在'}), 404
        
        data = request.get_json()
        
        # 更新字段
        if 'source_name' in data:
            config.source_name = data['source_name']
        if 'config_data' in data:
            config.config_data = data['config_data']
        if 'is_active' in data:
            config.is_active = data['is_active']
        if 'is_default' in data:
            config.is_default = data['is_default']
            # 如果设置为默认，取消其他数据源的默认状态
            if config.is_default:
                DataSourceConfig.query.filter(
                    DataSourceConfig.id != config_id,
                    DataSourceConfig.source_type == config.source_type,
                    DataSourceConfig.is_default == True
                ).update({'is_default': False})
        
        db.session.commit()
        
        logger.info(f"更新数据源配置成功: {config.source_name}")
        return jsonify({
            'success': True,
            'message': '更新成功',
            'data': config.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"更新数据源配置失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/datasources/<int:config_id>', methods=['DELETE'])
def delete_datasource(config_id):
    """删除数据源配置"""
    try:
        config = DataSourceConfig.query.get(config_id)
        if not config:
            return jsonify({'success': False, 'message': '配置不存在'}), 404
        
        db.session.delete(config)
        db.session.commit()
        
        logger.info(f"删除数据源配置成功: {config.source_name}")
        return jsonify({'success': True, 'message': '删除成功'})
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"删除数据源配置失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/datasources/<int:config_id>/test', methods=['POST'])
def test_datasource(config_id):
    """测试数据源连接"""
    try:
        config = DataSourceConfig.query.get(config_id)
        if not config:
            return jsonify({'success': False, 'message': '配置不存在'}), 404
        
        result = None
        
        # 根据数据源类型测试连接
        if config.source_type == 'tushare':
            token = config.config_data.get('token')
            if not token:
                return jsonify({
                    'success': False,
                    'message': 'Tushare Token未配置'
                }), 400
            
            tushare_service = TushareService(token)
            result = tushare_service.test_connection()
        
        elif config.source_type == 'yahoo':
            # Yahoo Finance不需要Token，直接返回成功
            result = {'success': True, 'message': 'Yahoo Finance无需配置'}
        
        else:
            return jsonify({
                'success': False,
                'message': f'不支持的数据源类型: {config.source_type}'
            }), 400
        
        # 更新配置状态
        from datetime import datetime
        config.status = '成功' if result.get('success') else '失败'
        config.last_test_time = datetime.now()
        config.error_message = result.get('message') if not result.get('success') else None
        db.session.commit()
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"测试数据源连接失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/datasources/active', methods=['GET'])
def get_active_datasource():
    """获取当前激活的数据源"""
    try:
        # 获取默认数据源
        config = DataSourceConfig.query.filter_by(
            is_active=True,
            is_default=True
        ).first()
        
        if not config:
            # 如果没有默认数据源，获取第一个激活的
            config = DataSourceConfig.query.filter_by(is_active=True).first()
        
        if config:
            return jsonify({
                'success': True,
                'data': config.to_dict()
            })
        else:
            return jsonify({
                'success': False,
                'message': '没有激活的数据源'
            }), 404
    
    except Exception as e:
        logger.error(f"获取激活数据源失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
