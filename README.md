# 多因子选股系统

一个功能完整的多因子选股系统，集成了因子计算、机器学习建模、股票选择、组合优化和回测验证等功能。

### 本系统目前项目未完成开发，仅限于学习交流，需要二次开发或定制化开发，请联系 39189996@qq.com

### 数据库下载地址：
-- 通过网盘分享的文件：stock.sql.zip
-- 链接: https://pan.baidu.com/s/1vOtkLP8pQEU8k0pGRaYwUw?pwd=q4mg 提取码: q4mg

![系统主界面](./images/1-2.png)

## 🌟 系统特色

### 核心功能
- **📊 因子管理**: 内置12个常用因子，支持自定义因子创建
- **🤖 机器学习**: 支持随机森林、XGBoost、LightGBM等算法
- **🎯 智能选股**: 基于因子和ML模型的多种选股策略
- **📈 组合优化**: 等权重、均值-方差、风险平价等优化方法
- **🔄 回测验证**: 完整的策略回测和多策略比较
- **📋 分析报告**: 行业分析、因子贡献度等深度分析

![系统功能概览](./images/1-3.png)

### 技术架构
- **后端**: Python 3.8+ / Flask / SQLAlchemy
- **数据处理**: Pandas / NumPy / Scikit-learn
- **机器学习**: XGBoost / LightGBM / CVXPY
- **前端**: Bootstrap 5 / JavaScript
- **数据库**: MySQL / SQLite

## 🚀 快速开始

### 1. 环境要求
- Python 3.8+
- MySQL 5.7或8.x

### 2. 安装依赖
```bash
# 克隆项目
git clone <repository-url>
cd quantitative_analysis

# 安装依赖
pip install -r requirements.txt
```

### 3. 启动系统
```bash
# 使用启动脚本
python run_system.py

# 或者直接运行（推荐）
python app.py
```
# 遇到以下问题
```
Traceback (most recent call last):
  File "/root/stock/run.py", line 9, in <module>
    app = create_app(os.getenv('FLASK_ENV', 'default'))

执行：pip install eventlet
```

![系统启动界面](./images/1-4.png)

### 4. 访问系统
- Web界面: http://localhost:5000
- API文档: http://localhost:5000/api

## 📖 使用指南

### 系统启动器
运行 `python run_system.py` 后，选择相应操作：

1. **检查系统依赖** - 验证Python版本和必需包
2. **初始化数据库** - 创建数据表和内置因子
3. **启动Web服务器** - 启动开发模式服务器
4. **启动Web服务器(生产模式)** - 启动生产模式服务器
5. **运行系统演示** - 执行完整功能演示
6. **显示系统信息** - 查看系统功能概览

![系统启动选项](./images/1-5.png)

### Web界面操作

#### 1. 仪表盘
- 查看系统状态和统计信息
- 快速访问主要功能

![仪表盘界面](./images/1-6.png)

#### 2. 因子管理
- 查看内置因子列表
- 创建自定义因子
- 计算因子值

![因子管理界面](./images/1-7.png)

![因子列表](./images/1-8.png)

#### 3. 模型管理
- 创建机器学习模型
- 训练模型
- 模型预测

![模型管理界面](./images/1-9.png)

![模型训练](./images/1-10.png)

#### 4. 股票选择
- 基于因子的选股
- 基于ML模型的选股
- 配置选股参数

![股票选择界面](./images/1-11.png)

![选股结果](./images/1-12.png)

#### 5. 组合优化
- 多种优化方法
- 约束条件设置
- 权重分配结果

![组合优化界面](./images/1-13.png)

![优化结果](./images/1-14.png)

#### 6. 分析报告
- 行业分析
- 因子贡献度分析

![分析报告界面](./images/1-15.png)

![行业分析](./images/1-16.png)

#### 7. 回测验证
- 单策略回测
- 多策略比较

![回测验证界面](./images/1-17.png)

