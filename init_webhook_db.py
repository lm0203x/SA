#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Webhook配置数据库初始化脚本
创建webhook_configs表并添加默认配置
"""

from app import create_app
from app.extensions import db
from app.models.webhook_config import WebhookConfig
import logging

logger = logging.getLogger(__name__)


def init_webhook_database():
    """初始化Webhook数据库"""
    app = create_app()

    with app.app_context():
        try:
            logger.info("开始创建webhook_configs表...")

            # 创建表
            db.create_all()

            logger.info("webhook_configs表创建成功")

            # 检查是否已有数据
            existing_count = WebhookConfig.query.filter_by(is_active=True).count()
            logger.info(f"现有Webhook配置数量: {existing_count}")

            # 如果没有配置，创建示例配置
            if existing_count == 0:
                logger.info("创建默认Webhook配置...")

                # 飞书Webhook配置示例
                feishu_config = WebhookConfig.create_config(
                    name="飞书群通知",
                    webhook_type="feishu",
                    url="https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK_URL",
                    description="发送预警消息到飞书群聊",
                    message_template="""
🚨 **股票异动预警**

**股票代码**: {{stock_code}}
**预警级别**: {{alert_level}}
**预警类型**: {{alert_type}}
**详细信息**: {{alert_message}}
**当前价格**: ¥{{current_price}}
**触发时间**: {{timestamp}}

请及时关注市场动态！
                    """.strip(),
                    timeout=30,
                    retry_count=3
                )

                # 钉钉Webhook配置示例
                dingtalk_config = WebhookConfig.create_config(
                    name="钉钉群通知",
                    webhook_type="dingtalk",
                    url="https://oapi.dingtalk.com/robot/send?access_token=YOUR_ACCESS_TOKEN",
                    description="发送预警消息到钉钉群聊",
                    message_template="""{
  "msgtype": "text",
  "text": {
    "content": "股票预警通知：\n股票代码：{{stock_code}}\n预警级别：{{alert_level}}\n详细信息：{{alert_message}}\n当前价格：¥{{current_price}}\n触发时间：{{timestamp}}"
  }
}""",
                    timeout=30,
                    retry_count=3
                )

                # 企业微信Webhook配置示例
                wechat_work_config = WebhookConfig.create_config(
                    name="企业微信通知",
                    webhook_type="wechat_work",
                    url="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY",
                    description="发送预警消息到企业微信群聊",
                    message_template="""{
  "msgtype": "text",
  "text": {
    "content": "股票预警通知：\n股票代码：{{stock_code}}\n预警级别：{{alert_level}}\n详细信息：{{alert_message}}\n当前价格：¥{{current_price}}\n触发时间：{{timestamp}}"
  }
}""",
                    timeout=30,
                    retry_count=3
                )

                logger.info("默认Webhook配置创建成功")

            # 显示所有配置
            configs = WebhookConfig.query.filter_by(is_active=True).all()
            logger.info(f"当前Webhook配置列表:")
            for config in configs:
                logger.info(f"  - {config.name} ({config.type}): {config.url}")

            return True

        except Exception as e:
            logger.error(f"初始化Webhook数据库失败: {e}")
            return False


def test_webhook_config():
    """测试Webhook配置"""
    app = create_app()

    with app.app_context():
        try:
            # 获取第一个配置进行测试
            config = WebhookConfig.query.filter_by(is_active=True).first()

            if not config:
                logger.warning("没有找到Webhook配置，请先创建配置")
                return False

            logger.info(f"测试Webhook配置: {config.name}")

            # 这里可以添加实际的测试逻辑
            from app.services.webhook_service import send_webhook_notification

            test_alert_data = {
                'ts_code': '000001.SZ',
                'stock_name': '平安银行',
                'alert_level': 'medium',
                'alert_type': 'price_change_pct',
                'alert_message': '涨跌幅超过5%阈值',
                'current_price': 15.68,
                'threshold_value': 5.0,
                'created_at': '2025-01-20T10:30:00'
            }

            result = send_webhook_notification(config.to_dict(), test_alert_data)
            logger.info(f"Webhook测试结果: {result}")

            return result.get('success', False)

        except Exception as e:
            logger.error(f"测试Webhook配置失败: {e}")
            return False


if __name__ == "__main__":
    print("🚀 初始化Webhook数据库...")

    success = init_webhook_database()

    if success:
        print("✅ Webhook数据库初始化完成")

        # 询问是否测试配置
        choice = input("\n是否要测试Webhook配置? (y/n): ").lower().strip()
        if choice == 'y':
            print("🧪 开始测试Webhook配置...")
            test_result = test_webhook_config()
            if test_result:
                print("✅ Webhook配置测试成功")
            else:
                print("❌ Webhook配置测试失败")
    else:
        print("❌ Webhook数据库初始化失败")