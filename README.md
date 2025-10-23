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

### 1. 环境要求
- Python 3.11+
- Node.js 18+
- MySQL 8.0+
- Tushare Pro账号 (免费)

### 2. 后端安装
```bash
# 安装Python依赖
pip install -r requirements_minimal.txt

# 初始化数据库
python init_datasource_db.py

# 启动后端服务
python run.py
```

### 3. 前端安装
```bash
# 进入前端目录
cd web

# 安装依赖
pnpm install

# 启动开发服务器
pnpm dev
```

### 4. 配置数据源
1. 访问 http://localhost:5173
2. 进入"数据源"标签页
3. 输入Tushare Token
4. 测试连接并激活

### 5. 访问系统
- **前端界面**: http://localhost:5173
- **后端API**: http://localhost:5000/api
- **WebSocket**: ws://localhost:5000

## 📖 使用指南

### 主要功能模块

#### 1. 股票行情监控
- **自选股管理**: 添加/删除关注的股票
- **K线图展示**: 实时价格走势图表
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

### API接口使用

详细的API文档请参考：[API_ROUTES_SUMMARY.md](./实时股票异动检测与智能预警系统核心功能设计/API_ROUTES_SUMMARY.md)

#### 股票数据接口
```python
import requests

# 获取股票列表
response = requests.get('http://localhost:5000/api/stocks')

# 获取日线数据
response = requests.get('http://localhost:5000/api/stocks/000001.SZ/daily?limit=60')

# 获取每日指标
response = requests.get('http://localhost:5000/api/stocks/000001.SZ/basic')

# 获取资金流向
response = requests.get('http://localhost:5000/api/stocks/000001.SZ/moneyflow')
```

#### 预警规则接口
```python
# 获取预警规则
response = requests.get('http://localhost:5000/api/rules')

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

# 触发预警检查
response = requests.post('http://localhost:5000/api/trigger/check')
```

#### WebSocket连接
```javascript
import io from 'socket.io-client';

const socket = io('http://localhost:5000');

// 连接成功
socket.on('connected', (data) => {
    console.log('连接成功:', data);
});

// 接收实时数据
socket.on('market_data_update', (data) => {
    console.log('市场数据更新:', data);
});

// 接收预警信息
socket.on('risk_alert', (data) => {
    console.log('预警信息:', data);
});
```

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

## 🐛 故障排除

### 常见问题

1. **数据库连接失败**
   ```bash
   # 确认MySQL服务已启动
   # 检查config.py中的数据库配置
   # 创建数据库
   CREATE DATABASE IF NOT EXISTS stock CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

2. **前端无法访问后端API**
   ```bash
   # 确认后端已启动在5000端口
   # 确认前端运行在5173端口
   # 检查CORS配置
   ```

3. **Tushare Token无效**
   ```bash
   # 确认Token已正确复制
   # 在Tushare官网验证Token状态
   # 检查积分余额
   ```

4. **WebSocket连接失败**
   ```bash
   # 安装eventlet: pip install eventlet
   # 使用python run.py启动（不是flask run）
   # 检查防火墙设置
   ```

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

## 📚 相关文档

- [快速启动指南](./实时股票异动检测与智能预警系统核心功能设计/快速启动指南.md)
- [API接口文档](./实时股票异动检测与智能预警系统核心功能设计/API_ROUTES_SUMMARY.md)
- [系统设计文档](./实时股票异动检测与智能预警系统核心功能设计/基于WebSocket的实时股票异动检测与智能预警系统.md)
- [前后端分离架构](./实时股票异动检测与智能预警系统核心功能设计/FRONTEND_BACKEND_SEPARATION.md)

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
- 发送邮件：39189996@qq.com

---

**实时股票异动检测与智能预警系统** - 让股票监控更智能！ 🚀