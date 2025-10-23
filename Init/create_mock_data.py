#!/usr/bin/env python3
"""
创建模拟数据脚本
用于演示K线图效果
"""

import random
from datetime import datetime, timedelta
from app import create_app, db
from app.models.watchlist import Watchlist
from app.models.stock_daily_history import StockDailyHistory

def generate_stock_data(ts_code, base_price, days=60):
    """生成模拟的K线数据"""
    data = []
    current_price = base_price
    pre_close = base_price
    
    # 从60天前开始
    start_date = datetime.now() - timedelta(days=days)
    
    for i in range(days):
        date = start_date + timedelta(days=i)
        
        # 跳过周末
        if date.weekday() >= 5:
            continue
        
        # 模拟价格波动（-2%到+2%）
        change_pct = random.uniform(-2, 2)
        current_price = current_price * (1 + change_pct / 100)
        
        # 生成OHLC数据
        open_price = current_price * random.uniform(0.98, 1.02)
        close_price = current_price
        high_price = max(open_price, close_price) * random.uniform(1.0, 1.03)
        low_price = min(open_price, close_price) * random.uniform(0.97, 1.0)
        
        # 成交量（随机）
        volume = random.randint(50000, 200000) * 100  # 手
        amount = volume * close_price / 100  # 千元
        
        # 涨跌幅
        change = close_price - pre_close
        pct_chg = (change / pre_close) * 100 if pre_close > 0 else 0
        
        data.append({
            'ts_code': ts_code,
            'trade_date': date.date(),  # Date对象
            'open': round(open_price, 2),
            'high': round(high_price, 2),
            'low': round(low_price, 2),
            'close': round(close_price, 2),
            'pre_close': round(pre_close, 2),
            'change_c': round(change, 2),  # 字段名是change_c
            'pct_chg': round(pct_chg, 2),
            'vol': volume,
            'amount': round(amount, 2)
        })
        
        # 更新pre_close为当前的close
        pre_close = close_price
    
    return data

def create_mock_data():
    """创建模拟数据"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("🎨 开始创建模拟数据...")
        print("=" * 60)
        
        # 定义模拟股票
        stocks = [
            {'ts_code': '000001.SZ', 'name': '平安银行', 'base_price': 12.50, 'note': '银行板块龙头'},
            {'ts_code': '600036.SH', 'name': '招商银行', 'base_price': 38.50, 'note': '银行股优质标的'},
            {'ts_code': '000858.SZ', 'name': '五粮液', 'base_price': 168.00, 'note': '白酒板块'},
            {'ts_code': '600519.SH', 'name': '贵州茅台', 'base_price': 1680.00, 'note': '白酒龙头'},
            {'ts_code': '000333.SZ', 'name': '美的集团', 'base_price': 58.50, 'note': '家电龙头'},
        ]
        
        # 1. 创建自选股
        print("\n📌 添加自选股...")
        for stock in stocks:
            existing = Watchlist.query.filter_by(ts_code=stock['ts_code']).first()
            if not existing:
                watchlist_item = Watchlist(
                    ts_code=stock['ts_code'],
                    name=stock['name'],
                    note=stock['note']
                )
                db.session.add(watchlist_item)
                print(f"   ✅ {stock['name']} ({stock['ts_code']})")
            else:
                print(f"   ⏭️  {stock['name']} 已存在")
        
        db.session.commit()
        
        # 2. 生成K线数据
        print("\n📊 生成K线数据...")
        for stock in stocks:
            print(f"\n   处理 {stock['name']} ({stock['ts_code']})...")
            
            # 检查是否已有数据
            existing_count = StockDailyHistory.query.filter_by(
                ts_code=stock['ts_code']
            ).count()
            
            if existing_count > 0:
                print(f"   ⏭️  已有 {existing_count} 条数据，跳过")
                continue
            
            # 生成60天数据
            daily_data = generate_stock_data(
                stock['ts_code'], 
                stock['base_price'], 
                days=60
            )
            
            # 插入数据库
            for data in daily_data:
                daily = StockDailyHistory(**data)
                db.session.add(daily)
            
            db.session.commit()
            print(f"   ✅ 生成了 {len(daily_data)} 天的K线数据")
        
        # 3. 显示统计
        print("\n" + "=" * 60)
        print("📈 数据创建完成！")
        print("=" * 60)
        
        watchlist_count = Watchlist.query.count()
        daily_count = StockDailyHistory.query.count()
        
        print(f"\n📊 数据统计:")
        print(f"   - 自选股数量: {watchlist_count} 只")
        print(f"   - K线数据: {daily_count} 条")
        
        print("\n💡 使用提示:")
        print("   1. 刷新浏览器页面")
        print("   2. 进入'股票行情'标签页")
        print("   3. 点击任意股票查看K线图")
        print()

if __name__ == '__main__':
    create_mock_data()
