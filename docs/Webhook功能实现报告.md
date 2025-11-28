# Webhook功能实现报告

## ✅ 已完成功能

### 🗄️ 数据模型设计 (`app/models/webhook_config.py`)
- **多渠道支持**: 钉钉、企业微信、飞书、邮件、通用Webhook、自定义接口
- **灵活配置**: 支持自定义消息模板、预警级别过滤、重试机制
- **安全保护**: API密钥等敏感信息自动掩码显示
- **消息格式化**: 针对不同渠道的特定消息格式
- **状态管理**: 连接状态和测试结果记录

### 🔌 服务层 (`app/services/webhook_service.py`)
- **统一接口**: 支持多种Webhook类型的发送服务
- **错误处理**: 完善的异常处理和重试机制
- **批量发送**: 支持向多个Webhook配置同时发送
- **签名验证**: 钉钉机器人签名验证支持
- **邮件支持**: SMTP邮件发送功能（需email模块支持）

### 📊 API接口 (`app/api/webhook_routes.py`)
- **完整CRUD**: 创建、读取、更新、删除Webhook配置
- **配置管理**: 启用/禁用、设置默认、批量操作
- **连通性测试**: Webhook配置连接测试功能
- **发送测试**: 支持测试消息发送和级别筛选
- **类型查询**: 获取支持的Webhook类型和配置模板

### 🔧 预警集成 (`app/services/alert_trigger_engine.py`)
- **自动通知**: 预警触发时自动发送Webhook通知（代码已实现）
- **手动触发**: 支持手动触发Webhook通知
- **级别过滤**: 根据预警级别自动匹配Webhook配置
- **完整数据**: 包含股票信息、规则信息、价格数据等

## ⚠️ 当前问题

### 1. 循环导入问题
- **问题**: `webhook_routes` -> `webhook_service` -> `alert_trigger_engine` -> `webhook_service` 形成循环导入
- **临时解决**: 已暂时注释掉部分导入以打破循环
- **影响**: 预警触发时的Webhook发送功能暂时被注释

### 2. 数据库表创建问题
- **问题**: MySQL用户权限问题导致表创建失败
- **错误**: `Access denied for user 'root'@'localhost'`
- **解决**: 需要检查MySQL用户权限和密码设置

### 3. 邮件模块依赖
- **问题**: `email.mime.text` 模块导入失败
- **临时解决**: 添加了异常处理，邮件功能不可用时跳过
- **影响**: 邮件通知暂时不可用

## 🎯 核心特性（已实现）

### ✅ 支持的通知渠道
1. **钉钉机器人**: 支持Markdown格式和签名验证
2. **企业微信机器人**: 文本消息发送
3. **飞书机器人**: 文本消息发送
4. **邮件通知**: HTML格式邮件，支持SMTP配置（暂时禁用）
5. **通用Webhook**: 自定义HTTP POST接口
6. **自定义接口**: 完全自定义的消息格式

### ✅ 消息格式化
- **动态模板**: 支持自定义消息模板
- **级别标识**: 不同预警级别的颜色和图标
- **股票信息**: 股票代码、名称、价格等
- **规则信息**: 规则名称、类型、描述
- **时间戳**: 触发时间和发送记录

### ✅ 可靠性保障
- **重试机制**: 可配置的重试次数和间隔
- **错误处理**: 完善的异常捕获和日志记录
- **状态管理**: 测试状态和发送结果记录
- **批量发送**: 支持多个Webhook同时通知

## 📋 API接口列表

### 基础配置管理
- `GET /api/webhook-configs` - 获取所有Webhook配置
- `POST /api/webhook-configs` - 创建Webhook配置
- `PUT /api/webhook-configs/{id}` - 更新Webhook配置
- `DELETE /api/webhook-configs/{id}` - 删除Webhook配置

### 状态管理
- `GET /api/webhook-configs/active` - 获取激活的Webhook配置
- `POST /api/webhook-configs/{id}/enable` - 启用Webhook配置
- `POST /api/webhook-configs/{id}/disable` - 禁用Webhook配置
- `POST /api/webhook-configs/{id}/set-default` - 设置默认Webhook配置