![回测结果](./images/1-18.png)

![策略比较](./images/1-19.png)

### API接口使用

![API接口文档](./images/1-20.png)

#### 因子相关接口
```python
import requests

# 获取因子列表
response = requests.get('http://localhost:5000/api/ml-factor/factors/list')

# 创建自定义因子
factor_data = {
    "factor_id": "custom_momentum",
    "factor_name": "自定义动量因子",
    "factor_type": "momentum",
    "factor_formula": "close.pct_change(10)",
    "description": "10日价格变化率"
}
response = requests.post('http://localhost:5000/api/ml-factor/factors/custom', json=factor_data)

# 计算因子值
calc_data = {
    "trade_date": "2024-01-15",
    "factor_ids": ["momentum_1d", "momentum_5d"]
}
response = requests.post('http://localhost:5000/api/ml-factor/factors/calculate', json=calc_data)
```

#### 模型相关接口
```python
# 创建模型
model_data = {
    "model_id": "my_xgb_model",
    "model_name": "我的XGBoost模型",
    "model_type": "xgboost",
    "factor_list": ["momentum_1d", "momentum_5d", "volatility_20d"],
    "target_type": "return_5d"
}
response = requests.post('http://localhost:5000/api/ml-factor/models/create', json=model_data)

# 训练模型
train_data = {
    "model_id": "my_xgb_model",
    "start_date": "2023-01-01",
    "end_date": "2023-12-31"
}
response = requests.post('http://localhost:5000/api/ml-factor/models/train', json=train_data)
```

#### 选股相关接口
```python
# 基于因子选股
selection_data = {
    "trade_date": "2024-01-15",
    "factor_list": ["momentum_1d", "momentum_5d"],
    "method": "equal_weight",
    "top_n": 50
}
response = requests.post('http://localhost:5000/api/ml-factor/scoring/factor-based', json=selection_data)

# 基于ML模型选股
ml_selection_data = {
    "trade_date": "2024-01-15",
    "model_ids": ["my_xgb_model"],
    "top_n": 50
}
response = requests.post('http://localhost:5000/api/ml-factor/scoring/ml-based', json=ml_selection_data)
```

#### 组合优化接口
```python
# 组合优化
optimization_data = {
    "expected_returns": {"000001.SZ": 0.05, "000002.SZ": 0.03},
    "method": "mean_variance",
    "constraints": {
        "max_weight": 0.1,
        "risk_aversion": 1.0
    }
}
response = requests.post('http://localhost:5000/api/ml-factor/portfolio/optimize', json=optimization_data)
```

## 🏗️ 系统架构

![系统架构图](./images/1-21.png)

### 目录结构
```
stock_analysis/
├── app/                    # 应用主目录
│   ├── api/               # API接口
│   ├── models/            # 数据模型
│   ├── services/          # 业务服务
│   ├── routes/            # 路由
│   └── utils/             # 工具函数
├── templates/             # HTML模板
├── static/               # 静态文件
├── examples/             # 使用示例
├── config.py             # 配置文件
├── requirements.txt      # 依赖包
├── run_system.py         # 系统启动器
└── README.md            # 说明文档
```

### 核心模块

#### 1. 因子引擎 (FactorEngine)
- 因子定义管理
- 因子值计算
- 支持自定义公式

#### 2. 机器学习管理器 (MLModelManager)
- 模型创建和训练
- 预测和评估
- 支持多种算法

#### 3. 股票打分引擎 (StockScoringEngine)
- 因子打分
- ML模型打分
- 综合评分

#### 4. 组合优化器 (PortfolioOptimizer)
- 多种优化算法
- 约束条件支持
- 风险模型估计

#### 5. 回测引擎 (BacktestEngine)
- 策略回测
- 性能指标计算
- 多策略比较

## 📊 数据源接入架构详解

