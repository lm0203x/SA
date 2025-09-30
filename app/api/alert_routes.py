"""
预警规则API路由
提供预警规则的创建、查询、更新、删除功能
"""

from flask import request, jsonify
from loguru import logger
from datetime import datetime
from app.api import api_bp
from app.extensions import db


# 临时使用内存存储预警规则和记录，后续可以迁移到数据库
alert_rules = []
alert_records = []


@api_bp.route('/rules', methods=['GET'])
def get_alert_rules():
    """获取预警规则列表"""
    try:
        return jsonify({
            'success': True,
            'data': alert_rules
        })
    except Exception as e:
        logger.error(f"获取预警规则失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/rules', methods=['POST'])
def create_alert_rule():
    """创建预警规则"""
    try:
        data = request.get_json()
        
        # 验证必需字段
        required_fields = ['name', 'symbol', 'rule_type', 'condition', 'threshold']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'缺少必需字段: {field}'
                }), 400
        
        # 创建新规则
        rule = {
            'id': len(alert_rules) + 1,
            'name': data['name'],
            'symbol': data['symbol'],
            'rule_type': data['rule_type'],
            'condition': data['condition'],
            'threshold': data['threshold'],
            'enabled': data.get('enabled', True),
            'created_at': datetime.now().isoformat()
        }
        
        alert_rules.append(rule)
        
        logger.info(f"创建预警规则成功: {rule['name']}")
        return jsonify({
            'success': True,
            'message': '创建成功',
            'data': rule
        })
    
    except Exception as e:
        logger.error(f"创建预警规则失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/rules/<int:rule_id>', methods=['PUT'])
def update_alert_rule(rule_id):
    """更新预警规则"""
    try:
        # 查找规则
        rule = next((r for r in alert_rules if r['id'] == rule_id), None)
        if not rule:
            return jsonify({'success': False, 'message': '规则不存在'}), 404
        
        data = request.get_json()
        
        # 更新字段
        if 'name' in data:
            rule['name'] = data['name']
        if 'symbol' in data:
            rule['symbol'] = data['symbol']
        if 'rule_type' in data:
            rule['rule_type'] = data['rule_type']
        if 'condition' in data:
            rule['condition'] = data['condition']
        if 'threshold' in data:
            rule['threshold'] = data['threshold']
        if 'enabled' in data:
            rule['enabled'] = data['enabled']
        
        rule['updated_at'] = datetime.now().isoformat()
        
        logger.info(f"更新预警规则成功: {rule['name']}")
        return jsonify({
            'success': True,
            'message': '更新成功',
            'data': rule
        })
    
    except Exception as e:
        logger.error(f"更新预警规则失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/rules/<int:rule_id>', methods=['DELETE'])
def delete_alert_rule(rule_id):
    """删除预警规则"""
    try:
        global alert_rules
        # 查找规则
        rule = next((r for r in alert_rules if r['id'] == rule_id), None)
        if not rule:
            return jsonify({'success': False, 'message': '规则不存在'}), 404
        
        # 删除规则
        alert_rules = [r for r in alert_rules if r['id'] != rule_id]
        
        logger.info(f"删除预警规则成功: {rule['name']}")
        return jsonify({'success': True, 'message': '删除成功'})
    
    except Exception as e:
        logger.error(f"删除预警规则失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/alerts', methods=['GET'])
def get_alert_records():
    """获取预警记录"""
    try:
        # 获取查询参数
        limit = request.args.get('limit', 50, type=int)
        
        # 返回最新的记录
        records = alert_records[-limit:] if alert_records else []
        
        return jsonify({
            'success': True,
            'data': records,
            'total': len(alert_records)
        })
    except Exception as e:
        logger.error(f"获取预警记录失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/alerts', methods=['POST'])
def create_alert_record():
    """创建预警记录（由系统内部调用）"""
    try:
        data = request.get_json()
        
        record = {
            'id': len(alert_records) + 1,
            'symbol': data.get('symbol'),
            'message': data.get('message'),
            'severity': data.get('severity', 'medium'),
            'price': data.get('price'),
            'change_percent': data.get('change_percent'),
            'timestamp': datetime.now().isoformat()
        }
        
        alert_records.append(record)
        
        logger.info(f"创建预警记录: {record['message']}")
        return jsonify({
            'success': True,
            'message': '创建成功',
            'data': record
        })
    
    except Exception as e:
        logger.error(f"创建预警记录失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
