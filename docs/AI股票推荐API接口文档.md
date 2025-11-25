# AI股票推荐API接口文档

## 📋 功能概述

AI股票推荐功能通过调用外部AI API（通义千问、OpenAI等）分析股票数据，为用户提供买入/卖出/持有的投资建议。功能简单易用，配置灵活，成本可控。

## 🔧 配置说明

### 1. 环境变量配置

在项目根目录的 `.env` 文件中配置：

```bash
# AI服务配置
AI_PROVIDER=tongyi  # 选择提供者: tongyi/openai

# 通义千问配置（推荐国内使用）
DASHSCOPE_API_KEY=your_dashscope_api_key_here
TONGYI_MODEL=qwen-plus  # 或 qwen-turbo（更便宜）

# OpenAI配置
# OPENAI_API_KEY=your_openai_api_key_here
# OPENAI_MODEL=gpt-3.5-turbo
```

### 2. 配置文件方式

也可以直接在 `config.py` 中配置：

```python
AI_CONFIG = {
    'provider': 'tongyi',
    'tongyi': {
        'api_key': 'sk-your-api-key-here',
        'model': 'qwen-plus',
        'base_url': 'https://dashscope.aliyuncs.com/api/v1',
        'timeout': 30
    }
}
```

## 🚀 API接口详情

### 1. 获取股票AI推荐

**接口地址**: `POST /api/ai/stock-recommendation`

**功能描述**: 对指定股票进行AI分析，生成投资建议

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
    "recommendation": "buy",           // buy/sell/hold
    "recommendation_name": "买入",
    "confidence": 0.75,                // 置信度 0-1
    "target_price": 16.50,              // 目标价格
    "risk_level": "medium",             // low/medium/high
    "risk_level_name": "中等风险",
    "reasons": [                       // 推荐理由数组
      "近期技术指标显示上涨趋势",
      "成交量显著放大",
      "行业整体表现良好"
    ],
    "ai_provider": "tongyi",
    "analysis_time": "2025-11-24T15:30:00",
    "data_summary": {                   // 分析数据摘要
      "current_price": 15.68,
      "change_pct": 2.5,
      "volume_ratio": 1.8,
      "pe_ratio": 8.2,
      "pb_ratio": 0.9
    }
  },
  "message": "AI分析完成"
}
```

**错误响应**:
```json
{
  "success": false,
  "message": "股票代码 000001.SZ 不存在"
}
```

### 2. 获取分析历史

**接口地址**: `GET /api/ai/analysis-history/{ts_code}`

**功能描述**: 获取指定股票的AI分析历史记录

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
    "records": [
      {
        "id": 1,
        "recommendation": "buy",
        "confidence": 0.75,
        "target_price": 16.50,
        "risk_level": "medium",
        "reasons": ["技术指标上涨", "成交量放大"],
        "created_at": "2025-11-24T15:30:00"
      }
    ],
    "total_count": 1,
    "period_days": 30
  }
}
```

### 3. 获取分析摘要

**接口地址**: `GET /api/ai/analysis-summary/{ts_code}`

**功能描述**: 获取单只股票的AI分析统计摘要

**请求参数**:
- `ts_code`: 股票代码（路径参数）
- `days`: 统计天数，默认30天（可选）

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
    "average_confidence": 0.72,
    "analysis_period": {
      "start_date": "2025-10-25T00:00:00",
      "end_date": "2025-11-24T00:00:00"
    }
  }
}
```

### 4. 获取AI配置信息

**接口地址**: `GET /api/ai/config`

**功能描述**: 获取AI服务配置状态

**响应示例**:
```json
{
  "success": true,
  "data": {
    "provider": "tongyi",
    "is_configured": true,     // 是否已配置API Key
    "model": "qwen-plus",
    "supported_providers": ["tongyi", "openai"]
  }
}
```

### 5. 获取分析统计

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
    "by_provider": {
      "tongyi": 120,
      "openai": 30
    },
    "average_confidence": 0.75
  }
}
```

## 📊 数据模型

### AIAnalysisRecord 表结构