### 测试功能
- `POST /api/webhook-configs/{id}/test` - 测试Webhook配置
- `POST /api/webhook-configs/send-test` - 发送测试预警消息
- `POST /api/webhook-configs/send-to-level` - 发送到指定级别

### 批量操作
- `POST /api/webhook-configs/batch-enable` - 批量启用配置
- `POST /api/webhook-configs/batch-disable` - 批量禁用配置
- `POST /api/webhook-configs/batch-delete` - 批量删除配置

### 配置信息
- `GET /api/webhook-configs/types` - 获取支持的Webhook类型

## 🔧 使用方法

### 1. 手动创建表（临时方案）
```sql
-- 在MySQL中直接执行
CREATE TABLE IF NOT EXISTS webhook_configs (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '配置ID',
    webhook_type VARCHAR(50) NOT NULL COMMENT 'Webhook类型',
    webhook_name VARCHAR(100) NOT NULL COMMENT 'Webhook名称',
    config_data JSON COMMENT '配置数据',
    is_enabled BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    is_default BOOLEAN DEFAULT FALSE COMMENT '是否为默认Webhook',
    status VARCHAR(20) DEFAULT '未测试' COMMENT '连接状态',
    last_test_time DATETIME COMMENT '最后测试时间',
    error_message TEXT COMMENT '错误信息',
    alert_levels JSON COMMENT '预警级别过滤',
    message_template TEXT COMMENT '消息模板',
    include_stock_info BOOLEAN DEFAULT TRUE COMMENT '包含股票信息',
    include_rule_info BOOLEAN DEFAULT TRUE COMMENT '包含规则信息',
    retry_count INT DEFAULT 3 COMMENT '重试次数',
    retry_interval INT DEFAULT 5 COMMENT '重试间隔（秒）',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
);
```

### 2. 配置示例
```json
// 钉钉机器人配置
{
    "webhook_type": "dingtalk",
    "webhook_name": "钉钉机器人",
    "config_data": {
        "webhook_url": "https://oapi.dingtalk.com/robot/send?access_token=xxx",
        "secret": "SECxxx"
    },
    "alert_levels": ["medium", "high", "critical"]
}

// 企业微信机器人配置
{
    "webhook_type": "wechat_work",
    "webhook_name": "企业微信机器人",
    "config_data": {
        "webhook_url": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx"
    }
}

// 邮件配置
{
    "webhook_type": "email",
    "webhook_name": "邮件通知",
    "config_data": {
        "smtp_host": "smtp.qq.com",
        "smtp_port": 587,
        "email": "your@qq.com",
        "password": "your_password",
        "to_emails": ["receiver@qq.com"],
        "use_tls": true
    }
}
```

### 3. 消息格式
**默认消息格式**:
- 🟡【中级预警】股票名称(股票代码) 价格: 10.50
- 预警消息内容
- 规则: 规则名称
- 时间: 2025-01-01T12:00:00

**自定义模板**:
```text
🚨{alert_level}预警 | {stock_name}({ts_code})
💰价格: {current_price}
📊阈值: {threshold_value}
📝规则: {rule_name}
⏰时间: {trigger_time}
```

## 📊 数据结构

### webhook_configs表
```sql
CREATE TABLE webhook_configs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    webhook_type VARCHAR(50) NOT NULL,  -- 类型: dingtalk, wechat_work, feishu, email, webhook, custom
    webhook_name VARCHAR(100) NOT NULL, -- 配置名称
    config_data JSON,                  -- 配置数据JSON
    is_enabled BOOLEAN DEFAULT TRUE,     -- 是否启用
    is_default BOOLEAN DEFAULT FALSE,    -- 是否默认配置
    status VARCHAR(20) DEFAULT '未测试', -- 状态: 成功, 失败, 未测试
    last_test_time DATETIME,           -- 最后测试时间
    error_message TEXT,                 -- 错误信息
    alert_levels JSON,                  -- 级别过滤: ["low", "medium", "high", "critical"]
    message_template TEXT,               -- 自定义消息模板
    include_stock_info BOOLEAN DEFAULT TRUE,  -- 是否包含股票信息
    include_rule_info BOOLEAN DEFAULT TRUE,  -- 是否包含规则信息
    retry_count INT DEFAULT 3,          -- 重试次数
    retry_interval INT DEFAULT 5,         -- 重试间隔(秒)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