### 数据源层次结构
```
数据获取层
├── Tushare Pro API (付费，高质量)
│   ├── 日线数据 (免费)
│   ├── 分钟线数据 (需要权限)
│   └── 基本面数据 (部分免费)
├── Baostock API (免费，开源)
│   ├── 日线数据 ✅
│   ├── 5分钟线数据 ✅
│   └── 基本面数据 ✅
└── 本地数据库缓存
    ├── MySQL/SQLite存储
    └── Redis缓存加速
```

### 核心数据管理器

#### 1. RealtimeDataManager (实时数据管理器)
**文件位置**: `app/services/realtime_data_manager.py`

**主要功能**:
- 统一管理多个数据源
- 分钟级数据同步和聚合
- 数据质量监控
- 实时价格获取

**数据源切换逻辑**:
```python
def sync_minute_data(self, ts_code, start_date, end_date, period_type, use_baostock=False):
    if use_baostock:
        # 使用Baostock免费数据源
        with self.minute_sync_service as sync_service:
            result = sync_service.sync_single_stock_data(ts_code, period_type, start_date, end_date)
    else:
        # 使用Tushare Pro API (需要token和权限)
        return self._sync_minute_data_legacy(ts_code, start_date, end_date, period_type)
```

**数据处理流程**:
1. **数据获取** → 从API获取原始数据
2. **格式转换** → 统一数据格式 (`_convert_to_model_format`)
3. **数据验证** → 检查数据完整性
4. **批量入库** → 使用 `StockMinuteData.bulk_insert()`
5. **数据聚合** → 生成5min、15min、30min、60min周期数据

#### 2. MinuteDataSyncService (分钟数据同步服务)
**文件位置**: `app/services/minute_data_sync_service.py`

**Baostock集成逻辑**:
```python
class MinuteDataSyncService:
    PERIOD_TYPES = {
        '1min': '1',    # 注意：Baostock不支持1分钟，会转为5分钟
        '5min': '5', 
        '15min': '15',
        '30min': '30',
        '60min': '60'
    }
    
    def get_stock_minute_data_bs(self, stock_code, start_date, end_date, period_type):
        # 1. 登录Baostock
        bs.login()
        
        # 2. 转换股票代码格式 (000001.SZ → sz.000001)
        bs_code = self.convert_ts_code_to_bs_code(stock_code)
        
        # 3. 调用Baostock API
        rs = bs.query_history_k_data_plus(
            bs_code, 
            "date,time,code,open,high,low,close,volume,amount",
            start_date=start_date, 
            end_date=end_date,
            frequency=frequency,  # 分钟级别
            adjustflag="3"        # 不复权
        )
        
        # 4. 数据清洗和转换
        return self._process_baostock_data(rs)
```

#### 3. StockService (股票基础服务)
**文件位置**: `app/services/stock_service.py`

**缓存策略**:
```python
@cached(expire=1800, key_prefix='stock_basic')  # 30分钟缓存
def get_stock_list(industry=None, area=None, page=1, page_size=20):
    # 从数据库获取股票列表，支持行业、地区筛选

@cached(expire=300, key_prefix='daily_history')  # 5分钟缓存
def get_daily_history(ts_code, start_date=None, end_date=None, limit=60):
    # 获取日线历史数据，按日期倒序
```

### 数据模型设计

#### StockMinuteData (分钟数据模型)
```python
class StockMinuteData(db.Model):
    ts_code = db.Column(db.String(10))      # 股票代码
    datetime = db.Column(db.DateTime)       # 时间戳
    period_type = db.Column(db.String(10))  # 周期类型
    open = db.Column(db.Float)              # 开盘价
    high = db.Column(db.Float)              # 最高价
    low = db.Column(db.Float)               # 最低价
    close = db.Column(db.Float)             # 收盘价
    volume = db.Column(db.BigInteger)       # 成交量
    amount = db.Column(db.Float)            # 成交额
    pre_close = db.Column(db.Float)         # 前收盘价
    change = db.Column(db.Float)            # 涨跌额
    pct_chg = db.Column(db.Float)           # 涨跌幅%
```

