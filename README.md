# 基于WebSocket的实时股票异动检测与智能预警系统

一个现代化的股票监控与预警系统，采用前后端分离架构，集成了实时数据获取、异动检测、智能预警、用户界面等完整功能。

## 🚀 项目状态

**当前版本**: v2.0 (重构版本)  
**开发状态**: 核心功能已完成，系统可正常使用  
**架构**: React + Flask + WebSocket 前后端分离  
**数据源**: Tushare Pro API (支持2120积分权限)  

### ✅ 已完成功能
- 📊 **数据获取系统**: Tushare Pro集成，支持日线、指标、资金流向数据
- ⚠️ **预警规则系统**: 多维度预警规则配置和管理
- 📝 **预警记录系统**: 完整的预警历史记录和统计
- 🎯 **前端界面**: 现代化React界面，自选股管理，K线图展示
- 🔌 **API接口**: 完整的RESTful API，支持CRUD操作
- 🗄️ **数据库架构**: 优化的MySQL表结构和索引设计

### 🚧 开发中功能
- 🌐 **WebSocket实时通信**: 架构完成，待激活
- 🔍 **异动检测算法**: 框架完成，待实现
- 📱 **实时监控面板**: 计划中

![系统主界面](./web/public/screenshot.png)

## 🌟 系统特色

### 核心功能
- **📊 实时数据监控**: 基于Tushare Pro的高质量股票数据
- **⚠️ 智能预警系统**: 多维度预警规则，支持价格、成交量、技术指标等
- **🔍 异动检测**: 统计学算法识别价格和成交量异常变化
- **📱 现代化界面**: React + Tailwind CSS响应式设计
- **🌐 实时通信**: WebSocket技术实现毫秒级数据推送
- **📈 数据可视化**: K线图、指标图表、实时更新

### 技术架构
- **后端**: Python 3.11+ / Flask / SQLAlchemy / WebSocket
- **前端**: React 18 / Vite / Tailwind CSS / Shadcn/UI
- **数据处理**: Pandas / NumPy / Tushare Pro
- **数据库**: MySQL 8.0+ / 优化索引设计
- **通信**: WebSocket / RESTful API / CORS支持

## 🚀 快速开始

### 📋 项目架构说明

本项目采用**完全前后端分离**架构：
- **前端**: React + Vite + Tailwind CSS (位于 `web/` 目录)
- **后端**: Flask + REST API + WebSocket (位于 `app/` 目录)
- **数据库**: MySQL 8.0+ (优化索引设计)
- **数据源**: Tushare Pro API (支持2120积分权限)

### 1. 环境要求
- **Python 3.11+** (后端开发语言)
- **Node.js 18+** (前端构建工具)
- **MySQL 8.0+** (数据存储)
- **Tushare Pro账号** (免费注册即可)

### 2. 后端安装与配置

#### 📦 第一步：安装后端依赖
```bash
# 在项目根目录下运行
pip install -r requirements_minimal.txt
```

**主要依赖说明**：
- ✅ Flask 及相关扩展（Web框架）
- ✅ Flask-SocketIO（WebSocket支持）
- ✅ SQLAlchemy（数据库ORM）
- ✅ Tushare（股票数据源）
- ✅ PyMySQL（MySQL数据库驱动）

#### 🗄️ 第二步：初始化数据库
```bash
python init_datasource_db.py
```

**这个脚本会**：
1. 创建 `data_source_config` 表
2. 添加默认的Tushare Pro配置（未激活）
3. 添加默认的Yahoo Finance配置（未激活）

**预期输出**：
```
✅ 数据源配置表创建成功
✅ 默认数据源配置创建成功
```

#### 🔧 第三步：配置检查

**检查数据库配置** - 确认 `config.py` 中的数据库连接信息：
```python
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = 'your_password'  # 修改为您的数据库密码
DB_NAME = 'stock'
```

**检查前后端分离配置** - 确认 `config.py` 中：
```python
ENABLE_LEGACY_TEMPLATES = False  # ✅ 已设置为False，不使用旧模板
```

#### 🎯 第四步：启动后端服务
```bash
python run.py
```

