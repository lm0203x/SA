# AI股票分析系统 - API接口文档整合

## 📋 功能概述

本系统提供完整的股票智能分析功能，包括：
- AI股票推荐（调用通义千问/OpenAI/智谱GLM等分析股票）
- 预警规则管理（多维度价格、成交量等技术指标监控）
- 预警记录管理（预警历史、状态处理、统计分析）
- Webhook通知（钉钉、企业微信、飞书、邮件等渠道）
- 实时数据推送（基于WebSocket）

---

## 一、AI股票推荐模块

### 1.1 核心API

#### 获取股票AI推荐

**接口地址**: `POST /api/ai/stock-recommendation`

**功能描述**: 对指定股票进行AI分析，生成买入/卖出/持有建议

**请求参数**:
```json
{
  "ts_code": "000001.SZ"  // 股票代码（必需）
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "ts_code": "000001.SZ",
    "stock_name": "平安银行",
    "recommendation": "buy",
    "recommendation_name": "买入",
    "confidence": 0.75,
    "target_price": 16.50,
    "risk_level": "medium",
    "reasons": ["近期技术指标显示上涨趋势", "成交量显著放大"],
    "ai_provider": "tongyi",
    "analysis_time": "2025-11-24T15:30:00",
    "data_summary": {
      "current_price": 15.68,
      "change_pct": 2.5
    }
  },
  "message": "AI分析完成"
}
```

---

#### 获取股票AI分析历史

**接口地址**: `GET /api/ai/analysis-history/{ts_code}`

**请求参数**:
- `ts_code`: 股票代码（路径参数）
- `days`: 查询天数，默认30天（可选）
- `limit`: 返回记录数，默认10条（可选）

**响应示例**:
```json
{
  "success": true,
  "data": {
    "ts_code": "000001.SZ",
    "stock_name": "平安银行",
    "records": [...],
    "total_count": 5,
    "period_days": 30
  }
}
```

---

#### 获取股票AI分析摘要

**接口地址**: `GET /api/ai/analysis-summary/{ts_code}`

**功能描述**: 获取单只股票的AI分析统计摘要

**响应示例**:
```json
{
  "success": true,
  "data": {
    "latest_analysis": {
      "recommendation": "buy",
      "confidence": 0.75,
      "target_price": 16.50
    },
    "total_analyses": 5,
    "recommendation_distribution": {
      "buy": 2,
      "sell": 1,
      "hold": 2
    },
    "average_confidence": 0.72
  }
}
```

---

#### 获取AI分析统计

**接口地址**: `GET /api/ai/analysis-stats`

**功能描述**: 获取AI分析的整体统计信息

**请求参数**:
- `days`: 统计天数，默认30天（可选）

**响应示例**:
```json
{
  "success": true,
  "data": {
    "period_days": 30,
    "total_analyses": 150,
    "successful_analyses": 145,
    "success_rate": 96.7,
    "by_recommendation": {
      "buy": 60,
      "sell": 30,
      "hold": 55
    },
    "by_risk_level": {
      "low": 40,
      "medium": 80,
      "high": 25
    },
    "average_confidence": 0.75
  }
}
```

---

#### 获取股票最新AI分析

**接口地址**: `GET /api/ai/latest-analysis/{ts_code}`

**功能描述**: 获取股票的最新一次AI分析结果

**响应示例**:
```json
{
  "success": true,
  "data": {
    "ts_code": "000001.SZ",
    "stock_name": "平安银行",
    "has_analysis": true,
    "analysis": {
      "recommendation": "buy",
      "confidence": 0.75,
      "analysis_time": "2025-11-24T15:30:00"
    }
  }
}
```

---

#### 获取AI配置信息

**接口地址**: `GET /api/ai/config`

**功能描述**: 获取AI服务配置状态

**响应示例**:
```json
{
  "success": true,
  "data": {
    "provider": "tongyi",
    "is_configured": true,
    "model": "qwen-plus",
    "provider_name": "通义千问",
    "supported_providers": ["tongyi", "openai", "zhipu", "ollama", "custom"]
  }
}
```

---

## 二、AI配置管理模块

### 2.1 核心API