```sql
CREATE TABLE ai_analysis_records (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '记录ID',
    ts_code VARCHAR(20) NOT NULL COMMENT '股票代码',
    stock_name VARCHAR(100) NOT NULL COMMENT '股票名称',
    recommendation ENUM('buy', 'sell', 'hold') NOT NULL COMMENT '推荐操作',
    confidence FLOAT NOT NULL COMMENT '置信度(0-1)',
    target_price FLOAT COMMENT '目标价格',
    risk_level ENUM('low', 'medium', 'high') NOT NULL COMMENT '风险等级',
    reasons TEXT COMMENT '推荐理由JSON',
    ai_provider VARCHAR(50) COMMENT 'AI提供者',
    model_name VARCHAR(100) COMMENT '使用的模型名称',
    analysis_data TEXT COMMENT '分析用的数据JSON',
    success BOOLEAN DEFAULT TRUE COMMENT '分析是否成功',
    error_message TEXT COMMENT '错误信息',
    response_time FLOAT COMMENT '响应时间(秒)',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
);
```

## 🎯 使用示例

### 1. 基础使用

```javascript
// 获取平安银行AI推荐
fetch('/api/ai/stock-recommendation', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        ts_code: '000001.SZ'
    })
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        console.log('推荐结果:', data.data);
        // 显示推荐
        showRecommendation(data.data);
    }
});
```

### 2. 批量分析

```javascript
const stockCodes = ['000001.SZ', '600036.SH', '000858.SZ'];

stockCodes.forEach(ts_code => {
    fetch('/api/ai/stock-recommendation', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ ts_code })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log(`${ts_code} 推荐:`, data.data.recommendation);
        }
    });
});
```

### 3. 历史记录查看

```javascript
// 获取平安银行分析历史
fetch('/api/ai/analysis-history/000001.SZ?days=30&limit=5')
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('分析历史:', data.data.records);
            // 显示历史图表
            showHistoryChart(data.data.records);
        }
    });
```

## ⚠️ 注意事项

### 1. 费用说明
- **通义千问**: qwen-plus模型约 ¥0.002/1K tokens
- **OpenAI**: gpt-3.5-turbo模型约 $0.002/1K tokens
- 单次分析大约消耗 200-300 tokens，成本约 ¥0.4-0.6

### 2. API限制
- 通义千问：默认QPS限制 20次/分钟
- OpenAI：默认RPM限制 3次/分钟
- 建议添加调用频率限制

### 3. 错误处理
- AI服务不可用时会返回默认的"持有"建议
- 网络错误时显示友好的错误信息
- 建议实现重试机制

### 4. 数据准确性
- AI建议仅供参考，不构成投资建议
- 建议结合其他技术分析工具
- 重要投资建议咨询专业顾问

## 🔧 开发配置建议

### 1. 开发环境
```bash
# 安装依赖
pip install requests flask

# 配置环境变量
export DASHSCOPE_API_KEY="your-api-key"
```

### 2. 生产环境
- 使用环境变量管理API密钥
- 实现API调用频率限制
- 添加监控和日志记录
- 考虑使用Redis缓存结果

### 3. 成本控制
- 设置合理的调用频率限制
- 使用更便宜的模型（如qwen-turbo）
- 实现结果缓存机制
- 监控API调用成本

## 📈 功能扩展建议

### 1. 短期扩展
- 支持更多AI提供者（Claude、Gemini等）
- 增加技术指标分析
- 实现自定义提示词模板
- 添加多语言支持

### 2. 高级功能
- 批量股票分析
- 投资组合建议
- 风险评估模型
- 分析结果验证

### 3. 集成功能
- 与预警系统集成
- 实时分析推送
- 分析结果导出
- 用户反馈收集

## 🎉 总结

AI股票推荐功能已经完整实现，包括：

✅ **核心功能**：
- AI股票推荐生成
- 多种AI提供者支持
- 完整的历史记录管理

✅ **技术实现**：
- RESTful API接口
- 数据库表和模型
- 错误处理和降级机制

✅ **用户友好**：
- 简单的配置方式
- 直观的API响应
- 丰富的查询功能

现在你可以开始实现前端部分了！所有的后端API接口都已经准备就绪。