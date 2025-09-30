import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Switch } from '@/components/ui/switch';
import { Textarea } from '@/components/ui/textarea';
import { Slider } from '@/components/ui/slider';
import { 
  TrendingUp, 
  TrendingDown, 
  BarChart3, 
  Target, 
  Brain, 
  Settings, 
  Plus, 
  Edit, 
  Trash2,
  Play,
  Pause,
  AlertTriangle,
  CheckCircle
} from 'lucide-react';

const StrategyConfig = () => {
  const [strategies, setStrategies] = useState([]);
  const [activeStrategies, setActiveStrategies] = useState([]);
  const [newStrategy, setNewStrategy] = useState({
    name: '',
    type: 'price_momentum',
    description: '',
    parameters: {},
    risk_level: 'medium',
    enabled: true
  });

  const strategyTypes = [
    {
      id: 'price_momentum',
      name: '价格动量策略',
      description: '基于价格趋势和动量指标进行分析',
      icon: TrendingUp,
      parameters: [
        { key: 'lookback_period', name: '回看周期', type: 'number', default: 20, min: 5, max: 100 },
        { key: 'momentum_threshold', name: '动量阈值', type: 'number', default: 0.05, min: 0.01, max: 0.2, step: 0.01 },
        { key: 'volume_factor', name: '成交量因子', type: 'number', default: 1.5, min: 1.0, max: 3.0, step: 0.1 }
      ]
    },
    {
      id: 'mean_reversion',
      name: '均值回归策略',
      description: '识别价格偏离均值的机会',
      icon: Target,
      parameters: [
        { key: 'ma_period', name: '均线周期', type: 'number', default: 20, min: 5, max: 200 },
        { key: 'deviation_threshold', name: '偏离阈值', type: 'number', default: 2.0, min: 1.0, max: 4.0, step: 0.1 },
        { key: 'reversion_strength', name: '回归强度', type: 'number', default: 0.7, min: 0.1, max: 1.0, step: 0.1 }
      ]
    },
    {
      id: 'volume_analysis',
      name: '成交量分析策略',
      description: '基于成交量异动进行分析',
      icon: BarChart3,
      parameters: [
        { key: 'volume_ma_period', name: '成交量均线周期', type: 'number', default: 10, min: 5, max: 50 },
        { key: 'volume_spike_threshold', name: '成交量激增阈值', type: 'number', default: 2.0, min: 1.5, max: 5.0, step: 0.1 },
        { key: 'price_volume_correlation', name: '价量相关性', type: 'number', default: 0.6, min: 0.1, max: 1.0, step: 0.1 }
      ]
    },
    {
      id: 'technical_indicators',
      name: '技术指标策略',
      description: '综合多种技术指标进行分析',
      icon: Brain,
      parameters: [
        { key: 'rsi_period', name: 'RSI周期', type: 'number', default: 14, min: 5, max: 30 },
        { key: 'rsi_overbought', name: 'RSI超买线', type: 'number', default: 70, min: 60, max: 90 },
        { key: 'rsi_oversold', name: 'RSI超卖线', type: 'number', default: 30, min: 10, max: 40 },
        { key: 'macd_fast', name: 'MACD快线', type: 'number', default: 12, min: 5, max: 20 },
        { key: 'macd_slow', name: 'MACD慢线', type: 'number', default: 26, min: 20, max: 50 }
      ]
    }
  ];

  const riskLevels = [
    { value: 'low', label: '低风险', color: 'bg-green-100 text-green-800' },
    { value: 'medium', label: '中等风险', color: 'bg-yellow-100 text-yellow-800' },
    { value: 'high', label: '高风险', color: 'bg-red-100 text-red-800' }
  ];

  useEffect(() => {
    loadStrategies();
    loadActiveStrategies();
  }, []);

  const loadStrategies = async () => {
    try {
      const response = await fetch('/api/strategies');
      if (response.ok) {
        const data = await response.json();
        setStrategies(data);
      }
    } catch (error) {
      console.error('Failed to load strategies:', error);
    }
  };

  const loadActiveStrategies = async () => {
    try {
      const response = await fetch('/api/strategies/active');
      if (response.ok) {
        const data = await response.json();
        setActiveStrategies(data);
      }
    } catch (error) {
      console.error('Failed to load active strategies:', error);
    }
  };

  const createStrategy = async () => {
    if (!newStrategy.name || !newStrategy.type) {
      alert('请填写策略名称和类型');
      return;
    }

    try {
      const response = await fetch('/api/strategies', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newStrategy),
      });

      if (response.ok) {
        const strategy = await response.json();
        setStrategies(prev => [...prev, strategy]);
        setNewStrategy({
          name: '',
          type: 'price_momentum',
          description: '',
          parameters: {},
          risk_level: 'medium',
          enabled: true
        });
      }
    } catch (error) {
      console.error('Failed to create strategy:', error);
    }
  };

  const toggleStrategy = async (strategyId, enabled) => {
    try {
      const response = await fetch(`/api/strategies/${strategyId}/toggle`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ enabled }),
      });

      if (response.ok) {
        setStrategies(prev => 
          prev.map(s => s.id === strategyId ? { ...s, enabled } : s)
        );
        loadActiveStrategies();
      }
    } catch (error) {
      console.error('Failed to toggle strategy:', error);
    }
  };

  const deleteStrategy = async (strategyId) => {
    if (!confirm('确定要删除这个策略吗？')) return;

    try {
      const response = await fetch(`/api/strategies/${strategyId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        setStrategies(prev => prev.filter(s => s.id !== strategyId));
        loadActiveStrategies();
      }
    } catch (error) {
      console.error('Failed to delete strategy:', error);
    }
  };

  const getStrategyTypeInfo = (type) => {
    return strategyTypes.find(st => st.id === type) || strategyTypes[0];
  };

  const getRiskLevelInfo = (level) => {
    return riskLevels.find(rl => rl.value === level) || riskLevels[1];
  };

  const updateStrategyParameter = (key, value) => {
    setNewStrategy(prev => ({
      ...prev,
      parameters: {
        ...prev.parameters,
        [key]: value
      }
    }));
  };

  const renderParameterInput = (param) => {
    const value = newStrategy.parameters[param.key] || param.default;
    
    if (param.type === 'number') {
      if (param.min !== undefined && param.max !== undefined) {
        return (
          <div className="space-y-2">
            <div className="flex justify-between">
              <Label>{param.name}</Label>
              <span className="text-sm text-slate-600">{value}</span>
            </div>
            <Slider
              value={[value]}
              onValueChange={([newValue]) => updateStrategyParameter(param.key, newValue)}
              min={param.min}
              max={param.max}
              step={param.step || 1}
              className="w-full"
            />
          </div>
        );
      } else {
        return (
          <div className="space-y-2">
            <Label>{param.name}</Label>
            <Input
              type="number"
              value={value}
              onChange={(e) => updateStrategyParameter(param.key, parseFloat(e.target.value))}
              min={param.min}
              max={param.max}
              step={param.step || 1}
            />
          </div>
        );
      }
    }
    
    return (
      <div className="space-y-2">
        <Label>{param.name}</Label>
        <Input
          value={value}
          onChange={(e) => updateStrategyParameter(param.key, e.target.value)}
        />
      </div>
    );
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">策略配置</h2>
          <p className="text-slate-600 mt-1">配置和管理股票分析策略</p>
        </div>
        <Badge variant="outline" className="flex items-center space-x-2">
          <Brain className="h-4 w-4" />
          <span>活跃策略: {activeStrategies.length}</span>
        </Badge>
      </div>

      <Tabs defaultValue="create" className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="create">创建策略</TabsTrigger>
          <TabsTrigger value="manage">管理策略</TabsTrigger>
          <TabsTrigger value="performance">策略表现</TabsTrigger>
        </TabsList>

        {/* 创建策略 */}
        <TabsContent value="create" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Plus className="h-5 w-5" />
                <span>创建新策略</span>
              </CardTitle>
              <CardDescription>
                选择策略类型并配置参数，创建个性化的分析策略
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* 基本信息 */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="strategy-name">策略名称</Label>
                  <Input
                    id="strategy-name"
                    placeholder="例如：我的动量策略"
                    value={newStrategy.name}
                    onChange={(e) => setNewStrategy(prev => ({ ...prev, name: e.target.value }))}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="strategy-type">策略类型</Label>
                  <Select 
                    value={newStrategy.type} 
                    onValueChange={(value) => setNewStrategy(prev => ({ ...prev, type: value, parameters: {} }))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {strategyTypes.map((type) => {
                        const Icon = type.icon;
                        return (
                          <SelectItem key={type.id} value={type.id}>
                            <div className="flex items-center space-x-2">
                              <Icon className="h-4 w-4" />
                              <span>{type.name}</span>
                            </div>
                          </SelectItem>
                        );
                      })}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="strategy-description">策略描述</Label>
                <Textarea
                  id="strategy-description"
                  placeholder="描述这个策略的目标和特点..."
                  value={newStrategy.description}
                  onChange={(e) => setNewStrategy(prev => ({ ...prev, description: e.target.value }))}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="risk-level">风险等级</Label>
                <Select 
                  value={newStrategy.risk_level} 
                  onValueChange={(value) => setNewStrategy(prev => ({ ...prev, risk_level: value }))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {riskLevels.map((level) => (
                      <SelectItem key={level.value} value={level.value}>
                        <Badge className={level.color}>{level.label}</Badge>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* 策略参数 */}
              {newStrategy.type && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">策略参数</CardTitle>
                    <CardDescription>
                      {getStrategyTypeInfo(newStrategy.type).description}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {getStrategyTypeInfo(newStrategy.type).parameters.map((param) => (
                      <div key={param.key}>
                        {renderParameterInput(param)}
                      </div>
                    ))}
                  </CardContent>
                </Card>
              )}

              <div className="flex items-center space-x-2">
                <Switch
                  id="strategy-enabled"
                  checked={newStrategy.enabled}
                  onCheckedChange={(checked) => setNewStrategy(prev => ({ ...prev, enabled: checked }))}
                />
                <Label htmlFor="strategy-enabled">创建后立即启用</Label>
              </div>

              <Button onClick={createStrategy} className="w-full">
                <Plus className="h-4 w-4 mr-2" />
                创建策略
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 管理策略 */}
        <TabsContent value="manage" className="space-y-4">
          {strategies.map((strategy) => {
            const typeInfo = getStrategyTypeInfo(strategy.type);
            const riskInfo = getRiskLevelInfo(strategy.risk_level);
            const Icon = typeInfo.icon;

            return (
              <Card key={strategy.id}>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className="p-2 bg-slate-100 rounded-lg">
                        <Icon className="h-6 w-6 text-slate-600" />
                      </div>
                      <div>
                        <h3 className="font-medium">{strategy.name}</h3>
                        <p className="text-sm text-slate-600">{typeInfo.name}</p>
                        <p className="text-xs text-slate-500 mt-1">{strategy.description}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge className={riskInfo.color}>{riskInfo.label}</Badge>
                      <Badge variant={strategy.enabled ? 'default' : 'secondary'}>
                        {strategy.enabled ? '运行中' : '已停用'}
                      </Badge>
                      <div className="flex items-center space-x-1">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => toggleStrategy(strategy.id, !strategy.enabled)}
                        >
                          {strategy.enabled ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                        </Button>
                        <Button variant="outline" size="sm">
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => deleteStrategy(strategy.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}

          {strategies.length === 0 && (
            <Card>
              <CardContent className="text-center py-12">
                <Brain className="h-12 w-12 text-slate-400 mx-auto mb-4" />
                <p className="text-slate-600">暂无策略</p>
                <p className="text-sm text-slate-500 mt-2">创建第一个分析策略开始使用</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* 策略表现 */}
        <TabsContent value="performance" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>策略表现统计</CardTitle>
              <CardDescription>查看各策略的历史表现和统计数据</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-green-600">85%</div>
                  <div className="text-sm text-slate-600">平均准确率</div>
                </div>
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">1,234</div>
                  <div className="text-sm text-slate-600">总预警次数</div>
                </div>
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-purple-600">67%</div>
                  <div className="text-sm text-slate-600">有效预警率</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>策略详细表现</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {activeStrategies.map((strategy, index) => (
                  <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                    <div>
                      <h4 className="font-medium">{strategy.name}</h4>
                      <p className="text-sm text-slate-600">{strategy.type}</p>
                    </div>
                    <div className="flex items-center space-x-4">
                      <div className="text-center">
                        <div className="text-lg font-bold text-green-600">92%</div>
                        <div className="text-xs text-slate-500">准确率</div>
                      </div>
                      <div className="text-center">
                        <div className="text-lg font-bold text-blue-600">156</div>
                        <div className="text-xs text-slate-500">预警数</div>
                      </div>
                      <Badge variant="default">
                        <CheckCircle className="h-3 w-3 mr-1" />
                        优秀
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default StrategyConfig;

