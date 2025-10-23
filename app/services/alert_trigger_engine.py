"""
预警规则触发引擎
基于日线数据实时检测预警规则并生成预警记录
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy import and_, or_, desc

from app.extensions import db
from app.models.alert_rule import AlertRule
from app.models.risk_alert import RiskAlert
from app.models.stock_basic import StockBasic
from app.models.stock_daily_history import StockDailyHistory
from app.models.stock_daily_basic import StockDailyBasic
from app.models.stock_moneyflow import StockMoneyflow

logger = logging.getLogger(__name__)


class AlertTriggerEngine:
    """预警规则触发引擎"""
    
    def __init__(self):
        """初始化触发引擎"""
        self.rule_processors = {
            'price_threshold': self._process_price_threshold,
            'price_change_pct': self._process_price_change_pct,
            'volume_ratio': self._process_volume_ratio,
            'turnover_rate': self._process_turnover_rate,
            'market_value': self._process_market_value,
            'technical_indicator': self._process_technical_indicator,
            'money_flow': self._process_money_flow
        }
    
    def run_alert_check(self, ts_codes: List[str] = None, 
                       rule_types: List[str] = None) -> Dict[str, Any]:
        """
        运行预警检查
        
        Args:
            ts_codes: 指定股票代码列表，为空则检查所有启用规则的股票
            rule_types: 指定规则类型列表，为空则检查所有类型
        
        Returns:
            检查结果统计
        """
        try:
            logger.info("开始运行预警检查...")
            
            # 获取启用的预警规则
            enabled_rules = self._get_enabled_rules(ts_codes, rule_types)
            
            if not enabled_rules:
                logger.info("没有找到启用的预警规则")
                return {
                    'success': True,
                    'message': '没有启用的预警规则',
                    'stats': {
                        'total_rules': 0,
                        'checked_rules': 0,
                        'triggered_alerts': 0,
                        'new_alerts': 0
                    }
                }
            
            logger.info(f"找到 {len(enabled_rules)} 个启用的预警规则")
            
            # 按股票代码分组规则
            rules_by_stock = self._group_rules_by_stock(enabled_rules)
            
            # 统计信息
            stats = {
                'total_rules': len(enabled_rules),
                'checked_rules': 0,
                'triggered_alerts': 0,
                'new_alerts': 0,
                'failed_checks': 0
            }
            
            # 逐个股票检查规则
            for ts_code, rules in rules_by_stock.items():
                try:
                    stock_stats = self._check_stock_rules(ts_code, rules)
                    
                    stats['checked_rules'] += stock_stats['checked_rules']
                    stats['triggered_alerts'] += stock_stats['triggered_alerts']
                    stats['new_alerts'] += stock_stats['new_alerts']
                    
                except Exception as e:
                    logger.error(f"检查股票 {ts_code} 规则失败: {str(e)}")
                    stats['failed_checks'] += len(rules)
                    continue
            
            logger.info(f"预警检查完成: {stats}")
            
            return {
                'success': True,
                'message': f'预警检查完成，触发 {stats["new_alerts"]} 个新预警',
                'stats': stats
            }
            
        except Exception as e:
            logger.error(f"运行预警检查失败: {str(e)}")
            return {
                'success': False,
                'message': f'预警检查失败: {str(e)}',
                'stats': {}
            }
    
    def _get_enabled_rules(self, ts_codes: List[str] = None, 
                          rule_types: List[str] = None) -> List[AlertRule]:
        """获取启用的预警规则"""
        query = AlertRule.query.filter_by(is_enabled=True, is_active=True)
        
        if ts_codes:
            query = query.filter(AlertRule.ts_code.in_(ts_codes))
        
        if rule_types:
            query = query.filter(AlertRule.rule_type.in_(rule_types))
        
        return query.order_by(AlertRule.created_at.desc()).all()
    
    def _group_rules_by_stock(self, rules: List[AlertRule]) -> Dict[str, List[AlertRule]]:
        """按股票代码分组规则"""
        rules_by_stock = {}
        
        for rule in rules:
            ts_code = rule.ts_code
            if ts_code not in rules_by_stock:
                rules_by_stock[ts_code] = []
            rules_by_stock[ts_code].append(rule)
        
        return rules_by_stock
    
    def _check_stock_rules(self, ts_code: str, rules: List[AlertRule]) -> Dict[str, int]:
        """检查单个股票的所有规则"""
        logger.debug(f"检查股票 {ts_code} 的 {len(rules)} 个规则")
        
        stats = {
            'checked_rules': 0,
            'triggered_alerts': 0,
            'new_alerts': 0
        }
        
        # 获取股票最新数据
        stock_data = self._get_latest_stock_data(ts_code)
        
        if not stock_data:
            logger.warning(f"股票 {ts_code} 没有最新数据，跳过检查")
            return stats
        
        # 逐个检查规则
        for rule in rules:
            try:
                stats['checked_rules'] += 1
                
                # 根据规则类型处理
                processor = self.rule_processors.get(rule.rule_type)
                if not processor:
                    logger.warning(f"不支持的规则类型: {rule.rule_type}")
                    continue
                
                # 处理规则
                result = processor(rule, stock_data)
                
                if result['triggered']:
                    stats['triggered_alerts'] += 1
                    
                    # 检查是否需要创建新预警（避免重复预警）
                    if self._should_create_alert(rule, result['current_value']):
                        alert = self._create_alert_record(rule, result, stock_data)
                        if alert:
                            stats['new_alerts'] += 1
                            logger.info(f"触发预警: {rule.rule_name} - {alert.alert_message}")
                
            except Exception as e:
                logger.error(f"处理规则 {rule.id} 失败: {str(e)}")
                continue
        
        return stats
    
    def _get_latest_stock_data(self, ts_code: str) -> Optional[Dict[str, Any]]:
        """获取股票最新数据"""
        try:
            # 获取股票基本信息
            stock_basic = StockBasic.query.filter_by(ts_code=ts_code).first()
            if not stock_basic:
                return None
            
            # 获取最新日线数据
            latest_daily = StockDailyHistory.query.filter_by(
                ts_code=ts_code
            ).order_by(desc(StockDailyHistory.trade_date)).first()
            
            # 获取最新每日指标
            latest_basic = StockDailyBasic.query.filter_by(
                ts_code=ts_code
            ).order_by(desc(StockDailyBasic.trade_date)).first()
            
            # 获取最新资金流向
            latest_moneyflow = StockMoneyflow.query.filter_by(
                ts_code=ts_code
            ).order_by(desc(StockMoneyflow.trade_date)).first()
            
            # 组装数据
            stock_data = {
                'ts_code': ts_code,
                'name': stock_basic.name,
                'industry': stock_basic.industry,
                'daily_data': latest_daily,
                'basic_data': latest_basic,
                'moneyflow_data': latest_moneyflow
            }
            
            return stock_data
            
        except Exception as e:
            logger.error(f"获取股票 {ts_code} 数据失败: {str(e)}")
            return None
    
    def _process_price_threshold(self, rule: AlertRule, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理价格阈值规则"""
        daily_data = stock_data.get('daily_data')
        if not daily_data:
            return {'triggered': False, 'current_value': None, 'message': '无日线数据'}
        
        current_price = daily_data.close
        triggered = rule.check_condition(current_price)
        
        return {
            'triggered': triggered,
            'current_value': current_price,
            'message': f'当前价格: {current_price}, 阈值: {rule.threshold_value}'
        }
    
    def _process_price_change_pct(self, rule: AlertRule, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理涨跌幅规则"""
        daily_data = stock_data.get('daily_data')
        if not daily_data:
            return {'triggered': False, 'current_value': None, 'message': '无日线数据'}
        
        change_pct = daily_data.pct_chg or 0.0
        triggered = rule.check_condition(change_pct)
        
        return {
            'triggered': triggered,
            'current_value': change_pct,
            'message': f'当前涨跌幅: {change_pct}%, 阈值: {rule.threshold_value}%'
        }
    
    def _process_volume_ratio(self, rule: AlertRule, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理成交量比率规则"""
        basic_data = stock_data.get('basic_data')
        if not basic_data:
            return {'triggered': False, 'current_value': None, 'message': '无每日指标数据'}
        
        volume_ratio = basic_data.volume_ratio or 0.0
        triggered = rule.check_condition(volume_ratio)
        
        return {
            'triggered': triggered,
            'current_value': volume_ratio,
            'message': f'当前量比: {volume_ratio}, 阈值: {rule.threshold_value}'
        }
    
    def _process_turnover_rate(self, rule: AlertRule, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理换手率规则"""
        basic_data = stock_data.get('basic_data')
        if not basic_data:
            return {'triggered': False, 'current_value': None, 'message': '无每日指标数据'}
        
        turnover_rate = basic_data.turnover_rate or 0.0
        triggered = rule.check_condition(turnover_rate)
        
        return {
            'triggered': triggered,
            'current_value': turnover_rate,
            'message': f'当前换手率: {turnover_rate}%, 阈值: {rule.threshold_value}%'
        }
    
    def _process_market_value(self, rule: AlertRule, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理市值变化规则"""
        basic_data = stock_data.get('basic_data')
        if not basic_data:
            return {'triggered': False, 'current_value': None, 'message': '无每日指标数据'}
        
        # 使用总市值（万元）
        market_value = basic_data.total_mv or 0.0
        triggered = rule.check_condition(market_value)
        
        return {
            'triggered': triggered,
            'current_value': market_value,
            'message': f'当前总市值: {market_value}万元, 阈值: {rule.threshold_value}万元'
        }
    
    def _process_technical_indicator(self, rule: AlertRule, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理技术指标规则"""
        # 这里可以扩展更多技术指标
        # 目前使用 PE 作为示例
        basic_data = stock_data.get('basic_data')
        if not basic_data:
            return {'triggered': False, 'current_value': None, 'message': '无每日指标数据'}
        
        pe_ratio = basic_data.pe or 0.0
        triggered = rule.check_condition(pe_ratio)
        
        return {
            'triggered': triggered,
            'current_value': pe_ratio,
            'message': f'当前PE: {pe_ratio}, 阈值: {rule.threshold_value}'
        }
    
    def _process_money_flow(self, rule: AlertRule, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理资金流向规则"""
        moneyflow_data = stock_data.get('moneyflow_data')
        if not moneyflow_data:
            return {'triggered': False, 'current_value': None, 'message': '无资金流向数据'}
        
        # 使用净流入金额（万元）
        net_mf = moneyflow_data.net_mf or 0.0
        triggered = rule.check_condition(net_mf)
        
        return {
            'triggered': triggered,
            'current_value': net_mf,
            'message': f'当前净流入: {net_mf}万元, 阈值: {rule.threshold_value}万元'
        }
    
    def _should_create_alert(self, rule: AlertRule, current_value: float) -> bool:
        """判断是否应该创建新预警（避免重复预警）"""
        try:
            # 检查最近1小时内是否已有相同规则的预警
            recent_time = datetime.utcnow() - timedelta(hours=1)
            
            existing_alert = RiskAlert.query.filter(
                and_(
                    RiskAlert.ts_code == rule.ts_code,
                    RiskAlert.alert_type == rule.rule_type,
                    RiskAlert.is_active == True,
                    RiskAlert.created_at >= recent_time
                )
            ).first()
            
            return existing_alert is None
            
        except Exception as e:
            logger.error(f"检查重复预警失败: {str(e)}")
            return True  # 出错时默认创建预警
    
    def _create_alert_record(self, rule: AlertRule, result: Dict[str, Any], 
                           stock_data: Dict[str, Any]) -> Optional[RiskAlert]:
        """创建预警记录"""
        try:
            # 生成预警消息
            alert_message = rule.generate_alert_message(
                result['current_value'], 
                stock_data.get('name')
            )
            
            # 获取当前价格
            current_price = None
            daily_data = stock_data.get('daily_data')
            if daily_data:
                current_price = daily_data.close
            
            # 创建预警记录
            alert = RiskAlert.create_alert(
                ts_code=rule.ts_code,
                alert_type=rule.rule_type,
                alert_level=rule.alert_level,
                alert_message=alert_message,
                risk_value=result['current_value'],
                threshold_value=rule.threshold_value,
                current_price=current_price
            )
            
            # 更新规则触发统计
            rule.record_trigger()
            
            return alert
            
        except Exception as e:
            logger.error(f"创建预警记录失败: {str(e)}")
            return None
    
    def get_trigger_stats(self, days: int = 7) -> Dict[str, Any]:
        """获取触发统计信息"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # 统计最近N天的预警
            recent_alerts = RiskAlert.query.filter(
                RiskAlert.created_at >= start_date
            ).all()
            
            # 按类型统计
            type_stats = {}
            level_stats = {}
            
            for alert in recent_alerts:
                # 按类型统计
                alert_type = alert.alert_type
                if alert_type not in type_stats:
                    type_stats[alert_type] = 0
                type_stats[alert_type] += 1
                
                # 按级别统计
                alert_level = alert.alert_level
                if alert_level not in level_stats:
                    level_stats[alert_level] = 0
                level_stats[alert_level] += 1
            
            return {
                'success': True,
                'data': {
                    'total_alerts': len(recent_alerts),
                    'active_alerts': len([a for a in recent_alerts if a.is_active]),
                    'resolved_alerts': len([a for a in recent_alerts if a.is_resolved]),
                    'by_type': type_stats,
                    'by_level': level_stats,
                    'period_days': days
                }
            }
            
        except Exception as e:
            logger.error(f"获取触发统计失败: {str(e)}")
            return {
                'success': False,
                'message': str(e)
            }


# 全局实例
alert_trigger_engine = AlertTriggerEngine()


def run_scheduled_alert_check():
    """定时预警检查任务"""
    logger.info("开始定时预警检查...")
    result = alert_trigger_engine.run_alert_check()
    logger.info(f"定时预警检查完成: {result}")
    return result


def check_stock_alerts(ts_codes: List[str]):
    """检查指定股票的预警"""
    logger.info(f"检查指定股票预警: {ts_codes}")
    result = alert_trigger_engine.run_alert_check(ts_codes=ts_codes)
    logger.info(f"股票预警检查完成: {result}")
    return result
