"""
创建AI配置表
简单的表创建脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db

def create_ai_config_table():
    """创建AI配置表"""
    app = create_app()

    with app.app_context():
        try:
            print("创建 ai_config 表...")
            # Flask-SQLAlchemy会自动创建表
            from app.models.ai_config import AIConfig

            # 强制创建表
            db.create_all()
            print("[OK] AI配置表创建成功")

            # 检查是否需要初始化默认配置
            from app.models.ai_config import AIConfig
            default_config = AIConfig.query.filter_by(provider_type='tongyi').first()

            if not default_config:
                print("初始化默认AI配置...")
                # 创建通义千问默认配置
                tongyi_config = AIConfig(
                    provider_type='tongyi',
                    provider_name='通义千问',
                    config_data={
                        'api_key': '',
                        'model': 'qwen-plus',
                        'base_url': 'https://dashscope.aliyuncs.com/api/v1',
                        'timeout': 30
                    },
                    is_active=False,
                    is_default=False
                )
                db.session.add(tongyi_config)

                # 创建OpenAI默认配置
                openai_config = AIConfig(
                    provider_type='openai',
                    provider_name='OpenAI',
                    config_data={
                        'api_key': '',
                        'model': 'gpt-3.5-turbo',
                        'base_url': 'https://api.openai.com/v1',
                        'timeout': 30
                    },
                    is_active=False,
                    is_default=False
                )
                db.session.add(openai_config)

                # 创建Ollama默认配置
                ollama_config = AIConfig(
                    provider_type='ollama',
                    provider_name='Ollama',
                    config_data={
                        'base_url': 'http://localhost:11434',
                        'model': 'qwen2.5-coder',
                        'timeout': 30
                    },
                    is_active=False,
                    is_default=False
                )
                db.session.add(ollama_config)

                db.session.commit()
                print("[OK] 默认AI配置初始化完成")

            return True

        except Exception as e:
            print(f"[ERROR] 创建表失败: {e}")
            return False

if __name__ == '__main__':
    success = create_ai_config_table()
    if success:
        print("AI配置表创建完成！")
    else:
        print("AI配置表创建失败！")
        sys.exit(1)