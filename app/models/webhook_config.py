"""
Webhook配置模型
用于存储和管理各种Webhook通知渠道的配置信息
"""

from datetime import datetime
from app.extensions import db
import json
import logging

logger = logging.getLogger(__name__)


class WebhookConfig(db.Model):
    """Webhook配置模型"""
    __tablename__ = 'webhook_configs'

    id = db.Column(db.Integer, primary_key=True, comment='配置ID')
    webhook_type = db.Column(db.String(50), nullable=False, comment='Webhook类型')
    webhook_name = db.Column(db.String(100), nullable=False, comment='Webhook名称')
    config_data = db.Column(db.JSON, comment='配置数据（URL、密钥、模板等）')
    is_enabled = db.Column(db.Boolean, default=True, comment='是否启用')
    is_default = db.Column(db.Boolean, default=False, comment='是否为默认Webhook')
    status = db.Column(db.String(20), default='未测试', comment='连接状态：成功、失败、未测试')
    last_test_time = db.Column(db.DateTime, comment='最后测试时间')
    error_message = db.Column(db.Text, comment='错误信息')

    # 预警级别过滤
    alert_levels = db.Column(db.JSON, comment='启用的预警级别：[\'low\', \'medium\', \'high\', \'critical\']')

    # 消息格式配置
    message_template = db.Column(db.Text, comment='自定义消息模板')
    include_stock_info = db.Column(db.Boolean, default=True, comment='是否包含股票信息')
    include_rule_info = db.Column(db.Boolean, default=True, comment='是否包含规则信息')

    # 重试配置
    retry_count = db.Column(db.Integer, default=3, comment='重试次数')
    retry_interval = db.Column(db.Integer, default=5, comment='重试间隔（秒）')

    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # ==================== Webhook类型常量 ====================
    WEBHOOK_TYPES = {
        'dingtalk': '钉钉机器人',
        'wechat_work': '企业微信机器人',
        'feishu': '飞书机器人',
        'email': '邮件通知',
        'webhook': '通用Webhook',
        'custom': '自定义接口'
    }

    # ==================== 预警级别常量 ====================
    ALERT_LEVELS = {
        'low': '低级预警',
        'medium': '中级预警',
        'high': '高级预警',
        'critical': '严重预警'
    }

    @classmethod
    def get_enabled_configs(cls):
        """获取所有启用的Webhook配置"""
        return cls.query.filter_by(is_enabled=True).all()

    @classmethod
    def get_configs_by_alert_level(cls, alert_level):
        """获取支持指定预警级别的Webhook配置"""
        configs = cls.get_enabled_configs()
        result = []

        for config in configs:
            if not config.alert_levels:
                # 如果没有配置级别过滤，则支持所有级别
                result.append(config)
            elif alert_level in config.alert_levels:
                result.append(config)

        return result

    @classmethod
    def get_default_config(cls):
        """获取默认Webhook配置"""
        return cls.query.filter_by(is_enabled=True, is_default=True).first()

    def set_as_default(self):
        """设置为默认配置"""
        # 取消其他Webhook配置的默认状态
        WebhookConfig.query.filter(
            WebhookConfig.id != self.id
        ).update({'is_default': False})

        self.is_default = True
        db.session.commit()

    def get_safe_config_data(self):
        """获取安全的配置数据（隐藏敏感信息）"""
        if not self.config_data:
            return {}

        safe_data = self.config_data.copy()
        sensitive_fields = ['secret', 'token', 'password', 'api_key', 'access_token']

        for field in sensitive_fields:
            if field in safe_data:
                value = str(safe_data[field])
                if len(value) > 8:
                    safe_data[field] = value[:4] + '*' * (len(value) - 8) + value[-4:]
                else:
                    safe_data[field] = '*' * len(value)

        return safe_data

    def to_dict(self, include_sensitive=False):
        """转换为字典"""
        config_data = self.config_data if include_sensitive else self.get_safe_config_data()

        return {
            'id': self.id,
            'webhook_type': self.webhook_type,
            'webhook_name': self.webhook_name,
            'webhook_type_name': self.WEBHOOK_TYPES.get(self.webhook_type, self.webhook_type),
            'config_data': config_data,
            'is_enabled': self.is_enabled,
            'is_default': self.is_default,
            'status': self.status,
            'last_test_time': self.last_test_time.isoformat() if self.last_test_time else None,
            'error_message': self.error_message,
            'alert_levels': self.alert_levels or list(self.ALERT_LEVELS.keys()),
            'message_template': self.message_template,
            'include_stock_info': self.include_stock_info,
            'include_rule_info': self.include_rule_info,
            'retry_count': self.retry_count,
            'retry_interval': self.retry_interval,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def test_connection(self):
        """测试Webhook连接"""
        try:
            from app.services.webhook_service import WebhookService

            webhook_service = WebhookService()

            # 创建测试消息
            test_alert = {
                'ts_code': '000001.SZ',
                'stock_name': '平安银行',
                'alert_level': 'medium',
                'alert_message': '[测试] Webhook连接测试消息',
                'current_price': 10.50,
                'threshold_value': 10.00,
                'trigger_time': datetime.now().isoformat(),
                'rule_name': '测试规则'
            }

            result = webhook_service.send_message(self, test_alert)

            # 更新测试状态
            self.status = '成功' if result['success'] else '失败'
            self.last_test_time = datetime.now()
            self.error_message = result.get('error_message') if not result['success'] else None
            db.session.commit()

            return result

        except Exception as e:
            logger.error(f"测试Webhook连接失败: {self.webhook_name} - {str(e)}")
            # 更新状态
            self.status = '失败'
            self.last_test_time = datetime.now()
            self.error_message = str(e)
            db.session.commit()

            return {
                'success': False,
                'error_message': str(e)
            }

    def format_message(self, alert_data):
        """格式化消息内容"""
        try:
            if self.message_template:
                # 使用自定义模板
                message = self.message_template.format(**alert_data)
            else:
                # 使用默认模板
                message = self._generate_default_message(alert_data)

            # 根据Webhook类型调整格式
            if self.webhook_type == 'dingtalk':
                return self._format_dingtalk_message(message, alert_data)
            elif self.webhook_type == 'wechat_work':
                return self._format_wechat_work_message(message, alert_data)
            elif self.webhook_type == 'feishu':
                return self._format_feishu_message(message, alert_data)
            elif self.webhook_type == 'email':
                return self._format_email_message(message, alert_data)
            else:
                return message

        except Exception as e:
            logger.error(f"格式化消息失败: {str(e)}")
            return f"[格式化错误] {alert_data.get('alert_message', '预警消息')}"

    def _generate_default_message(self, alert_data):
        """生成默认消息模板"""
        level_map = {
            'low': '🔵',
            'medium': '🟡',
            'high': '🟠',
            'critical': '🔴'
        }

        level_icon = level_map.get(alert_data.get('alert_level', 'medium'), '🟡')

        # 基本信息
        message_parts = [
            f"{level_icon}【{self.ALERT_LEVELS.get(alert_data.get('alert_level', 'medium'), '预警')}】"
        ]

        # 股票信息
        if self.include_stock_info:
            stock_info = f"{alert_data.get('stock_name', '')}({alert_data.get('ts_code', '')})"
            if alert_data.get('current_price'):
                stock_info += f" 价格: {alert_data['current_price']}"
            message_parts.append(stock_info)

        # 预警消息
        message_parts.append(alert_data.get('alert_message', ''))

        # 规则信息
        if self.include_rule_info and alert_data.get('rule_name'):
            message_parts.append(f"规则: {alert_data['rule_name']}")

        # 时间信息
        if alert_data.get('trigger_time'):
            message_parts.append(f"时间: {alert_data['trigger_time']}")

        return '\n'.join(message_parts)

    def _format_dingtalk_message(self, message, alert_data):
        """格式化钉钉消息"""
        level_color_map = {
            'low': '#93C5FD',  # 蓝色
            'medium': '#FDE047',  # 黄色
            'high': '#FB923C',  # 橙色
            'critical': '#F87171'  # 红色
        }

        color = level_color_map.get(alert_data.get('alert_level', 'medium'), '#FDE047')

        return {
            "msgtype": "markdown",
            "markdown": {
                "title": "股票预警通知",
                "text": f"<font color={color}>**{message}**</font>"
            }
        }

    def _format_wechat_work_message(self, message, alert_data):
        """格式化企业微信消息"""
        return {
            "msgtype": "text",
            "text": {
                "content": message
            }
        }

    def _format_feishu_message(self, message, alert_data):
        """格式化飞书消息"""
        return {
            "msg_type": "text",
            "content": {
                "text": message
            }
        }

    def _format_email_message(self, message, alert_data):
        """格式化邮件消息"""
        level_map = {
            'low': '[低级预警]',
            'medium': '[中级预警]',
            'high': '[高级预警]',
            'critical': '[严重预警]'
        }

        level_tag = level_map.get(alert_data.get('alert_level', 'medium'), '[预警]')
        subject = f"股票预警通知 {level_tag} {alert_data.get('stock_name', '')}"

        # 构建HTML邮件内容
        html_content = f"""
        <html>
        <body>
            <h3 style="color: {self._get_email_color(alert_data.get('alert_level', 'medium'))}">{level_tag}</h3>
            <p>{message.replace(chr(10), '<br>')}</p>
            <hr>
            <small>本消息由股票预警系统自动发送</small>
        </body>
        </html>
        """

        return {
            'subject': subject,
            'html_content': html_content,
            'text_content': message
        }

    def _get_email_color(self, alert_level):
        """获取邮件颜色"""
        color_map = {
            'low': '#93C5FD',  # 蓝色
            'medium': '#FDE047',  # 黄色
            'high': '#FB923C',  # 橙色
            'critical': '#F87171'  # 红色
        }
        return color_map.get(alert_level, '#FDE047')

    @classmethod
    def get_webhook_types_info(cls):
        """获取支持的Webhook类型信息"""
        return [
            {
                'type': 'dingtalk',
                'name': '钉钉机器人',
                'description': '钉钉群机器人Webhook通知',
                'required_fields': ['webhook_url'],
                'optional_fields': ['secret'],
                'config_template': {
                    'webhook_url': '',
                    'secret': ''
                }
            },
            {
                'type': 'wechat_work',
                'name': '企业微信机器人',
                'description': '企业微信群机器人Webhook通知',
                'required_fields': ['webhook_url'],
                'optional_fields': [],
                'config_template': {
                    'webhook_url': ''
                }
            },
            {
                'type': 'feishu',
                'name': '飞书机器人',
                'description': '飞书群机器人Webhook通知',
                'required_fields': ['webhook_url'],
                'optional_fields': [],
                'config_template': {
                    'webhook_url': ''
                }
            },
            {
                'type': 'email',
                'name': '邮件通知',
                'description': '通过邮件发送预警通知',
                'required_fields': ['smtp_host', 'smtp_port', 'email', 'password', 'to_emails'],
                'optional_fields': ['use_tls', 'use_ssl', 'from_name'],
                'config_template': {
                    'smtp_host': 'smtp.gmail.com',
                    'smtp_port': 587,
                    'email': '',
                    'password': '',
                    'to_emails': [''],
                    'use_tls': True,
                    'use_ssl': False,
                    'from_name': '股票预警系统'
                }
            },
            {
                'type': 'webhook',
                'name': '通用Webhook',
                'description': '通用HTTP POST接口',
                'required_fields': ['webhook_url'],
                'optional_fields': ['headers', 'auth_type', 'username', 'password'],
                'config_template': {
                    'webhook_url': '',
                    'headers': {},
                    'auth_type': 'none',  # none, basic, bearer
                    'username': '',
                    'password': ''
                }
            },
            {
                'type': 'custom',
                'name': '自定义接口',
                'description': '自定义格式的通知接口',
                'required_fields': ['api_url'],
                'optional_fields': ['method', 'headers', 'body_template', 'auth_type'],
                'config_template': {
                    'api_url': '',
                    'method': 'POST',
                    'headers': {'Content-Type': 'application/json'},
                    'body_template': '{"message": "{{alert_message}}"}',
                    'auth_type': 'none',
                    'username': '',
                    'password': ''
                }
            }
        ]

    def __repr__(self):
        return f'<WebhookConfig {self.webhook_name} ({self.webhook_type})>'