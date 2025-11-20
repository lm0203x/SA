/**
 * 预警记录管理组件
 * 显示、管理和筛选预警记录
 */

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  AlertTriangle,
  CheckCircle,
  Clock,
  Search,
  Filter,
  RefreshCw,
  Eye,
  TrendingUp,
  TrendingDown
} from 'lucide-react';
import {
  getAlertRecords,
  resolveAlertRecord,
  createAlertRecord
} from '@/services/api';

export default function AlertRecords() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [filters, setFilters] = useState({
    ts_code: '',
    days: 7
  });

  // 预警类型映射
  const alertTypeMap = {
    'price_threshold': '价格阈值',
    'price_change_pct': '涨跌幅',
    'volume_ratio': '成交量比率',
    'turnover_rate': '换手率',
    'market_value': '市值变化',
    'technical_indicator': '技术指标',
    'money_flow': '资金流向'
  };

  // 预警级别配置
  const alertLevelConfig = {
    'low': { name: '低级', color: 'bg-blue-100 text-blue-800' },
    'medium': { name: '中级', color: 'bg-yellow-100 text-yellow-800' },
    'high': { name: '高级', color: 'bg-orange-100 text-orange-800' },
    'critical': { name: '严重', color: 'bg-red-100 text-red-800' }
  };

  // 加载预警记录
  const loadAlerts = async () => {
    setLoading(true);
    setError(null);

    try {
      console.log('开始加载预警记录...');

      // 构建查询参数
      const params = {
        ...filters
      };

      // 移除空值
      Object.keys(params).forEach(key => {
        if (!params[key]) {
          delete params[key];
        }
      });

      console.log('请求参数:', params);
      const response = await getAlertRecords(params);
      console.log('API响应:', response);

      if (response.success) {
        const records = response.data?.records || response.data || [];
        console.log('获取到预警记录:', records);
        console.log('记录数量:', records.length);
        setAlerts(records);
      } else {
        console.error('API返回失败:', response);
        setError(response.message || '获取预警记录失败');
      }
    } catch (err) {
      console.error('加载预警记录失败:', err);
      console.error('错误详情:', err);
      setError(err.message || '网络请求失败');
    } finally {
      setLoading(false);
    }
  };

  // 解决预警
  const handleResolve = async (alertId) => {
    try {
      const response = await resolveAlertRecord(alertId);

      if (response.success) {
        setSuccess('预警记录已解决');
        // 重新加载数据
        await loadAlerts();
        setTimeout(() => setSuccess(null), 3000);
      } else {
        setError(response.message || '解决预警失败');
      }
    } catch (err) {
      setError(err.message || '解决预警失败');
    }
  };

  // 筛选变化
  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  // 搜索
  const handleSearch = () => {
    loadAlerts();
  };

  // 刷新
  const handleRefresh = () => {
    loadAlerts();
  };

  // 格式化时间
  const formatTime = (timeString) => {
    if (!timeString) return '-';
    const date = new Date(timeString);
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // 获取预警级别Badge
  const getAlertLevelBadge = (level) => {
    const config = alertLevelConfig[level] || alertLevelConfig.medium;
    return <Badge className={config.color}>{config.name}</Badge>;
  };

  // 创建测试数据
  const createTestData = async () => {
    try {
      console.log('开始创建测试预警记录...');

      const testData = [
        {
          ts_code: '000001.SZ',
          alert_type: 'price_change_pct',
          alert_level: 'medium',
          alert_message: '【中级预警】平安银行(000001.SZ) 涨跌幅大于等于5.0%，当前值：6.5%',
          risk_value: 6.5,
          threshold_value: 5.0,
          current_price: 15.68
        },
        {
          ts_code: '600036.SH',
          alert_type: 'price_threshold',
          alert_level: 'high',
          alert_message: '【高级预警】招商银行(600036.SH) 价格突破阈值35.0，当前值：36.2',
          risk_value: 36.2,
          threshold_value: 35.0,
          current_price: 36.2
        },
        {
          ts_code: '000858.SZ',
          alert_type: 'volume_ratio',
          alert_level: 'low',
          alert_message: '【低级预警】五粮液(000858.SZ) 成交量异动，当前量比：2.3',
          risk_value: 2.3,
          threshold_value: 2.0,
          current_price: 168.5,
          is_resolved: true
        }
      ];

      for (let i = 0; i < testData.length; i++) {
        const data = testData[i];
        console.log(`创建第${i + 1}条测试记录:`, data);
        const response = await createAlertRecord(data);
        console.log(`第${i + 1}条记录创建结果:`, response);
      }

      console.log('测试数据创建完成，重新加载数据...');
      await loadAlerts();

    } catch (err) {
      console.error('创建测试数据失败:', err);
      setError('创建测试数据失败: ' + err.message);
    }
  };

  // 测试API连接
  const testAPIConnection = async () => {
    try {
      console.log('测试API连接...');
      const response = await fetch('http://localhost:5000/api/alerts');
      console.log('API状态:', response.status);

      if (response.ok) {
        const data = await response.json();
        console.log('API返回数据:', data);
        setSuccess('API连接正常');
        setTimeout(() => setSuccess(null), 3000);
      } else {
        console.error('API错误:', response.status, response.statusText);
        setError(`API错误: ${response.status} ${response.statusText}`);
      }
    } catch (err) {
      console.error('API连接失败:', err);
      setError(`API连接失败: ${err.message}`);
    }
  };

  // 初始化加载
  useEffect(() => {
    loadAlerts();
  }, []);

  // 计算统计信息
  const stats = {
    total: alerts.length,
    active: alerts.filter(a => a.is_active && !a.is_resolved).length,
    resolved: alerts.filter(a => a.is_resolved).length
  };

  return (
    <div className="space-y-6">
      {/* 错误和成功提示 */}
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {success && (
        <Alert className="bg-green-50 border-green-200">
          <AlertDescription className="text-green-800">{success}</AlertDescription>
        </Alert>
      )}

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">总预警数</p>
                <p className="text-2xl font-bold">{stats.total}</p>
              </div>
              <AlertTriangle className="h-8 w-8 text-gray-400" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">活跃预警</p>
                <p className="text-2xl font-bold text-yellow-600">{stats.active}</p>
              </div>
              <Clock className="h-8 w-8 text-yellow-400" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">已解决</p>
                <p className="text-2xl font-bold text-green-600">{stats.resolved}</p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-400" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">解决率</p>
                <p className="text-2xl font-bold text-blue-600">
                  {stats.total > 0 ? Math.round((stats.resolved / stats.total) * 100) : 0}%
                </p>
              </div>
              <div className="h-8 w-8 text-blue-400">📊</div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 筛选器 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span className="flex items-center">
              <Filter className="h-5 w-5 mr-2" />
              筛选条件
            </span>
            <Button variant="outline" size="sm" onClick={handleRefresh}>
              <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              刷新
            </Button>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="text-sm font-medium text-gray-700">股票代码</label>
              <Input
                placeholder="如: 000001.SZ"
                value={filters.ts_code}
                onChange={(e) => handleFilterChange('ts_code', e.target.value)}
              />
            </div>

            <div>
              <label className="text-sm font-medium text-gray-700">时间范围</label>
              <select
                value={filters.days}
                onChange={(e) => handleFilterChange('days', parseInt(e.target.value))}
                className="w-full p-2 border border-gray-300 rounded-md"
              >
                <option value={1}>最近1天</option>
                <option value={3}>最近3天</option>
                <option value={7}>最近7天</option>
                <option value={30}>最近30天</option>
              </select>
            </div>

            <div className="flex items-end">
              <Button onClick={handleSearch} className="w-full">
                <Search className="h-4 w-4 mr-2" />
                搜索
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 预警记录列表 */}
      <Card>
        <CardHeader>
          <CardTitle>预警记录</CardTitle>
          <CardDescription>
            显示 {stats.total} 条预警记录
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-12">
              <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4 text-blue-600" />
              <p className="text-gray-600">加载中...</p>
            </div>
          ) : alerts.length === 0 ? (
            <div className="text-center py-12">
              <AlertTriangle className="h-16 w-16 mx-auto text-gray-300 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">暂无预警记录</h3>
              <p className="text-gray-500">
                {filters.ts_code || filters.days !== 7 ? '没有符合筛选条件的记录' : '目前没有预警记录'}
              </p>
              <p className="text-sm text-gray-400 mt-2">
                请先在"预警规则"页面创建预警规则，然后触发预警检查
              </p>

              {/* 测试按钮 */}
              <div className="mt-6 space-y-3">
                <div className="flex gap-2 justify-center">
                  <Button
                    onClick={createTestData}
                    className="bg-blue-500 hover:bg-blue-600"
                  >
                    创建测试预警记录
                  </Button>
                  <Button
                    onClick={testAPIConnection}
                    variant="outline"
                  >
                    测试API连接
                  </Button>
                </div>
                <div className="text-xs text-gray-500">
                  创建测试数据或测试API连接来诊断问题
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              {alerts.map((alert) => (
                <div
                  key={alert.id}
                  className={`p-4 rounded-lg border transition-all ${
                    alert.is_resolved
                      ? 'border-gray-200 bg-gray-50'
                      : 'border-yellow-200 bg-yellow-50'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h4 className="font-medium">{alert.ts_code}</h4>
                        {getAlertLevelBadge(alert.alert_level)}
                        <Badge variant="outline">
                          {alertTypeMap[alert.alert_type] || alert.alert_type}
                        </Badge>
                        {alert.is_resolved ? (
                          <Badge className="bg-green-100 text-green-800">
                            <CheckCircle className="w-3 h-3 mr-1" />
                            已解决
                          </Badge>
                        ) : (
                          <Badge className="bg-yellow-100 text-yellow-800">
                            <Clock className="w-3 h-3 mr-1" />
                            活跃
                          </Badge>
                        )}
                      </div>

                      <div className="text-sm text-gray-600 space-y-1">
                        <p>{alert.alert_message}</p>

                        <div className="flex items-center gap-4 text-xs text-gray-500">
                          <span>风险值: {alert.risk_value || '-'}</span>
                          <span>阈值: {alert.threshold_value || '-'}</span>
                          <span>当前价格: ¥{alert.current_price || '-'}</span>
                        </div>

                        <p className="text-xs text-gray-400">
                          创建时间: {formatTime(alert.created_at)}
                          {alert.resolved_at && ` • 解决时间: ${formatTime(alert.resolved_at)}`}
                        </p>
                      </div>
                    </div>

                    <div className="flex gap-2">
                      {!alert.is_resolved && (
                        <Button
                          size="sm"
                          onClick={() => handleResolve(alert.id)}
                        >
                          <CheckCircle className="h-4 w-4 mr-1" />
                          解决
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}