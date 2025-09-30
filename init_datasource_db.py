#!/usr/bin/env python3
"""
数据库初始化脚本
创建所有必要的数据表并初始化默认数据
"""

from app import create_app, db
from app.models.data_source_config import DataSourceConfig
from app.models.stock_basic import StockBasic
from app.models.stock_daily_history import StockDailyHistory
from app.models.watchlist import Watchlist
from loguru import logger

def init_database():
    """初始化数据库，创建所有表"""
    app = create_app()
    
    with app.app_context():
        try:
            print("=" * 60)
            print("🚀 开始初始化数据库...")
            print("=" * 60)
            
            # 1. 创建所有表
            print("\n📊 创建数据表...")
            db.create_all()
            
            # 检查创建的表
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            print(f"✅ 成功创建以下数据表:")
            for table in tables:
                print(f"   - {table}")
            
            # 2. 初始化数据源配置
            print("\n🔧 初始化数据源配置...")
            existing_config = DataSourceConfig.query.first()
            
            if not existing_config:
                # 创建默认的Tushare配置
                default_config = DataSourceConfig(
                    source_type='tushare',
                    source_name='Tushare Pro',
                    config_data={'token': ''},
                    is_active=False,
                    is_default=False,
                    status='未测试'
                )
                db.session.add(default_config)
                
                # 创建Yahoo Finance配置
                yahoo_config = DataSourceConfig(
                    source_type='yahoo',
                    source_name='Yahoo Finance',
                    config_data={},
                    is_active=False,
                    is_default=False,
                    status='未测试'
                )
                db.session.add(yahoo_config)
                
                db.session.commit()
                print("✅ 默认数据源配置创建成功")
            else:
                print("ℹ️  数据源配置已存在，跳过初始化")
            
            # 3. 检查股票数据表状态
            print("\n📈 检查股票数据状态...")
            stock_count = StockBasic.query.count()
            daily_count = StockDailyHistory.query.count()
            
            print(f"   - stock_basic: {stock_count} 条记录")
            print(f"   - stock_daily_history: {daily_count} 条记录")
            
            if stock_count == 0:
                print("\n💡 提示: 股票列表为空，请在前端或使用以下命令同步数据:")
                print("   POST /api/stocks/sync")
            
            print("\n" + "=" * 60)
            print("✅ 数据库初始化完成！")
            print("=" * 60)
            
            # 4. 显示下一步操作
            print("\n📋 下一步操作:")
            print("1. 启动后端服务: python run.py")
            print("2. 配置Tushare Token（在前端数据源页面）")
            print("3. 同步股票列表: POST /api/stocks/sync")
            print("4. 开始使用系统")
            print()
            
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            db.session.rollback()
            print(f"\n❌ 初始化失败: {e}")
            raise

if __name__ == '__main__':
    init_database()
