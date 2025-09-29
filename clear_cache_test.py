#!/usr/bin/env python3
"""清除缓存并测试API"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.services.stock_service import StockService
from app.utils.cache import cache
from loguru import logger

def clear_cache_and_test():
    """清除缓存并测试"""
    app = create_app()
    
    with app.app_context():
        try:
            # 清除缓存
            logger.info("清除缓存...")
            cache.clear()
            
            # 测试获取股票列表
            logger.info("测试获取股票列表...")
            result = StockService.get_stock_list(page=1, page_size=20)
            logger.info(f"结果: {result}")
            
            # 测试不同的参数
            logger.info("\n测试不同参数...")
            result2 = StockService.get_stock_list(page=1, page_size=10)
            logger.info(f"结果2: {result2}")
            
        except Exception as e:
            logger.error(f"测试失败: {e}")
            import traceback
            logger.error(f"详细错误: {traceback.format_exc()}")

if __name__ == '__main__':
    clear_cache_and_test()