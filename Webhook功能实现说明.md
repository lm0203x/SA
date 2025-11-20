# 飞书Webhook功能实现说明

## 🎉 功能完成状态

### ✅ 已实现的功能

**1. Webhook配置管理**
- 📝 **完整的Webhook配置管理**：创建、查询、更新、删除、启用/禁用
- 🏗️ **数据库模型**：WebhookConfig模型，支持多种Webhook类型
- 🔧 **配置选项**：URL、密钥、重试次数、超时时间等

**2. 飞书Webhook集成**
- 🚀 **飞书消息发送**：支持文本和富文本消息格式
- 🔐 **签名验证**：支持飞书Webhook签名验证
- 📊 **富文本卡片**：美观的卡片式预警消息
- 🎨 **自定义模板**：支持消息模板自定义

**3. 预警系统集成**
- ⚡ **自动通知**：预警触发时自动发送Webhook通知
- 🔄 **异步处理**：不阻塞预警触发过程
- 📈 **统计功能**：发送成功/失败统计
- 🔁 **重试机制**：支持配置重试次数

**4. 完整的API接口**
- 🌐 **RESTful API**：完整的Webhook管理API
- 🧪 **测试功能**：API测试功能
- 📊 **统计接口**：Webhook使用统计
- ⚙️ **配置选项**：Webhook类型和选项接口

## 🚀 使用方法

### 1. 初始化数据库

```bash
python init_webhook_db.py
```

### 2. 安装依赖

```bash
pip install aiohttp>=3.8.0
```

### 3. 配置飞书Webhook

#### 3.1 创建飞书机器人
1. 在飞书群聊中添加自定义机器人
2. 获取Webhook URL
3. （可选）设置签名密钥

#### 3.2 通过API配置
```bash
curl -X POST http://localhost:5000/api/webhooks \
  -H "Content-Type: application/json" \
  -d '{
    "name": "飞书群通知",
    "type": "feishu",
    "url": "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK_URL",
    "description": "股票预警通知",
    "message_template": "🚨 股票预警：{{stock_code}} {{alert_message}}",
    "timeout": 30,
    "retry_count": 3
  }'
```

### 4. 验证功能

#### 4.1 测试Webhook
```bash
curl -X POST http://localhost:5000/api/webhooks/1/test \
  -H "Content-Type: application/json" \
  -d '{
    "ts_code": "000001.SZ",
    "stock_name": "平安银行",
    "alert_level": "medium",
    "alert_message": "涨跌幅超过5%阈值",
    "current_price": 15.68
  }'
```

#### 4.2 创建预警规则触发通知
在"预警规则"页面创建预警规则，当规则触发时会自动发送飞书通知

## 📱 飞书消息格式

### 默认消息格式（推荐）
系统会自动生成美观的富文本卡片消息，包含：
- 🎯 预警标题和级别
- 📈 股票信息和代码
- ⚠️ 详细预警信息
- 💰 当前价格信息
- ⏰ 触发时间

### 自定义消息模板
可以在配置时设置自定义消息模板，支持变量：
- `{{stock_code}}`: 股票代码
- `{{stock_name}}`: 股票名称
- `{{alert_level}}`: 预警级别
- `{{alert_type}}`: 预警类型
- `{{alert_message}}`: 预警消息
- `{{current_price}}`: 当前价格
- `{{threshold_value}}`: 阈值
- `{{timestamp}}`: 时间戳

示例模板：
```
🚨 **股票预警通知**
**股票**: {{stock_name}}({{stock_code}})
**级别**: {{alert_level}}
**信息**: {{alert_message}}
**价格**: ¥{{current_price}}
**时间**: {{timestamp}}
```

## 🔧 API接口文档

### Webhook配置管理

#### 获取Webhook列表
```http
GET /api/webhooks
```

#### 创建Webhook配置
```http
POST /api/webhooks
Content-Type: application/json

{
  "name": "飞书群通知",
  "type": "feishu",
  "url": "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK_URL",
  "description": "股票预警通知",
  "message_template": "自定义消息模板",
  "timeout": 30,
  "retry_count": 3
}
```

#### 更新Webhook配置
```http
PUT /api/webhooks/{id}
Content-Type: application/json

{
  "name": "更新后的名称",
  "enabled": true
}
```

#### 删除Webhook配置
```http
DELETE /api/webhooks/{id}
```

### 测试和统计

#### 测试Webhook
```http
POST /api/webhooks/{id}/test
Content-Type: application/json

{
  "ts_code": "000001.SZ",
  "alert_level": "medium",
  "alert_message": "测试消息"
}
```

#### 获取Webhook统计
```http
GET /api/webhooks/stats
```

#### 获取配置选项
```http
GET /api/webhooks/options
```

## 🎯 支持的Webhook类型

### 1. 飞书 (feishu)
- ✅ 富文本卡片消息
- ✅ 签名验证
- ✅ 自定义模板

### 2. 钉钉 (dingtalk)
- ✅ 文本消息
- ⏳ 签名验证（开发中）

### 3. 企业微信 (wechat_work)
- ✅ 文本消息
- ⏳ 签名验证（开发中）

### 4. Slack
- ✅ 基础消息格式（开发中）

### 5. 通用HTTP (generic)
- ✅ 自定义HTTP请求（开发中）

## 📋 技术特性

### 消息发送
- 🔄 **异步处理**：不阻塞预警触发
- 🔄 **自动重试**：可配置重试次数
- ⏱️ **超时控制**：可配置请求超时
- 📊 **发送统计**：成功/失败次数统计

### 错误处理
- 🛡️ **网络错误处理**：自动重试机制
- 📝 **详细日志**：完整的错误日志记录
- 🔍 **状态跟踪**：发送状态实时更新
- 📊 **失败统计**：失败原因分析

### 安全性
- 🔐 **签名验证**：支持飞书签名验证
- 🌐 **HTTPS支持**：强制HTTPS请求
- 🔒 **密钥保护**：敏感信息加密存储

## 🧪 测试建议

### 1. 基础功能测试
1. 创建Webhook配置
2. 测试Webhook连通性
3. 验证消息格式

### 2. 预警集成测试
1. 创建预警规则
2. 触发预警检查
3. 验证Webhook通知

### 3. 性能测试
1. 批量预警触发测试
2. 并发Webhook发送测试
3. 网络异常恢复测试

## 🔮 下一步计划

### 短期优化
- 📧 **邮件通知**：实现SMTP邮件Webhook
- 🔗 **Slack集成**：完善Slack消息格式
- 📱 **移动端优化**：移动端消息适配

### 长期规划
- 🤖 **AI消息优化**：AI生成消息摘要
- 📊 **消息模板市场**：预设消息模板
- 🎨 **可视化配置**：图形化Webhook配置

## 📞 故障排除

### 常见问题

**1. Webhook发送失败**
- 检查URL是否正确
- 确认网络连接正常
- 查看日志错误信息

**2. 飞书消息格式问题**
- 确认飞书机器人权限
- 检查消息格式是否符合飞书要求
- 验证签名密钥配置

**3. 预警不触发通知**
- 确认Webhook配置已启用
- 检查预警规则是否正确
- 查看预警触发日志

### 日志查看
```bash
tail -f logs/stock_analysis.log | grep webhook
```

## 🎉 总结

飞书Webhook功能已完全实现并集成到预警系统中，支持：
- ✅ 美观的富文本卡片消息
- ✅ 安全的签名验证机制
- ✅ 可靠的异步发送处理
- ✅ 完整的统计和监控功能
- ✅ 灵活的自定义模板支持

现在可以通过飞书实时接收股票预警通知，大大提升了预警的及时性和便利性！