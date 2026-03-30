"""
AI股票分析API路由
提供AI股票推荐和分析功能
"""

from flask import request, jsonify
from loguru import logger
from datetime import datetime, timedelta
import json
from app.api import api_bp
from app.extensions import db
from app.services.ai_stock_analyzer import get_ai_analyzer
from app.services.news_service import NewsService
from app.services.operation_log_service import OperationLogService
from app.models.ai_analysis import AIAnalysisRecord
from app.models.analysis import AnalysisStrategy, AnalysisTask, AnalysisResult
from app.models.stock_basic import StockBasic
from app.models.stock_daily_history import StockDailyHistory
from app.models.stock_daily_basic import StockDailyBasic
from app.models.stock_moneyflow import StockMoneyflow
from app.models.watchlist import Watchlist
from app.utils.auth import get_request_user


@api_bp.route('/ai/stock-recommendation', methods=['POST'])
def get_stock_recommendation():
    """获取股票AI推荐"""
    try:
        data = request.get_json()
        ts_code = data.get('ts_code')

        if not ts_code:
            return jsonify({
                'success': False,
                'message': '请提供股票代码'
            }), 400

        # 验证股票代码格式
        if not ts_code.endswith(('.SZ', '.SH')):
            return jsonify({
                'success': False,
                'message': '股票代码格式错误，请使用 .SZ 或 .SH 结尾'
            }), 400

        # 获取股票信息
        stock_info = StockBasic.query.filter_by(ts_code=ts_code).first()
        if not stock_info:
            return jsonify({
                'success': False,
                'message': f'股票代码 {ts_code} 不存在'
            }), 404

        # 记录开始时间
        start_time = datetime.utcnow()

        # 获取最新数据
        latest_daily = StockDailyHistory.query.filter_by(
            ts_code=ts_code
        ).order_by(StockDailyHistory.trade_date.desc()).first()

        latest_basic = StockDailyBasic.query.filter_by(
            ts_code=ts_code
        ).order_by(StockDailyBasic.trade_date.desc()).first()

        # 检查是否在自选股中
        from app.models.watchlist import Watchlist
        is_watchlist = Watchlist.query.filter_by(ts_code=ts_code).first() is not None

        # 获取最新资讯
        try:
            news_list = NewsService.get_stock_news(ts_code, stock_info.name, limit=3)
            news_text = NewsService.format_news_for_prompt(news_list)
        except Exception as e:
            logger.warning(f"获取股票资讯失败: {e}")
            news_list = []
            news_text = "暂无最新资讯"

        # 准备分析数据
        def _to_float(val, default=0.0):
            try:
                return float(val)
            except (TypeError, ValueError):
                return default

        stock_data = {
            'current_price': _to_float(latest_daily.close) if latest_daily else 0.0,
            'change_pct': _to_float(latest_daily.pct_chg) if latest_daily else 0.0,
            'volume_ratio': _to_float(latest_basic.volume_ratio) if latest_basic else 0.0,
            'pe_ratio': _to_float(latest_basic.pe) if latest_basic else 0.0,
            'pb_ratio': _to_float(latest_basic.pb) if latest_basic else 0.0,
            'turnover_rate': _to_float(latest_basic.turnover_rate) if latest_basic else 0.0,
            'total_mv': _to_float(latest_basic.total_mv) if latest_basic else 0.0,
            'is_watchlist': is_watchlist,  # 自选股标记
            'news': news_text,  # 最新资讯
            'news_list': news_list  # 资讯列表（用于返回给前端）
        }

        # AI分析
        try:
            analyzer = get_ai_analyzer()
            # 每次分析前重新加载配置，确保使用最新的配置（如timeout）
            analyzer.reload_config()
            result = analyzer.analyze_stock(ts_code, stock_info.name, stock_data)
            response_time = (datetime.utcnow() - start_time).total_seconds()

            # 保存分析记录
            AIAnalysisRecord.create_record(
                ts_code=ts_code,
                stock_name=stock_info.name,
                recommendation=result['recommendation'],
                confidence=result['confidence'],
                target_price=result.get('target_price', 0.0),
                risk_level=result.get('risk_level', 'medium'),
                reasons=result.get('reasons', []),
                ai_provider=result.get('ai_provider'),
                analysis_data=stock_data,
                success=True,
                response_time=response_time
            )

            logger.info(f"AI推荐生成成功: {ts_code} - {result['recommendation']}")
            OperationLogService.record(
                module='ai_analysis',
                action_type='analyze',
                action_name='AI股票分析',
                user=get_request_user(),
                target_type='stock',
                target_id=ts_code,
                target_name=stock_info.name,
                message=f"分析完成: {result['recommendation']}",
            )

            # 添加股票数据到响应中，供前端显示
            result['data_summary'] = {
                'current_price': stock_data.get('current_price', 0.0),
                'change_pct': stock_data.get('change_pct', 0.0)
            }

            return jsonify({
                'success': True,
                'data': result,
                'message': 'AI分析完成'
            })

        except Exception as e:
            response_time = (datetime.utcnow() - start_time).total_seconds()
            error_msg = str(e)

            # 保存失败记录
            AIAnalysisRecord.create_record(
                ts_code=ts_code,
                stock_name=stock_info.name,
                recommendation='hold',
                confidence=0.0,
                risk_level='medium',
                reasons=[f'分析失败: {error_msg}'],
                analysis_data=stock_data,
                success=False,
                error_message=error_msg,
                response_time=response_time
            )

            logger.error(f"AI分析失败: {e}")
            return jsonify({
                'success': False,
                'message': f'AI分析失败: {error_msg}'
            }), 500

    except Exception as e:
        logger.error(f"获取AI推荐失败: {e}")
        return jsonify({
            'success': False,
            'message': f'请求处理失败: {str(e)}'
        }), 500


