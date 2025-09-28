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
    
    # 注册蓝图 - 多个功能模块
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(ml_factor_bp)           # 多因子API
    app.register_blueprint(text2sql_bp)            # 文本转SQL
    app.register_blueprint(realtime_analysis_bp)   # 实时分析
    app.register_blueprint(realtime_indicators_bp) # 实时指标
    app.register_blueprint(websocket_api_bp)       # WebSocket
    # ... 其他蓝图
```

### 3.2 核心业务模块详解

#### 3.2.1 因子引擎 (services/factor_engine.py)
```python
class FactorEngine:
    def __init__(self):
        self.factor_definitions = {}
        self.builtin_factors = {}
        self._init_builtin_factors()
        
    # 内置因子类型
    builtin_factors = {
        # 技术面因子
        'momentum_1d': self._momentum_factor,      # 1日动量
        'momentum_5d': self._momentum_factor,      # 5日动量  
        'momentum_20d': self._momentum_factor,     # 20日动量
        'volatility_20d': self._volatility_factor, # 20日波动率
        'volume_ratio_20d': self._volume_ratio_factor, # 成交量比率
        'price_to_ma20': self._price_to_ma_factor, # 价格相对均线
        
        # 基本面因子
        'pe_percentile': self._pe_percentile_factor,   # PE百分位
        'pb_percentile': self._pb_percentile_factor,   # PB百分位
        'roe_ttm': self._roe_factor,                   # ROE
        'revenue_growth': self._revenue_growth_factor, # 营收增长
        
        # 资金面因子
        'money_flow_strength': self._money_flow_strength_factor, # 资金流强度
        'big_order_ratio': self._big_order_ratio_factor,        # 大单比例
    }
```

#### 3.2.2 机器学习管理器 (services/ml_models.py)
```python
class MLModelManager:
    def __init__(self):
        self.models = {}      # 缓存已加载的模型
        self.scalers = {}     # 缓存特征缩放器
        
    # 支持的模型配置
    model_configs = {
        'random_forest': {
            'regressor': RandomForestRegressor,
            'classifier': RandomForestClassifier,
            'default_params': {
                'n_estimators': 100,
                'max_depth': 10,
                'min_samples_split': 5,
                'random_state': 42,
                'n_jobs': -1
            }
        },
        'xgboost': {
            'regressor': xgb.XGBRegressor,
            'classifier': xgb.XGBClassifier,
            'default_params': {
                'n_estimators': 100,
                'max_depth': 6,
                'learning_rate': 0.1,
                # ... 更多参数
            }
        },
        'lightgbm': {
            'regressor': lgb.LGBMRegressor,
            'classifier': lgb.LGBMClassifier,
            # ... 配置参数
        }
    }
```

#### 3.2.3 股票评分引擎 (services/stock_scoring.py)
```python
class StockScoringEngine:
    def __init__(self):
        self.scoring_methods = {
            'equal_weight': self._equal_weight_scoring,    # 等权重评分
            'factor_weight': self._factor_weight_scoring,  # 因子权重评分
            'ml_ensemble': self._ml_ensemble_scoring,      # ML集成评分
            'rank_ic': self._rank_ic_scoring               # 排序IC评分
        }
    
    def calculate_factor_scores(self, trade_date: str, factor_list: List[str]):
        """计算因子分数 - 使用Z-score标准化"""
        # 获取因子数据并透视
        factor_scores = factor_data.pivot_table(
            index='ts_code',
            columns='factor_id', 
            values='z_score',  # 使用标准化后的Z分数
            aggfunc='first'
        ).fillna(0)
        return factor_scores
```

#### 3.2.4 组合优化器 (services/portfolio_optimizer.py)
```python
class PortfolioOptimizer:
    def __init__(self):
        self.optimization_methods = {
            'mean_variance': self._mean_variance_optimization,      # 均值-方差优化
            'risk_parity': self._risk_parity_optimization,         # 风险平价
            'equal_weight': self._equal_weight_optimization,       # 等权重
            'factor_neutral': self._factor_neutral_optimization,   # 因子中性
            'black_litterman': self._black_litterman_optimization  # Black-Litterman
        }
    
    def optimize_portfolio(self, expected_returns, risk_model, method, constraints):
        """使用CVXPY进行组合优化"""
        # 支持多种约束条件：
        # - 权重上下限
        # - 行业中性
        # - 风险预算
        # - 换手率限制
```

### 3.3 API接口层详解

#### 3.3.1 多因子API (api/ml_factor_api.py)
```python
# 延迟初始化服务实例 - 避免循环导入
factor_engine = None
ml_manager = None
scoring_engine = None
portfolio_optimizer = None
backtest_engine = None

# 主要API端点
@ml_factor_bp.route('/factors/calculate', methods=['POST'])
def calculate_factors():
    """计算因子值"""
    data = request.get_json()
    # 调用因子引擎计算

