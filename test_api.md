# API测试指南

## 🧪 测试准备

**前置条件**:
1. ✅ 后端服务运行中 (`python run.py`)
2. ✅ Tushare数据源已配置并激活
3. ✅ 有效的Tushare Token

---

## 📡 API测试

### 测试1: 获取股票列表

**请求**:
```
GET http://localhost:5000/api/stocks
```

**预期响应**:
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
      "market": "主板",
      "list_date": "19910403"
    },
    ...
  ],
  "total": 5000,
  "source": "tushare"
}
```

**浏览器测试**: 直接访问 http://localhost:5000/api/stocks

---

### 测试2: 获取日线数据

**请求**:
```
GET http://localhost:5000/api/stocks/000001.SZ/daily?limit=30
```

**预期响应**:
```json
{
  "success": true,
  "data": [
    {
      "ts_code": "000001.SZ",
      "trade_date": "20230901",
      "open": 12.50,
      "high": 12.80,
      "low": 12.45,
      "close": 12.75,
      "pre_close": 12.50,
      "change": 0.25,
      "pct_chg": 2.00,
      "vol": 150000,
      "amount": 187500
    },
    ...
  ],
  "source": "tushare"
}
```

**浏览器测试**: 访问 http://localhost:5000/api/stocks/000001.SZ/daily?limit=10

---

### 测试3: 获取实时行情

**请求**:
```
POST http://localhost:5000/api/stocks/realtime
Content-Type: application/json

{
  "symbols": ["000001.SZ", "600000.SH"]
}
```

**使用PowerShell测试**:
```powershell
$body = @{
    symbols = @("000001.SZ", "600000.SH")
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/stocks/realtime" -Method Post -Body $body -ContentType "application/json"
```

---

## ✅ 成功标志

如果看到以下输出，说明API工作正常：
1. `success: true`
2. `data` 包含股票数据
3. `source: "tushare"`

---

## ⚠️ 可能的错误

### 错误1: 没有激活的数据源
```json
{
  "success": false,
  "message": "没有激活的数据源，请先配置数据源"
}
```
**解决**: 在前端配置Tushare并激活

### 错误2: Token未配置
```json
{
  "success": false,
  "message": "Tushare Token未配置"
}
```
**解决**: 在数据源配置中添加Token

### 错误3: API调用限制
```
"抱歉，您每小时最多访问该接口1次"
```
**解决**: 等待1小时后再次调用，或使用缓存的数据

---

## 🚀 快速测试

在PowerShell中运行：
```powershell
# 测试股票列表
Invoke-RestMethod -Uri "http://localhost:5000/api/stocks" | ConvertTo-Json -Depth 3

# 测试日线数据
Invoke-RestMethod -Uri "http://localhost:5000/api/stocks/000001.SZ/daily?limit=5" | ConvertTo-Json -Depth 3
```
