"""
创建系统配置表
简单的表创建脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db

def create_system_config_table():
    """创建系统配置表"""
    app = create_app()

    with app.app_context():
        try:
            print("创建 system_configs 表...")
            # Flask-SQLAlchemy会自动创建表
            from app.models.system_config import SystemConfig

            # 强制创建表
            db.create_all()
            print("[OK] 系统配置表创建成功")

            # 初始化默认配置
            from app.models.system_config import SystemConfig

            # 检查是否已有配置
            existing_config = SystemConfig.query.filter_by(config_key='ai_provider').first()
            if not existing_config:
                print("初始化默认AI配置...")
                # 初始化默认AI配置
                default_ai_config = {
                    'provider': 'tongyi',
                    'tongyi': {
                        'api_key': '',
                        'model': 'qwen-plus',
                        'base_url': 'https://dashscope.aliyuncs.com/api/v1',
                        'timeout': 30
                    },
                    'openai': {
                        'api_key': '',
                        'model': 'gpt-3.5-turbo',
                        'base_url': 'https://api.openai.com/v1',
                        'timeout': 30
                    },
                    'ollama': {
                        'base_url': 'http://localhost:11434',
                        'model': 'qwen2.5-coder',
                        'timeout': 30
                    }
                }
                SystemConfig.set_ai_config(default_ai_config)
                print("[OK] 默认AI配置初始化完成")

            return True

        except Exception as e:
            print(f"[ERROR] 创建表失败: {e}")
            return False

if __name__ == '__main__':
    success = create_system_config_table()
    if success:
        print("系统配置表创建完成！")
    else:
        print("系统配置表创建失败！")
        sys.exit(1)