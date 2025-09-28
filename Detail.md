# 多因子选股系统 - 二次开发详细文档

## 系统概述

这是一个基于Python Flask的量化投资系统，集成了因子计算、机器学习建模、股票选择、组合优化和回测验证等功能。

## 1. 项目结构分析

### 1.1 目录结构
```
lm_quantitative_analysis/
├── app/                          # 核心应用目录
│   ├── __init__.py              # Flask应用工厂
│   ├── extensions.py            # 扩展初始化
│   ├── api/                     # API接口层
│   │   ├── ml_factor_api.py     # 多因子API
│   │   ├── text2sql_api.py      # 文本转SQL API
│   │   ├── realtime_*.py        # 实时分析API
│   │   └── websocket_api.py     # WebSocket API
│   ├── models/                  # 数据模型层
│   ├── services/                # 业务逻辑层
│   │   ├── factor_engine.py     # 因子引擎
│   │   ├── ml_model_manager.py  # ML模型管理
│   │   ├── stock_scoring.py     # 股票评分
│   │   └── portfolio_optimizer.py # 组合优化
│   ├── routes/                  # 路由层
│   ├── templates/               # HTML模板
│   ├── static/                  # 静态资源
│   ├── utils/                   # 工具函数
│   └── websocket/               # WebSocket处理
├── config.py                    # 配置文件
├── requirements.txt             # 依赖包
├── run.py                      # 主启动文件
├── run_system.py               # 系统管理器
└── quick_start_fixed.py        # 快速启动脚本
```

## 2. 配置文件详解

### 2.1 主配置文件 (config.py)
```python
class Config:
    # 数据库配置
    DB_HOST = 'localhost'
    DB_USER = 'root'
    DB_PASSWORD = '20050204Ylm'  # 当前密码
    DB_NAME = 'stock'
    DB_CHARSET = 'utf8mb4'
    
    # SQLAlchemy配置
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}?charset={DB_CHARSET}"
    
    # Redis配置
    REDIS_HOST = 'localhost'
    REDIS_PORT = 6379
    REDIS_DB = 0
    
    # 日志配置
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'logs/stock_analysis.log'
    
    # 大模型配置
    LLM_CONFIG = {
        'provider': 'ollama',
        'ollama': {
            'base_url': 'http://localhost:11434',
            'model': 'qwen2.5-coder:latest'
        }
    }
```

### 2.2 环境配置
- **开发环境**: DevelopmentConfig (DEBUG=True)
- **生产环境**: ProductionConfig (DEBUG=False)

## 3. 核心后端代码分析

### 3.1 Flask应用初始化 (app/__init__.py)
```python
def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    db.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*", async_mode='eventlet')
    CORS(app)
    
    # 注册蓝图
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(ml_factor_bp)
    # ... 其他蓝图
```

### 3.2 核心业务模块

#### 3.2.1 因子引擎 (services/factor_engine.py)
- **功能**: 因子定义管理、因子值计算
- **内置因子**: 12个因子（动量、波动率、技术指标、基本面）
- **支持**: 自定义因子公式

#### 3.2.2 机器学习管理器 (services/ml_model_manager.py)
- **支持算法**: RandomForest, XGBoost, LightGBM
- **功能**: 模型训练、预测、评估

#### 3.2.3 股票评分引擎 (services/stock_scoring.py)
- **因子评分**: 基于因子值的股票排序
- **ML评分**: 基于机器学习模型的预测评分

#### 3.2.4 组合优化器 (services/portfolio_optimizer.py)
- **优化方法**: 等权重、均值-方差、风险平价
- **依赖**: CVXPY优化库

### 3.3 API接口层

#### 3.3.1 多因子API (api/ml_factor_api.py)
```python
# 主要端点
/api/ml-factor/factors/list          # 获取因子列表
/api/ml-factor/factors/calculate     # 计算因子值
/api/ml-factor/models/create         # 创建模型
/api/ml-factor/models/train          # 训练模型
/api/ml-factor/scoring/factor-based  # 因子选股
/api/ml-factor/portfolio/optimize    # 组合优化
```

#### 3.3.2 实时分析API
- `realtime_analysis.py`: 实时分析主接口
- `realtime_indicators.py`: 技术指标计算
- `realtime_signals.py`: 交易信号生成
- `realtime_monitor.py`: 实时监控
- `realtime_risk.py`: 风险管理
- `realtime_report.py`: 报告生成

### 3.4 数据模型层 (models/)
- 使用SQLAlchemy ORM
- 支持MySQL和SQLite数据库
- 主要表：股票基础信息、因子数据、模型配置等

## 4. 前端代码分析