### API接口层

#### 实时分析API (`/api/realtime-analysis/`)
```python
# 数据同步接口
POST /api/realtime-analysis/data/sync
{
    "ts_code": "000001.SZ",
    "start_date": "2025-09-21", 
    "end_date": "2025-09-28",
    "period_type": "5min",
    "use_baostock": true  # 选择数据源
}

# 批量同步接口
POST /api/realtime-analysis/data/sync-multiple
{
    "stock_list": ["000001.SZ", "000002.SZ"],
    "period_type": "5min",
    "batch_size": 10,
    "use_baostock": true
}

# 数据质量检查
GET /api/realtime-analysis/data/quality?ts_code=000001.SZ&period_type=5min

# 获取实时价格
GET /api/realtime-analysis/data/price?ts_code=000001.SZ
```

### 数据源配置

#### 1. Tushare Pro配置
```python
# 环境变量配置
TUSHARE_TOKEN = "your_tushare_token_here"

# 或在config.py中配置
class Config:
    TUSHARE_TOKEN = os.getenv('TUSHARE_TOKEN')
    
# 使用方式
data_manager = RealtimeDataManager(tushare_token="your_token")
result = data_manager.sync_minute_data("000001.SZ", use_baostock=False)
```

#### 2. Baostock配置 (推荐)
```python
# 无需token，直接使用
data_manager = RealtimeDataManager()
result = data_manager.sync_minute_data("000001.SZ", use_baostock=True)

# 批量同步示例
stock_list = ["000001.SZ", "000002.SZ", "600519.SH"]
result = data_manager.sync_multiple_stocks_data(
    stock_list=stock_list,
    period_type="5min",
    use_baostock=True,
    batch_size=10
)
```

### 数据源对比

| 特性 | Tushare Pro | Baostock | 本地数据库 |
|------|-------------|----------|------------|
| **费用** | 付费(分钟线需权限) | 完全免费 | 无额外费用 |
| **数据质量** | 高质量，实时性好 | 质量良好，有延迟 | 取决于数据源 |
| **访问限制** | 有积分和频率限制 | 无严格限制 | 无限制 |
| **支持周期** | 1min, 5min, 15min等 | 5min, 15min, 30min, 60min | 全支持 |
| **历史数据** | 丰富(2005年至今) | 较丰富(1990年至今) | 取决于同步情况 |
| **实时性** | 准实时(延迟<1分钟) | 日终数据(T+1) | 取决于更新频率 |
| **股票覆盖** | A股全覆盖 | A股全覆盖 | 取决于同步范围 |

### 推荐使用方案

#### 方案一：纯Baostock (推荐新手)
```python
# 优点：免费、稳定、数据质量好
# 缺点：无实时数据、只有日终数据

# 配置
USE_BAOSTOCK_ONLY = True

# 使用
result = data_manager.sync_minute_data("000001.SZ", use_baostock=True)
```

#### 方案二：Tushare Pro + Baostock (推荐生产)
```python
# 优点：数据质量最高、实时性好
# 缺点：需要付费、有访问限制

# 配置
TUSHARE_TOKEN = "your_premium_token"
FALLBACK_TO_BAOSTOCK = True

# 使用 (自动降级)
try:
    result = data_manager.sync_minute_data("000001.SZ", use_baostock=False)
except Exception:
    result = data_manager.sync_minute_data("000001.SZ", use_baostock=True)
```

#### 方案三：混合模式 (推荐开发)
```python
# 历史数据用Baostock，实时数据用Tushare
def hybrid_sync_strategy(ts_code, start_date, end_date):
    # 1. 历史数据用Baostock (免费、稳定)
    if start_date < "2025-01-01":
        return data_manager.sync_minute_data(ts_code, start_date, end_date, use_baostock=True)
    
    # 2. 近期数据用Tushare (实时性好)
    else:
        try:
            return data_manager.sync_minute_data(ts_code, start_date, end_date, use_baostock=False)
        except Exception:
            return data_manager.sync_minute_data(ts_code, start_date, end_date, use_baostock=True)
```