@api_bp.route('/analysis/tasks', methods=['GET'])
def get_analysis_tasks():
    """获取分析任务列表"""
    try:
        strategy_id = request.args.get('strategy_id', type=int)
        status = request.args.get('status')
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)

        query = AnalysisTask.query

        if strategy_id:
            query = query.filter_by(strategy_id=strategy_id)
        if status:
            query = query.filter_by(status=status)

        pagination = query.order_by(
            AnalysisTask.created_at.desc(),
            AnalysisTask.id.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)

        strategy_map = {}
        if pagination.items:
            strategy_ids = list({task.strategy_id for task in pagination.items})
            strategy_map = {
                item.id: item
                for item in AnalysisStrategy.query.filter(
                    AnalysisStrategy.id.in_(strategy_ids)
                ).all()
            }

        tasks = []
        for task in pagination.items:
            task_data = task.to_dict()
            strategy = strategy_map.get(task.strategy_id)
            task_data['strategy_name'] = strategy.name if strategy else None
            task_data['strategy_code'] = strategy.code if strategy else None
            tasks.append(task_data)

        OperationLogService.record(
            module='strategy',
            action_type='view',
            action_name='查看分析任务列表',
            user=get_request_user(),
            message=f'共返回 {len(tasks)} 条任务',
        )
        return jsonify({
            'success': True,
            'data': {
                'tasks': tasks,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            },
            'message': f'获取到 {len(tasks)} 条分析任务'
        })
    except Exception as e:
        logger.error(f'获取分析任务列表失败: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/analysis/tasks/<int:task_id>', methods=['GET'])
def get_analysis_task_detail(task_id):
    """获取分析任务详情及结果"""
    try:
        task = AnalysisTask.query.filter_by(id=task_id).first()
        if not task:
            return jsonify({
                'success': False,
                'message': f'分析任务 {task_id} 不存在'
            }), 404

        strategy = AnalysisStrategy.query.filter_by(id=task.strategy_id).first()
        results = AnalysisResult.query.filter_by(task_id=task.id).order_by(
            AnalysisResult.score.desc(),
            AnalysisResult.id.asc()
        ).all()

        task_data = task.to_dict()
        task_data['strategy_name'] = strategy.name if strategy else None
        task_data['strategy_code'] = strategy.code if strategy else None

        OperationLogService.record(
            module='strategy',
            action_type='view',
            action_name='查看分析任务详情',
            user=get_request_user(),
            target_type='task',
            target_id=task.id,
            target_name=strategy.name if strategy else str(task.id),
            message=f'查看任务 {task.id} 详情',
        )
        return jsonify({
            'success': True,
            'data': {
                'task': task_data,
                'results': [item.to_dict() for item in results]
            },
            'message': f'获取分析任务 {task_id} 详情成功'
        })
    except Exception as e:
        logger.error(f'获取分析任务详情失败: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/analysis/stocks/<string:ts_code>/history-legacy', methods=['GET'])
