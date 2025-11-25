"""
创建AI分析记录表
简单的表创建脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db

def create_ai_analysis_table():
    """创建AI分析记录表"""
    app = create_app()

    with app.app_context():
        try:
            print("创建 ai_analysis_records 表...")
            # Flask-SQLAlchemy会自动创建表
            from app.models.ai_analysis import AIAnalysisRecord

            # 强制创建表
            db.create_all()
            print("[OK] AI分析记录表创建成功")

            return True

        except Exception as e:
            print(f"[ERROR] 创建表失败: {e}")
            return False

if __name__ == '__main__':
    success = create_ai_analysis_table()
    if success:
        print("表创建完成！")
    else:
        print("表创建失败！")
        sys.exit(1)