### 数据同步策略

#### 1. 增量同步
```python
def sync_incremental_data(self, ts_code):
    # 1. 获取数据库中最新数据时间
    latest_time = StockMinuteData.get_latest_time(ts_code)
    
    # 2. 从最新时间开始同步到当前时间
    start_date = latest_time.strftime('%Y-%m-%d') if latest_time else '2025-01-01'
    end_date = datetime.now().strftime('%Y-%m-%d')
    
    # 3. 调用数据源API
    return self.sync_minute_data(ts_code, start_date, end_date)
```

#### 2. 数据聚合策略
```python
def aggregate_data(self, ts_code, source_period='1min', target_period='5min'):
    # 1. 获取源周期数据
    source_data = StockMinuteData.get_data_by_time_range(ts_code, start_date, end_date, source_period)
    
    # 2. 使用pandas进行时间序列聚合
    df = pd.DataFrame([data.to_dict() for data in source_data])
    df.set_index('datetime', inplace=True)
    
    # 3. 按目标周期聚合 (OHLCV)
    agg_data = df.resample('5T').agg({
        'open': 'first',   # 开盘价取第一个
        'high': 'max',     # 最高价取最大值
        'low': 'min',      # 最低价取最小值
        'close': 'last',   # 收盘价取最后一个
        'volume': 'sum',   # 成交量求和
        'amount': 'sum'    # 成交额求和
    })
    
    # 4. 计算技术指标
    agg_data['pct_chg'] = (agg_data['close'] / agg_data['close'].shift(1) - 1) * 100
    
    # 5. 批量入库
    StockMinuteData.bulk_insert(aggregated_list)
```

### 错误处理和容错机制

#### 1. 数据源切换
```python
def _fetch_minute_data_from_source(self, ts_code, start_date, end_date):
    try:
        # 优先使用Tushare Pro
        if self.pro:
            df = self.pro.stk_mins(ts_code=ts_code, start_date=start_date, end_date=end_date)
            return df
    except Exception as e:
        logger.warning(f"Tushare获取失败: {e}, 切换到Baostock")
        
        # 降级到Baostock
        try:
            with self.minute_sync_service as sync_service:
                return sync_service.get_stock_minute_data_bs(ts_code, start_date, end_date)
        except Exception as e2:
            logger.error(f"Baostock也获取失败: {e2}")
            return pd.DataFrame()
```

#### 2. 数据验证
```python
def _convert_to_model_format(self, df, ts_code, period_type):
    data_list = []
    for _, row in df.iterrows():
        try:
            # 时间字段容错处理
            if 'trade_date' in row:
                trade_date = str(row['trade_date'])
            else:
                trade_date = datetime.now().strftime('%Y%m%d')
            
            # 价格字段容错处理
            open_price = row.get('open', 0)
            high_price = row.get('high', 0)
            low_price = row.get('low', 0)
            close_price = row.get('close', 0)
            
            # 数据有效性检查
            if close_price <= 0:
                continue
                
            data_list.append({...})
        except Exception as e:
            logger.warning(f"处理数据行失败: {e}, 跳过该行")
    
    return data_list
```

### 数据库设计优化

#### 索引策略
```python
# 复合索引设计 (stock_minute_data表)
__table_args__ = (
    Index('idx_ts_code_datetime_period', 'ts_code', 'datetime', 'period_type'),  # 主查询索引
    Index('idx_datetime_period', 'datetime', 'period_type'),                     # 时间范围查询
    Index('idx_ts_code_period', 'ts_code', 'period_type'),                       # 股票周期查询
)
```