#### 获取所有AI配置

**接口地址**: `GET /api/ai-configs`

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "provider_type": "tongyi",
      "provider_name": "通义千问",
      "config_data": {
        "api_key": "sk-****-****",
        "model": "qwen-plus"
      },
      "is_active": true,
      "is_default": true,
      "status": "成功"
    }
  ]
}
```

---

#### 创建AI配置

**接口地址**: `POST /api/ai-configs`

**请求参数**:
```json
{
  "provider_type": "tongyi",
  "provider_name": "通义千问-生产",
  "config_data": {
    "api_key": "your_api_key",
    "model": "qwen-plus",
    "base_url": "https://dashscope.aliyuncs.com/api/v1",
    "timeout": 30
  },
  "is_active": true,
  "is_default": true
}
```

---

#### 更新AI配置

**接口地址**: `PUT /api/ai-configs/{config_id}`

---

#### 删除AI配置

**接口地址**: `DELETE /api/ai-configs/{config_id}`

**注意**: 不能删除默认配置

---

#### 测试AI配置连通性

**接口地址**: `POST /api/ai-configs/{config_id}/test`

**响应示例**:
```json
{
  "success": true,
  "message": "连接测试成功",
  "data": {
    "test_response": "测试成功",
    "test_time": "2025-11-24T16:00:00"
  }
}
```

---

#### 获取当前激活的AI配置

**接口地址**: `GET /api/ai-configs/active`

---

#### 获取当前AI配置（兼容接口）

**接口地址**: `GET /api/ai-configs/current`

---

#### 设置默认AI配置

**接口地址**: `POST /api/ai-configs/{config_id}/set-default`

---

#### 获取支持的AI配置类型

**接口地址**: `GET /api/ai-configs/types`

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "type": "tongyi",
      "name": "通义千问",
      "required_fields": ["api_key", "model"],
      "optional_fields": ["base_url", "timeout"]
    },
    {
      "type": "openai",
      "name": "OpenAI",
      "required_fields": ["api_key", "model"]
    },
    {
      "type": "zhipu",
      "name": "智谱GLM",
      "required_fields": ["api_key", "model"]
    },
    {
      "type": "ollama",
      "name": "Ollama",
      "required_fields": [],
      "optional_fields": ["base_url", "model", "timeout"]
    },
    {
      "type": "custom",
      "name": "自定义",
      "required_fields": ["api_key", "model", "base_url"]
    }
  ]
}
```

---

## 三、预警规则管理模块

### 3.1 规则管理API

#### 获取预警规则列表

**接口地址**: `GET /api/rules`

**请求参数**:
- `ts_code`: 股票代码过滤（可选）
- `rule_type`: 规则类型过滤（可选）
- `is_enabled`: 启用状态过滤（可选）
- `page`: 页码，默认1
- `per_page`: 每页条数，默认20，最大100

---

#### 创建预警规则

**接口地址**: `POST /api/rules`

**请求参数**:
```json
{
  "rule_name": "价格预警",
  "ts_code": "000001.SZ",
  "rule_type": "price_threshold",
  "threshold_value": 15.0,
  "comparison_operator": ">",
  "alert_level": "medium",
  "alert_message_template": "股票价格突破阈值"
}
```

**支持的规则类型**:
- `price_threshold` - 价格阈值
- `pct_chg` - 涨跌幅
- `volume_ratio` - 成交量比率
- `turnover_rate` - 换手率
- `market_cap` - 市值变化
- `technical_indicator` - 技术指标
- `money_flow` - 资金流向

**支持的比较运算符**:
- `>` - 大于
- `>=` - 大于等于
- `<` - 小于
- `<=` - 小于等于
- `==` - 等于
- `!=` - 不等于

**支持的预警级别**:
- `low` - 低级
- `medium` - 中级
- `high` - 高级
- `critical` - 严重

---

#### 获取单个预警规则详情

**接口地址**: `GET /api/rules/{rule_id}`

---

#### 更新预警规则

**接口地址**: `PUT /api/rules/{rule_id}`

**可更新字段**: `rule_name`, `threshold_value`, `comparison_operator`, `alert_level`, `alert_message_template`, `is_enabled`, `extra_config`