**后端服务信息**：
- API地址: `http://localhost:5000/api`
- WebSocket地址: `ws://localhost:5000`
- 支持CORS: `http://localhost:5173` (Vite开发服务器)

### 3. 前端安装与启动

#### 💻 第五步：启动前端服务
```bash
# 进入前端目录
cd web

# 安装依赖（如果还没安装）
pnpm install

# 启动开发服务器
pnpm dev
```

**前端服务信息**：
- 开发地址: `http://localhost:5173`
- 框架: Vite + React 18
- UI库: Shadcn/UI + Tailwind CSS

### 4. 配置Tushare数据源

#### 🔑 方法1：通过前端界面配置（推荐）
1. 访问 `http://localhost:5173`
2. 点击"数据源"标签页
3. 输入您的Tushare Token
4. 点击"测试连接"
5. 测试成功后，点击"激活"

#### 🔑 方法2：通过API直接配置
```bash
curl -X PUT http://localhost:5000/api/datasources/1 \
  -H "Content-Type: application/json" \
  -d '{
    "config_data": {
      "token": "YOUR_TUSHARE_TOKEN_HERE"
    },
    "is_active": true,
    "is_default": true
  }'
```

#### 📝 获取Tushare Token
1. 访问 https://tushare.pro/
2. 注册账号（免费）
3. 在个人中心获取Token
4. 免费版足够个人使用

### 5. 验证安装

#### ✅ 测试后端API
打开浏览器访问：`http://localhost:5000/api/datasources`

应该返回JSON数据：
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "source_type": "tushare",
      "source_name": "Tushare Pro",
      "is_active": false
    }
  ]
}
```

#### ✅ 测试前端页面
打开浏览器访问：`http://localhost:5173`

应该看到股票异动检测与智能预警系统的主界面。

### 6. 访问系统
- **前端界面**: http://localhost:5173
- **后端API**: http://localhost:5000/api
- **WebSocket**: ws://localhost:5000

## 📖 使用指南

### 主要功能模块

#### 1. 股票行情监控

##### 🌟 自选股管理功能

**为什么要用自选股？**
- ✅ **精准高效**: 只添加您关注的股票，避免一次性获取所有5000只股票
- ✅ **节省资源**: 只获取和存储自选股数据，避免浪费空间
- ✅ **不会超限**: 避免频繁调用Tushare API，符合免费版限制
- ✅ **用户友好**: 更符合个人使用习惯

**功能特点**：
- ✅ 手动添加股票代码
- ✅ 设置股票备注
- ✅ 删除不关注的股票
- ✅ 查看最后同步时间
- ✅ 单只股票同步
- ✅ 批量同步所有自选股

**使用流程**：

1. **添加自选股**
   ```
   1. 点击"添加"按钮
   2. 输入股票代码（例如: 000001.SZ）
   3. 输入股票名称（选填）
   4. 添加备注（选填）
   5. 点击"确认添加"
   ```

2. **常见股票代码格式**：
   - 深圳市场：`000001.SZ`、`002594.SZ`、`300750.SZ`
   - 上海市场：`600000.SH`、`601318.SH`、`688981.SH`

3. **推荐添加的股票**（示例）：
   ```
   000001.SZ - 平安银行
   600036.SH - 招商银行
   000858.SZ - 五粮液
   600519.SH - 贵州茅台
   000333.SZ - 美的集团
   ```

4. **同步数据**
   - **自动同步**: 第一次点击股票查看K线图时自动获取
   - **手动同步**: 点击"同步"按钮，同步所有自选股数据

5. **查看K线图**
   ```
   1. 在自选股列表中点击任意股票
   2. 右侧显示K线图
   3. 鼠标悬停查看详细信息
   ```

- **K线图展示**: 60个交易日历史数据，双Y轴（价格+成交量）
- **指标面板**: 每日指标和资金流向数据
- **时间切换**: 支持不同时间周期(开发中)

#### 2. 预警规则配置
- **规则类型**: 价格阈值、涨跌幅、成交量、换手率等
- **比较条件**: 大于、小于、等于等逻辑运算
- **预警级别**: 低级、中级、高级、严重四个级别
- **规则管理**: 启用/禁用、编辑、删除规则

