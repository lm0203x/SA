#!/usr/bin/env python3
"""
预警系统数据库初始化脚本
创建预警规则和预警记录相关数据表
"""

import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.extensions import db
from app.models.alert_rule import AlertRule
from app.models.risk_alert import RiskAlert
from app.models.stock_basic import StockBasic
from config import Config


def init_alert_tables():
    """初始化预警相关数据表"""
    
    print("=" * 60)
    print("🚀 开始初始化预警系统数据表...")
    print("=" * 60)
    
    try:
        # 创建数据表
        print("\n📋 创建数据表结构...")
        db.create_all()
        print("✅ 数据表创建成功")
        
        # 检查表是否存在
        print("\n🔍 验证表结构...")
        
        # 检查 alert_rules 表
        try:
            rule_count = AlertRule.query.count()
            print(f"✅ alert_rules 表存在，当前记录数: {rule_count}")
        except Exception as e:
            print(f"❌ alert_rules 表检查失败: {e}")
            return False
        
        # 检查 risk_alerts 表  
        try:
            alert_count = RiskAlert.query.count()
            print(f"✅ risk_alerts 表存在，当前记录数: {alert_count}")
        except Exception as e:
            print(f"❌ risk_alerts 表检查失败: {e}")
            return False
        
        # 插入示例数据
        if rule_count == 0:
            print("\n📝 插入示例预警规则...")
            insert_sample_rules()
        
        print("\n" + "=" * 60)
        print("🎉 预警系统数据库初始化完成！")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 数据库初始化失败: {e}")
        return False


def insert_sample_rules():
    """插入示例预警规则"""
    
    # 获取一些股票代码用于示例
    sample_stocks = StockBasic.query.limit(3).all()
    
    if not sample_stocks:
        print("⚠️  未找到股票基础数据，跳过示例规则创建")
        return
    
    sample_rules = []
    
    for stock in sample_stocks:
        # 涨幅预警规则
        rule1 = {
            'rule_name': f'{stock.name}涨幅超5%预警',
            'ts_code': stock.ts_code,
            'rule_type': 'price_change_pct',
            'condition_type': 'daily_change',
            'threshold_value': 5.0,
            'comparison_operator': 'gte',
            'alert_level': 'medium',
            'alert_message_template': '涨跌幅大于等于5.0%，当前涨跌幅：{current_value}%'
        }
        
        # 跌幅预警规则
        rule2 = {
            'rule_name': f'{stock.name}跌幅超3%预警',
            'ts_code': stock.ts_code,
            'rule_type': 'price_change_pct',
            'condition_type': 'daily_change',
            'threshold_value': -3.0,
            'comparison_operator': 'lte',
            'alert_level': 'high',
            'alert_message_template': '涨跌幅小于等于-3.0%，当前涨跌幅：{current_value}%'
        }
        
        # 换手率预警规则
        rule3 = {
            'rule_name': f'{stock.name}换手率异常预警',
            'ts_code': stock.ts_code,
            'rule_type': 'turnover_rate',
            'condition_type': 'daily_turnover',
            'threshold_value': 10.0,
            'comparison_operator': 'gt',
            'alert_level': 'medium',
            'alert_message_template': '换手率大于10.0%，当前换手率：{current_value}%'
        }
        
        sample_rules.extend([rule1, rule2, rule3])
    
    # 创建规则
    created_count = 0
    for rule_data in sample_rules:
        try:
            rule = AlertRule.create_rule(**rule_data)
            created_count += 1
            print(f"  ✅ 创建规则: {rule.rule_name}")
        except Exception as e:
            print(f"  ❌ 创建规则失败: {rule_data['rule_name']} - {e}")
    
    print(f"\n📊 成功创建 {created_count} 条示例预警规则")


def show_table_info():
    """显示表信息"""
    
    print("\n" + "=" * 60)
    print("📊 数据表信息统计")
    print("=" * 60)
    
    try:
        # 预警规则统计
        rule_stats = AlertRule.get_rule_stats()
        print(f"\n📋 预警规则统计:")
        print(f"  - 总规则数: {rule_stats['total_rules']}")
        print(f"  - 启用规则数: {rule_stats['total_enabled']}")
        
        if rule_stats['by_type']:
            print(f"  - 按类型分布:")
            for rule_type, count in rule_stats['by_type'].items():
                type_name = AlertRule.RULE_TYPES.get(rule_type, rule_type)
                print(f"    * {type_name}: {count}")
        
        if rule_stats['by_level']:
            print(f"  - 按级别分布:")
            for level, count in rule_stats['by_level'].items():
                level_name = AlertRule.ALERT_LEVELS.get(level, level)
                print(f"    * {level_name}: {count}")
        
        # 预警记录统计
        alert_stats = RiskAlert.get_alert_stats()
        alert_count = RiskAlert.query.count()
        print(f"\n🚨 预警记录统计:")
        print(f"  - 总记录数: {alert_count}")
        
        if alert_stats:
            print(f"  - 活跃预警分布:")
            for level, count in alert_stats.items():
                level_name = AlertRule.ALERT_LEVELS.get(level, level)
                print(f"    * {level_name}: {count}")
        
    except Exception as e:
        print(f"❌ 获取统计信息失败: {e}")


def main():
    """主函数"""
    
    print("🔧 预警系统数据库初始化工具")
    print(f"⏰ 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查数据库连接
    try:
        from app import create_app
        app = create_app()
        
        with app.app_context():
            # 测试数据库连接
            db.engine.execute('SELECT 1')
            print("✅ 数据库连接正常")
            
            # 初始化表
            success = init_alert_tables()
            
            if success:
                # 显示表信息
                show_table_info()
                
                print("\n🎯 下一步操作建议:")
                print("1. 启动后端服务: python run.py")
                print("2. 测试API接口: GET /api/alert/rules")
                print("3. 在前端配置预警规则")
                
                return 0
            else:
                return 1
                
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        print("\n💡 解决建议:")
        print("1. 检查数据库服务是否启动")
        print("2. 检查 config.py 中的数据库配置")
        print("3. 确认数据库用户权限")
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