#### 批量操作实现
```python
@classmethod
def bulk_insert(cls, data_list):
    """批量插入数据，提高性能"""
    if not data_list:
        return 0
    
    try:
        # 使用SQLAlchemy的bulk_insert_mappings提高性能
        db.session.bulk_insert_mappings(cls, data_list)
        db.session.commit()
        return len(data_list)
    except Exception as e:
        db.session.rollback()
        logger.error(f"批量插入失败: {e}")
        return 0

@classmethod 
def bulk_upsert(cls, data_list):
    """批量更新插入，处理重复数据"""
    success_count = 0
    for data in data_list:
        try:
            # 检查是否存在
            existing = cls.query.filter_by(
                ts_code=data['ts_code'],
                datetime=data['datetime'], 
                period_type=data['period_type']
            ).first()
            
            if existing:
                # 更新现有记录
                for key, value in data.items():
                    setattr(existing, key, value)
            else:
                # 插入新记录
                new_record = cls(**data)
                db.session.add(new_record)
            
            success_count += 1
        except Exception as e:
            logger.warning(f"处理数据失败: {e}")
    
    db.session.commit()
    return success_count
```

### 数据质量监控

#### 数据完整性检查
```python
@classmethod
def check_data_quality(cls, ts_code, period_type='1min', hours=24):
    """检查数据质量和完整性"""
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=hours)
    
    # 获取实际数据
    actual_data = cls.query.filter(
        cls.ts_code == ts_code,
        cls.period_type == period_type,
        cls.datetime >= start_time,
        cls.datetime <= end_time
    ).count()
    
    # 计算期望数据量 (交易时间: 9:30-11:30, 13:00-15:00)
    trading_minutes_per_day = 240  # 4小时 * 60分钟
    expected_data = trading_minutes_per_day * (hours / 24)
    
    if period_type == '5min':
        expected_data = expected_data / 5
    elif period_type == '15min':
        expected_data = expected_data / 15
    # ... 其他周期
    
    completeness = (actual_data / expected_data * 100) if expected_data > 0 else 0
    
    return {
        'ts_code': ts_code,
        'period_type': period_type,
        'time_range': f'{start_time} - {end_time}',
        'actual_count': actual_data,
        'expected_count': int(expected_data),
        'completeness': round(completeness, 2),
        'status': 'good' if completeness >= 90 else 'warning' if completeness >= 70 else 'poor'
    }
```

### 实时数据处理流程

#### 1. 数据接收和预处理
```python
def process_realtime_tick(self, tick_data):
    """处理实时tick数据"""
    # 1. 数据验证
    if not self._validate_tick_data(tick_data):
        return False
    
    # 2. 数据清洗
    cleaned_data = self._clean_tick_data(tick_data)
    
    # 3. 聚合到分钟K线
    minute_bar = self._aggregate_to_minute_bar(cleaned_data)
    
    # 4. 存储到数据库
    self._store_minute_bar(minute_bar)
    
    # 5. 触发实时计算
    self._trigger_realtime_calculation(minute_bar)
    
    return True

def _aggregate_to_minute_bar(self, tick_data):
    """将tick数据聚合为分钟K线"""
    current_minute = datetime.now().replace(second=0, microsecond=0)
    
    # 获取当前分钟的所有tick
    minute_ticks = self._get_minute_ticks(tick_data['ts_code'], current_minute)
    
    if not minute_ticks:
        return None
    
    # OHLCV聚合
    return {
        'ts_code': tick_data['ts_code'],
        'datetime': current_minute,
        'period_type': '1min',
        'open': minute_ticks[0]['price'],      # 第一个tick价格
        'high': max(t['price'] for t in minute_ticks),
        'low': min(t['price'] for t in minute_ticks),
        'close': minute_ticks[-1]['price'],    # 最后一个tick价格
        'volume': sum(t['volume'] for t in minute_ticks),
        'amount': sum(t['amount'] for t in minute_ticks)
    }
```

