"""
Webhook服务类
支持多种通知渠道的消息发送功能
"""

import time
import json
import hashlib
import hmac
import requests
import smtplib
try:
    from email.mime.text import MimeText
    from email.mime.multipart import MimeMultipart
    from email.header import Header
except ImportError:
    MimeText = None
    MimeMultipart = None
    Header = None
from datetime import datetime
from loguru import logger


class WebhookService:
    """Webhook通知服务"""

    def __init__(self):
        """初始化Webhook服务"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'StockAlertSystem/1.0'
        })

    def send_message(self, webhook_config, alert_data):
        """
        发送预警消息到指定的Webhook

        Args:
            webhook_config: WebhookConfig实例
            alert_data: 预警数据字典

        Returns:
            发送结果字典
        """
        try:
            logger.info(f"开始发送Webhook消息: {webhook_config.webhook_name}")

            # 格式化消息
            formatted_message = webhook_config.format_message(alert_data)

            # 根据Webhook类型发送
            if webhook_config.webhook_type == 'dingtalk':
                return self._send_dingtalk(webhook_config, formatted_message)
            elif webhook_config.webhook_type == 'wechat_work':
                return self._send_wechat_work(webhook_config, formatted_message)
            elif webhook_config.webhook_type == 'feishu':
                return self._send_feishu(webhook_config, formatted_message)
            elif webhook_config.webhook_type == 'email':
                if MimeText is None:
                    return self._create_error_result("邮件功能需要email模块支持")
                return self._send_email(webhook_config, formatted_message, alert_data)
            elif webhook_config.webhook_type == 'webhook':
                return self._send_generic_webhook(webhook_config, formatted_message, alert_data)
            elif webhook_config.webhook_type == 'custom':
                return self._send_custom_webhook(webhook_config, formatted_message, alert_data)
            else:
                return self._create_error_result(f"不支持的Webhook类型: {webhook_config.webhook_type}")

        except Exception as e:
            logger.error(f"发送Webhook消息失败: {webhook_config.webhook_name} - {str(e)}")
            return self._create_error_result(str(e))

    def _send_dingtalk(self, webhook_config, message_data):
        """发送钉钉消息"""
        try:
            config_data = webhook_config.config_data
            webhook_url = config_data.get('webhook_url')
            secret = config_data.get('secret')

            if not webhook_url:
                return self._create_error_result("钉钉Webhook URL未配置")

            # 构建请求数据
            payload = {
                "msgtype": message_data["msgtype"],
                "markdown": message_data["markdown"]
            }

            # 添加签名验证
            if secret:
                timestamp = str(round(time.time() * 1000))
                sign = self._generate_dingtalk_sign(timestamp, secret)
                webhook_url = f"{webhook_url}&timestamp={timestamp}&sign={sign}"

            # 发送请求
            response = self.session.post(
                webhook_url,
                json=payload,
                timeout=webhook_config.retry_interval or 30
            )

            return self._process_response(response, "钉钉")

        except Exception as e:
            return self._create_error_result(f"钉钉消息发送失败: {str(e)}")

    def _send_wechat_work(self, webhook_config, message_data):
        """发送企业微信消息"""
        try:
            config_data = webhook_config.config_data
            webhook_url = config_data.get('webhook_url')

            if not webhook_url:
                return self._create_error_result("企业微信Webhook URL未配置")

            # 构建请求数据
            payload = {
                "msgtype": message_data["msgtype"],
                "text": message_data["text"]
            }

            # 发送请求
            response = self.session.post(
                webhook_url,
                json=payload,
                timeout=webhook_config.retry_interval or 30
            )

            return self._process_response(response, "企业微信")

        except Exception as e:
            return self._create_error_result(f"企业微信消息发送失败: {str(e)}")

    def _send_feishu(self, webhook_config, message_data):
        """发送飞书消息"""
        try:
            config_data = webhook_config.config_data
            webhook_url = config_data.get('webhook_url')

            if not webhook_url:
                return self._create_error_result("飞书Webhook URL未配置")

            # 构建请求数据
            payload = {
                "msg_type": message_data["msg_type"],
                "content": message_data["content"]
            }

            # 发送请求
            response = self.session.post(
                webhook_url,
                json=payload,
                timeout=webhook_config.retry_interval or 30
            )

            return self._process_response(response, "飞书")

        except Exception as e:
            return self._create_error_result(f"飞书消息发送失败: {str(e)}")

    def _send_email(self, webhook_config, message_data, alert_data):
        """发送邮件消息"""
        try:
            config_data = webhook_config.config_data
            smtp_host = config_data.get('smtp_host')
            smtp_port = config_data.get('smtp_port', 587)
            email = config_data.get('email')
            password = config_data.get('password')
            to_emails = config_data.get('to_emails', [])
            use_tls = config_data.get('use_tls', True)
            from_name = config_data.get('from_name', '股票预警系统')

            # 验证必需配置
            if not all([smtp_host, email, password, to_emails]):
                return self._create_error_result("邮件配置不完整，缺少必要参数")

            # 创建邮件
            msg = MimeMultipart('alternative')
            msg['Subject'] = Header(message_data['subject'], 'utf-8')
            msg['From'] = f"{from_name} <{email}>"
            msg['To'] = ', '.join(to_emails)

            # 添加HTML内容
            html_part = MimeText(message_data['html_content'], 'html', 'utf-8')
            msg.attach(html_part)

            # 添加纯文本内容
            text_part = MimeText(message_data['text_content'], 'plain', 'utf-8')
            msg.attach(text_part)

            # 发送邮件
            server = smtplib.SMTP(smtp_host, smtp_port)
            if use_tls:
                server.starttls()

            server.login(email, password)
            server.send_message(msg)
            server.quit()

            logger.info(f"邮件发送成功: {to_emails}")
            return {
                'success': True,
                'message': '邮件发送成功',
                'provider': 'email',
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            return self._create_error_result(f"邮件发送失败: {str(e)}")

    def _send_generic_webhook(self, webhook_config, message_data, alert_data):
        """发送通用Webhook消息"""
        try:
            config_data = webhook_config.config_data
            webhook_url = config_data.get('webhook_url')
            headers = config_data.get('headers', {})
            auth_type = config_data.get('auth_type', 'none')
            username = config_data.get('username', '')
            password = config_data.get('password', '')

            if not webhook_url:
                return self._create_error_result("Webhook URL未配置")

            # 构建请求头
            request_headers = {
                'Content-Type': 'application/json',
                **headers
            }

            # 构建认证
            auth = None
            if auth_type == 'basic' and username and password:
                auth = (username, password)
            elif auth_type == 'bearer' and password:
                request_headers['Authorization'] = f'Bearer {password}'

            # 构建消息体
            payload = {
                'alert_message': alert_data.get('alert_message'),
                'ts_code': alert_data.get('ts_code'),
                'stock_name': alert_data.get('stock_name'),
                'alert_level': alert_data.get('alert_level'),
                'current_price': alert_data.get('current_price'),
                'threshold_value': alert_data.get('threshold_value'),
                'rule_name': alert_data.get('rule_name'),
                'trigger_time': alert_data.get('trigger_time'),
                'message': message_data
            }

            # 发送请求
            response = self.session.post(
                webhook_url,
                json=payload,
                headers=request_headers,
                auth=auth,
                timeout=webhook_config.retry_interval or 30
            )

            return self._process_response(response, "通用Webhook")

        except Exception as e:
            return self._create_error_result(f"通用Webhook消息发送失败: {str(e)}")

    def _send_custom_webhook(self, webhook_config, message_data, alert_data):
        """发送自定义Webhook消息"""
        try:
            config_data = webhook_config.config_data
            api_url = config_data.get('api_url')
            method = config_data.get('method', 'POST')
            headers = config_data.get('headers', {'Content-Type': 'application/json'})
            body_template = config_data.get('body_template', '{"message": "{{alert_message}}"}')
            auth_type = config_data.get('auth_type', 'none')
            username = config_data.get('username', '')
            password = config_data.get('password', '')

            if not api_url:
                return self._create_error_result("自定义API URL未配置")

            # 构建认证
            auth = None
            if auth_type == 'basic' and username and password:
                auth = (username, password)
            elif auth_type == 'bearer' and password:
                headers['Authorization'] = f'Bearer {password}'

            # 渲染消息体模板
            try:
                body_data = body_template.format(**alert_data, message=message_data)
                body_json = json.loads(body_data) if body_data.startswith('{') else body_data
            except Exception as e:
                logger.warning(f"自定义消息体模板渲染失败: {e}")
                body_json = {
                    'alert_message': alert_data.get('alert_message'),
                    'message': message_data
                }

            # 发送请求
            if method.upper() == 'GET':
                response = self.session.get(
                    api_url,
                    headers=headers,
                    auth=auth,
                    params=body_json if isinstance(body_json, dict) else None,
                    timeout=webhook_config.retry_interval or 30
                )
            elif method.upper() == 'POST':
                response = self.session.post(
                    api_url,
                    json=body_json if isinstance(body_json, dict) else {'data': body_json},
                    headers=headers,
                    auth=auth,
                    timeout=webhook_config.retry_interval or 30
                )
            elif method.upper() == 'PUT':
                response = self.session.put(
                    api_url,
                    json=body_json if isinstance(body_json, dict) else {'data': body_json},
                    headers=headers,
                    auth=auth,
                    timeout=webhook_config.retry_interval or 30
                )
            else:
                return self._create_error_result(f"不支持的HTTP方法: {method}")

            return self._process_response(response, "自定义Webhook")

        except Exception as e:
            return self._create_error_result(f"自定义Webhook消息发送失败: {str(e)}")

    def _send_with_retry(self, send_func, webhook_config, *args, **kwargs):
        """带重试的消息发送"""
        max_retries = webhook_config.retry_count or 3
        retry_interval = webhook_config.retry_interval or 5

        for attempt in range(max_retries):
            try:
                result = send_func(webhook_config, *args, **kwargs)

                if result['success']:
                    if attempt > 0:
                        logger.info(f"Webhook消息重试成功: {webhook_config.webhook_name} (第{attempt + 1}次尝试)")
                    return result
                else:
                    logger.warning(f"Webhook消息发送失败: {webhook_config.webhook_name} - {result.get('error_message', '未知错误')}")

                if attempt < max_retries - 1:
                    time.sleep(retry_interval)

            except Exception as e:
                logger.error(f"Webhook消息发送异常: {webhook_config.webhook_name} - {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_interval)

        return self._create_error_result(f"Webhook消息发送失败，已重试{max_retries}次")

    def _generate_dingtalk_sign(self, timestamp, secret):
        """生成钉钉签名"""
        try:
            string_to_sign = f'{timestamp}\n{secret}'
            hmac_code = hmac.new(
                secret.encode('utf-8'),
                string_to_sign.encode('utf-8'),
                digestmod=hashlib.sha256
            ).digest()

            sign = hmac_code.hex()
            return sign
        except Exception as e:
            logger.error(f"生成钉钉签名失败: {str(e)}")
            return ""

    def _process_response(self, response, provider_name):
        """处理HTTP响应"""
        try:
            if response.status_code == 200:
                response_data = response.json() if response.content else {}

                # 检查不同平台的成功响应格式
                if provider_name == "钉钉":
                    success = response_data.get('errcode') == 0
                    error_msg = response_data.get('errmsg', '未知错误')
                elif provider_name == "企业微信":
                    success = response_data.get('errcode') == 0
                    error_msg = response_data.get('errmsg', '未知错误')
                elif provider_name == "飞书":
                    success = response_data.get('code') == 0
                    error_msg = response_data.get('msg', '未知错误')
                else:
                    # 通用Webhook默认成功
                    success = True
                    error_msg = None

                if success:
                    logger.info(f"{provider_name}消息发送成功")
                    return {
                        'success': True,
                        'message': f'{provider_name}消息发送成功',
                        'provider': provider_name,
                        'response_data': response_data,
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    logger.error(f"{provider_name}消息发送失败: {error_msg}")
                    return self._create_error_result(f'{provider_name}消息发送失败: {error_msg}')
            else:
                error_msg = f"HTTP错误: {response.status_code}"
                logger.error(f"{provider_name}消息发送失败: {error_msg}")
                return self._create_error_result(f'{provider_name}消息发送失败: {error_msg}')

        except Exception as e:
            error_msg = f"响应处理失败: {str(e)}"
            logger.error(f"{provider_name}消息发送失败: {error_msg}")
            return self._create_error_result(f'{provider_name}消息发送失败: {error_msg}')

    def _create_error_result(self, error_message):
        """创建错误结果"""
        return {
            'success': False,
            'error_message': error_message,
            'timestamp': datetime.now().isoformat()
        }

    def send_alert_to_webhooks(self, alert_data):
        """
        发送预警消息到所有匹配的Webhook配置

        Args:
            alert_data: 预警数据字典

        Returns:
            发送结果汇总
        """
        try:
            from app.models.webhook_config import WebhookConfig

            alert_level = alert_data.get('alert_level', 'medium')
            webhook_configs = WebhookConfig.get_configs_by_alert_level(alert_level)

            if not webhook_configs:
                logger.warning(f"没有找到支持{alert_level}级别的Webhook配置")
                return {
                    'success': True,
                    'message': '没有找到匹配的Webhook配置',
                    'sent_count': 0,
                    'results': []
                }

            results = []
            success_count = 0

            for webhook_config in webhook_configs:
                try:
                    logger.info(f"发送预警到Webhook: {webhook_config.webhook_name}")

                    result = self.send_with_retry(
                        self.send_message,
                        webhook_config,
                        alert_data
                    )

                    results.append({
                        'webhook_name': webhook_config.webhook_name,
                        'webhook_type': webhook_config.webhook_type,
                        'result': result
                    })

                    if result['success']:
                        success_count += 1

                except Exception as e:
                    logger.error(f"发送Webhook消息异常: {webhook_config.webhook_name} - {str(e)}")
                    results.append({
                        'webhook_name': webhook_config.webhook_name,
                        'webhook_type': webhook_config.webhook_type,
                        'result': self._create_error_result(f"发送异常: {str(e)}")
                    })

            return {
                'success': success_count > 0,
                'message': f'发送完成，成功: {success_count}/{len(webhook_configs)}',
                'sent_count': len(webhook_configs),
                'success_count': success_count,
                'results': results,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"批量发送Webhook消息失败: {str(e)}")
            return self._create_error_result(f"批量发送失败: {str(e)}")

    def test_webhook_connection(self, webhook_config):
        """测试Webhook连接"""
        test_alert_data = {
            'ts_code': '000001.SZ',
            'stock_name': '平安银行',
            'alert_level': 'medium',
            'alert_message': '[测试] Webhook连接测试消息',
            'current_price': 10.50,
            'threshold_value': 10.00,
            'trigger_time': datetime.now().isoformat(),
            'rule_name': '测试规则'
        }

        return self.send_message(webhook_config, test_alert_data)


# 全局实例
webhook_service = WebhookService()


def send_alert_to_webhooks(alert_data):
    """发送预警消息到Webhook"""
    return webhook_service.send_alert_to_webhooks(alert_data)


def test_webhook(webhook_config):
    """测试Webhook连接"""
    return webhook_service.test_webhook_connection(webhook_config)