def get_analysis_stock_history_legacy(ts_code):
    """获取单只股票的分析历史"""
    try:
        limit = min(request.args.get('limit', 20, type=int), 100)
        stock_info = StockBasic.query.filter_by(ts_code=ts_code).first()

        query = db.session.query(AnalysisResult, AnalysisTask, AnalysisStrategy).join(
            AnalysisTask, AnalysisResult.task_id == AnalysisTask.id
        ).join(
            AnalysisStrategy, AnalysisTask.strategy_id == AnalysisStrategy.id
        ).filter(
            AnalysisResult.ts_code == ts_code
        ).order_by(
            AnalysisTask.task_date.desc(),
            AnalysisResult.id.desc()
        ).limit(limit)

        history = []
        for result, task, strategy in query.all():
            history.append({
                'result_id': result.id,
                'task_id': task.id,
                'task_date': task.task_date.isoformat() if task.task_date else None,
                'strategy_id': strategy.id,
                'strategy_name': strategy.name,
                'strategy_code': strategy.code,
                'stock_name': result.stock_name or (stock_info.name if stock_info else ts_code),
                'ts_code': result.ts_code,
                'score': result.score,
                'signal': result.signal,
                'risk_level': result.risk_level,
                'reasons': AnalysisStrategy.parse_json(result.reason_json, []),
                'metrics': AnalysisStrategy.parse_json(result.metrics_json, {}),
                'created_at': result.created_at.isoformat() if result.created_at else None,
            })

        return jsonify({
            'success': True,
            'data': {
                'ts_code': ts_code,
                'stock_name': stock_info.name if stock_info else None,
                'records': history,
                'total_count': len(history),
            },
            'message': f'获取到 {len(history)} 条股票分析历史'
        })
    except Exception as e:
        logger.error(f'获取股票分析历史失败: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/analysis/stocks/<string:ts_code>/history', methods=['GET'])