#### 3. 预警记录查看
- **历史记录**: 完整的预警触发历史
- **统计分析**: 按类型、级别、时间的统计信息
- **状态管理**: 预警解决状态跟踪

#### 4. 数据源配置
- **Tushare集成**: 支持Tushare Pro API配置
- **连接测试**: 验证数据源连接状态
- **权限管理**: 根据积分显示可用功能

## 📋 开发进度与TODO

### ✅ 已完成功能 (Phase 1)

#### 数据获取与存储系统 (100%)
- ✅ Tushare Pro API集成，支持2120积分权限
- ✅ 股票基础数据同步 (`stock_basic`)
- ✅ 日线行情数据 (`stock_daily_history`)
- ✅ 每日指标数据 (`stock_daily_basic`)
- ✅ 资金流向数据 (`stock_moneyflow`)
- ✅ NaN值处理和数据清洗机制
- ✅ 增量同步和全量刷新

#### 预警系统核心 (100%)
- ✅ 预警规则数据库设计 (`alert_rules`)
- ✅ 预警记录系统 (`risk_alerts`)
- ✅ 多维度预警规则支持
- ✅ 预警触发引擎 (手动触发版本)
- ✅ 预警统计和历史管理

#### 前端用户界面 (95%)
- ✅ React + Tailwind CSS现代化界面
- ✅ 自选股管理功能
- ✅ K线图展示 (ECharts集成)
- ✅ 预警规则配置页面
- ✅ 数据源配置界面
- ✅ 响应式设计和优雅交互
- ✅ 自定义确认对话框

#### API接口系统 (100%)
- ✅ RESTful API设计
- ✅ 完整的CRUD操作
- ✅ 数据验证和错误处理
- ✅ CORS跨域支持
- ✅ 统一响应格式

### 🚧 进行中功能 (Phase 2)

#### 实时监控系统 (架构完成，待激活)
- 🔄 WebSocket实时通信框架
- 🔄 实时数据推送服务
- 🔄 客户端连接管理
- ⏳ 实时数据流激活
- ⏳ 前端WebSocket集成

#### 异动检测算法 (框架完成，待实现)
- 🔄 统计学异动检测框架
- 🔄 技术指标分析模块
- ⏳ 价格异动检测算法
- ⏳ 成交量异动检测算法
- ⏳ 多维度综合分析

### ⏳ 计划中功能 (Phase 3)

#### 自动化预警监控
- 📅 **定时任务调度器**: 替代手动触发的自动监控机制
- 📅 **实时数据管道**: 数据更新时自动触发预警检查
- 📅 **多渠道通知**: 邮件、短信、WebSocket推送等
- 📅 **预警性能优化**: 大量规则和股票的高效处理

#### 高级功能扩展
- 📅 **实时监控面板**: 市场概览和异动榜单
- 📅 **机器学习预测**: 基于历史数据的价格预测
- 📅 **投资组合管理**: 多股票组合风险管理
- 📅 **策略回测**: 预警策略历史回测分析
- 📅 **移动端适配**: 响应式设计优化

#### 系统优化
- 📅 **缓存策略**: Redis集成和多层缓存
- 📅 **数据库优化**: 索引优化和查询性能提升
- 📅 **负载均衡**: 多实例部署支持
- 📅 **监控告警**: 系统运行状态监控

### 🎯 近期重点任务

1. **自动化预警监控** (优先级: 高)
   - 实现定时任务调度器，每分钟自动运行预警检查
   - 替代当前的手动触发机制
   - 集成实时数据更新触发

2. **WebSocket实时通信激活** (优先级: 高)
   - 激活现有WebSocket框架
   - 实现前端实时数据接收
   - 完成实时预警推送

3. **异动检测算法实现** (优先级: 中)
   - 实现基于统计学的价格异动检测
   - 实现成交量异动检测算法
   - 集成技术指标分析

## 🏗️ 系统架构

