#!/usr/bin/env python3
"""分析系统中数据的来源"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models.stock_minute_data import StockMinuteData
from loguru import logger
from sqlalchemy import text

def analyze_data_source():
    """分析数据来源"""
    app = create_app()
    
    with app.app_context():
        try:
            # 1. 检查数据库表结构
            logger.info("=== 数据库表结构分析 ===")
            
            # 获取所有表名 (MySQL)
            result = db.session.execute(text("SHOW TABLES;"))
            tables = [row[0] for row in result.fetchall()]
            logger.info(f"数据库中的表: {tables}")
            
            # 2. 分析stock_minute_data表的数据
            logger.info("\n=== stock_minute_data表数据分析 ===")
            
            # 检查数据总量
            total_count = StockMinuteData.query.count()
            logger.info(f"总记录数: {total_count}")
            
            # 检查股票数量
            distinct_stocks = db.session.query(StockMinuteData.ts_code).distinct().count()
            logger.info(f"不同股票数量: {distinct_stocks}")
            
            # 检查时间范围
            earliest = StockMinuteData.query.order_by(StockMinuteData.datetime.asc()).first()
            latest = StockMinuteData.query.order_by(StockMinuteData.datetime.desc()).first()
            
            if earliest and latest:
                logger.info(f"时间范围: {earliest.datetime} 到 {latest.datetime}")
                
                # 计算天数
                time_diff = latest.datetime - earliest.datetime
                logger.info(f"数据跨度: {time_diff.days} 天")
            
            # 3. 分析数据特征
            logger.info("\n=== 数据特征分析 ===")
            
            # 检查period_type分布
            period_types = db.session.query(
                StockMinuteData.period_type, 
                db.func.count(StockMinuteData.id)
            ).group_by(StockMinuteData.period_type).all()
            
            logger.info("周期类型分布:")
            for period_type, count in period_types:
                logger.info(f"  {period_type}: {count} 条记录")
            
            # 检查每只股票的数据量
            stock_counts = db.session.query(
                StockMinuteData.ts_code,
                db.func.count(StockMinuteData.id),
                db.func.min(StockMinuteData.datetime),
                db.func.max(StockMinuteData.datetime)
            ).group_by(StockMinuteData.ts_code).all()
            
            logger.info("\n各股票数据统计:")
            for ts_code, count, min_date, max_date in stock_counts:
                logger.info(f"  {ts_code}: {count} 条记录, {min_date} 到 {max_date}")
            
            # 4. 分析数据质量
            logger.info("\n=== 数据质量分析 ===")
            
            # 检查空值
            null_counts = {}
            columns = ['open', 'high', 'low', 'close', 'volume', 'amount']
            
            for col in columns:
                null_count = db.session.query(StockMinuteData).filter(
                    getattr(StockMinuteData, col).is_(None)
                ).count()
                null_counts[col] = null_count
            
            logger.info("空值统计:")
            for col, count in null_counts.items():
                percentage = (count / total_count * 100) if total_count > 0 else 0
                logger.info(f"  {col}: {count} 条 ({percentage:.2f}%)")
            
            # 5. 推断数据来源
            logger.info("\n=== 数据来源推断 ===")
            
            # 检查数据的时间间隔模式
            sample_data = StockMinuteData.query.filter_by(ts_code='000001.SZ').order_by(
                StockMinuteData.datetime.asc()
            ).limit(10).all()
            
            if len(sample_data) > 1:
                logger.info("时间间隔分析 (前10条记录):")
                for i in range(1, len(sample_data)):
                    time_diff = sample_data[i].datetime - sample_data[i-1].datetime
                    logger.info(f"  {sample_data[i-1].datetime} -> {sample_data[i].datetime}: {time_diff}")
            
            # 检查数据格式特征
            sample = StockMinuteData.query.first()
            if sample:
                logger.info(f"\n样本数据格式:")
                logger.info(f"  股票代码: {sample.ts_code}")
                logger.info(f"  时间: {sample.datetime}")
                logger.info(f"  周期: {sample.period_type}")
                logger.info(f"  开盘价: {sample.open}")
                logger.info(f"  收盘价: {sample.close}")
                logger.info(f"  成交量: {sample.volume}")
                logger.info(f"  成交额: {sample.amount}")
                
                # 根据数据特征推断来源
                logger.info(f"\n数据来源推断:")
                if sample.period_type == '5min':
                    logger.info("  ✓ 周期为5分钟，符合Baostock数据特征")
                if sample.ts_code.endswith('.SZ') or sample.ts_code.endswith('.SH'):
                    logger.info("  ✓ 股票代码格式为Tushare格式 (XXXXXX.SZ/SH)")
                if sample.volume and sample.amount:
                    logger.info("  ✓ 包含成交量和成交额数据")
                
                # 检查是否有Baostock特有的字段或格式
                logger.info(f"\n可能的数据源:")
                logger.info(f"  1. Baostock - 免费数据源，支持5分钟K线")
                logger.info(f"  2. Tushare - 付费数据源，支持多种周期")
                logger.info(f"  3. 其他数据源 - 如akshare、yfinance等")
                
        except Exception as e:
            logger.error(f"分析数据来源失败: {e}")
            import traceback
            logger.error(f"详细错误: {traceback.format_exc()}")

if __name__ == '__main__':
    analyze_data_source()