@ml_factor_bp.route('/factors/list', methods=['GET'])
def get_factors_list():
    """获取因子列表"""
    
@ml_factor_bp.route('/models/create', methods=['POST'])
def create_model():
    """创建ML模型"""
    
@ml_factor_bp.route('/models/train', methods=['POST'])
def train_model():
    """训练模型"""
    
@ml_factor_bp.route('/scoring/factor-based', methods=['POST'])
def factor_based_scoring():
    """基于因子的股票评分"""
    
@ml_factor_bp.route('/portfolio/optimize', methods=['POST'])
def optimize_portfolio():
    """组合优化"""

# JSON序列化辅助函数
def convert_numpy_types(obj):
    """将numpy类型转换为Python原生类型"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    # ... 处理其他numpy类型
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
├── index.html                   # 主页
├── ml_factor/                   # 多因子系统页面
│   ├── index.html              # 因子管理主页
│   ├── analysis.html           # 因子分析
│   ├── models.html             # 模型管理
│   ├── scoring.html            # 股票评分
│   ├── portfolio.html          # 组合优化
│   └── backtest.html           # 回测验证
├── realtime_analysis/          # 实时分析页面
├── text2sql/                   # 文本转SQL页面
├── analysis.html               # 分析页面
├── backtest.html               # 回测页面
├── screen.html                 # 选股页面
└── stocks.html                 # 股票列表
```

### 4.2 前端核心功能分析

#### 4.2.1 多因子系统主页 (ml_factor/index.html)
```html
<!-- 因子统计卡片 -->
<div class="row mb-4">
    <div class="col-md-3">
        <div class="card text-center">
            <div class="card-body">
                <h3 class="text-primary" id="total-factors">--</h3>
                <p class="card-text">总因子数</p>
            </div>
        </div>
    </div>
    <!-- 内置因子、自定义因子、活跃因子统计 -->
</div>

<!-- 因子筛选功能 -->
<div class="row mb-4">
    <div class="col-12">
        <div class="card">
            <div class="card-body">
                <select class="form-select" id="factorTypeFilter">
                    <option value="technical">技术面</option>
                    <option value="fundamental">基本面</option>
                    <option value="money_flow">资金面</option>
                    <option value="chip">筹码面</option>
                </select>
            </div>
        </div>
    </div>
</div>
```

#### 4.2.2 JavaScript功能模块
```javascript
// 主要功能函数
function calculateAllFactors() {
    // 计算所有因子值
}

function createCustomFactor() {
    // 创建自定义因子
}

function loadFactorList() {
    // 加载因子列表
    fetch('/api/ml-factor/factors/list')
        .then(response => response.json())
        .then(data => {
            // 更新界面
        });
}
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

## 6. 启动方式（精简版）

### 6.1 快速启动（推荐新手）
```bash
python quick_start_fixed.py
```
- 自动安装最小依赖
- 创建SQLite数据库
- 启动简化Web服务
- 适合快速体验和测试

### 6.2 完整启动（推荐开发）
```bash
python run.py
```
- 完整功能支持
- WebSocket实时通信
- 支持MySQL数据库
- 适合生产环境和开发

**注意**: 其他启动脚本已被清理，只保留这两种方式。

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

## 10. 项目清理建议

### 10.1 冗余文件分析
当前项目包含大量重复和冗余文件：
- **启动脚本**: 8个重复的启动文件
- **演示文件**: 15个类似的演示脚本
- **配置文件**: 6个重复的配置文件
- **临时文件**: 大量调试和测试文件

### 10.2 自动清理
```bash
# 运行清理脚本
python clean_project.py
```

清理内容：
- 删除重复的启动脚本（保留2个）
- 删除冗余的演示文件（保留2个）
- 删除临时和调试文件
- 删除空目录和缓存文件
- 清理IDE配置文件

### 10.3 精简后结构
```
lm_quantitative_analysis/
├── app/                    # 核心应用
├── examples/               # 使用示例（2个）
├── docs/                   # 文档
├── images/                 # 截图
├── logs/                   # 日志
├── config.py              # 主配置
├── requirements.txt       # 依赖包
├── run.py                 # 主启动
├── quick_start_fixed.py   # 快速启动
└── README.md              # 说明文档
```

**清理效果**: 减少约60%的冗余文件，项目更加清晰简洁。

## 11. 扩展方向

### 11.1 功能扩展
- 增加更多技术指标
- 支持期货、期权等衍生品
- 添加风险管理模块
- 集成更多数据源

### 11.2 性能优化
- 使用Redis缓存
- 数据库查询优化
- 异步任务处理
- 分布式计算支持

### 11.3 用户体验
- 移动端适配
- 实时图表更新
- 个性化配置
- 多语言支持

---

**注意**: 建议先运行清理脚本精简项目，再进行二次开发。