### 整体架构设计
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端界面层     │    │   通信层        │    │   后端服务层     │
│                │    │                │    │                │
│ React 18       │◄──►│ WebSocket      │◄──►│ Flask API      │
│ Tailwind CSS   │    │ RESTful API    │    │ SQLAlchemy ORM │
│ Shadcn/UI      │    │ CORS Support   │    │ 业务逻辑层      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                      │
                       ┌─────────────────┐            │
                       │   数据源层       │◄───────────┘
                       │                │
                       │ Tushare Pro    │
                       │ Yahoo Finance  │
                       │ 本地缓存       │
                       └─────────────────┘
                                │
                       ┌─────────────────┐
                       │   数据存储层     │
                       │                │
                       │ MySQL 8.0+     │
                       │ 索引优化       │
                       │ 数据完整性     │
                       └─────────────────┘
```

### 核心模块

#### 1. 数据管理层
- **TushareService**: Tushare Pro API集成
- **StockDataService**: 数据同步和缓存管理
- **RealtimeDataManager**: 实时数据处理

#### 2. 业务逻辑层
- **AlertTriggerEngine**: 预警规则触发引擎
- **AnomalyDetectionEngine**: 异动检测算法 (开发中)
- **RealtimeMonitorService**: 实时监控服务 (开发中)

#### 3. 通信层
- **WebSocket服务**: 实时双向通信
- **RESTful API**: 标准HTTP接口
- **事件驱动**: 异步消息处理

#### 4. 前端组件
- **StockDashboard**: 主控制面板
- **WatchlistManager**: 自选股管理
- **AlertRules**: 预警规则配置
- **StockChart**: K线图表组件

## 🔌 API接口文档

### 📈 数据源配置API

**基础路径**: `/api/datasources`

#### 1. 获取所有数据源配置
```http
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

#### 2. 测试数据源连接
```http
POST /api/datasources/{id}/test
```

#### 3. 更新数据源配置
```http
PUT /api/datasources/{id}
Content-Type: application/json

{
  "config_data": {
    "token": "your-tushare-token-here"
  },
  "is_active": true,
  "is_default": true
}
```

### 📈 股票数据API

#### 1. 获取股票列表
```python
import requests

# 获取股票列表
response = requests.get('http://localhost:5000/api/stocks')
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

#### 2. 获取日线数据
```python
# 获取日线数据
response = requests.get('http://localhost:5000/api/stocks/000001.SZ/daily?limit=60')
```

**参数**:
- `start_date`: 开始日期 (YYYYMMDD格式，可选)
- `end_date`: 结束日期 (YYYYMMDD格式，可选)
- `limit`: 返回条数限制 (默认60)

#### 3. 获取实时行情
```python
# 获取实时行情
response = requests.post('http://localhost:5000/api/stocks/realtime', 
                        json={"symbols": ["000001.SZ", "600000.SH"]})
```

#### 4. 获取每日指标
```python
# 获取每日指标
response = requests.get('http://localhost:5000/api/stocks/000001.SZ/basic')
```

#### 5. 获取资金流向
```python
# 获取资金流向
response = requests.get('http://localhost:5000/api/stocks/000001.SZ/moneyflow')
```

### ⚠️ 预警规则API

#### 1. 获取预警规则列表
```python
# 获取预警规则
response = requests.get('http://localhost:5000/api/rules')
```

#### 2. 创建预警规则
```python
# 创建预警规则
rule_data = {
    "rule_name": "平安银行涨幅预警",
    "stock_code": "000001.SZ",
    "rule_type": "price_change_percent",
    "comparison_operator": "greater_than",
    "threshold_value": 5.0,
    "alert_level": "medium"
}
response = requests.post('http://localhost:5000/api/rules', json=rule_data)
```

**rule_type 可选值**:
- `price_change_percent`: 价格涨跌幅
- `price_threshold`: 价格阈值
- `volume_ratio`: 成交量比率
- `turnover_rate`: 换手率
- `market_value_change`: 市值变化

**comparison_operator 可选值**:
- `greater_than`: 大于
- `greater_than_or_equal`: 大于等于
- `less_than`: 小于
- `less_than_or_equal`: 小于等于
- `equal`: 等于
- `not_equal`: 不等于

**alert_level 级别**:
- `low`: 低级预警
- `medium`: 中级预警
- `high`: 高级预警
- `critical`: 严重预警

#### 3. 获取预警记录
```python
# 获取预警记录
response = requests.get('http://localhost:5000/api/alerts?limit=50')
```

#### 4. 触发预警检查
```python
# 手动触发预警检查
response = requests.post('http://localhost:5000/api/trigger/check')
```

### 🔌 WebSocket实时通信

#### 连接地址
```
ws://localhost:5000
```

#### 使用示例
```javascript
import io from 'socket.io-client';

