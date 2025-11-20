"""
Webhook通知服务
支持飞书、钉钉、企业微信等多种Webhook消息发送
"""

import json
import asyncio
import aiohttp
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from urllib.parse import urlparse
import hashlib
import hmac
import base64

logger = logging.getLogger(__name__)


class WebhookService:
    """Webhook通知服务"""

    def __init__(self):
        self.session = None
        self.timeout = 30

    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout),
            connector=aiohttp.TCPConnector(limit=10)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()

    async def send_webhook(self, webhook_config: Dict[str, Any],
                          alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        发送Webhook通知

        Args:
            webhook_config: Webhook配置
            alert_data: 预警数据

        Returns:
            发送结果
        """
        try:
            webhook_type = webhook_config.get('type', 'generic')

            if webhook_type == 'feishu':
                return await self._send_feishu_webhook(webhook_config, alert_data)
            elif webhook_type == 'dingtalk':
                return await self._send_dingtalk_webhook(webhook_config, alert_data)
            elif webhook_type == 'wechat_work':
                return await self._send_wechat_work_webhook(webhook_config, alert_data)
            elif webhook_type == 'slack':
                return await self._send_slack_webhook(webhook_config, alert_data)
            elif webhook_type == 'generic':
                return await self._send_generic_webhook(webhook_config, alert_data)
            else:
                return {
                    'success': False,
                    'message': f'不支持的Webhook类型: {webhook_type}',
                    'error': 'unsupported_type'
                }

        except Exception as e:
            logger.error(f"发送Webhook失败: {str(e)}")
            return {
                'success': False,
                'message': f'发送Webhook失败: {str(e)}',
                'error': str(e)
            }

    async def _send_feishu_webhook(self, config: Dict[str, Any],
                                  alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """发送飞书Webhook消息"""

        url = config.get('url')
        if not url:
            return {
                'success': False,
                'message': '飞书Webhook URL未配置',
                'error': 'missing_url'
            }

        # 构建飞书消息
        message = self._build_feishu_message(alert_data, config)

        headers = {
            'Content-Type': 'application/json'
        }

        # 如果配置了签名，添加签名
        if config.get('secret'):
            timestamp = str(int(datetime.now().timestamp()))
            sign = self._generate_feishu_sign(config['secret'], timestamp)
            headers['X-Lark-Request-Timestamp'] = timestamp
            headers['X-Lark-Signature'] = sign

        try:
            async with self.session.post(url, json=message, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()

                    # 检查飞书API响应
                    if result.get('code') == 0:
                        return {
                            'success': True,
                            'message': '飞书消息发送成功',
                            'response': result
                        }
                    else:
                        return {
                            'success': False,
                            'message': f"飞书API错误: {result.get('msg', '未知错误')}",
                            'error': result,
                            'code': result.get('code')
                        }
                else:
                    return {
                        'success': False,
                        'message': f'HTTP错误: {response.status}',
                        'error': f'http_{response.status}',
                        'status_code': response.status
                    }

        except asyncio.TimeoutError:
            return {
                'success': False,
                'message': '请求超时',
                'error': 'timeout'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'网络请求失败: {str(e)}',
                'error': str(e)
            }

    def _build_feishu_message(self, alert_data: Dict[str, Any],
                             config: Dict[str, Any]) -> Dict[str, Any]:
        """构建飞书消息格式"""

        # 获取消息模板
        message_template = config.get('message_template')
        if message_template:
            # 使用自定义模板
            try:
                # 解析模板中的变量
                template_vars = {
                    'stock_code': alert_data.get('ts_code', ''),
                    'stock_name': alert_data.get('stock_name', ''),
                    'alert_level': alert_data.get('alert_level', ''),
                    'alert_type': alert_data.get('alert_type', ''),
                    'alert_message': alert_data.get('alert_message', ''),
                    'current_price': alert_data.get('current_price', ''),
                    'threshold_value': alert_data.get('threshold_value', ''),
                    'risk_value': alert_data.get('risk_value', ''),
                    'timestamp': alert_data.get('created_at', datetime.now().isoformat()),
                    'change_percent': self._calculate_change_percent(alert_data)
                }

                # 替换模板变量
                message_content = self._replace_template_vars(message_template, template_vars)

                return {
                    "msg_type": "text",
                    "content": {
                        "text": message_content
                    }
                }

            except Exception as e:
                logger.error(f"处理飞书消息模板失败: {str(e)}")
                # 使用默认消息
        else:
            # 使用默认消息格式
            return self._build_default_feishu_message(alert_data)

    def _build_default_feishu_message(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """构建默认飞书消息格式"""

        # 确定预警级别对应的颜色
        level_colors = {
            'low': 'blue',
            'medium': 'yellow',
            'high': 'orange',
            'critical': 'red'
        }

        alert_level = alert_data.get('alert_level', 'medium')
        color = level_colors.get(alert_level, 'blue')

        # 股票代码和名称
        stock_code = alert_data.get('ts_code', '')
        stock_name = alert_data.get('stock_name', '')
        stock_display = f"{stock_name}({stock_code})" if stock_name else stock_code

        # 构建富文本消息
        elements = [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**股票预警通知**"
                }
            }
        ]

        # 股票信息
        if stock_display:
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**股票代码**: {stock_display}"
                }
            })

        # 预警级别
        level_names = {
            'low': '低级预警',
            'medium': '中级预警',
            'high': '高级预警',
            'critical': '严重预警'
        }
        level_name = level_names.get(alert_level, '未知级别')

        elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**预警级别**: {level_name}"
            }
        })

        # 预警消息
        alert_message = alert_data.get('alert_message', '')
        if alert_message:
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**详细信息**: {alert_message}"
                }
            })

        # 价格信息
        current_price = alert_data.get('current_price')
        if current_price:
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**当前价格**: ¥{current_price}"
                }
            })

        # 时间
        timestamp = alert_data.get('created_at', datetime.now().isoformat())
        elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**触发时间**: {timestamp}"
            }
        })

        return {
            "msg_type": "interactive",
            "card": {
                "config": {
                    "wide_screen_mode": True
                },
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": "🚨 股票异动预警"
                    },
                    "template": color
                },
                "elements": elements
            }
        }

    def _generate_feishu_sign(self, secret: str, timestamp: str) -> str:
        """生成飞书签名"""
        string_to_sign = f"{timestamp}\n{secret}"
        hmac_code = hmac.new(
            string_to_sign.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        return base64.b64encode(hmac_code).decode('utf-8')

    def _replace_template_vars(self, template: str, vars_dict: Dict[str, Any]) -> str:
        """替换模板变量"""
        result = template
        for key, value in vars_dict.items():
            placeholder = f"{{{{{key}}}}}"
            result = result.replace(placeholder, str(value))
        return result

    def _calculate_change_percent(self, alert_data: Dict[str, Any]) -> str:
        """计算涨跌幅"""
        try:
            current_price = alert_data.get('current_price', 0)
            threshold_value = alert_data.get('threshold_value', 0)

            if current_price and threshold_value and current_price != 0:
                change_percent = ((current_price - threshold_value) / threshold_value) * 100
                return f"{change_percent:+.2f}%"
        except:
            pass
        return ""

    async def _send_dingtalk_webhook(self, config: Dict[str, Any],
                                   alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """发送钉钉Webhook消息"""
        # 钉钉Webhook实现
        pass

    async def _send_wechat_work_webhook(self, config: Dict[str, Any],
                                       alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """发送企业微信Webhook消息"""
        # 企业微信Webhook实现
        pass

    async def _send_slack_webhook(self, config: Dict[str, Any],
                                 alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """发送Slack Webhook消息"""
        # Slack Webhook实现
        pass

    async def _send_generic_webhook(self, config: Dict[str, Any],
                                   alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """发送通用Webhook消息"""
        # 通用Webhook实现
        pass


# 全局实例
webhook_service = WebhookService()


async def send_webhook_notification(webhook_config: Dict[str, Any],
                                   alert_data: Dict[str, Any]) -> Dict[str, Any]:
    """发送Webhook通知的便捷函数"""
    async with webhook_service as service:
        return await service.send_webhook(webhook_config, alert_data)


def sync_send_webhook_notification(webhook_config: Dict[str, Any],
                                  alert_data: Dict[str, Any]) -> Dict[str, Any]:
    """同步发送Webhook通知"""
    try:
        # 在同步环境中使用asyncio.run
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(send_webhook_notification(webhook_config, alert_data))
        finally:
            loop.close()
    except Exception as e:
        logger.error(f"同步发送Webhook失败: {str(e)}")
        return {
            'success': False,
            'message': f'同步发送Webhook失败: {str(e)}',
            'error': str(e)
        }