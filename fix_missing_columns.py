"""
修复缺失的数据库列
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.extensions import db
from app import create_app
from sqlalchemy import text

def fix_missing_columns():
    """修复缺失的列"""

    app = create_app()

    with app.app_context():
        try:
            print("开始修复缺失的列...")

            # 使用连接进行数据库操作
            with db.engine.connect() as conn:
                # 开始事务
                trans = conn.begin()

                try:
                    # 添加缺失的 is_ignored 列
                    print("添加 is_ignored 列...")
                    conn.execute(text("""
                        ALTER TABLE risk_alerts
                        ADD COLUMN is_ignored BOOLEAN DEFAULT FALSE COMMENT '是否已忽略'
                    """))
                    print("  is_ignored 列添加成功")

                    # 更新现有数据的 is_ignored 值
                    print("更新现有数据的 is_ignored 默认值...")
                    conn.execute(text("""
                        UPDATE risk_alerts
                        SET is_ignored = CASE
                            WHEN alert_status = 'ignored' THEN TRUE
                            ELSE FALSE
                        END
                        WHERE is_ignored IS NULL
                    """))
                    print("  数据更新成功")

                    # 提交事务
                    trans.commit()

                    print("✅ 所有缺失列修复成功！")

                except Exception as e:
                    # 回滚事务
                    trans.rollback()
                    print(f"❌ 修复失败: {e}")
                    return False

            # 显示更新后的表结构
            print("\n更新后的表结构:")
            with db.engine.connect() as conn:
                result = conn.execute(text("DESCRIBE risk_alerts")).fetchall()
                for row in result:
                    if row[0]:
                        print(f"  {row[0]:20} {row[1]:15} {row[2]:5} {row[3]:10} {row[4]:20} {row[5] or ''}")

            return True

        except Exception as e:
            print(f"❌ 修复列失败: {e}")
            return False

if __name__ == '__main__':
    success = fix_missing_columns()
    if success:
        print("\n数据库修复成功！")
    else:
        print("\n数据库修复失败！")
        sys.exit(1)