const socket = io('http://localhost:5000');

// 连接成功
socket.on('connected', (data) => {
    console.log('连接成功:', data);
});

// 订阅市场数据
socket.emit('subscribe', {
    type: 'market_data',
    params: { symbol: '000001.SZ' }
});

// 接收实时数据
socket.on('market_data_update', (data) => {
    console.log('市场数据更新:', data);
});

// 接收预警信息
socket.on('risk_alert', (data) => {
    console.log('预警信息:', data);
});

// 取消订阅
socket.emit('unsubscribe', {
    type: 'market_data',
    params: { symbol: '000001.SZ' }
});
```

#### 订阅类型
- `market_data`: 市场数据
- `indicators`: 技术指标
- `signals`: 交易信号
- `monitor`: 实时监控
- `risk_alerts`: 风险预警
- `portfolio`: 投资组合

### 😨 错误处理

#### 错误响应格式
```json
{
  "success": false,
  "message": "错误描述信息"
}
```

#### 常见HTTP状态码
- `200`: 成功
- `400`: 请求参数错误
- `404`: 资源不存在
- `500`: 服务器内部错误

## 📁 项目目录结构

```
lm_quantitative_analysis/
├── app/                          # 后端应用
│   ├── api/                      # REST API接口
│   │   ├── stock_routes.py      # 股票数据API
│   │   ├── alert_routes.py      # 预警规则API
│   │   └── datasource_routes.py # 数据源配置API
│   ├── models/                   # 数据模型
│   │   ├── stock_basic.py       # 股票基础信息
│   │   ├── alert_rule.py        # 预警规则模型
│   │   └── risk_alert.py        # 预警记录模型
│   ├── services/                 # 业务服务
│   │   ├── tushare_service.py   # Tushare数据服务
│   │   ├── stock_data_service.py # 股票数据服务
│   │   └── alert_trigger_engine.py # 预警触发引擎
│   ├── websocket/               # WebSocket事件
│   │   └── websocket_events.py  # 实时通信事件
│   └── utils/                   # 工具函数
├── web/                         # 前端应用
│   ├── src/
│   │   ├── components/          # React组件
│   │   │   ├── ui/             # Shadcn UI组件
│   │   │   ├── StockDashboard.jsx
│   │   │   ├── WatchlistManager.jsx
│   │   │   ├── AlertRules.jsx
│   │   │   └── StockChart.jsx
│   │   ├── services/           # 前端服务
│   │   │   └── api.js          # API调用封装
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── 实时股票异动检测与智能预警系统核心功能设计/  # 项目文档
│   ├── 基于WebSocket的实时股票异动检测与智能预警系统.md
│   ├── 快速启动指南.md
│   └── API_ROUTES_SUMMARY.md
├── config.py                    # 配置文件
├── run.py                       # 启动脚本
├── requirements_minimal.txt     # 依赖清单
└── README.md                   # 项目说明
```

## 🔧 配置说明

### 数据库配置
在 `config.py` 中修改数据库连接：

```python
# MySQL配置
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = 'your_password'
DB_NAME = 'stock'
SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
```

### Tushare配置
```python
# 在前端界面配置，或通过环境变量
TUSHARE_TOKEN = "your_tushare_token_here"
```

### 日志配置
```python
LOG_LEVEL = 'INFO'
LOG_FILE = 'logs/stock_analysis.log'
```

## 📊 Tushare数据源说明

### 🎯 系统需要的核心数据

#### 1. 股票列表数据 ✅ 已实现
**接口**: `pro.stock_basic()`
**用途**: 获取所有A股上市公司基本信息
**权限**: 免费用户可用

**返回字段**:
- `ts_code`: 股票代码（如 000001.SZ）
- `symbol`: 股票代码（如 000001）
- `name`: 股票名称
- `area`: 地域
- `industry`: 行业
- `market`: 市场类型（主板/创业板/科创板）
- `list_date`: 上市日期

#### 2. 日线行情数据 ✅ 已实现
**接口**: `pro.daily()`
**用途**: 获取股票每日K线数据
**权限**: 免费用户可获取近3年日线数据

**返回字段**:
- `ts_code`: 股票代码
- `trade_date`: 交易日期
- `open/high/low/close`: 开盘价/最高价/最低价/收盘价
- `pre_close`: 昨收价
- `change`: 涨跌额
- `pct_chg`: 涨跌幅（%）
- `vol`: 成交量（手）
- `amount`: 成交额（千元）

#### 3. 每日指标数据 ✅ 已实现
**接口**: `pro.daily_basic()`
**用途**: 获取股票每日基本面指标
**权限**: 免费用户可用

**返回字段**:
- `turnover_rate`: 换手率（%）
- `volume_ratio`: 量比
- `pe`: 市盈率
- `pb`: 市净率
- `ps`: 市销率
- `dv_ratio`: 股息率
- `dv_ttm`: 股息率（TTM）
- `total_share`: 总股本（万股）
- `float_share`: 流通股本（万股）
- `free_share`: 自由流通股本（万股）
- `total_mv`: 总市值（万元）
- `circ_mv`: 流通市值（万元）

#### 4. 资金流向数据 ✅ 已实现
**接口**: `pro.moneyflow()`
**用途**: 获取沪深A股票资金流向数据
**权限**: 需要2000积分以上（免费用户可能无法访问）

**返回字段**:
- `buy_sm_vol`: 小单买入量（手）
- `buy_sm_amount`: 小单买入金额（万元）
- `sell_sm_vol`: 小单卖出量（手）
- `sell_sm_amount`: 小单卖出金额（万元）
- `buy_md_vol`: 中单买入量（手）
- `buy_md_amount`: 中单买入金额（万元）
- `sell_md_vol`: 中单卖出量（手）
- `sell_md_amount`: 中单卖出金额（万元）
- `buy_lg_vol`: 大单买入量（手）
- `buy_lg_amount`: 大单买入金额（万元）
- `sell_lg_vol`: 大单卖出量（手）
- `sell_lg_amount`: 大单卖出金额（万元）
- `buy_elg_vol`: 特大单买入量（手）
- `buy_elg_amount`: 特大单买入金额（万元）
- `sell_elg_vol`: 特大单卖出量（手）
- `sell_elg_amount`: 特大单卖出金额（万元）
- `net_mf_vol`: 净流入量（手）
- `net_mf_amount`: 净流入额（万元）

### 📋 权限说明

**免费用户（0积分）**:
- ✅ 股票基本信息
- ✅ 日线行情数据（近3年）
- ✅ 每日基本面指标
- ❌ 实时行情数据
- ❌ 分钟级数据
- ❌ 资金流向数据

**2120积分用户**:
- ✅ 所有免费功能
- ✅ 资金流向数据
- ✅ 更多历史数据
- ❌ 实时行情（需5000积分）
- ❌ 分钟级数据（需5000积分）

### 🔄 数据同步策略

1. **增量同步**: 只获取最新的交易日数据
2. **全量刷新**: 定期更新历史数据
3. **智能缓存**: 避免重复调用API
4. **错误重试**: 网络异常时自动重试
5. **限流控制**: 遵守API调用频率限制

## 🐛 故障排除

### 常见问题解决方案

#### 1. 数据库连接失败
**错误**: `Can't connect to MySQL server`

