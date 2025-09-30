#!/usr/bin/env python3
"""
股票数据同步脚本
用于初始化和更新股票数据
"""

import sys
from app import create_app
from app.services.stock_data_service import StockDataService
from loguru import logger

def sync_stocks(force_update=False):
    """同步股票列表"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("📊 开始同步股票列表...")
        print("=" * 60)
        
        result = StockDataService.sync_stock_list(force_update=force_update)
        
        if result['success']:
            print(f"\n✅ 同步成功!")
            if result.get('added'):
                print(f"   新增: {result['added']} 只股票")
            if result.get('updated'):
                print(f"   更新: {result['updated']} 只股票")
            print(f"   总计: {result.get('total', 0)} 只股票")
            print(f"   来源: {result.get('source', 'unknown')}")
        else:
            print(f"\n❌ 同步失败: {result.get('message')}")
            
            if "没有激活的数据源" in result.get('message', ''):
                print("\n💡 提示: 请先在前端配置并激活Tushare数据源")
                print("   1. 访问 http://localhost:5173")
                print("   2. 进入'数据源'标签页")
                print("   3. 配置Tushare Token")
                print("   4. 点击'测试连接'")
                print("   5. 点击'激活'")
                print("\n   然后重新运行此脚本")
        
        print("\n" + "=" * 60)

if __name__ == '__main__':
    # 检查命令行参数
    force = '--force' in sys.argv or '-f' in sys.argv
    
    if force:
        print("⚠️  强制更新模式")
    
    sync_stocks(force_update=force)
