import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { TrendingUp, TrendingDown, AlertTriangle, Activity, Plus, Settings, Database, Brain, Webhook } from 'lucide-react';
import DataSourceConfig from '@/components/DataSourceConfig';

// 模拟股票数据
const generateMockStockData = () => {
  const stocks = {
    'AAPL': { name: 'Apple Inc.', basePrice: 175.0 },
    'GOOGL': { name: 'Alphabet Inc.', basePrice: 140.0 },
    'MSFT': { name: 'Microsoft Corp.', basePrice: 380.0 },
    'TSLA': { name: 'Tesla Inc.', basePrice: 250.0 },
    'AMZN': { name: 'Amazon.com Inc.', basePrice: 145.0 }
  };

  const mockData = {};
  Object.entries(stocks).forEach(([symbol, info]) => {
    const changePercent = (Math.random() - 0.5) * 6; // -3% 到 +3%
    const currentPrice = info.basePrice * (1 + changePercent / 100);
    
    mockData[symbol] = {
      symbol,
      name: info.name,
      timestamp: new Date().toISOString(),
      price: Number(currentPrice.toFixed(2)),
      open: Number((info.basePrice * (0.98 + Math.random() * 0.04)).toFixed(2)),
      high: Number((currentPrice * (1 + Math.random() * 0.05)).toFixed(2)),
      low: Number((currentPrice * (0.95 + Math.random() * 0.05)).toFixed(2)),
      volume: Math.floor(Math.random() * 50000000) + 1000000,
      previous_close: info.basePrice,
      price_change: Number((currentPrice - info.basePrice).toFixed(2)),
      price_change_percent: Number(changePercent.toFixed(2)),
      market_cap: Math.floor(Math.random() * 2500000000000) + 500000000000,
      avg_volume: Math.floor(Math.random() * 80000000) + 20000000
    };
  });
  
  return mockData;
};

// 生成模拟预警数据
const generateMockAlerts = () => {
  const symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN'];
  const alertTypes = ['价格异动', '成交量异动', '涨幅预警', '跌幅预警'];
  const severities = ['low', 'medium', 'high'];
  
  return Array.from({ length: 8 }, (_, i) => {
    const symbol = symbols[Math.floor(Math.random() * symbols.length)];
    const alertType = alertTypes[Math.floor(Math.random() * alertTypes.length)];
    const severity = severities[Math.floor(Math.random() * severities.length)];
    const price = (100 + Math.random() * 300).toFixed(2);
    const changePercent = ((Math.random() - 0.5) * 10).toFixed(2);
    
    return {
      id: i + 1,
      symbol,
      message: `${alertType}: ${symbol} 当前价格 $${price}`,
      severity,
      timestamp: new Date(Date.now() - Math.random() * 3600000).toISOString(),
      price: Number(price),
      change_percent: Number(changePercent)
    };
  });
};

// 生成模拟预警规则
const generateMockRules = () => {
  return [
    {
      id: 1,
      name: 'AAPL价格预警',
      symbol: 'AAPL',
      rule_type: 'price_change',
      condition: 'greater_than',
      threshold: '5',
      enabled: true,
      created_at: '2024-01-15T10:30:00Z'
    },
    {
      id: 2,
      name: 'TSLA成交量异动',
      symbol: 'TSLA',
      rule_type: 'volume_spike',
      condition: 'greater_than',
      threshold: '200',
      enabled: true,
      created_at: '2024-01-14T15:20:00Z'
    },
    {
      id: 3,
      name: 'MSFT跌幅预警',
      symbol: 'MSFT',
      rule_type: 'price_change',
      condition: 'less_than',
      threshold: '-3',
      enabled: false,
      created_at: '2024-01-13T09:15:00Z'
    }
  ];
};

// 生成模拟图表数据
const generateChartData = (symbol) => {
  const basePrice = {
    'AAPL': 175,
    'GOOGL': 140,
    'MSFT': 380,
    'TSLA': 250,
    'AMZN': 145
  }[symbol] || 175;

  return Array.from({ length: 24 }, (_, i) => {
    const time = new Date();
    time.setHours(time.getHours() - (23 - i));
    
    const variation = (Math.random() - 0.5) * 0.1;
    const price = basePrice * (1 + variation);
    
    return {
      time: time.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
      price: Number(price.toFixed(2)),
      volume: Math.floor(Math.random() * 5000000) + 1000000
    };
  });
};