**解决方案**:
```bash
# 1. 确认MySQL服务已启动
sudo systemctl start mysql  # Linux
# 或在Windows服务中启动MySQL

# 2. 检查config.py中的数据库配置
# 确认用户名、密码、主机地址正确

# 3. 创建数据库
mysql -u root -p
CREATE DATABASE IF NOT EXISTS stock CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### 2. 前端无法访问后端API
**错误**: `CORS policy: No 'Access-Control-Allow-Origin'`

**解决方案**:
```bash
# 1. 确认后端已启动在5000端口
# 检查终端输出: * Running on http://localhost:5000

# 2. 确认前端运行在5173端口
# 检查终端输出: Local: http://localhost:5173/

# 3. 检查CORS配置
# 确认app/__init__.py中已配置CORS允许localhost:5173
```

#### 3. Tushare Token无效
**错误**: `Token未设置或无效`

**解决方案**:
```bash
# 1. 确认Token已正确复制（不要有空格或换行）
# 2. 在Tushare官网验证Token状态
# 3. 检查积分余额（某些接口需要积分）
# 4. 尝试在Tushare官网重新生成Token
```

#### 4. WebSocket连接失败
**错误**: `WebSocket connection failed`

**解决方案**:
```bash
# 1. 安装eventlet依赖
pip install eventlet