#### 2. 多周期数据生成
```python
def generate_multi_period_bars(self, minute_bar):
    """从1分钟K线生成多周期K线"""
    periods = ['5min', '15min', '30min', '60min']
    
    for period in periods:
        try:
            # 获取当前周期的时间窗口
            window_start = self._get_period_window_start(minute_bar['datetime'], period)
            
            # 获取窗口内的所有1分钟数据
            window_data = StockMinuteData.query.filter(
                StockMinuteData.ts_code == minute_bar['ts_code'],
                StockMinuteData.datetime >= window_start,
                StockMinuteData.datetime <= minute_bar['datetime'],
                StockMinuteData.period_type == '1min'
            ).order_by(StockMinuteData.datetime.asc()).all()
            
            if not window_data:
                continue
            
            # 聚合计算
            period_bar = {
                'ts_code': minute_bar['ts_code'],
                'datetime': window_start,
                'period_type': period,
                'open': window_data[0].open,
                'high': max(d.high for d in window_data),
                'low': min(d.low for d in window_data),
                'close': window_data[-1].close,
                'volume': sum(d.volume for d in window_data),
                'amount': sum(d.amount for d in window_data)
            }
            
            # 计算技术指标
            period_bar['pre_close'] = self._get_previous_close(minute_bar['ts_code'], window_start, period)
            period_bar['change'] = period_bar['close'] - period_bar['pre_close']
            period_bar['pct_chg'] = (period_bar['change'] / period_bar['pre_close'] * 100) if period_bar['pre_close'] > 0 else 0
            
            # 存储周期K线
            self._upsert_period_bar(period_bar)
            
        except Exception as e:
            logger.error(f"生成{period}周期数据失败: {e}")

def _get_period_window_start(self, current_time, period):
    """获取周期窗口开始时间"""
    if period == '5min':
        # 5分钟对齐: 9:30, 9:35, 9:40...
        minute = current_time.minute
        aligned_minute = (minute // 5) * 5
        return current_time.replace(minute=aligned_minute, second=0, microsecond=0)
    elif period == '15min':
        # 15分钟对齐: 9:30, 9:45, 10:00...
        minute = current_time.minute
        aligned_minute = (minute // 15) * 15
        return current_time.replace(minute=aligned_minute, second=0, microsecond=0)
    # ... 其他周期类似处理
```

### 性能优化策略

#### 1. 批量操作
- 使用 `bulk_insert()` 批量插入数据
- 分批处理大量股票数据 (batch_size=1000)
- 使用事务确保数据一致性

#### 2. 缓存机制
```python
# Redis缓存配置
CACHE_CONFIG = {
    'stock_basic': {'expire': 1800, 'key_prefix': 'stock_basic'},      # 30分钟
    'daily_history': {'expire': 300, 'key_prefix': 'daily_history'},   # 5分钟
    'realtime_price': {'expire': 60, 'key_prefix': 'realtime_price'},  # 1分钟
}

# 缓存装饰器使用
@cached(expire=300, key_prefix='minute_data')
def get_latest_minute_data(ts_code, period_type, limit):
    return StockMinuteData.get_latest_data(ts_code, period_type, limit)
```

#### 3. 异步处理
```python
# 使用Celery进行异步任务处理
@celery.task
def sync_stock_data_async(ts_code, start_date, end_date):
    """异步同步股票数据"""
    data_manager = RealtimeDataManager()
    return data_manager.sync_minute_data(ts_code, start_date, end_date)

@celery.task
def batch_sync_stocks_async(stock_list, period_type):
    """批量异步同步多只股票"""
    results = []
    for ts_code in stock_list:
        result = sync_stock_data_async.delay(ts_code, None, None)
        results.append(result)
    return results
```

#### 4. 数据库连接池优化
```python
# SQLAlchemy连接池配置
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 20,           # 连接池大小
    'pool_recycle': 3600,      # 连接回收时间
    'pool_pre_ping': True,     # 连接预检查
    'max_overflow': 30,        # 最大溢出连接数
    'pool_timeout': 30         # 获取连接超时时间
}
```

