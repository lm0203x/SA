"""
预警规则API路由
提供预警规则的创建、查询、更新、删除功能
"""

from flask import request, jsonify
from loguru import logger
from datetime import datetime, timedelta
from app.api import api_bp
from app.extensions import db
from app.models.alert_rule import AlertRule
from app.models.risk_alert import RiskAlert
from app.models.stock_basic import StockBasic
from app.services.stock_data_service import StockDataService
from app.services.alert_trigger_engine import alert_trigger_engine


# ==================== 预警规则管理 ====================

@api_bp.route('/rules', methods=['GET'])
def get_alert_rules():
    """获取预警规则列表"""
    try:
        # 获取查询参数
        ts_code = request.args.get('ts_code')
        rule_type = request.args.get('rule_type')
        is_enabled = request.args.get('is_enabled')
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        
        # 构建查询
        query = AlertRule.query.filter_by(is_active=True)
        
        if ts_code:
            query = query.filter_by(ts_code=ts_code)
        if rule_type:
            query = query.filter_by(rule_type=rule_type)
        if is_enabled is not None:
            enabled = is_enabled.lower() == 'true'
            query = query.filter_by(is_enabled=enabled)
        
        # 分页查询
        pagination = query.order_by(AlertRule.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        rules = [rule.to_dict() for rule in pagination.items]
        
        return jsonify({
            'success': True,
            'data': {
                'rules': rules,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            },
            'message': f'获取到 {len(rules)} 条预警规则'
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
        required_fields = ['rule_name', 'ts_code', 'rule_type', 'threshold_value', 'comparison_operator']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'缺少必需字段: {field}'
                }), 400
        
        # 验证股票代码是否存在
        stock = StockBasic.query.filter_by(ts_code=data['ts_code']).first()
        if not stock:
            # 检查是否有任何股票数据
            total_stocks = StockBasic.query.count()
            if total_stocks == 0:
                return jsonify({
                    'success': False,
                    'message': '股票基础数据为空，请先同步股票列表。运行命令：python sync_stock_data.py'
                }), 400
            else:
                return jsonify({
                    'success': False,
                    'message': f'股票代码 {data["ts_code"]} 不存在，请检查代码格式（如：000001.SZ）'
                }), 400
        
        # 验证规则类型
        if data['rule_type'] not in AlertRule.RULE_TYPES:
            return jsonify({
                'success': False,
                'message': f'无效的规则类型: {data["rule_type"]}'
            }), 400
        
        # 验证比较运算符
        if data['comparison_operator'] not in AlertRule.OPERATORS:
            return jsonify({
                'success': False,
                'message': f'无效的比较运算符: {data["comparison_operator"]}'
            }), 400
        
        # 创建预警规则
        rule = AlertRule.create_rule(
            rule_name=data['rule_name'],
            ts_code=data['ts_code'],
            rule_type=data['rule_type'],
            condition_type=data.get('condition_type', 'realtime'),
            threshold_value=float(data['threshold_value']),
            comparison_operator=data['comparison_operator'],
            alert_level=data.get('alert_level', 'medium'),
            alert_message_template=data.get('alert_message_template'),
            extra_config=data.get('extra_config')
        )
        
        logger.info(f"创建预警规则成功: {rule.rule_name} ({rule.id})")
        
        return jsonify({
            'success': True,
            'data': rule.to_dict(),
            'message': f'预警规则 "{rule.rule_name}" 创建成功'
        }), 201
        
    except Exception as e:
        logger.error(f"创建预警规则失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/rules/<int:rule_id>', methods=['GET'])
def get_alert_rule(rule_id):
    """获取单个预警规则详情"""
    try:
        rule = AlertRule.query.filter_by(id=rule_id, is_active=True).first()
        if not rule:
            return jsonify({
                'success': False,
                'message': f'预警规则 {rule_id} 不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'data': rule.to_dict(),
            'message': '获取预警规则详情成功'
        })
        
    except Exception as e:
        logger.error(f"获取预警规则详情失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/rules/<int:rule_id>', methods=['PUT'])
def update_alert_rule(rule_id):
    """更新预警规则"""
    try:
        rule = AlertRule.query.filter_by(id=rule_id, is_active=True).first()
        if not rule:
            return jsonify({
                'success': False,
                'message': f'预警规则 {rule_id} 不存在'
            }), 404
        
        data = request.get_json()
        
        # 可更新的字段
        updatable_fields = [
            'rule_name', 'threshold_value', 'comparison_operator', 
            'alert_level', 'alert_message_template', 'is_enabled', 'extra_config'
        ]
        
        update_data = {}
        for field in updatable_fields:
            if field in data:
                update_data[field] = data[field]
        
        if update_data:
            rule.update_rule(**update_data)
            logger.info(f"更新预警规则成功: {rule.rule_name} ({rule.id})")
        
        return jsonify({
            'success': True,
            'data': rule.to_dict(),
            'message': f'预警规则 "{rule.rule_name}" 更新成功'
        })
        
    except Exception as e:
        logger.error(f"更新预警规则失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/rules/<int:rule_id>', methods=['DELETE'])
def delete_alert_rule(rule_id):
    """删除预警规则（软删除）"""
    try:
        rule = AlertRule.query.filter_by(id=rule_id, is_active=True).first()
        if not rule:
            return jsonify({
                'success': False,
                'message': f'预警规则 {rule_id} 不存在'
            }), 404
        
        # 软删除
        rule.update_rule(is_active=False)
        
        logger.info(f"删除预警规则成功: {rule.rule_name} ({rule.id})")
        
        return jsonify({
            'success': True,
            'message': f'预警规则 "{rule.rule_name}" 删除成功'
        })
        
    except Exception as e:
        logger.error(f"删除预警规则失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/rules/<int:rule_id>/toggle', methods=['POST'])
def toggle_alert_rule(rule_id):
    """切换预警规则启用状态"""
    try:
        rule = AlertRule.query.filter_by(id=rule_id, is_active=True).first()
        if not rule:
            return jsonify({
                'success': False,
                'message': f'预警规则 {rule_id} 不存在'
            }), 404
        
        # 切换启用状态
        if rule.is_enabled:
            rule.disable_rule()
            action = '禁用'
        else:
            rule.enable_rule()
            action = '启用'
        
        logger.info(f"{action}预警规则成功: {rule.rule_name} ({rule.id})")
        
        return jsonify({
            'success': True,
            'data': rule.to_dict(),
            'message': f'预警规则 "{rule.rule_name}" {action}成功'
        })
        
    except Exception as e:
        logger.error(f"切换预警规则状态失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ==================== 预警记录管理 ====================

@api_bp.route('/alerts', methods=['GET'])
def get_alert_records():
    """获取预警记录列表"""
    try:
        # 获取查询参数
        ts_code = request.args.get('ts_code')
        alert_type = request.args.get('alert_type')
        alert_level = request.args.get('alert_level')
        is_active = request.args.get('is_active')
        days = int(request.args.get('days', 7))  # 默认查询最近7天
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 50)), 100)
        
        # 构建查询
        query = RiskAlert.query
        
        # 时间范围过滤
        start_date = datetime.now() - timedelta(days=days)
        query = query.filter(RiskAlert.created_at >= start_date)
        
        if ts_code:
            query = query.filter_by(ts_code=ts_code)
        if alert_type:
            query = query.filter_by(alert_type=alert_type)
        if alert_level:
            query = query.filter_by(alert_level=alert_level)
        if is_active is not None:
            active = is_active.lower() == 'true'
            query = query.filter_by(is_active=active)
        
        # 分页查询
        pagination = query.order_by(RiskAlert.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        records = [record.to_dict() for record in pagination.items]
        
        return jsonify({
            'success': True,
            'data': {
                'records': records,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            },
            'message': f'获取到 {len(records)} 条预警记录'
        })
        
    except Exception as e:
        logger.error(f"获取预警记录失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/alerts', methods=['POST'])
def create_alert_record():
    """创建预警记录"""
    try:
        data = request.get_json()
        
        # 验证必需字段
        required_fields = ['ts_code', 'alert_type', 'alert_level', 'alert_message']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'缺少必需字段: {field}'
                }), 400
        
        # 创建预警记录
        alert = RiskAlert.create_alert(
            ts_code=data['ts_code'],
            alert_type=data['alert_type'],
            alert_level=data['alert_level'],
            alert_message=data['alert_message'],
            risk_value=data.get('risk_value'),
            threshold_value=data.get('threshold_value'),
            current_price=data.get('current_price'),
            position_size=data.get('position_size'),
            portfolio_weight=data.get('portfolio_weight')
        )
        
        logger.info(f"创建预警记录成功: {alert.ts_code} - {alert.alert_type}")
        
        return jsonify({
            'success': True,
            'data': alert.to_dict(),
            'message': '预警记录创建成功'
        }), 201
        
    except Exception as e:
        logger.error(f"创建预警记录失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/alerts/<int:alert_id>/resolve', methods=['POST'])
def resolve_alert_record(alert_id):
    """解决预警记录"""
    try:
        alert = RiskAlert.query.get(alert_id)
        if not alert:
            return jsonify({
                'success': False,
                'message': f'预警记录 {alert_id} 不存在'
            }), 404
        
        alert.resolve_alert()
        
        logger.info(f"解决预警记录成功: {alert.ts_code} - {alert.alert_type}")
        
        return jsonify({
            'success': True,
            'data': alert.to_dict(),
            'message': '预警记录已解决'
        })
        
    except Exception as e:
        logger.error(f"解决预警记录失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ==================== 统计信息 ====================

@api_bp.route('/alert/stats', methods=['GET'])
def get_alert_stats():
    """获取预警统计信息"""
    try:
        # 获取规则统计
        rule_stats = AlertRule.get_rule_stats()
        
        # 获取预警统计
        alert_stats = RiskAlert.get_alert_stats()
        
        # 最近预警趋势（最近7天）
        recent_alerts = []
        for i in range(7):
            date = datetime.now().date() - timedelta(days=i)
            start_time = datetime.combine(date, datetime.min.time())
            end_time = datetime.combine(date, datetime.max.time())
            
            count = RiskAlert.query.filter(
                RiskAlert.created_at >= start_time,
                RiskAlert.created_at <= end_time
            ).count()
            
            recent_alerts.append({
                'date': date.isoformat(),
                'count': count
            })
        
        return jsonify({
            'success': True,
            'data': {
                'rule_stats': rule_stats,
                'alert_stats': alert_stats,
                'recent_trend': list(reversed(recent_alerts))
            },
            'message': '获取预警统计信息成功'
        })
        
    except Exception as e:
        logger.error(f"获取预警统计信息失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ==================== 规则类型和选项 ====================

@api_bp.route('/alert/options', methods=['GET'])
def get_alert_options():
    """获取预警配置选项"""
    try:
        # 获取股票数量统计
        stock_count = StockBasic.query.count()
        
        return jsonify({
            'success': True,
            'data': {
                'rule_types': AlertRule.RULE_TYPES,
                'operators': AlertRule.OPERATORS,
                'alert_levels': AlertRule.ALERT_LEVELS,
                'stock_count': stock_count
            },
            'message': '获取预警配置选项成功'
        })
        
    except Exception as e:
        logger.error(f"获取预警配置选项失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/alert/sync-stocks', methods=['POST'])
def sync_alert_stocks():
    """同步股票基础数据"""
    try:
        force_update = request.json.get('force_update', False) if request.json else False
        
        logger.info(f"开始同步股票数据，强制更新: {force_update}")
        
        result = StockDataService.sync_stock_list(force_update=force_update)
        
        if result['success']:
            logger.info(f"股票数据同步成功: {result}")
            return jsonify(result)
        else:
            logger.error(f"股票数据同步失败: {result}")
            return jsonify(result), 500
        
    except Exception as e:
        logger.error(f"同步股票数据失败: {e}")
        return jsonify({
            'success': False,
            'message': f'同步股票数据失败: {str(e)}'
        }), 500


@api_bp.route('/alert/stocks/search', methods=['GET'])
def search_stocks():
    """搜索股票"""
    try:
        query = request.args.get('q', '').strip()
        limit = min(int(request.args.get('limit', 20)), 100)
        
        if not query:
            return jsonify({
                'success': False,
                'message': '请提供搜索关键词'
            }), 400
        
        # 搜索股票（按代码或名称）
        stocks = StockBasic.query.filter(
            db.or_(
                StockBasic.ts_code.like(f'%{query}%'),
                StockBasic.name.like(f'%{query}%'),
                StockBasic.symbol.like(f'%{query}%')
            )
        ).limit(limit).all()
        
        results = []
        for stock in stocks:
            results.append({
                'ts_code': stock.ts_code,
                'symbol': stock.symbol,
                'name': stock.name,
                'area': stock.area,
                'industry': stock.industry,
                'list_date': stock.list_date.isoformat() if stock.list_date else None
            })
        
        return jsonify({
            'success': True,
            'data': results,
            'message': f'找到 {len(results)} 只股票'
        })
        
    except Exception as e:
        logger.error(f"搜索股票失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ==================== 预警触发检查 ====================

@api_bp.route('/trigger/check', methods=['POST'])
def trigger_alert_check():
    """手动触发预警检查"""
    try:
        data = request.get_json() or {}
        
        # 获取参数
        ts_codes = data.get('ts_codes')  # 指定股票代码列表
        rule_types = data.get('rule_types')  # 指定规则类型列表
        
        # 运行预警检查
        result = alert_trigger_engine.run_alert_check(
            ts_codes=ts_codes,
            rule_types=rule_types
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"触发预警检查失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'触发预警检查失败: {str(e)}'
        }), 500


@api_bp.route('/trigger/stats', methods=['GET'])
def get_trigger_stats():
    """获取预警触发统计"""
    try:
        days = request.args.get('days', 7, type=int)
        
        result = alert_trigger_engine.get_trigger_stats(days=days)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"获取触发统计失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取触发统计失败: {str(e)}'
        }), 500


@api_bp.route('/trigger/stock/<string:ts_code>', methods=['POST'])
def trigger_stock_check(ts_code):
    """触发指定股票的预警检查"""
    try:
        # 运行指定股票的预警检查
        result = alert_trigger_engine.run_alert_check(ts_codes=[ts_code])
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"触发股票 {ts_code} 预警检查失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'触发股票预警检查失败: {str(e)}'
        }), 500