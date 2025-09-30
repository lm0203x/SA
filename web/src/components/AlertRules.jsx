/**
 * 预警规则管理组件
 * 设置价格、涨跌幅等预警条件
 */

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Bell, Plus, Trash2, AlertTriangle, CheckCircle } from 'lucide-react';
import { 
  getWatchlist,
  getAlertRules,
  createAlertRule,
  deleteAlertRule,
  updateAlertRule
} from '@/services/api';

export default function AlertRules() {
  const [rules, setRules] = useState([]);
  const [watchlist, setWatchlist] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [showAddForm, setShowAddForm] = useState(false);
  
  // 新规则表单
  const [newRule, setNewRule] = useState({
    name: '',
    ts_code: '',
    rule_type: 'price',
    condition: 'greater',
    threshold: '',
    enabled: true
  });

  // 加载自选股列表
  const loadWatchlist = async () => {
    try {
      const response = await getWatchlist();
      if (response.success) {
        setWatchlist(response.data || []);
      }
    } catch (err) {
      console.error('获取自选股失败:', err);
    }
  };

  // 加载预警规则
  const loadRules = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await getAlertRules();
      
      if (response.success) {
        setRules(response.data || []);
      } else {
        setError(response.message || '获取预警规则失败');
      }
    } catch (err) {
      setError(err.message || '网络请求失败');
    } finally {
      setLoading(false);
    }
  };

  // 添加规则
  const handleAdd = async () => {
    if (!newRule.name || !newRule.ts_code || !newRule.threshold) {
      setError('请填写完整的规则信息');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      const response = await createAlertRule(newRule);
      
      if (response.success) {
        setSuccess('规则添加成功');
        setNewRule({
          name: '',
          ts_code: '',
          rule_type: 'price',
          condition: 'greater',
          threshold: '',
          enabled: true
        });
        setShowAddForm(false);
        await loadRules();
        setTimeout(() => setSuccess(null), 3000);
      } else {
        setError(response.message || '添加失败');
      }
    } catch (err) {
      setError(err.message || '添加失败');
    } finally {
      setLoading(false);
    }
  };

  // 删除规则
  const handleDelete = async (id, name) => {
    if (!confirm(`确认删除规则 "${name}" ?`)) return;
    
    try {
      const response = await deleteAlertRule(id);
      
      if (response.success) {
        setSuccess('规则删除成功');
        await loadRules();
        setTimeout(() => setSuccess(null), 3000);
      } else {
        setError(response.message || '删除失败');
      }
    } catch (err) {
      setError(err.message || '删除失败');
    }
  };

  // 切换规则启用状态
  const handleToggle = async (rule) => {
    try {
      const response = await updateAlertRule(rule.id, {
        ...rule,
        enabled: !rule.enabled
      });
      
      if (response.success) {
        setSuccess(rule.enabled ? '规则已禁用' : '规则已启用');
        await loadRules();
        setTimeout(() => setSuccess(null), 2000);
      } else {
        setError(response.message || '更新失败');
      }
    } catch (err) {
      setError(err.message || '更新失败');
    }
  };

  // 初始化
  useEffect(() => {
    loadWatchlist();
    loadRules();
  }, []);

  // 获取规则类型中文名
  const getRuleTypeText = (type) => {
    const types = {
      'price': '价格',
      'pct_chg': '涨跌幅',
      'volume': '成交量',
      'amount': '成交额'
    };
    return types[type] || type;
  };

  // 获取条件中文名
  const getConditionText = (condition) => {
    const conditions = {
      'greater': '大于',
      'less': '小于',
      'equal': '等于',
      'greater_equal': '大于等于',
      'less_equal': '小于等于'
    };
    return conditions[condition] || condition;
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

      {/* 规则列表 */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Bell className="h-5 w-5 text-blue-500" />
              预警规则
              {rules.length > 0 && (
                <Badge variant="secondary">{rules.length}</Badge>
              )}
            </CardTitle>
            <Button 
              size="sm"
              onClick={() => setShowAddForm(!showAddForm)}
            >
              <Plus className="h-4 w-4 mr-1" />
              添加规则
            </Button>
          </div>
        </CardHeader>
        
        <CardContent>
          {/* 添加规则表单 */}
          {showAddForm && (
            <div className="mb-6 p-4 border rounded-lg bg-gray-50 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>规则名称 *</Label>
                  <Input
                    placeholder="例如: 平安银行涨停提醒"
                    value={newRule.name}
                    onChange={(e) => setNewRule({...newRule, name: e.target.value})}
                  />
                </div>
                
                <div>
                  <Label>选择股票 *</Label>
                  <Select 
                    value={newRule.ts_code}
                    onValueChange={(value) => setNewRule({...newRule, ts_code: value})}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="选择自选股" />
                    </SelectTrigger>
                    <SelectContent>
                      {watchlist.map((stock) => (
                        <SelectItem key={stock.ts_code} value={stock.ts_code}>
                          {stock.name} ({stock.ts_code})
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <Label>监控指标 *</Label>
                  <Select 
                    value={newRule.rule_type}
                    onValueChange={(value) => setNewRule({...newRule, rule_type: value})}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="price">价格</SelectItem>
                      <SelectItem value="pct_chg">涨跌幅(%)</SelectItem>
                      <SelectItem value="volume">成交量</SelectItem>
                      <SelectItem value="amount">成交额</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label>条件 *</Label>
                  <Select 
                    value={newRule.condition}
                    onValueChange={(value) => setNewRule({...newRule, condition: value})}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="greater">大于</SelectItem>
                      <SelectItem value="less">小于</SelectItem>
                      <SelectItem value="greater_equal">大于等于</SelectItem>
                      <SelectItem value="less_equal">小于等于</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label>阈值 *</Label>
                  <Input
                    type="number"
                    step="0.01"
                    placeholder="例如: 15.00"
                    value={newRule.threshold}
                    onChange={(e) => setNewRule({...newRule, threshold: e.target.value})}
                  />
                </div>
              </div>

              <div className="flex gap-2">
                <Button 
                  size="sm" 
                  onClick={handleAdd}
                  disabled={loading}
                >
                  确认添加
                </Button>
                <Button 
                  size="sm" 
                  variant="outline"
                  onClick={() => {
                    setShowAddForm(false);
                    setNewRule({
                      name: '',
                      ts_code: '',
                      rule_type: 'price',
                      condition: 'greater',
                      threshold: '',
                      enabled: true
                    });
                  }}
                >
                  取消
                </Button>
              </div>

              <div className="text-sm text-gray-500">
                💡 示例：设置"平安银行价格大于15元"，当价格达到15元时触发预警
              </div>
            </div>
          )}

          {/* 规则列表 */}
          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
              <p className="text-sm text-gray-500">加载中...</p>
            </div>
          ) : rules.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <Bell className="h-12 w-12 mx-auto mb-3 text-gray-300" />
              <p className="text-sm">暂无预警规则</p>
              <p className="text-xs mt-1">点击"添加规则"创建第一个预警</p>
            </div>
          ) : (
            <div className="space-y-3">
              {rules.map((rule) => (
                <div
                  key={rule.id}
                  className={`p-4 rounded-lg border transition-all ${
                    rule.enabled 
                      ? 'border-blue-200 bg-blue-50' 
                      : 'border-gray-200 bg-gray-50'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h4 className="font-medium">{rule.name}</h4>
                        {rule.enabled ? (
                          <Badge className="bg-green-500">启用中</Badge>
                        ) : (
                          <Badge variant="secondary">已禁用</Badge>
                        )}
                      </div>
                      
                      <div className="text-sm text-gray-600 space-y-1">
                        <p>📊 股票: {rule.stock_name || rule.ts_code}</p>
                        <p>
                          📈 条件: {getRuleTypeText(rule.rule_type)} {getConditionText(rule.condition)} {rule.threshold}
                          {rule.rule_type === 'pct_chg' && '%'}
                        </p>
                        {rule.created_at && (
                          <p className="text-xs text-gray-400">
                            创建时间: {new Date(rule.created_at).toLocaleString('zh-CN')}
                          </p>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleToggle(rule)}
                      >
                        {rule.enabled ? (
                          <>
                            <CheckCircle className="h-4 w-4 mr-1" />
                            禁用
                          </>
                        ) : (
                          <>
                            <AlertTriangle className="h-4 w-4 mr-1" />
                            启用
                          </>
                        )}
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => handleDelete(rule.id, rule.name)}
                      >
                        <Trash2 className="h-4 w-4 text-red-500" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* 使用说明 */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">💡 使用说明</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-gray-600 space-y-2">
          <p>• <strong>价格预警</strong>: 监控股票价格达到设定值时触发提醒</p>
          <p>• <strong>涨跌幅预警</strong>: 监控当日涨跌幅超过设定百分比时提醒</p>
          <p>• <strong>成交量预警</strong>: 监控成交量异常放大或缩小时提醒</p>
          <p>• <strong>规则管理</strong>: 可以随时启用/禁用规则，无需删除重建</p>
        </CardContent>
      </Card>
    </div>
  );
}
