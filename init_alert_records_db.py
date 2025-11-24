"""
预警记录功能数据库更新脚本
更新 risk_alerts 表结构，添加新字段和索引
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.extensions import db
from app import create_app
from sqlalchemy import text

def update_risk_alerts_table():
    """更新 risk_alerts 表结构"""

    app = create_app()

    with app.app_context():
        try:
            print("开始更新 risk_alerts 表结构...")

            # 检查表是否存在
            with db.engine.connect() as conn:
                table_check = conn.execute(text("""
                    SELECT COUNT(*) as count
                    FROM information_schema.tables
                    WHERE table_schema = DATABASE() AND table_name = 'risk_alerts'
                """)).fetchone()

                if table_check.count == 0:
                    print("risk_alerts 表不存在，请先创建基础表")
                    return False

                # 获取现有列信息
                columns = conn.execute(text("""
                    SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
                    FROM information_schema.columns
                    WHERE table_schema = DATABASE() AND table_name = 'risk_alerts'
                """)).fetchall()

            existing_columns = {col.COLUMN_NAME for col in columns}
            print(f"现有列: {existing_columns}")

            # 需要添加的新列
            new_columns = {
                'rule_id': 'INT',
                'trigger_source': "VARCHAR(20) DEFAULT 'auto'",
                'alert_status': "VARCHAR(20) DEFAULT 'active'",
                'updated_at': 'DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP',
                'ignored_at': 'DATETIME NULL',
                'extra_data': 'TEXT NULL',
                'resolution_note': 'TEXT NULL'
            }

            # 使用连接进行所有数据库操作
            with db.engine.connect() as conn:
                # 开始事务
                trans = conn.begin()

                try:
                    # 添加新列
                    for column_name, column_def in new_columns.items():
                        if column_name not in existing_columns:
                            print(f"添加列: {column_name}")
                            if column_name == 'rule_id':
                                # 添加外键列
                                conn.execute(text(f"""
                                    ALTER TABLE risk_alerts
                                    ADD COLUMN {column_name} {column_def} NULL COMMENT '关联的预警规则ID'
                                """))
                                # 添加外键约束
                                try:
                                    conn.execute(text("""
                                        ALTER TABLE risk_alerts
                                        ADD CONSTRAINT fk_risk_alerts_rule_id
                                        FOREIGN KEY (rule_id) REFERENCES alert_rules(id)
                                    """))
                                    print("  添加外键约束成功")
                                except Exception as e:
                                    print(f"  添加外键约束失败（可能alert_rules表不存在）: {e}")
                            else:
                                comment_map = {
                                    'trigger_source': '触发源: auto/manual/api/system',
                                    'alert_status': '预警状态: active/resolved/ignored/pending',
                                    'updated_at': '更新时间',
                                    'ignored_at': '忽略时间',
                                    'extra_data': '扩展数据JSON',
                                    'resolution_note': '解决备注'
                                }
                                comment = comment_map.get(column_name, '')

                                conn.execute(text(f"""
                                    ALTER TABLE risk_alerts
                                    ADD COLUMN {column_name} {column_def} COMMENT '{comment}'
                                """))
                            print(f"  列 {column_name} 添加成功")
                        else:
                            print(f"列 {column_name} 已存在，跳过")

                    # 检查并添加索引
                    indexes_to_add = [
                        ('idx_risk_alerts_level_status', 'alert_level, alert_status'),
                        ('idx_risk_alerts_rule_id', 'rule_id'),
                        ('idx_risk_alerts_source', 'trigger_source'),
                        ('idx_risk_alerts_updated_at', 'updated_at')
                    ]

                    for index_name, index_columns in indexes_to_add:
                        # 检查索引是否存在
                        index_check = conn.execute(text(f"""
                            SELECT COUNT(*) as count
                            FROM information_schema.statistics
                            WHERE table_schema = DATABASE()
                            AND table_name = 'risk_alerts'
                            AND index_name = '{index_name}'
                        """)).fetchone()

                        if index_check.count == 0:
                            print(f"添加索引: {index_name}")
                            conn.execute(text(f"""
                                ALTER TABLE risk_alerts
                                ADD INDEX {index_name} ({index_columns})
                            """))
                            print(f"  索引 {index_name} 添加成功")
                        else:
                            print(f"索引 {index_name} 已存在，跳过")

                    # 更新现有数据的默认值
                    print("更新现有数据的默认值...")
                    conn.execute(text("""
                        UPDATE risk_alerts
                        SET alert_status = CASE
                            WHEN is_resolved = 1 THEN 'resolved'
                            WHEN is_active = 0 THEN 'ignored'
                            ELSE 'active'
                        END
                        WHERE alert_status IS NULL OR alert_status = ''
                    """))

                    conn.execute(text("""
                        UPDATE risk_alerts
                        SET trigger_source = 'auto'
                        WHERE trigger_source IS NULL OR trigger_source = ''
                    """))

                    conn.execute(text("""
                        UPDATE risk_alerts
                        SET updated_at = created_at
                        WHERE updated_at IS NULL
                    """))

                    # 提交事务
                    trans.commit()

                except Exception as e:
                    # 回滚事务
                    trans.rollback()
                    raise e

            print("risk_alerts 表结构更新完成！")

            # 显示表结构
            print("\n更新后的表结构:")
            with db.engine.connect() as conn:
                result = conn.execute(text("DESCRIBE risk_alerts")).fetchall()
                for row in result:
                    print(f"  {row[0]:20} {row[1]:15} {row[2]:5} {row[3]:10} {row[4]:20} {row[5] or ''}")

            return True

        except Exception as e:
            print(f"更新风险预警表失败: {e}")
            return False

if __name__ == '__main__':
    success = update_risk_alerts_table()
    if success:
        print("\n数据库更新成功！")
    else:
        print("\n数据库更新失败！")
        sys.exit(1)