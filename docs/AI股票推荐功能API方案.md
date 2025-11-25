# AI股票推荐功能API方案

## 📋 功能概述

通过调用外部AI API（如OpenAI、通义千问等）分析股票数据，为用户提供简单的买入/卖出/持有建议。采用token认证，配置简单，快速实现。

## 🎯 核心特点

- **配置简单**：只需配置API token
- **实现快速**：核心代码几十行即可完成
- **成本低廉**：按使用量计费
- **响应迅速**：调用外部API，无需本地资源

## 🔧 技术实现

### 1. AI提供者配置

#### 1.1 通义千问（推荐）
```python
# config.py 添加配置
AI_CONFIG = {
    'provider': 'tongyi',  # tongyi/openai/claude
    'tongyi': {
        'api_key': 'YOUR_DASHSCOPE_API_KEY',
        'model': 'qwen-plus',  # 或 qwen-turbo(更便宜)
        'base_url': 'https://dashscope.aliyuncs.com/api/v1'
    },
    'openai': {
        'api_key': 'YOUR_OPENAI_API_KEY',
        'model': 'gpt-3.5-turbo'
    }
}
```

#### 1.2 AI服务类
```python
import requests
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AIStockAnalyzer:
    def __init__(self):
        self.config = current_app.config.get('AI_CONFIG', {})
        self.provider = self.config.get('provider', 'tongyi')

    def analyze_stock(self, ts_code, stock_name, stock_data):
        """分析股票并给出建议"""
        try:
            # 构建分析提示词
            prompt = self.build_analysis_prompt(ts_code, stock_name, stock_data)

            # 调用AI API
            response = self.call_ai_api(prompt)

            # 解析结果
            result = self.parse_response(response)

            # 补充数据
            result.update({
                'ts_code': ts_code,
                'stock_name': stock_name,
                'analysis_time': datetime.now().isoformat()
            })

            return result

        except Exception as e:
            logger.error(f"AI分析失败: {e}")
            return self.get_default_result(ts_code, stock_name)

    def call_ai_api(self, prompt):
        """调用AI API"""
        if self.provider == 'tongyi':
            return self.call_tongyi_api(prompt)
        elif self.provider == 'openai':
            return self.call_openai_api(prompt)
        else:
            raise ValueError(f"不支持的AI提供者: {self.provider}")

    def call_tongyi_api(self, prompt):
        """调用通义千问API"""
        config = self.config['tongyi']

        headers = {
            'Authorization': f'Bearer {config["api_key"]}',
            'Content-Type': 'application/json'
        }

        data = {
            "model": config.get("model", "qwen-plus"),
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            },
            "parameters": {
                "temperature": 0.1,
                "max_tokens": 500
            }
        }

        response = requests.post(
            f"{config['base_url']}/services/aigc/text-generation/generation",
            headers=headers,
            json=data,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            return result['output']['text']
        else:
            raise Exception(f"API调用失败: {response.status_code}, {response.text}")

    def call_openai_api(self, prompt):
        """调用OpenAI API"""
        config = self.config['openai']

        headers = {
            'Authorization': f'Bearer {config["api_key"]}',
            'Content-Type': 'application/json'
        }

        data = {
            "model": config.get("model", "gpt-3.5-turbo"),
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.1,
            "max_tokens": 500
        }

        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            raise Exception(f"API调用失败: {response.status_code}, {response.text}")
```

### 2. 提示词设计

#### 2.1 简化版提示词
```python
def build_analysis_prompt(self, ts_code, stock_name, stock_data):
    """构建分析提示词"""

    prompt = f"""
你是专业的股票分析师，请分析以下股票并给出投资建议：

股票代码：{ts_code}
股票名称：{stock_name}
当前价格：{stock_data.get('current_price', 'N/A')}
今日涨跌：{stock_data.get('change_pct', 'N/A')}%
成交量比：{stock_data.get('volume_ratio', 'N/A')}
市盈率：{stock_data.get('pe_ratio', 'N/A')}
5日均价：{stock_data.get('ma5', 'N/A')}
20日均价：{stock_data.get('ma20', 'N/A')}
RSI指标：{stock_data.get('rsi', 'N/A')}

请基于以上信息给出投资建议，以JSON格式返回：
{{
    "recommendation": "buy/sell/hold",
    "reasons": ["理由1", "理由2"],
    "target_price": 目标价格数字,
    "risk_level": "low/medium/high",
    "confidence": 0.0-1.0
}}

注意：只返回JSON，不要其他文字。
"""
    return prompt
```

#### 2.2 结果解析
```python
def parse_response(self, response_text):
    """解析AI响应"""
    try:
        # 尝试解析JSON
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1

        if start_idx != -1 and end_idx != 0:
            json_str = response_text[start_idx:end_idx]
            result = json.loads(json_str)

            # 验证必需字段
            required_fields = ['recommendation', 'reasons', 'confidence']
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"缺少必需字段: {field}")

            return result
        else:
            raise ValueError("响应中未找到有效的JSON")

    except Exception as e:
        logger.error(f"解析AI响应失败: {e}")
        return self.get_default_result()

def get_default_result(self, ts_code="000001.SZ", stock_name="平安银行"):
    """默认结果"""
    return {
        "recommendation": "hold",
        "reasons": ["AI分析服务暂时不可用，建议谨慎投资"],
        "target_price": 0,
        "risk_level": "medium",
        "confidence": 0.0,
        "ts_code": ts_code,
        "stock_name": stock_name,
        "analysis_time": datetime.now().isoformat()
    }
```

