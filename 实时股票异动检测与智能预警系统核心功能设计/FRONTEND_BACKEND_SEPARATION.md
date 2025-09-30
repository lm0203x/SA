# 前后端分离架构重构说明

## 📋 重构概述

本项目已从传统的Flask模板渲染架构重构为**完全前后端分离**架构：

- **前端**: React 18 + Vite + Tailwind CSS + Shadcn/UI (位于 `web/` 目录)
- **后端**: Flask + WebSocket + REST API (位于 `app/` 目录)

## 🔧 主要配置更改

### 1. Flask应用配置 (`app/__init__.py`)

#### ✅ 已完成的更改：

**CORS配置优化**
- ✅ 更新允许的域名列表，支持Vite开发服务器（端口5173）
- ✅ 添加完整的CORS头部支持
- ✅ 支持开发和生产环境的不同配置

**蓝图注册重构**
- ✅ 所有API蓝图使用 `/api` 前缀
- ✅ 旧的模板路由通过 `ENABLE_LEGACY_TEMPLATES` 开关控制
- ✅ 默认情况下，旧模板路由已禁用

### 2. 配置文件更新 (`config.py`)

#### 新增配置项：

```python
# 前后端分离配置
ENABLE_LEGACY_TEMPLATES = False  # 是否启用旧的HTML模板路由
```

**说明**：
- 设为 `False`：纯API模式，不加载HTML模板路由（推荐用于新架构）
- 设为 `True`：同时支持API和旧的HTML模板页面（用于过渡期或调试）

## 🚀 启动指南

### 前端启动 (Vite + React)

```bash
cd web
pnpm install  # 如果还没安装依赖
pnpm dev      # 启动开发服务器，默认端口 5173
```

访问地址: http://localhost:5173

### 后端启动 (Flask API)

```bash
# 1. 安装Tushare（如果还没安装）
pip install tushare

# 2. 初始化数据源配置表
python init_datasource_db.py

# 3. 启动Flask应用
python run.py
```

后端API地址: http://localhost:5000/api

## 📡 API接口列表

### 数据源管理 API

| 方法 | 路径 | 说明 |
|-----|------|------|
| GET | `/api/datasources` | 获取所有数据源配置 |
| POST | `/api/datasources` | 创建数据源配置 |
| PUT | `/api/datasources/<id>` | 更新数据源配置 |
| DELETE | `/api/datasources/<id>` | 删除数据源配置 |
| POST | `/api/datasources/<id>/test` | 测试数据源连接 |
| GET | `/api/datasources/active` | 获取激活的数据源 |

### 股票数据 API

| 方法 | 路径 | 说明 |
|-----|------|------|
| GET | `/api/stocks` | 获取股票列表 |
| POST | `/api/stocks/realtime` | 获取实时行情 |
| GET | `/api/stocks/<ts_code>/daily` | 获取日线数据 |

### 预警规则 API

| 方法 | 路径 | 说明 |
|-----|------|------|
| GET | `/api/rules` | 获取预警规则列表 |
| POST | `/api/rules` | 创建预警规则 |
| PUT | `/api/rules/<id>` | 更新预警规则 |
| DELETE | `/api/rules/<id>` | 删除预警规则 |
| GET | `/api/alerts` | 获取预警记录 |

### WebSocket 实时通信

连接地址: `ws://localhost:5000`

**事件列表**：
- `connect` - 连接成功
- `subscribe` - 订阅数据推送
- `unsubscribe` - 取消订阅
- `market_data_update` - 市场数据更新
- `risk_alert` - 风险预警

## 📂 目录结构说明

### 前端目录 (`web/`)
```
web/
├── src/
│   ├── components/       # React组件
│   │   ├── ui/          # Shadcn UI组件库
│   │   └── StockDashboard.jsx  # 主仪表板
│   ├── lib/             # 工具函数
│   ├── App.jsx          # 应用入口
│   └── main.jsx         # 主入口文件
├── index.html
├── package.json
└── vite.config.js       # Vite配置
```

### 后端目录 (`app/`)
```
app/
├── api/                 # REST API路由（新架构）
│   ├── datasource_routes.py  # 数据源配置API
│   ├── stock_routes.py        # 股票数据API
│   └── alert_routes.py        # 预警规则API
├── models/              # 数据库模型
│   └── data_source_config.py  # 数据源配置模型
├── services/            # 业务服务
│   └── tushare_service.py     # Tushare数据服务
├── websocket/           # WebSocket事件处理
├── routes/              # 旧的模板路由（已禁用）
├── templates/           # HTML模板（已不使用）
└── __init__.py          # 应用工厂（已更新）
```

## 🔄 迁移说明

### 旧架构 vs 新架构

| 特性 | 旧架构 | 新架构 |
|-----|--------|--------|
| 前端渲染 | Flask Jinja2模板 | React组件 |
| 数据获取 | 页面刷新 | REST API + WebSocket |
| 路由 | Flask路由 | React Router |
| 样式 | 传统CSS | Tailwind CSS |
| 组件库 | Bootstrap | Shadcn/UI |
| 开发服务器 | Flask内置 | Vite (端口5173) |

### 保留的旧功能

如果需要临时启用旧的HTML模板页面（用于调试或过渡）：

1. 修改 `config.py`:
```python
ENABLE_LEGACY_TEMPLATES = True
```

2. 重启Flask应用

3. 访问旧页面:
   - http://localhost:5000/ml-factor/
   - http://localhost:5000/realtime-analysis/
   - http://localhost:5000/

**注意**：旧模板页面不再维护，建议完全迁移到新的React前端。

## ⚠️ 注意事项

1. **端口配置**：
   - 前端开发服务器：5173 (Vite默认)
   - 后端API服务器：5000 (Flask默认)
   - WebSocket：5000 (与Flask共用端口)

2. **CORS配置**：
   - 开发环境已配置允许localhost:5173访问
   - 生产环境需要在 `app/__init__.py` 中添加生产域名

3. **数据库**：
   - 需要先运行 `init_datasource_db.py` 创建数据源配置表
   - 其他表结构保持不变

4. **依赖安装**：
   - 前端：`cd web && pnpm install`
   - 后端：`pip install tushare` (新增依赖)

## 🎯 下一步计划

- [ ] 完善数据源配置前端页面
- [ ] 实现实时股票数据推送
- [ ] 添加预警规则管理界面
- [ ] 集成更多数据源（Yahoo Finance等）
- [ ] 优化WebSocket连接稳定性

## 📞 技术支持

如有问题，请查看：
- Flask API文档：http://localhost:5000/api/docs (待添加)
- React应用：http://localhost:5173
- WebSocket测试：使用 `test_websocket.html` 进行调试