const StockDashboard = () => {
  const [stockData, setStockData] = useState({});
  const [alerts, setAlerts] = useState([]);
  const [alertRules, setAlertRules] = useState([]);
  const [connectionStatus, setConnectionStatus] = useState('connected');
  const [selectedStock, setSelectedStock] = useState('AAPL');
  const [chartData, setChartData] = useState([]);
  const [newRule, setNewRule] = useState({
    name: '',
    symbol: '',
    rule_type: 'price_change',
    condition: 'greater_than',
    threshold: ''
  });

  useEffect(() => {
    // 初始化模拟数据
    setStockData(generateMockStockData());
    setAlerts(generateMockAlerts());
    setAlertRules(generateMockRules());
    setChartData(generateChartData(selectedStock));
    
    // 模拟实时数据更新
    const interval = setInterval(() => {
      setStockData(prevData => {
        const newData = { ...prevData };
        Object.keys(newData).forEach(symbol => {
          const stock = newData[symbol];
          const priceChange = (Math.random() - 0.5) * 0.02; // -1% 到 +1%
          const newPrice = stock.price * (1 + priceChange);
          
          stock.price = Number(newPrice.toFixed(2));
          stock.price_change = Number((newPrice - stock.previous_close).toFixed(2));
          stock.price_change_percent = Number(((newPrice - stock.previous_close) / stock.previous_close * 100).toFixed(2));
          stock.timestamp = new Date().toISOString();
          stock.volume += Math.floor((Math.random() - 0.5) * 200000);
          
          // 更新最高最低价
          if (newPrice > stock.high) stock.high = newPrice;
          if (newPrice < stock.low) stock.low = newPrice;
        });
        return newData;
      });
      
      // 随机生成新预警
      if (Math.random() < 0.3) { // 30%概率生成新预警
        const symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN'];
        const alertTypes = ['价格异动', '成交量异动', '涨幅预警', '跌幅预警'];
        const severities = ['low', 'medium', 'high'];
        
        const symbol = symbols[Math.floor(Math.random() * symbols.length)];
        const alertType = alertTypes[Math.floor(Math.random() * alertTypes.length)];
        const severity = severities[Math.floor(Math.random() * severities.length)];
        const price = (100 + Math.random() * 300).toFixed(2);
        const changePercent = ((Math.random() - 0.5) * 10).toFixed(2);
        
        const newAlert = {
          id: Date.now(),
          symbol,
          message: `${alertType}: ${symbol} 当前价格 $${price}`,
          severity,
          timestamp: new Date().toISOString(),
          price: Number(price),
          change_percent: Number(changePercent)
        };
        
        setAlerts(prev => [newAlert, ...prev.slice(0, 9)]);
      }
    }, 5000); // 每5秒更新一次
    
    return () => clearInterval(interval);
  }, []);

  // 当选择的股票改变时，更新图表数据
  useEffect(() => {
    setChartData(generateChartData(selectedStock));
  }, [selectedStock]);

  const formatNumber = (num) => {
    if (num >= 1e9) return (num / 1e9).toFixed(2) + 'B';
    if (num >= 1e6) return (num / 1e6).toFixed(2) + 'M';
    if (num >= 1e3) return (num / 1e3).toFixed(2) + 'K';
    return num.toString();
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'high': return 'destructive';
      case 'medium': return 'default';
      case 'low': return 'secondary';
      default: return 'default';
    }
  };

  const getSeverityText = (severity) => {
    switch (severity) {
      case 'high': return '高';
      case 'medium': return '中';
      case 'low': return '低';
      default: return '未知';
    }
  };

  const addAlertRule = () => {
    if (newRule.name && newRule.symbol && newRule.threshold) {
      const rule = {
        id: Date.now(),
        ...newRule,
        enabled: true,
        created_at: new Date().toISOString()
      };
      setAlertRules(prev => [...prev, rule]);
      setNewRule({
        name: '',
        symbol: '',
        rule_type: 'price_change',
        condition: 'greater_than',
        threshold: ''
      });
    }
  };

  const toggleRule = (id) => {
    setAlertRules(prev => prev.map(rule => 
      rule.id === id ? { ...rule, enabled: !rule.enabled } : rule
    ));
  };

  const deleteRule = (id) => {
    setAlertRules(prev => prev.filter(rule => rule.id !== id));
  };

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-7xl mx-auto">
        {/* 头部 */}
        <div className="mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">股票异动检测与智能预警系统</h1>
              <p className="text-gray-600 mt-1">实时监控股票异动，智能预警系统助您把握投资机会</p>
            </div>
            <div className="flex items-center space-x-2">
              <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
                <Database className="w-3 h-3 mr-1" />
                API模式
              </Badge>
              <div className="flex items-center space-x-1">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm text-gray-600">前后端已连接</span>
              </div>
            </div>
          </div>
        </div>

        {/* 标签页导航 */}
        <Tabs defaultValue="datasource" className="w-full">
          <TabsList className="grid w-full grid-cols-6">
            <TabsTrigger value="datasource" className="flex items-center space-x-2">
              <Database className="w-4 h-4" />
              <span>数据源</span>
            </TabsTrigger>
            <TabsTrigger value="monitor" className="flex items-center space-x-2">
              <Activity className="w-4 h-4" />
              <span>实时监控</span>
            </TabsTrigger>
            <TabsTrigger value="alerts" className="flex items-center space-x-2">
              <AlertTriangle className="w-4 h-4" />
              <span>预警记录</span>
            </TabsTrigger>
            <TabsTrigger value="rules" className="flex items-center space-x-2">
              <Settings className="w-4 h-4" />
              <span>预警规则</span>
            </TabsTrigger>
            <TabsTrigger value="strategy" className="flex items-center space-x-2">
              <Brain className="w-4 h-4" />
              <span>策略配置</span>
            </TabsTrigger>
            <TabsTrigger value="webhook" className="flex items-center space-x-2">
              <Webhook className="w-4 h-4" />
              <span>Webhook</span>
            </TabsTrigger>
          </TabsList>

          {/* 数据源配置页面 */}
          <TabsContent value="datasource" className="space-y-6">
            <DataSourceConfig />
          </TabsContent>

          {/* 实时监控页面 */}
          <TabsContent value="monitor" className="space-y-6">
            {/* 股票卡片网格 */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
              {Object.values(stockData).map((stock) => (
                <Card key={stock.symbol} className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => setSelectedStock(stock.symbol)}>
                  <CardHeader className="pb-2">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-lg">{stock.symbol}</CardTitle>
                      {stock.price_change >= 0 ? (
                        <TrendingUp className="w-5 h-5 text-green-500" />
                      ) : (
                        <TrendingDown className="w-5 h-5 text-red-500" />
                      )}
                    </div>
                    <CardDescription className="text-xs">{stock.name}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <div className="text-2xl font-bold">{formatCurrency(stock.price)}</div>
                      <div className={`flex items-center space-x-1 ${stock.price_change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        <span className="text-sm font-medium">
                          {stock.price_change >= 0 ? '+' : ''}{formatCurrency(stock.price_change)}
                        </span>
                        <span className="text-sm">
                          ({stock.price_change_percent >= 0 ? '+' : ''}{stock.price_change_percent}%)
                        </span>
                      </div>
                      <div className="text-xs text-gray-500 space-y-1">
                        <div>成交量: {formatNumber(stock.volume)}</div>
                        <div>市值: {formatCurrency(stock.market_cap)}</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* 详细图表 */}
            {selectedStock && stockData[selectedStock] && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <span>{selectedStock} - {stockData[selectedStock].name}</span>
                    <Select value={selectedStock} onValueChange={setSelectedStock}>
                      <SelectTrigger className="w-32">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {Object.keys(stockData).map(symbol => (
                          <SelectItem key={symbol} value={symbol}>{symbol}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 mb-6">
                    <div className="space-y-1">
                      <div className="text-sm text-gray-500">开盘价</div>
                      <div className="text-lg font-semibold">{formatCurrency(stockData[selectedStock].open)}</div>
                    </div>
                    <div className="space-y-1">
                      <div className="text-sm text-gray-500">最高价</div>
                      <div className="text-lg font-semibold text-green-600">{formatCurrency(stockData[selectedStock].high)}</div>
                    </div>
                    <div className="space-y-1">
                      <div className="text-sm text-gray-500">最低价</div>
                      <div className="text-lg font-semibold text-red-600">{formatCurrency(stockData[selectedStock].low)}</div>
                    </div>
                    <div className="space-y-1">
                      <div className="text-sm text-gray-500">平均成交量</div>
                      <div className="text-lg font-semibold">{formatNumber(stockData[selectedStock].avg_volume)}</div>
                    </div>
                  </div>
                  
                  <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="time" />
                        <YAxis domain={['dataMin - 5', 'dataMax + 5']} />
                        <Tooltip 
                          formatter={(value, name) => [formatCurrency(value), '价格']}
                          labelFormatter={(label) => `时间: ${label}`}
                        />
                        <Line 
                          type="monotone" 
                          dataKey="price" 
                          stroke="#2563eb" 
                          strokeWidth={2}
                          dot={false}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* 预警记录页面 */}
          <TabsContent value="alerts" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>预警记录</CardTitle>
                <CardDescription>查看最近的股票预警信息</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {alerts.map((alert) => (
                    <Alert key={alert.id} className="border-l-4 border-l-blue-500">
                      <AlertTriangle className="h-4 w-4" />
                      <div className="flex items-center justify-between w-full">
                        <div className="flex-1">
                          <AlertDescription className="font-medium">
                            {alert.message}
                          </AlertDescription>
                          <div className="text-sm text-gray-500 mt-1">
                            {new Date(alert.timestamp).toLocaleString('zh-CN')}
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge variant={getSeverityColor(alert.severity)}>
                            {getSeverityText(alert.severity)}
                          </Badge>
                          <Badge variant="outline">{alert.symbol}</Badge>
                        </div>
                      </div>
                    </Alert>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* 预警规则页面 */}
          <TabsContent value="rules" className="space-y-6">
            {/* 添加新规则 */}
            <Card>
              <CardHeader>
                <CardTitle>创建预警规则</CardTitle>
                <CardDescription>设置个性化的股票预警条件</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="rule-name">规则名称</Label>
                    <Input
                      id="rule-name"
                      placeholder="输入规则名称"
                      value={newRule.name}
                      onChange={(e) => setNewRule(prev => ({ ...prev, name: e.target.value }))}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="rule-symbol">股票代码</Label>
                    <Select value={newRule.symbol} onValueChange={(value) => setNewRule(prev => ({ ...prev, symbol: value }))}>
                      <SelectTrigger>
                        <SelectValue placeholder="选择股票" />
                      </SelectTrigger>
                      <SelectContent>
                        {Object.keys(stockData).map(symbol => (
                          <SelectItem key={symbol} value={symbol}>{symbol}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="rule-type">规则类型</Label>
                    <Select value={newRule.rule_type} onValueChange={(value) => setNewRule(prev => ({ ...prev, rule_type: value }))}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="price_change">价格变动</SelectItem>
                        <SelectItem value="volume_spike">成交量异动</SelectItem>
                        <SelectItem value="price_threshold">价格阈值</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="rule-condition">条件</Label>
                    <Select value={newRule.condition} onValueChange={(value) => setNewRule(prev => ({ ...prev, condition: value }))}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="greater_than">大于</SelectItem>
                        <SelectItem value="less_than">小于</SelectItem>
                        <SelectItem value="equal_to">等于</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="rule-threshold">阈值</Label>
                    <div className="flex space-x-2">
                      <Input
                        id="rule-threshold"
                        placeholder="输入阈值"
                        value={newRule.threshold}
                        onChange={(e) => setNewRule(prev => ({ ...prev, threshold: e.target.value }))}
                      />
                      <Button onClick={addAlertRule}>
                        <Plus className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* 现有规则列表 */}
            <Card>
              <CardHeader>
                <CardTitle>预警规则列表</CardTitle>
                <CardDescription>管理您的预警规则</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {alertRules.map((rule) => (
                    <div key={rule.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex-1">
                        <div className="font-medium">{rule.name}</div>
                        <div className="text-sm text-gray-500">
                          {rule.symbol} - {rule.rule_type === 'price_change' ? '价格变动' : rule.rule_type === 'volume_spike' ? '成交量异动' : '价格阈值'} 
                          {rule.condition === 'greater_than' ? ' 大于 ' : rule.condition === 'less_than' ? ' 小于 ' : ' 等于 '}
                          {rule.threshold}
                          {rule.rule_type === 'price_change' ? '%' : ''}
                        </div>
                        <div className="text-xs text-gray-400">
                          创建时间: {new Date(rule.created_at).toLocaleString('zh-CN')}
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge variant={rule.enabled ? 'default' : 'secondary'}>
                          {rule.enabled ? '启用' : '禁用'}
                        </Badge>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => toggleRule(rule.id)}
                        >
                          {rule.enabled ? '禁用' : '启用'}
                        </Button>
                        <Button
                          variant="destructive"
                          size="sm"
                          onClick={() => deleteRule(rule.id)}
                        >
                          删除
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>


          {/* 策略配置页面 */}
          <TabsContent value="strategy" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>策略配置</CardTitle>
                <CardDescription>配置智能分析策略和风险控制参数</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-12">
                  <Brain className="w-16 h-16 mx-auto text-gray-400 mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">策略配置功能开发中...</h3>
                  <p className="text-gray-500 mb-4">
                    将支持多种量化分析策略和智能预警算法
                  </p>
                  <div className="space-y-2 text-sm text-gray-600">
                    <div>• 价格动量策略</div>
                    <div>• 均值回归策略</div>
                    <div>• 成交量分析策略</div>
                    <div>• 技术指标策略</div>
                    <div>• 风险控制参数</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Webhook配置页面 */}
          <TabsContent value="webhook" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Webhook通知配置</CardTitle>
                <CardDescription>配置预警消息的推送渠道和格式</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-12">
                  <Webhook className="w-16 h-16 mx-auto text-gray-400 mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Webhook配置功能开发中...</h3>
                  <p className="text-gray-500 mb-4">
                    将支持多种通知渠道和自定义消息格式
                  </p>
                  <div className="space-y-2 text-sm text-gray-600">
                    <div>• 钉钉机器人通知</div>
                    <div>• 企业微信通知</div>
                    <div>• Slack通知</div>
                    <div>• Telegram通知</div>
                    <div>• 邮件通知</div>
                    <div>• 自定义Webhook</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default StockDashboard;