---

#### 删除预警规则（软删除）

**接口地址**: `DELETE /api/rules/{rule_id}`

---

#### 切换预警规则启用状态

**接口地址**: `POST /api/rules/{rule_id}/toggle`

---

### 3.2 预警记录管理API

#### 获取预警记录列表

**接口地址**: `GET /api/alerts`

**请求参数**:
- `ts_code`: 股票代码过滤
- `alert_type`: 预警类型过滤
- `alert_level`: 预警级别过滤
- `alert_status`: 预警状态过滤（active/resolved/ignored）
- `trigger_source`: 触发源过滤（auto/manual/api/system）
- `rule_id`: 预警规则ID过滤
- `start_date`: 开始日期
- `end_date`: 结束日期
- `page`: 页码
- `per_page`: 每页条数
- `order_by`: 排序字段
- `order_dir`: 排序方向（asc/desc）

---

#### 创建预警记录

**接口地址**: `POST /api/alerts`

**请求参数**:
```json
{
  "ts_code": "000001.SZ",
  "alert_type": "price_threshold",
  "alert_level": "medium",
  "alert_message": "价格突破15元",
  "rule_id": 1,
  "risk_value": 15.5,
  "threshold_value": 15.0,
  "current_price": 15.5,
  "trigger_source": "manual"
}
```

---

#### 获取单个预警记录详情

**接口地址**: `GET /api/alerts/{alert_id}`

---

#### 更新预警记录

**接口地址**: `PUT /api/alerts/{alert_id}`

**可更新字段**: `alert_message`, `current_price`, `position_size`, `portfolio_weight`, `extra_data`

---

#### 删除预警记录

**接口地址**: `DELETE /api/alerts/{alert_id}`

---

### 3.3 预警状态管理API

#### 解决预警记录

**接口地址**: `POST /api/alerts/{alert_id}/resolve`

**请求参数**:
```json
{
  "resolution_note": "已处理"
}
```

---

#### 忽略预警记录

**接口地址**: `POST /api/alerts/{alert_id}/ignore`

**请求参数**:
```json
{
  "ignore_note": "无需处理"
}
```

---

#### 重新激活预警记录

**接口地址**: `POST /api/alerts/{alert_id}/reactivate`

---

#### 批量解决预警记录

**接口地址**: `POST /api/alerts/batch/resolve`

**请求参数**:
```json
{
  "alert_ids": [1, 2, 3],
  "resolution_note": "批量处理"
}
```

---

#### 批量忽略预警记录

**接口地址**: `POST /api/alerts/batch/ignore`

---

### 3.4 统计与导出API

#### 获取预警统计信息

**接口地址**: `GET /api/alerts/stats`

**请求参数**:
- `days`: 统计天数，默认30
- `ts_code`: 股票代码过滤

**响应示例**:
```json
{
  "success": true,
  "data": {
    "period_days": 30,
    "total_alerts": 150,
    "active_alerts": 25,
    "resolved_alerts": 100,
    "ignored_alerts": 25,
    "by_level": {
      "low": 30,
      "medium": 60,
      "high": 40,
      "critical": 20
    },
    "by_type": {
      "price_threshold": 80,
      "volume_ratio": 30
    }
  }
}
```

---

#### 导出预警记录

**接口地址**: `POST /api/alerts/export`

**请求参数**:
```json
{
  "ts_code": "000001.SZ",
  "alert_level": "high",
  "start_date": "2025-01-01",
  "end_date": "2025-11-24",
  "format": "csv"  // 或 json
}
```

---

#### 获取预警配置选项

**接口地址**: `GET /api/alerts/options`

**响应示例**:
```json
{
  "success": true,
  "data": {
    "alert_types": {
      "price_threshold": "价格阈值",
      "volume_ratio": "成交量比率"
    },
    "alert_levels": {
      "low": "低级预警",
      "medium": "中级预警"
    },
    "alert_statuses": {
      "active": "活跃",
      "resolved": "已解决"
    }
  }
}
```

---

### 3.5 股票数据同步API

#### 同步股票基础数据