def get_analysis_stock_history(ts_code):
    """获取单只股票的分析历史"""
    try:
        strategy_id = request.args.get('strategy_id', type=int)
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        stock_info = StockBasic.query.filter_by(ts_code=ts_code).first()

        query = db.session.query(AnalysisResult, AnalysisTask, AnalysisStrategy).join(
            AnalysisTask, AnalysisResult.task_id == AnalysisTask.id
        ).join(
            AnalysisStrategy, AnalysisTask.strategy_id == AnalysisStrategy.id
        ).filter(
            AnalysisResult.ts_code == ts_code
        )

        if strategy_id:
            query = query.filter(AnalysisTask.strategy_id == strategy_id)

        pagination = query.order_by(
            AnalysisTask.task_date.desc(),
            AnalysisResult.id.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)

        history = []
        for result, task, strategy in pagination.items:
            history.append({
                'result_id': result.id,
                'task_id': task.id,
                'task_date': task.task_date.isoformat() if task.task_date else None,
                'strategy_id': strategy.id,
                'strategy_name': strategy.name,
                'strategy_code': strategy.code,
                'stock_name': result.stock_name or (stock_info.name if stock_info else ts_code),
                'ts_code': result.ts_code,
                'score': result.score,
                'signal': result.signal,
                'risk_level': result.risk_level,
                'reasons': AnalysisStrategy.parse_json(result.reason_json, []),
                'metrics': AnalysisStrategy.parse_json(result.metrics_json, {}),
                'created_at': result.created_at.isoformat() if result.created_at else None,
            })

        OperationLogService.record(
            module='strategy',
            action_type='view',
            action_name='查看股票分析历史',
            user=get_request_user(),
            target_type='stock',
            target_id=ts_code,
            target_name=stock_info.name if stock_info else ts_code,
            message=f'获取到 {len(history)} 条股票分析历史',
        )
        return jsonify({
            'success': True,
            'data': {
                'ts_code': ts_code,
                'stock_name': stock_info.name if stock_info else None,
                'records': history,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                },
            },
            'message': f'获取到 {len(history)} 条股票分析历史'
        })
    except Exception as e:
        logger.error(f'获取股票分析历史失败: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500


def _safe_json_loads(raw_value, default):
    if not raw_value:
        return default
    try:
        return json.loads(raw_value)
    except (TypeError, json.JSONDecodeError):
        return default


def _to_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _build_scored_result(score, reasons):
    if score >= 70:
        signal = 'buy'
        risk_level = 'medium'
    elif score >= 40:
        signal = 'watch'
        risk_level = 'medium'
    else:
        signal = 'avoid'
        risk_level = 'high'

    return {
        'score': round(score, 2),
        'signal': signal,
        'risk_level': risk_level,
        'reasons': reasons or ['当前未出现明显的结构化优势信号'],
    }


def _score_trend_metrics(metrics):
    score = 0.0
    reasons = []

    if metrics['pct_chg'] >= 1:
        score += 25
        reasons.append('最近交易日涨幅较强')
    if metrics['volume_ratio'] >= 1.2:
        score += 25
        reasons.append('量比放大，趋势延续有量能支持')
    if 2 <= metrics['turnover_rate'] <= 8:
        score += 20
        reasons.append('换手率处于趋势策略偏好的活跃区间')
    if metrics['net_mf_amount'] > 0:
        score += 10
        reasons.append('资金面没有明显拖累趋势')
    if metrics['close'] > 0:
        score += 5
        reasons.append('存在有效收盘价数据')

    return _build_scored_result(score, reasons)


def _score_fund_flow_metrics(metrics):
    score = 0.0
    reasons = []

    if metrics['net_mf_amount'] > 0:
        score += 40
        reasons.append('最新资金流为净流入')
    if metrics['volume_ratio'] >= 1:
        score += 20
        reasons.append('量比不弱，资金驱动更容易延续')
    if metrics['pct_chg'] >= 0:
        score += 15
        reasons.append('价格未走弱，资金流信号更可信')
    if 1 <= metrics['turnover_rate'] <= 12:
        score += 15
        reasons.append('换手率匹配资金流策略的活跃要求')
    if metrics['close'] > 0:
        score += 10
        reasons.append('存在有效收盘价数据')

    return _build_scored_result(score, reasons)


def _score_value_metrics(metrics):
    score = 0.0
    reasons = []

    if 0 < metrics['pb'] < 1:
        score += 40
        reasons.append('市净率低于1，估值具备安全边际')
    if 0 < metrics['pe'] < 15:
        score += 30
        reasons.append('市盈率处于价值策略偏好的区间')
    if metrics['pct_chg'] > -3:
        score += 10
        reasons.append('短期价格未出现明显破位')
    if metrics['net_mf_amount'] > 0:
        score += 10
        reasons.append('资金流未明显恶化')
    if metrics['close'] > 0:
        score += 10
        reasons.append('存在有效收盘价数据')

    return _build_scored_result(score, reasons)


def _score_metrics_by_strategy_type(metrics, strategy_type):
    if strategy_type == 'fund_flow':
        return _score_fund_flow_metrics(metrics)
    if strategy_type == 'value':
        return _score_value_metrics(metrics)
    return _score_trend_metrics(metrics)


def _resolve_analysis_scope(scope_type, scope_config):
    if scope_type == 'watchlist':
        items = Watchlist.query.order_by(Watchlist.added_at.desc()).all()
        return [(item.ts_code, item.name) for item in items]

    if scope_type == 'manual':
        stocks = scope_config.get('stocks', [])
        return [
            (item.get('ts_code'), item.get('name'))
            for item in stocks
            if item.get('ts_code')
        ]

    return []


def _build_analysis_result(ts_code, stock_name, strategy_type='trend'):
    resolved_name = stock_name
    if not resolved_name:
        stock_info = StockBasic.query.filter_by(ts_code=ts_code).first()
        resolved_name = stock_info.name if stock_info else ts_code

    latest_daily = StockDailyHistory.query.filter_by(ts_code=ts_code).order_by(
        StockDailyHistory.trade_date.desc()
    ).first()
    latest_basic = StockDailyBasic.query.filter_by(ts_code=ts_code).order_by(
        StockDailyBasic.trade_date.desc()
    ).first()
    latest_moneyflow = StockMoneyflow.query.filter_by(ts_code=ts_code).order_by(
        StockMoneyflow.trade_date.desc()
    ).first()

    metrics = {
        'close': _to_float(latest_daily.close) if latest_daily else 0.0,
        'pct_chg': _to_float(latest_daily.pct_chg) if latest_daily else 0.0,
        'volume_ratio': _to_float(latest_basic.volume_ratio) if latest_basic else 0.0,
        'turnover_rate': _to_float(latest_basic.turnover_rate) if latest_basic else 0.0,
        'pb': _to_float(latest_basic.pb) if latest_basic else 0.0,
        'pe': _to_float(latest_basic.pe) if latest_basic else 0.0,
        'net_mf_amount': _to_float(latest_moneyflow.net_mf_amount) if latest_moneyflow else 0.0,
    }

    scored_result = _score_metrics_by_strategy_type(metrics, strategy_type)

    return {
        'ts_code': ts_code,
        'stock_name': resolved_name,
        'score': scored_result['score'],
        'signal': scored_result['signal'],
        'risk_level': scored_result['risk_level'],
        'reasons': scored_result['reasons'],
        'metrics': metrics,
    }


@api_bp.route('/analysis/strategies', methods=['GET'])
def get_analysis_strategies():
    try:
        strategies = AnalysisStrategy.query.order_by(AnalysisStrategy.created_at.desc()).all()
        return jsonify({
            'success': True,
            'data': [item.to_dict() for item in strategies],
            'message': f'获取到 {len(strategies)} 条分析策略'
        })
    except Exception as e:
        logger.error(f'获取分析策略失败: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/analysis/strategies', methods=['POST'])
def create_analysis_strategy():
    try:
        data = request.get_json() or {}
        for field in ['name', 'code', 'strategy_type']:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'缺少必填字段: {field}'}), 400

        existing = AnalysisStrategy.query.filter_by(code=data['code']).first()
        if existing:
            return jsonify({'success': False, 'message': f'策略编码已存在: {data["code"]}'}), 400

        strategy = AnalysisStrategy(
            name=data['name'],
            code=data['code'],
            strategy_type=data['strategy_type'],
            description=data.get('description'),
            conditions_json=json.dumps(data.get('conditions', {}), ensure_ascii=False),
            prompt_template=data.get('prompt_template'),
            is_active=data.get('is_active', True),
            schedule_type=data.get('schedule_type', 'manual'),
        )
        db.session.add(strategy)
        db.session.commit()

        OperationLogService.record(
            module='strategy',
            action_type='create',
            action_name='创建分析策略',
            user=get_request_user(),
            target_type='strategy',
            target_id=strategy.id,
            target_name=strategy.name,
            message='分析策略创建成功',
        )
        return jsonify({
            'success': True,
            'data': strategy.to_dict(),
            'message': f'分析策略 "{strategy.name}" 创建成功'
        }), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f'创建分析策略失败: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/analysis/strategies/<int:strategy_id>/run', methods=['POST'])
