#!/usr/bin/env python3
"""检查历史数据"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models import StockDailyHistory, StockMinuteData
from loguru import logger

def check_history_data():
    """检查历史数据情况"""
    app = create_app()
    
    with app.app_context():
        try:
            # 检查stock_daily_history表
            daily_count = StockDailyHistory.query.count()
            logger.info(f"stock_daily_history表中有 {daily_count} 条记录")
            
            # 检查000001.SZ的历史数据
            stock_daily = StockDailyHistory.query.filter_by(ts_code='000001.SZ').count()
            logger.info(f"000001.SZ在stock_daily_history表中有 {stock_daily} 条记录")
            
            # 检查stock_minute_data表中000001.SZ的数据
            minute_count = StockMinuteData.query.filter_by(ts_code='000001.SZ').count()
            logger.info(f"000001.SZ在stock_minute_data表中有 {minute_count} 条记录")
            
            if minute_count > 0:
                # 显示分钟数据的日期范围
                earliest = StockMinuteData.query.filter_by(ts_code='000001.SZ').order_by(
                    StockMinuteData.datetime.asc()
                ).first()
                latest = StockMinuteData.query.filter_by(ts_code='000001.SZ').order_by(
                    StockMinuteData.datetime.desc()
                ).first()
                
                logger.info(f"分钟数据时间范围: {earliest.datetime} 到 {latest.datetime}")
                
                # 显示几条样本数据
                samples = StockMinuteData.query.filter_by(ts_code='000001.SZ').order_by(
                    StockMinuteData.datetime.desc()
                ).limit(5).all()
                
                logger.info("最新5条分钟数据:")
                for sample in samples:
                    logger.info(f"  {sample.datetime} - 开:{sample.open} 高:{sample.high} 低:{sample.low} 收:{sample.close}")
            
        except Exception as e:
            logger.error(f"检查历史数据失败: {e}")
            import traceback
            logger.error(f"详细错误: {traceback.format_exc()}")

if __name__ == '__main__':
    check_history_data()