**接口地址**: `POST /api/alert/sync-stocks`

**请求参数**:
```json
{
  "force_update": false  // 是否强制更新
}
```

---

#### 搜索股票

**接口地址**: `GET /api/alert/stocks/search`

**请求参数**:
- `q`: 搜索关键词（股票代码或名称）
- `limit`: 返回条数，默认20

---

### 3.6 预警触发检查API

#### 手动触发预警检查

**接口地址**: `POST /api/trigger/check`

**请求参数**:
```json
{
  "ts_codes": ["000001.SZ", "600036.SH"],  // 指定股票（可选）
  "rule_types": ["price_threshold"]         // 指定规则类型（可选）
}
```

---

#### 获取预警触发统计

**接口地址**: `GET /api/trigger/stats`

**请求参数**:
- `days`: 统计天数，默认7

---

#### 触发指定股票预警检查

**接口地址**: `POST /api/trigger/stock/{ts_code}`

---

### 3.7 预警统计总览API

#### 获取预警规则和记录统计

**接口地址**: `GET /api/alert/stats`

---

#### 获取预警配置选项

**接口地址**: `GET /api/alert/options`

---

## 四、Webhook通知模块

### 4.1 配置管理API

#### 获取所有Webhook配置

**接口地址**: `GET /api/webhook-configs`

---

#### 创建Webhook配置

**接口地址**: `POST /api/webhook-configs`

**请求参数**:
```json
{
  "webhook_type": "dingtalk",
  "webhook_name": "钉钉机器人",
  "config_data": {
    "webhook_url": "https://oapi.dingtalk.com/robot/send?access_token=xxx",
    "secret": "SECxxx"
  },
  "alert_levels": ["medium", "high", "critical"],
  "message_template": "自定义模板",
  "retry_count": 3,
  "retry_interval": 5
}
```

**支持的Webhook类型**:
- `dingtalk` - 钉钉机器人
- `wechat_work` - 企业微信机器人
- `feishu` - 飞书机器人
- `email` - 邮件通知
- `webhook` - 通用Webhook
- `custom` - 自定义接口

---

#### 更新Webhook配置

**接口地址**: `PUT /api/webhook-configs/{config_id}`

---

#### 删除Webhook配置

**接口地址**: `DELETE /api/webhook-configs/{config_id}`

**注意**: 不能删除默认配置

---

### 4.2 状态管理API

#### 测试Webhook配置连通性

**接口地址**: `POST /api/webhook-configs/{config_id}/test`

---

#### 获取当前激活的Webhook配置

**接口地址**: `GET /api/webhook-configs/active`

---

#### 获取默认Webhook配置

**接口地址**: `GET /api/webhook-configs/default`

---

#### 设置默认Webhook配置

**接口地址**: `POST /api/webhook-configs/{config_id}/set-default`

---

#### 启用Webhook配置

**接口地址**: `POST /api/webhook-configs/{config_id}/enable`

---

#### 禁用Webhook配置

**接口地址**: `POST /api/webhook-configs/{config_id}/disable`

---

#### 切换Webhook配置状态

**接口地址**: `POST /api/webhook-configs/{config_id}/toggle`

---

### 4.3 消息发送API

#### 发送测试预警消息

**接口地址**: `POST /api/webhook-configs/send-test`

**请求参数**:
```json
{
  "alert_data": {
    "ts_code": "000001.SZ",
    "stock_name": "平安银行",
    "alert_level": "medium",
    "alert_message": "这是一条测试预警消息"
  }
}
```

---

#### 发送预警到指定级别

**接口地址**: `POST /api/webhook-configs/send-to-level`

**请求参数**:
```json
{
  "alert_level": "high",
  "alert_data": {...}
}
```

---

### 4.4 批量操作API

#### 批量启用Webhook配置

**接口地址**: `POST /api/webhook-configs/batch-enable`

**请求参数**:
```json
{
  "config_ids": [1, 2, 3]
}
```

---

#### 批量禁用Webhook配置

**接口地址**: `POST /api/webhook-configs/batch-disable`

---

#### 批量删除Webhook配置

**接口地址**: `POST /api/webhook-configs/batch-delete`