def run_analysis_strategy(strategy_id):
    try:
        strategy = AnalysisStrategy.query.filter_by(id=strategy_id, is_active=True).first()
        if not strategy:
            return jsonify({'success': False, 'message': f'分析策略 {strategy_id} 不存在'}), 404

        payload = request.get_json() or {}
        strategy_conditions = _safe_json_loads(strategy.conditions_json, {})
        scope_type = payload.get('stock_scope_type') or strategy_conditions.get('stock_scope_type', 'watchlist')
        scope_config = payload.get('stock_scope') or strategy_conditions.get('stock_scope', {})
        stocks = _resolve_analysis_scope(scope_type, scope_config)

        if not stocks:
            return jsonify({'success': False, 'message': '当前策略没有可执行的股票范围'}), 400

        task = AnalysisTask(
            strategy_id=strategy.id,
            task_date=datetime.utcnow().date(),
            status='running',
            started_at=datetime.utcnow(),
            stock_scope_type=scope_type,
            stock_scope_json=json.dumps(scope_config, ensure_ascii=False),
        )
        db.session.add(task)
        db.session.flush()

        created_results = []
        for ts_code, stock_name in stocks:
            result_data = _build_analysis_result(ts_code, stock_name, strategy.strategy_type)
            db.session.add(AnalysisResult(
                task_id=task.id,
                ts_code=result_data['ts_code'],
                stock_name=result_data['stock_name'],
                score=result_data['score'],
                signal=result_data['signal'],
                risk_level=result_data['risk_level'],
                reason_json=json.dumps(result_data['reasons'], ensure_ascii=False),
                metrics_json=json.dumps(result_data['metrics'], ensure_ascii=False),
            ))
            created_results.append(result_data)

        summary = {
            'total': len(created_results),
            'buy_count': sum(1 for item in created_results if item['signal'] == 'buy'),
            'watch_count': sum(1 for item in created_results if item['signal'] == 'watch'),
            'avoid_count': sum(1 for item in created_results if item['signal'] == 'avoid'),
        }
        task.status = 'completed'
        task.finished_at = datetime.utcnow()
        task.summary_json = json.dumps(summary, ensure_ascii=False)
        db.session.commit()

        OperationLogService.record(
            module='strategy',
            action_type='analyze',
            action_name='执行分析策略',
            user=get_request_user(),
            target_type='strategy',
            target_id=strategy.id,
            target_name=strategy.name,
            message=f'分析策略执行完成，扫描 {len(created_results)} 只股票',
        )
        return jsonify({
            'success': True,
            'data': {
                'task': task.to_dict(),
                'results': created_results,
            },
            'message': f'分析策略 "{strategy.name}" 执行完成'
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f'执行分析策略失败: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/ai/analysis-history/<string:ts_code>', methods=['GET'])
def get_analysis_history(ts_code):
    """获取股票的AI分析历史"""
    try:
        # 验证股票代码
        stock_info = StockBasic.query.filter_by(ts_code=ts_code).first()
        if not stock_info:
            return jsonify({
                'success': False,
                'message': f'股票代码 {ts_code} 不存在'
            }), 404

        # 获取查询参数
        days = request.args.get('days', 30, type=int)
        limit = request.args.get('limit', 10, type=int)

        # 获取历史记录
        records = AIAnalysisRecord.get_analysis_history(ts_code, days, limit)

        history_data = [record.to_dict() for record in records]

        return jsonify({
            'success': True,
            'data': {
                'ts_code': ts_code,
                'stock_name': stock_info.name,
                'records': history_data,
                'total_count': len(history_data),
                'period_days': days
            },
            'message': f'获取到 {len(history_data)} 条分析历史'
        })

    except Exception as e:
        logger.error(f"获取分析历史失败: {e}")
        return jsonify({
            'success': False,
            'message': f'获取分析历史失败: {str(e)}'
        }), 500


@api_bp.route('/ai/analysis-summary/<string:ts_code>', methods=['GET'])
def get_analysis_summary(ts_code):
    """获取股票的AI分析摘要"""
    try:
        # 验证股票代码
        stock_info = StockBasic.query.filter_by(ts_code=ts_code).first()
        if not stock_info:
            return jsonify({
                'success': False,
                'message': f'股票代码 {ts_code} 不存在'
            }), 404

        # 获取查询参数
        days = request.args.get('days', 30, type=int)

        # 获取分析摘要
        summary = AIAnalysisRecord.get_stock_analysis_summary(ts_code, days)

        if not summary:
            return jsonify({
                'success': True,
                'data': {
                    'ts_code': ts_code,
                    'stock_name': stock_info.name,
                    'message': '暂无分析记录'
                },
                'message': '该股票暂无分析记录'
            })

        return jsonify({
            'success': True,
            'data': summary,
            'message': '获取分析摘要成功'
        })

    except Exception as e:
        logger.error(f"获取分析摘要失败: {e}")
        return jsonify({
            'success': False,
            'message': f'获取分析摘要失败: {str(e)}'
        }), 500


@api_bp.route('/ai/analysis-stats', methods=['GET'])
def get_analysis_stats():
    """获取AI分析统计信息"""
    try:
        # 获取查询参数
        days = request.args.get('days', 30, type=int)

        # 获取统计信息
        stats = AIAnalysisRecord.get_analysis_stats(days)

        return jsonify({
            'success': True,
            'data': stats,
            'message': f'获取最近{days}天AI分析统计成功'
        })

    except Exception as e:
        logger.error(f"获取分析统计失败: {e}")
        return jsonify({
            'success': False,
            'message': f'获取分析统计失败: {str(e)}'
        }), 500


@api_bp.route('/ai/latest-analysis/<string:ts_code>', methods=['GET'])
def get_latest_analysis(ts_code):
    """获取股票的最新AI分析"""
    try:
        # 验证股票代码
        stock_info = StockBasic.query.filter_by(ts_code=ts_code).first()
        if not stock_info:
            return jsonify({
                'success': False,
                'message': f'股票代码 {ts_code} 不存在'
            }), 404

        # 获取最新分析记录
        latest_record = AIAnalysisRecord.get_latest_analysis(ts_code)

        if not latest_record:
            return jsonify({
                'success': True,
                'data': {
                    'ts_code': ts_code,
                    'stock_name': stock_info.name,
                    'has_analysis': False,
                    'message': '暂无AI分析记录'
                },
                'message': '该股票暂无AI分析记录'
            })

        return jsonify({
            'success': True,
            'data': {
                'ts_code': ts_code,
                'stock_name': stock_info.name,
                'has_analysis': True,
                'analysis': latest_record.to_dict()
            },
            'message': '获取最新AI分析成功'
        })

    except Exception as e:
        logger.error(f"获取最新分析失败: {e}")
        return jsonify({
            'success': False,
            'message': f'获取最新分析失败: {str(e)}'
        }), 500


@api_bp.route('/ai/config', methods=['GET'])
def get_ai_config():
    """获取AI配置信息"""
    try:
        from app.models.ai_config import AIConfig
        
        # 获取当前激活的配置
        active_config = AIConfig.get_active_config()
        
        if active_config:
            return jsonify({
                'success': True,
                'data': {
                    'provider': active_config.provider_type,
                    'is_configured': True,
                    'model': active_config.config_data.get('model'),
                    'provider_name': active_config.provider_name,
                    'supported_providers': ['tongyi', 'openai', 'zhipu', 'ollama', 'custom']
                },
                'message': '获取AI配置信息成功'
            })
        else:
            # 尝试获取系统配置（兼容旧方式）
            from flask import current_app
            ai_config = current_app.config.get('AI_CONFIG', {})
            provider = ai_config.get('provider', 'tongyi')
            provider_config = ai_config.get(provider, {})
            is_configured = bool(provider_config.get('api_key'))
            
            return jsonify({
                'success': True,
                'data': {
                    'provider': provider,
                    'is_configured': is_configured,
                    'model': provider_config.get('model'),
                    'supported_providers': ['tongyi', 'openai', 'zhipu', 'ollama', 'custom']
                },
                'message': '获取AI配置信息成功'
            })

    except Exception as e:
        logger.error(f"获取AI配置失败: {e}")
        return jsonify({
            'success': False,
            'message': f'获取AI配置失败: {str(e)}'
        }), 500
