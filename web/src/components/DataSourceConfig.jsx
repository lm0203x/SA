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
import { Database, Settings, TestTube, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';

const DataSourceConfig = () => {
  const [dataSources, setDataSources] = useState([]);
  const [activeSource, setActiveSource] = useState('yahoo');
  const [tushareConfig, setTushareConfig] = useState({
    token: '',
    enabled: false,
    test_status: 'untested'
  });
  const [yahooConfig, setYahooConfig] = useState({
    enabled: true,
    test_status: 'connected'
  });
  const [testResults, setTestResults] = useState({});

  useEffect(() => {
    loadDataSourceConfigs();
  }, []);

  const loadDataSourceConfigs = async () => {
    try {
      const response = await fetch('/api/data-sources/config');
      if (response.ok) {
        const config = await response.json();
        setTushareConfig(config.tushare || tushareConfig);
        setYahooConfig(config.yahoo || yahooConfig);
        setActiveSource(config.active_source || 'yahoo');
      }
    } catch (error) {
      console.error('Failed to load data source configs:', error);
    }
  };

  const saveDataSourceConfig = async (sourceType, config) => {
    try {
      const response = await fetch(`/api/data-sources/${sourceType}/config`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(config),
      });

      if (response.ok) {
        const result = await response.json();
        if (sourceType === 'tushare') {
          setTushareConfig(prev => ({ ...prev, ...result }));
        } else if (sourceType === 'yahoo') {
          setYahooConfig(prev => ({ ...prev, ...result }));
        }
        return true;
      }
      return false;
    } catch (error) {
      console.error(`Failed to save ${sourceType} config:`, error);
      return false;
    }
  };

  const testDataSource = async (sourceType) => {
    try {
      setTestResults(prev => ({ ...prev, [sourceType]: 'testing' }));
      
      const response = await fetch(`/api/data-sources/${sourceType}/test`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(
          sourceType === 'tushare' ? { token: tushareConfig.token } : {}
        ),
      });

      const result = await response.json();
      
      if (response.ok && result.success) {
        setTestResults(prev => ({ ...prev, [sourceType]: 'success' }));
        if (sourceType === 'tushare') {
          setTushareConfig(prev => ({ ...prev, test_status: 'connected' }));
        } else if (sourceType === 'yahoo') {
          setYahooConfig(prev => ({ ...prev, test_status: 'connected' }));
        }
      } else {
        setTestResults(prev => ({ ...prev, [sourceType]: 'failed' }));
        if (sourceType === 'tushare') {
          setTushareConfig(prev => ({ ...prev, test_status: 'failed' }));
        } else if (sourceType === 'yahoo') {
          setYahooConfig(prev => ({ ...prev, test_status: 'failed' }));
        }
      }
    } catch (error) {
      console.error(`Failed to test ${sourceType}:`, error);
      setTestResults(prev => ({ ...prev, [sourceType]: 'failed' }));
    }
  };

  const setActiveDataSource = async (sourceType) => {
    try {
      const response = await fetch('/api/data-sources/active', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ active_source: sourceType }),
      });

      if (response.ok) {
        setActiveSource(sourceType);
      }
    } catch (error) {
      console.error('Failed to set active data source:', error);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'connected':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-500" />;
      case 'testing':
        return <TestTube className="h-4 w-4 text-blue-500 animate-pulse" />;
      default:
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'connected':
        return <Badge variant="default" className="bg-green-100 text-green-800">已连接</Badge>;
      case 'failed':
        return <Badge variant="destructive">连接失败</Badge>;
      case 'testing':
        return <Badge variant="secondary">测试中...</Badge>;
      default:
        return <Badge variant="outline">未测试</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">数据源配置</h2>
          <p className="text-slate-600 mt-1">配置和管理股票数据源</p>
        </div>
        <Badge variant="outline" className="flex items-center space-x-2">
          <Database className="h-4 w-4" />
          <span>当前: {activeSource === 'tushare' ? 'Tushare' : 'Yahoo Finance'}</span>
        </Badge>
      </div>

      <Tabs defaultValue="tushare" className="space-y-6">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="tushare">Tushare Pro</TabsTrigger>
          <TabsTrigger value="yahoo">Yahoo Finance</TabsTrigger>
        </TabsList>

        {/* Tushare配置 */}
        <TabsContent value="tushare" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center space-x-2">
                    <Database className="h-5 w-5" />
                    <span>Tushare Pro 配置</span>
                  </CardTitle>
                  <CardDescription>
                    Tushare是专业的中文财经数据接口，提供A股、港股、美股等全球股票数据
                  </CardDescription>
                </div>
                <div className="flex items-center space-x-2">
                  {getStatusIcon(tushareConfig.test_status)}
                  {getStatusBadge(tushareConfig.test_status)}
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="tushare-token">API Token</Label>
                <Input
                  id="tushare-token"
                  type="password"
                  placeholder="请输入您的Tushare Pro Token"
                  value={tushareConfig.token}
                  onChange={(e) => setTushareConfig(prev => ({ ...prev, token: e.target.value }))}
                />
                <p className="text-sm text-slate-500">
                  请访问 <a href="https://tushare.pro" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">tushare.pro</a> 注册账号并获取Token
                </p>
              </div>

              <div className="flex items-center space-x-2">
                <Switch
                  id="tushare-enabled"
                  checked={tushareConfig.enabled}
                  onCheckedChange={(checked) => setTushareConfig(prev => ({ ...prev, enabled: checked }))}
                />
                <Label htmlFor="tushare-enabled">启用Tushare数据源</Label>
              </div>

              <div className="flex space-x-2">
                <Button
                  variant="outline"
                  onClick={() => testDataSource('tushare')}
                  disabled={!tushareConfig.token || testResults.tushare === 'testing'}
                >
                  <TestTube className="h-4 w-4 mr-2" />
                  测试连接
                </Button>
                <Button
                  onClick={() => saveDataSourceConfig('tushare', tushareConfig)}
                  disabled={!tushareConfig.token}
                >
                  保存配置
                </Button>
                <Button
                  variant="default"
                  onClick={() => setActiveDataSource('tushare')}
                  disabled={!tushareConfig.enabled || tushareConfig.test_status !== 'connected'}
                >
                  设为主数据源
                </Button>
              </div>

              {tushareConfig.test_status === 'failed' && (
                <Alert>
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription>
                    连接失败，请检查Token是否正确，或者网络连接是否正常。
                  </AlertDescription>
                </Alert>
              )}

              <div className="bg-slate-50 p-4 rounded-lg">
                <h4 className="font-medium mb-2">Tushare Pro 特性</h4>
                <ul className="text-sm text-slate-600 space-y-1">
                  <li>• 支持A股、港股、美股等全球市场</li>
                  <li>• 提供实时行情、历史数据、财务数据</li>
                  <li>• 高频数据更新，专业级数据质量</li>
                  <li>• 需要注册账号并获取积分</li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Yahoo Finance配置 */}
        <TabsContent value="yahoo" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center space-x-2">
                    <Database className="h-5 w-5" />
                    <span>Yahoo Finance 配置</span>
                  </CardTitle>
                  <CardDescription>
                    Yahoo Finance提供免费的全球股票数据，适合个人投资者使用
                  </CardDescription>
                </div>
                <div className="flex items-center space-x-2">
                  {getStatusIcon(yahooConfig.test_status)}
                  {getStatusBadge(yahooConfig.test_status)}
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center space-x-2">
                <Switch
                  id="yahoo-enabled"
                  checked={yahooConfig.enabled}
                  onCheckedChange={(checked) => setYahooConfig(prev => ({ ...prev, enabled: checked }))}
                />
                <Label htmlFor="yahoo-enabled">启用Yahoo Finance数据源</Label>
              </div>

              <div className="flex space-x-2">
                <Button
                  variant="outline"
                  onClick={() => testDataSource('yahoo')}
                  disabled={testResults.yahoo === 'testing'}
                >
                  <TestTube className="h-4 w-4 mr-2" />
                  测试连接
                </Button>
                <Button
                  onClick={() => saveDataSourceConfig('yahoo', yahooConfig)}
                >
                  保存配置
                </Button>
                <Button
                  variant="default"
                  onClick={() => setActiveDataSource('yahoo')}
                  disabled={!yahooConfig.enabled || yahooConfig.test_status !== 'connected'}
                >
                  设为主数据源
                </Button>
              </div>

              <div className="bg-slate-50 p-4 rounded-lg">
                <h4 className="font-medium mb-2">Yahoo Finance 特性</h4>
                <ul className="text-sm text-slate-600 space-y-1">
                  <li>• 免费使用，无需注册</li>
                  <li>• 支持全球主要股票市场</li>
                  <li>• 提供实时行情和历史数据</li>
                  <li>• 适合个人投资者和小型应用</li>
                  <li>• 可能存在请求频率限制</li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* 数据源状态总览 */}
      <Card>
        <CardHeader>
          <CardTitle>数据源状态总览</CardTitle>
          <CardDescription>查看所有配置的数据源状态</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div className="flex items-center space-x-3">
                <Database className="h-8 w-8 text-blue-500" />
                <div>
                  <h4 className="font-medium">Tushare Pro</h4>
                  <p className="text-sm text-slate-600">专业财经数据</p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                {activeSource === 'tushare' && <Badge variant="default">主数据源</Badge>}
                {getStatusBadge(tushareConfig.test_status)}
              </div>
            </div>

            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div className="flex items-center space-x-3">
                <Database className="h-8 w-8 text-purple-500" />
                <div>
                  <h4 className="font-medium">Yahoo Finance</h4>
                  <p className="text-sm text-slate-600">免费股票数据</p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                {activeSource === 'yahoo' && <Badge variant="default">主数据源</Badge>}
                {getStatusBadge(yahooConfig.test_status)}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default DataSourceConfig;