---

### 4.5 配置信息API

#### 获取支持的Webhook类型

**接口地址**: `GET /api/webhook-configs/types`

---

## 五、数据库模型

### AI分析记录表

```sql
CREATE TABLE ai_analysis_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ts_code VARCHAR(20) NOT NULL,
    stock_name VARCHAR(100) NOT NULL,
    recommendation ENUM('buy', 'sell', 'hold') NOT NULL,
    confidence FLOAT NOT NULL,
    target_price FLOAT,
    risk_level ENUM('low', 'medium', 'high') NOT NULL,
    reasons TEXT,
    ai_provider VARCHAR(50),
    model_name VARCHAR(100),
    analysis_data TEXT,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    response_time FLOAT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### AI配置表

```sql
CREATE TABLE ai_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    provider_type VARCHAR(50) NOT NULL,
    provider_name VARCHAR(100) NOT NULL,
    config_data JSON,
    is_active BOOLEAN DEFAULT FALSE,
    is_default BOOLEAN DEFAULT FALSE,
    status VARCHAR(20) DEFAULT '未测试',
    last_test_time DATETIME,
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### 预警规则表

```sql
CREATE TABLE alert_rules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rule_name VARCHAR(100) NOT NULL,
    ts_code VARCHAR(20) NOT NULL,
    rule_type VARCHAR(50) NOT NULL,
    condition_type VARCHAR(20) DEFAULT 'realtime',
    threshold_value FLOAT NOT NULL,
    comparison_operator VARCHAR(10) NOT NULL,
    alert_level ENUM('low', 'medium', 'high', 'critical') DEFAULT 'medium',
    alert_message_template TEXT,
    is_enabled BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    extra_config JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### 预警记录表

```sql
CREATE TABLE risk_alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ts_code VARCHAR(20) NOT NULL,
    alert_type VARCHAR(50) NOT NULL,
    alert_level ENUM('low', 'medium', 'high', 'critical') NOT NULL,
    alert_message TEXT,
    alert_status ENUM('active', 'resolved', 'ignored', 'pending') DEFAULT 'active',
    rule_id INT,
    trigger_source VARCHAR(20) DEFAULT 'manual',
    risk_value FLOAT,
    threshold_value FLOAT,
    current_price FLOAT,
    resolution_note TEXT,
    extra_data JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### Webhook配置表

```sql
CREATE TABLE webhook_configs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    webhook_type VARCHAR(50) NOT NULL,
    webhook_name VARCHAR(100) NOT NULL,
    config_data JSON,
    is_enabled BOOLEAN DEFAULT TRUE,
    is_default BOOLEAN DEFAULT FALSE,
    status VARCHAR(20) DEFAULT '未测试',
    last_test_time DATETIME,
    error_message TEXT,
    alert_levels JSON,
    message_template TEXT,
    include_stock_info BOOLEAN DEFAULT TRUE,
    include_rule_info BOOLEAN DEFAULT TRUE,
    retry_count INT DEFAULT 3,
    retry_interval INT DEFAULT 5,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

---

## 六、已知问题与状态

### ✅ 已解决的问题

1. **循环导入问题**: alert_trigger_engine 与 webhook_service 的循环依赖已解决
2. **API密钥掩码**: 前端更新配置时自动处理密钥掩码

### ⚠️ 需用户处理的问题

1. **MySQL权限**: 确保数据库用户有创建表的权限
2. **邮件模块**: 需要安装 `email` 模块支持邮件通知

### ⏳ 待实现功能

1. **异动检测API**: `anomaly_api.py` 文件存在但为空，异动检测功能待实现

---

## 七、使用注意事项

### 1. 费用说明
- **通义千问**: qwen-plus约 ¥0.002/1K tokens
- **OpenAI**: gpt-3.5-turbo约 $0.002/1K tokens
- 单次分析约消耗 200-300 tokens

### 2. API限制
- 通义千问：默认QPS 20次/分钟
- 建议添加调用频率限制

### 3. 数据准确性
- AI建议仅供参考，不构成投资建议
- 重要投资咨询专业顾问

---

**最后更新**: 2026-03-02
