#!/usr/bin/env python3
"""
初始化数据源配置表
"""

from app import create_app, db
from app.models.data_source_config import DataSourceConfig

def init_datasource_table():
    """创建数据源配置表"""
    app = create_app()
    
    with app.app_context():
        # 创建数据源配置表
        db.create_all()
        print("✅ 数据源配置表创建成功")
        
        # 检查是否已有配置
        existing_config = DataSourceConfig.query.first()
        
        if not existing_config:
            # 创建默认的Tushare配置（未激活状态）
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
            print("ℹ️ 数据源配置已存在，跳过初始化")

if __name__ == '__main__':
    init_datasource_table()
