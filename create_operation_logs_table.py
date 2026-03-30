"""
创建操作日志表
"""

from app import create_app
from app.extensions import db
from app.models.operation_log import OperationLog


def main():
    app = create_app()
    with app.app_context():
        OperationLog.__table__.create(bind=db.engine, checkfirst=True)
        print("operation_logs 表已创建或已存在")


if __name__ == '__main__':
    main()