### 4.1 模板结构 (templates/)
```
templates/
├── base.html                    # 基础模板
├── ml_factor/                   # 多因子系统页面
│   ├── dashboard.html           # 仪表盘
│   ├── factor_management.html   # 因子管理
│   ├── model_management.html    # 模型管理
│   ├── stock_selection.html     # 股票选择
│   ├── portfolio_optimization.html # 组合优化
│   └── backtest.html           # 回测验证
└── realtime_analysis/          # 实时分析页面
```

### 4.2 静态资源 (static/)
```
static/
├── css/
│   ├── financial-theme.css     # 金融主题样式
│   └── responsive-financial.css # 响应式样式
├── js/
│   ├── ml-factor.js           # 多因子系统JS
│   ├── charts.js              # 图表功能
│   └── websocket.js           # WebSocket客户端
└── images/                    # 图片资源
```

### 4.3 前端技术栈
- **CSS框架**: Bootstrap 5
- **图表库**: Chart.js, Plotly.js
- **WebSocket**: 实时数据推送
- **AJAX**: 异步数据交互

## 5. 外部组件依赖

### 5.1 必需组件

#### 5.1.1 数据库
```bash
# MySQL 5.7+ 或 8.x (推荐)
# 配置信息在config.py中
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = '20050204Ylm'
DB_NAME = 'stock'
```

#### 5.1.2 Python依赖包
```bash
# 核心框架
Flask>=2.3.0
SQLAlchemy>=2.0.0
pandas>=2.0.0
numpy>=1.24.0

# 机器学习
scikit-learn>=1.3.0
xgboost>=1.7.0
lightgbm>=4.0.0

# 组合优化
cvxpy>=1.4.0

# WebSocket支持
eventlet>=0.33.0
Flask-SocketIO>=5.3.0
```

### 5.2 可选组件

#### 5.2.1 Redis (缓存)
```bash
# Redis 5.0+
# 用于缓存股票数据和计算结果
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
```

#### 5.2.2 大语言模型 (可选)
```bash
# Ollama本地部署
# 用于自然语言查询功能
LLM_CONFIG = {
    'provider': 'ollama',
    'ollama': {
        'base_url': 'http://localhost:11434',
        'model': 'qwen2.5-coder:latest'
    }
}
```

### 5.3 数据源
- **股票数据**: 支持baostock、tushare等数据源
- **数据库文件**: stock.sql.zip (百度网盘下载)

## 6. 启动方式

### 6.1 快速启动 (推荐)
```bash
python quick_start_fixed.py
```

### 6.2 完整启动
```bash
python run_system.py
# 选择相应操作：
# 1. 检查系统依赖
# 2. 初始化数据库  
# 3. 启动Web服务器
```

### 6.3 直接启动
```bash
python start_web_server.py  # 简化启动
python run.py              # 完整功能启动
```

## 7. 二次开发指南

### 7.1 添加新因子
1. 在因子管理界面创建因子定义
2. 编写因子计算公式
3. 在`services/factor_engine.py`中注册

### 7.2 扩展机器学习模型
1. 在`services/ml_model_manager.py`中添加新算法
2. 实现训练和预测方法
3. 更新API接口

### 7.3 添加新的优化算法
1. 在`services/portfolio_optimizer.py`中实现
2. 添加约束条件支持
3. 更新前端界面

### 7.4 自定义API接口
1. 在`api/`目录下创建新的API文件
2. 在`app/__init__.py`中注册蓝图
3. 添加对应的前端页面

## 8. 部署建议

### 8.1 开发环境
- Python 3.8-3.11
- SQLite数据库（快速测试）
- 无需Redis（可选）

### 8.2 生产环境
- Python 3.8+
- MySQL 8.x数据库
- Redis缓存
- Nginx反向代理
- Gunicorn WSGI服务器

### 8.3 Docker部署（建议）
```dockerfile
# 可以创建Docker容器化部署
# 包含Python环境、MySQL、Redis等
```

## 9. 常见问题

### 9.1 依赖包问题
- 使用`requirements_minimal.txt`避免兼容性问题
- Python 3.12可能有包兼容性问题，推荐3.8-3.11

### 9.2 数据库连接
- 检查MySQL服务是否启动
- 确认数据库用户权限
- 验证连接字符串配置

### 9.3 端口冲突
- 默认端口5000，可在启动脚本中修改
- WebSocket使用5001端口

## 10. 扩展方向

### 10.1 功能扩展
- 增加更多技术指标
- 支持期货、期权等衍生品
- 添加风险管理模块
- 集成更多数据源

### 10.2 性能优化
- 使用Redis缓存
- 数据库查询优化
- 异步任务处理
- 分布式计算支持

### 10.3 用户体验
- 移动端适配
- 实时图表更新
- 个性化配置
- 多语言支持

---

**注意**: 本文档基于当前系统状态分析，实际开发时请结合具体需求进行调整。