### 3. API接口实现

#### 3.1 路由定义
```python
# app/api/ai_routes.py
from flask import request, jsonify
from app.services.ai_analyzer import AIStockAnalyzer
from app.models.stock_basic import StockBasic
from app.models.stock_daily_history import StockDailyHistory
from app.models.stock_daily_basic import StockDailyBasic

ai_analyzer = AIStockAnalyzer()

@api_bp.route('/ai/stock-recommendation', methods=['POST'])
def get_stock_recommendation():
    """获取股票AI推荐"""
    try:
        data = request.get_json()
        ts_code = data.get('ts_code')

        if not ts_code:
            return jsonify({
                'success': False,
                'message': '请提供股票代码'
            }), 400

        # 获取股票信息
        stock_info = StockBasic.query.filter_by(ts_code=ts_code).first()
        if not stock_info:
            return jsonify({
                'success': False,
                'message': f'股票代码 {ts_code} 不存在'
            }), 404

        # 获取最新数据
        latest_daily = StockDailyHistory.query.filter_by(
            ts_code=ts_code
        ).order_by(StockDailyHistory.trade_date.desc()).first()

        latest_basic = StockDailyBasic.query.filter_by(
            ts_code=ts_code
        ).order_by(StockDailyBasic.trade_date.desc()).first()

        # 准备分析数据
        stock_data = {
            'current_price': float(latest_daily.close) if latest_daily else 0,
            'change_pct': float(latest_daily.pct_chg) if latest_daily else 0,
            'volume_ratio': float(latest_basic.volume_ratio) if latest_basic else 0,
            'pe_ratio': float(latest_basic.pe) if latest_basic else 0,
            'ma5': 0,  # 可以后续计算
            'ma20': 0,
            'rsi': 0
        }

        # AI分析
        result = ai_analyzer.analyze_stock(ts_code, stock_info.name, stock_data)

        return jsonify({
            'success': True,
            'data': result,
            'message': 'AI分析完成'
        })

    except Exception as e:
        logger.error(f"获取AI推荐失败: {e}")
        return jsonify({
            'success': False,
            'message': f'AI分析失败: {str(e)}'
        }), 500
```

## 📊 数据库设计（简化版）

### 1. 分析记录表
```sql
CREATE TABLE ai_analysis_records (
    id INT PRIMARY KEY AUTO_INCREMENT,
    ts_code VARCHAR(20) NOT NULL,
    recommendation ENUM('buy', 'sell', 'hold') NOT NULL,
    confidence FLOAT,
    target_price FLOAT,
    risk_level ENUM('low', 'medium', 'high'),
    reasons TEXT,
    analysis_data TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_ts_code_created (ts_code, created_at)
);
```

## 🎨 前端集成

### 1. 按钮添加
```javascript
// 在股票详情页面添加AI分析按钮
<button
  onClick={() => handleAIAnalysis(stock.ts_code)}
  className="ai-analysis-btn"
  disabled={analyzing}
>
  {analyzing ? 'AI分析中...' : 'AI智能分析'}
</button>
```

### 2. API调用
```javascript
const handleAIAnalysis = async (tsCode) => {
  setAnalyzing(true);

  try {
    const response = await fetch('/api/ai/stock-recommendation', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        ts_code: tsCode
      })
    });

    const result = await response.json();

    if (result.success) {
      setAnalysisResult(result.data);
    } else {
      alert('AI分析失败: ' + result.message);
    }
  } catch (error) {
    alert('请求失败: ' + error.message);
  } finally {
    setAnalyzing(false);
  }
};
```

### 3. 结果展示
```javascript
// 分析结果展示组件
const AnalysisResult = ({ data }) => {
  const getRecommendationColor = (rec) => {
    switch(rec) {
      case 'buy': return '#22c55e';  // 绿色
      case 'sell': return '#ef4444'; // 红色
      case 'hold': return '#f59e0b'; // 黄色
      default: return '#6b7280';
    }
  };

  return (
    <div className="ai-analysis-result">
      <div className="recommendation-header">
        <span
          className="recommendation-badge"
          style={{ backgroundColor: getRecommendationColor(data.recommendation) }}
        >
          {data.recommendation === 'buy' ? '买入' :
           data.recommendation === 'sell' ? '卖出' : '持有'}
        </span>
        <span className="confidence">置信度: {Math.round(data.confidence * 100)}%</span>
      </div>

      <div className="target-price">
        目标价位: ¥{data.target_price}
      </div>

      <div className="reasons">
        <h4>分析理由：</h4>
        <ul>
          {data.reasons.map((reason, index) => (
            <li key={index}>{reason}</li>
          ))}
        </ul>
      </div>

      <div className="analysis-time">
        分析时间: {new Date(data.analysis_time).toLocaleString()}
      </div>
    </div>
  );
};
```

## 🔧 快速配置指南
通过前端页面配置




## 📈 使用建议

### 1. 成本控制
- 使用qwen-turbo模型（更便宜）
- 设置合理的调用频率限制
- 添加缓存机制，避免重复分析

### 2. 提示词优化
- 保持提示词简洁明确
- 指定JSON输出格式
- 设置合理的temperature值

### 3. 错误处理
- 实现降级机制
- 记录API调用日志
- 设置合理的超时时间

这个方案只需要配置API token即可开始使用，实现简单快速，非常适合快速开发验证。