# 2. 确认使用python run.py启动（不是flask run）
python run.py

# 3. 检查防火墙设置
# 确认5000端口未被阻止

# 4. 检查浏览器控制台错误信息
```

#### 5. 导入错误
**错误**: `ModuleNotFoundError: No module named 'xxx'`

**解决方案**:
```bash
# 重新安装依赖
pip install -r requirements_minimal.txt

# 如果使用虚拟环境，确认已激活
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

#### 6. 数据同步失败
**错误**: `数据同步失败` 或 `API调用超限`

**解决方案**:
```bash
# 1. 检查网络连接
# 2. 验证Tushare Token有效性
# 3. 检查API调用频率（免费版有限制）
# 4. 等待一段时间后重试
# 5. 使用自选股功能减少API调用
```

### 🔍 调试技巧

#### 1. 查看日志
```bash
# 后端日志
tail -f logs/stock_analysis.log

# 前端控制台
# 打开浏览器开发者工具 -> Console
```

#### 2. 测试API连接
```bash
# 测试后端API
curl http://localhost:5000/api/datasources

# 测试数据源连接
curl -X POST http://localhost:5000/api/datasources/1/test
```

#### 3. 检查数据库
```sql
-- 连接数据库
mysql -u root -p stock

-- 查看表结构
SHOW TABLES;
DESCRIBE data_source_config;

-- 查看数据
SELECT * FROM data_source_config;
```

### 📞 获取帮助

如果问题仍未解决，请：
1. 查看项目GitHub Issues
2. 提供详细的错误信息和日志
3. 说明操作系统和Python版本
4. 描述重现问题的步骤

## 📝 更新日志

### v2.0.0 (2025-10-23) - 重构版本
- ✅ **架构重构**: 从多因子选股系统重构为实时股票异动检测与预警系统
- ✅ **前后端分离**: React + Flask架构，替代原有的模板系统
- ✅ **数据源集成**: 完整的Tushare Pro API集成，支持2120积分权限
- ✅ **预警系统**: 完整的预警规则和记录系统
- ✅ **现代化界面**: React 18 + Tailwind CSS + Shadcn/UI
- ✅ **API标准化**: RESTful API设计，完整的CRUD操作
- ✅ **数据库优化**: MySQL表结构优化和索引设计

### v1.0.0 (2024-06-01) - 初始版本
- 多因子选股系统基础功能
- 机器学习模型集成
- 组合优化和回测功能

## 📚 扩展阅读

如需更详细的技术设计文档，请参考：
- [系统设计文档](./实时股票异动检测与智能预警系统核心功能设计/基于WebSocket的实时股票异动检测与智能预警系统.md) - 完整的系统设计和实现细节

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进这个项目：

1. **Bug报告**: 请详细描述问题和复现步骤
2. **功能建议**: 请说明功能需求和使用场景
3. **代码贡献**: 请遵循项目的代码规范
4. **文档改进**: 帮助完善项目文档

## 📄 许可证

本项目采用 MIT 许可证。

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 提交Issue到项目仓库
- 发送邮件：2389934506@qq.com

---

**实时股票异动检测与智能预警系统** - 让股票监控更智能！ 🚀