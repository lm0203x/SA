#!/usr/bin/env python3
"""检查数据库中的股票数据"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models import StockBasic, StockMinuteData
from loguru import logger

def check_database():
    """检查数据库中的数据情况"""
    app = create_app()
    
    with app.app_context():
        try:
            # 检查stock_basic表
            basic_count = StockBasic.query.count()
            logger.info(f"stock_basic表中有 {basic_count} 条记录")
            
            if basic_count > 0:
                # 显示前5条记录
                sample_basic = StockBasic.query.limit(5).all()
                logger.info("stock_basic表样本数据:")
                for stock in sample_basic:
                    logger.info(f"  {stock.ts_code} - {stock.name} - {stock.industry}")
            
            # 检查stock_minute_data表
            minute_count = StockMinuteData.query.count()
            logger.info(f"stock_minute_data表中有 {minute_count} 条记录")
            
            if minute_count > 0:
                # 显示不同股票代码的数量
                distinct_codes = db.session.query(StockMinuteData.ts_code).distinct().count()
                logger.info(f"stock_minute_data表中有 {distinct_codes} 只不同的股票")
                
                # 显示前5只股票
                sample_codes = db.session.query(StockMinuteData.ts_code).distinct().limit(5).all()
                logger.info("stock_minute_data表样本股票代码:")
                for code_tuple in sample_codes:
                    code = code_tuple[0]
                    latest_data = StockMinuteData.query.filter_by(ts_code=code).order_by(
                        StockMinuteData.datetime.desc()
                    ).first()
                    logger.info(f"  {code} - 最新时间: {latest_data.datetime} - 价格: {latest_data.close}")
            
            # 检查其他相关表
            from app.models import StockDailyHistory, StockBusiness
            
            daily_count = StockDailyHistory.query.count()
            logger.info(f"stock_daily_history表中有 {daily_count} 条记录")
            
            business_count = StockBusiness.query.count()
            logger.info(f"stock_business表中有 {business_count} 条记录")
            
        except Exception as e:
            logger.error(f"检查数据库失败: {e}")
            import traceback
            logger.error(f"详细错误: {traceback.format_exc()}")

if __name__ == '__main__':
    check_database()