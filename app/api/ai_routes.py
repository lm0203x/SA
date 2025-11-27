"""
AI股票分析API路由
提供AI股票推荐和分析功能
"""

from flask import request, jsonify
from loguru import logger
from datetime import datetime, timedelta
from app.api import api_bp
from app.extensions import db
from app.services.ai_stock_analyzer import get_ai_analyzer
from app.models.ai_analysis import AIAnalysisRecord
from app.models.stock_basic import StockBasic
from app.models.stock_daily_history import StockDailyHistory
from app.models.stock_daily_basic import StockDailyBasic


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

        # 准备分析数据
        stock_data = {
            'current_price': float(latest_daily.close) if latest_daily else 0.0,
            'change_pct': float(latest_daily.pct_chg) if latest_daily else 0.0,
            'volume_ratio': float(latest_basic.volume_ratio) if latest_basic else 0.0,
            'pe_ratio': float(latest_basic.pe) if latest_basic else 0.0,
            'pb_ratio': float(latest_basic.pb) if latest_basic else 0.0,
            'turnover_rate': float(latest_basic.turnover_rate) if latest_basic else 0.0,
            'total_mv': float(latest_basic.total_mv) if latest_basic else 0.0
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