## 📊 内置因子

### 动量因子
- `momentum_1d`: 1日动量
- `momentum_5d`: 5日动量
- `momentum_20d`: 20日动量

### 波动率因子
- `volatility_20d`: 20日波动率

### 技术指标
- `rsi_14`: RSI相对强弱指标

### 成交量因子
- `turnover_rate`: 换手率

### 基本面因子
- `pe_ratio`: 市盈率
- `pb_ratio`: 市净率
- `roe`: 净资产收益率
- `debt_ratio`: 资产负债率
- `current_ratio`: 流动比率
- `gross_margin`: 毛利率

## 🔧 配置说明

### 数据库配置
在 `config.py` 中修改数据库连接：

```python
# SQLite (默认)
SQLALCHEMY_DATABASE_URI = 'sqlite:///stock_analysis.db'

# MySQL
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://user:password@localhost/stock_analysis'
```

### 日志配置
```python
LOG_LEVEL = 'INFO'
LOG_FILE = 'logs/app.log'
```

## 🧪 运行演示

系统提供了完整的功能演示：

```bash
# 运行完整演示
python examples/complete_system_example.py

# 或通过启动器运行
python run_system.py
# 选择 "5. 运行系统演示"
```

![系统演示](./images/1-22.png)

演示内容包括：
1. 因子管理演示
2. 模型管理演示
3. 股票选择演示
4. 组合优化演示
5. 集成选股和优化演示
6. 回测验证演示
7. 分析功能演示

## 📈 性能指标

系统支持的回测指标：
- 总收益率
- 年化收益率
- 年化波动率
- 夏普比率
- 最大回撤
- 胜率
- 卡尔玛比率

## 🛠️ 开发指南

### 添加自定义因子
1. 在因子管理界面创建因子定义
2. 编写因子计算公式
3. 测试因子计算结果

### 扩展机器学习模型
1. 在 `MLModelManager` 中添加新算法
2. 实现训练和预测方法
3. 更新API接口

### 添加优化算法
1. 在 `PortfolioOptimizer` 中实现新方法
2. 添加约束条件支持
3. 测试优化结果

## 🐛 故障排除

### ⚠️ 依赖包兼容性问题

如果遇到 `empyrical` 或 `TA-Lib` 安装失败，请使用修复版启动脚本：

```bash
# 使用修复版快速启动（推荐）
python quick_start_fixed.py

# 或使用最小化依赖
pip install -r requirements_minimal.txt
```

详细解决方案请查看：[安装指南](INSTALL_GUIDE.md)

### 常见问题

1. **依赖包安装失败**
   ```bash
   # 方案1：使用修复版启动脚本
   python quick_start_fixed.py
   
   # 方案2：手动安装核心依赖
   pip install Flask pandas numpy scikit-learn
   
   # 方案3：使用国内镜像
   pip install -r requirements_minimal.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
   ```

2. **Python版本兼容性**
   - 推荐使用 Python 3.8-3.11
   - Python 3.12 可能有部分包兼容性问题
   - 使用修复版脚本可以自动处理

3. **数据库连接失败**
   - 检查数据库配置
   - 确保数据库服务运行
   - 验证连接权限

4. **因子计算失败**
   - 检查数据是否存在
   - 验证因子公式语法
   - 查看日志错误信息

5. **模型训练失败**
   - 确保有足够的训练数据
   - 检查因子数据完整性
   - 调整模型参数

## 📝 更新日志

### v1.0.0 (2025-06-01)
- 完整的多因子选股系统
- 支持因子管理和计算
- 机器学习模型集成
- 组合优化功能
- 回测验证引擎
- Web界面和API接口

## 📄 许可证

本项目采用 MIT 许可证。

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 提交Issue
- 发送邮件：39189996@qq.com

---

**多因子选股系统** - 让量化投资更简单！ 
