# API路由汇总文档

## 🔍 快速查找

本文档列出了所有可用的API接口，供前端开发使用。

---

## 📊 数据源配置 API

基础路径: `/api/datasources`

### 1. 获取所有数据源配置
```
GET /api/datasources
```

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "source_type": "tushare",
      "source_name": "Tushare Pro",
      "is_active": true,
      "is_default": true,
      "status": "成功",
      "last_test_time": "2025-09-30T12:00:00"
    }
  ]
}
```

### 2. 创建数据源配置
```
POST /api/datasources
Content-Type: application/json
```

**请求体**:
```json
{
  "source_type": "tushare",
  "source_name": "我的Tushare",
  "config_data": {
    "token": "your-tushare-token-here"
  },
  "is_active": true,
  "is_default": true
}
```

### 3. 更新数据源配置
```
PUT /api/datasources/{id}
Content-Type: application/json
```

**请求体**:
```json
{
  "is_active": true,
  "config_data": {
    "token": "new-token"
  }
}
```

### 4. 删除数据源配置
```
DELETE /api/datasources/{id}
```

### 5. 测试数据源连接
```
POST /api/datasources/{id}/test
```

**响应示例**:
```json
{
  "success": true,
  "message": "连接成功",
  "sample_data": {
    "ts_code": "000001.SZ",
    "name": "平安银行"
  }
}
```

### 6. 获取激活的数据源
```
GET /api/datasources/active
```

---

## 📈 股票数据 API

### 1. 获取股票列表
```
GET /api/stocks
```

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "ts_code": "000001.SZ",
      "symbol": "000001",
      "name": "平安银行",
      "area": "深圳",
      "industry": "银行",
      "market": "主板"
    }
  ],
  "total": 4500,
  "source": "tushare"
}
```

### 2. 获取实时行情
```
POST /api/stocks/realtime
Content-Type: application/json
```

**请求体**:
```json
{
  "symbols": ["000001.SZ", "600000.SH", "000858.SZ"]
}
```

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "ts_code": "000001.SZ",
      "name": "平安银行",
      "trade_date": "20250930",
      "open": 12.50,
      "high": 12.80,
      "low": 12.45,
      "close": 12.75,
      "volume": 150000000,
      "price_change": 0.25,
      "price_change_percent": 2.00,
      "timestamp": "2025-09-30T15:00:00"
    }
  ],
  "source": "tushare"
}
```

### 3. 获取日线数据
```
GET /api/stocks/{ts_code}/daily?start_date=20250901&end_date=20250930&limit=60
```

**参数**:
- `start_date`: 开始日期 (YYYYMMDD格式，可选)
- `end_date`: 结束日期 (YYYYMMDD格式，可选)
- `limit`: 返回条数限制 (默认60)

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "ts_code": "000001.SZ",
      "trade_date": "20250930",
      "open": 12.50,
      "high": 12.80,
      "low": 12.45,
      "close": 12.75,
      "volume": 150000000,
      "amount": 1875000000
    }
  ],
  "source": "tushare"
}
```

---

## ⚠️ 预警规则 API

### 1. 获取预警规则列表
```
GET /api/rules
```

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "AAPL价格预警",
      "symbol": "AAPL",
      "rule_type": "price_change",
      "condition": "greater_than",
      "threshold": "5",
      "enabled": true,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### 2. 创建预警规则
```
POST /api/rules
Content-Type: application/json
```

**请求体**:
```json
{
  "name": "平安银行涨幅预警",
  "symbol": "000001.SZ",
  "rule_type": "price_change",
  "condition": "greater_than",
  "threshold": "3",
  "enabled": true
}
```

**rule_type 可选值**:
- `price_change`: 价格变动
- `volume_spike`: 成交量异动
- `price_threshold`: 价格阈值

**condition 可选值**:
- `greater_than`: 大于
- `less_than`: 小于
- `equal_to`: 等于

### 3. 更新预警规则
```
PUT /api/rules/{id}
Content-Type: application/json
```

**请求体**:
```json
{
  "enabled": false,
  "threshold": "5"
}
```

### 4. 删除预警规则
```
DELETE /api/rules/{id}
```

### 5. 获取预警记录
```
GET /api/alerts?limit=50
```

**参数**:
- `limit`: 返回记录数 (默认50)

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "symbol": "000001.SZ",
      "message": "价格异动: 000001.SZ 当前价格 $12.75",
      "severity": "high",
      "price": 12.75,
      "change_percent": 5.2,
      "timestamp": "2025-09-30T14:30:00"
    }
  ],
  "total": 100
}
```

**severity 级别**:
- `high`: 高级预警
- `medium`: 中级预警
- `low`: 低级预警

---

## 🔌 WebSocket 实时通信

### 连接地址
```
ws://localhost:5000
```

### 事件列表

#### 1. 连接事件
```javascript
// 客户端连接成功后，服务器返回
{
  "event": "connected",
  "data": {
    "client_id": "xxx",
    "server_time": "2025-09-30T12:00:00",
    "message": "连接成功"
  }
}
```

#### 2. 订阅数据
```javascript
// 客户端发送
socket.emit('subscribe', {
  type: 'market_data',  // 订阅类型
  params: {
    symbol: '000001.SZ'  // 股票代码
  }
});

// 服务器响应
{
  "event": "subscribed",
  "data": {
    "type": "market_data",
    "room": "market_data_000001.SZ",
    "message": "订阅成功"
  }
}
```

**订阅类型**:
- `market_data`: 市场数据
- `indicators`: 技术指标
- `signals`: 交易信号
- `monitor`: 实时监控
- `risk_alerts`: 风险预警
- `portfolio`: 投资组合
- `news`: 新闻资讯

#### 3. 接收市场数据更新
```javascript
// 服务器推送
socket.on('market_data_update', (data) => {
  console.log(data);
  // {
  //   "symbol": "000001.SZ",
  //   "data": {
  //     "price": 12.75,
  //     "change": 0.25,
  //     "volume": 150000000
  //   },
  //   "timestamp": "2025-09-30T14:30:00"
  // }
});
```

#### 4. 接收风险预警
```javascript
socket.on('risk_alert', (data) => {
  console.log(data);
  // {
  //   "alert": {
  //     "symbol": "000001.SZ",
  //     "message": "价格异动预警",
  //     "severity": "high"
  //   },
  //   "timestamp": "2025-09-30T14:30:00"
  // }
});
```

#### 5. 取消订阅
```javascript
socket.emit('unsubscribe', {
  type: 'market_data',
  params: {
    symbol: '000001.SZ'
  }
});
```

#### 6. 心跳检测
```javascript
// 客户端发送
socket.emit('ping');

// 服务器响应
socket.on('pong', (data) => {
  console.log(data.timestamp);
});
```

---

## 🚨 错误处理

### 错误响应格式
```json
{
  "success": false,
  "message": "错误描述信息"
}
```

### 常见HTTP状态码
- `200`: 成功
- `400`: 请求参数错误
- `404`: 资源不存在
- `500`: 服务器内部错误

---

## 🔧 前端调用示例

### React + Axios 示例

```javascript
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

// 获取股票列表
const getStocks = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/stocks`);
    return response.data;
  } catch (error) {
    console.error('获取股票列表失败:', error);
    throw error;
  }
};

// 创建预警规则
const createAlertRule = async (ruleData) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/rules`, ruleData);
    return response.data;
  } catch (error) {
    console.error('创建预警规则失败:', error);
    throw error;
  }
};
```

### WebSocket 连接示例

```javascript
import io from 'socket.io-client';

const socket = io('http://localhost:5000');

// 连接成功
socket.on('connected', (data) => {
  console.log('连接成功:', data);
  
  // 订阅市场数据
  socket.emit('subscribe', {
    type: 'market_data',
    params: { symbol: '000001.SZ' }
  });
});

// 接收市场数据
socket.on('market_data_update', (data) => {
  console.log('市场数据更新:', data);
  // 更新UI
});

// 断开连接
// socket.disconnect();
```

---

## 📝 开发注意事项

1. **CORS配置**: 前端运行在 `localhost:5173`，后端已配置允许跨域
2. **数据格式**: 所有日期使用ISO 8601格式 (`YYYY-MM-DDTHH:mm:ss`)
3. **股票代码**: 使用Tushare格式 (如 `000001.SZ`, `600000.SH`)
4. **WebSocket重连**: 建议在前端实现自动重连机制
5. **API版本**: 当前版本 v1，路径前缀 `/api`
