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
import { Bell, Plus, Trash2, AlertTriangle, CheckCircle, Play, BarChart3 } from 'lucide-react';
import { 
  getWatchlist,
  getAlertRules,
  createAlertRule,
  deleteAlertRule,
  updateAlertRule,
  triggerAlertCheck,
  getTriggerStats
} from '@/services/api';

export default function AlertRules() {
  const [rules, setRules] = useState([]);
  const [watchlist, setWatchlist] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [triggering, setTriggering] = useState(false);
  const [triggerStats, setTriggerStats] = useState(null);
  const [showAddForm, setShowAddForm] = useState(false);
  
  // 新规则表单
  const [newRule, setNewRule] = useState({
    rule_name: '',
    ts_code: '',
    rule_type: 'price_change_pct',
    comparison_operator: 'gte',
    threshold_value: '',
    alert_level: 'medium'
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
        // 处理后端返回的数据结构
        const rulesData = response.data?.rules || response.data || [];
        setRules(rulesData);
      } else {
        setError(response.message || '获取预警规则失败');
      }
    } catch (err) {
      console.error('加载预警规则失败:', err);
      setError(err.message || '网络请求失败');
    } finally {
      setLoading(false);
    }
  };

  // 添加规则
  const handleAdd = async () => {
    if (!newRule.rule_name || !newRule.ts_code || !newRule.threshold_value) {
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
          rule_name: '',
          ts_code: '',
          rule_type: 'price_change_pct',
          comparison_operator: 'gte',
          threshold_value: '',
          alert_level: 'medium'
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
    // 创建现代化确认对话框
    const confirmDelete = () => {
      return new Promise((resolve) => {
        // 创建模态框元素
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4';
        modal.innerHTML = `
          <div class="bg-white rounded-2xl p-6 max-w-sm w-full shadow-2xl transform transition-all">
            <div class="text-center">
              <h3 class="text-lg font-semibold text-gray-900 mb-2">确认删除 ${name}</h3>
              <p class="text-gray-600 mb-6">此操作无法撤销</p>
              <div class="flex gap-3 justify-center">
                <button id="cancel-btn" class="px-6 py-2 bg-gray-100 text-gray-700 rounded-xl font-medium hover:bg-gray-200 transition-all duration-200 min-w-[80px]">
                  取消
                </button>
                <button id="confirm-btn" class="px-6 py-2 bg-blue-500 text-white rounded-xl font-medium hover:bg-blue-600 transition-all duration-200 min-w-[80px]">
                  删除
                </button>
              </div>
            </div>
          </div>
        `;
        
        document.body.appendChild(modal);
        
        // 绑定事件
        modal.querySelector('#cancel-btn').onclick = () => {
          document.body.removeChild(modal);
          resolve(false);
        };
        
        modal.querySelector('#confirm-btn').onclick = () => {
          document.body.removeChild(modal);
          resolve(true);
        };
        
        // 点击背景关闭
        modal.onclick = (e) => {
          if (e.target === modal) {
            document.body.removeChild(modal);
            resolve(false);
          }
        };
      });
    };
    
    const confirmed = await confirmDelete();
    if (!confirmed) return;
    
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
        is_enabled: !rule.is_enabled
      });
      
      if (response.success) {
        setSuccess(rule.is_enabled ? '规则已禁用' : '规则已启用');
        await loadRules();
        setTimeout(() => setSuccess(null), 2000);
      } else {
        setError(response.message || '更新失败');
      }
    } catch (err) {
      setError(err.message || '更新失败');
    }
  };

  // 触发预警检查
  const handleTriggerCheck = async () => {
    setTriggering(true);
    setError(null);
    
    try {
      const response = await triggerAlertCheck();
      
      if (response.success) {
        setSuccess(`预警检查完成：${response.message}`);
        setTriggerStats(response.stats);
        
        // 3秒后清除成功提示
        setTimeout(() => setSuccess(null), 5000);
      } else {
        setError(response.message || '预警检查失败');
      }
    } catch (err) {
      setError(err.message || '预警检查失败');
    } finally {
      setTriggering(false);
    }
  };

  // 加载触发统计
  const loadTriggerStats = async () => {
    try {
      const response = await getTriggerStats(7);
      if (response.success) {
        setTriggerStats(response.data);
      }
    } catch (err) {
      console.error('加载触发统计失败:', err);
    }
  };

  // 初始化
  useEffect(() => {
    loadWatchlist();
    loadRules();
    loadTriggerStats();
  }, []);

  // 获取规则类型中文名
  const getRuleTypeText = (type) => {
    const types = {
      'price_threshold': '价格阈值',
      'price_change_pct': '涨跌幅',
      'volume_ratio': '成交量比率',
      'turnover_rate': '换手率',
      'market_value': '市值变化',
      'technical_indicator': '技术指标',
      'money_flow': '资金流向'
    };
    return types[type] || type;
  };

  // 获取条件中文名
  const getConditionText = (operator) => {
    const operators = {
      'gt': '大于',
      'gte': '大于等于',
      'lt': '小于',
      'lte': '小于等于',
      'eq': '等于',
      'ne': '不等于'
    };
    return operators[operator] || operator;
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
            <div className="flex gap-2">
              <Button 
                onClick={handleTriggerCheck}
                disabled={triggering || rules.length === 0}
                variant="outline"
                size="sm"
              >
                <Play className={`h-4 w-4 mr-1 ${triggering ? 'animate-spin' : ''}`} />
                {triggering ? '检查中...' : '触发检查'}
              </Button>
              <Button 
                size="sm"
                onClick={() => setShowAddForm(!showAddForm)}
              >
                <Plus className="h-4 w-4 mr-1" />
                添加规则
              </Button>
            </div>
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
                    value={newRule.rule_name}
                    onChange={(e) => setNewRule({...newRule, rule_name: e.target.value})}
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
                      <SelectItem value="price_threshold">价格阈值</SelectItem>
                      <SelectItem value="price_change_pct">涨跌幅(%)</SelectItem>
                      <SelectItem value="volume_ratio">成交量比率</SelectItem>
                      <SelectItem value="turnover_rate">换手率</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label>条件 *</Label>
                  <Select 
                    value={newRule.comparison_operator}
                    onValueChange={(value) => setNewRule({...newRule, comparison_operator: value})}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="gt">大于</SelectItem>
                      <SelectItem value="gte">大于等于</SelectItem>
                      <SelectItem value="lt">小于</SelectItem>
                      <SelectItem value="lte">小于等于</SelectItem>
                      <SelectItem value="eq">等于</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label>阈值 *</Label>
                  <Input
                    type="number"
                    step="0.01"
                    placeholder="例如: 15.00"
                    value={newRule.threshold_value}
                    onChange={(e) => setNewRule({...newRule, threshold_value: e.target.value})}
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
                      rule_name: '',
                      ts_code: '',
                      rule_type: 'price_change_pct',
                      comparison_operator: 'gte',
                      threshold_value: '',
                      alert_level: 'medium'
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
                        <h4 className="font-medium">{rule.rule_name}</h4>
                        {rule.is_enabled ? (
                          <Badge className="bg-green-500">启用中</Badge>
                        ) : (
                          <Badge variant="secondary">已禁用</Badge>
                        )}
                      </div>
                      
                      <div className="text-sm text-gray-600 space-y-1">
                        <p>📊 股票: {rule.stock_name || rule.ts_code}</p>
                        <p>
                          📈 条件: {getRuleTypeText(rule.rule_type)} {getConditionText(rule.comparison_operator)} {rule.threshold_value}
                          {rule.rule_type === 'price_change_pct' && '%'}
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
                        {rule.is_enabled ? (
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
                        onClick={() => handleDelete(rule.id, rule.rule_name)}
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

      {/* 触发统计 */}
      {triggerStats && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm flex items-center gap-2">
              <BarChart3 className="h-4 w-4 text-green-500" />
              预警触发统计 (最近7天)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
              <div>
                <div className="text-2xl font-bold text-green-600">{triggerStats.total_alerts || 0}</div>
                <div className="text-sm text-gray-500">总预警数</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-blue-600">{triggerStats.active_alerts || 0}</div>
                <div className="text-sm text-gray-500">活跃预警</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-600">{triggerStats.resolved_alerts || 0}</div>
                <div className="text-sm text-gray-500">已解决</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-purple-600">
                  {Object.keys(triggerStats.by_type || {}).length}
                </div>
                <div className="text-sm text-gray-500">规则类型</div>
              </div>
            </div>
            {triggerStats.by_level && Object.keys(triggerStats.by_level).length > 0 && (
              <div className="mt-4 pt-4 border-t">
                <div className="text-sm text-gray-700 mb-2">按级别分布:</div>
                <div className="flex gap-2 flex-wrap">
                  {Object.entries(triggerStats.by_level).map(([level, count]) => (
                    <Badge key={level} variant="outline" className="text-xs">
                      {level}: {count}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

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
          <p>• <strong>触发检查</strong>: 点击"触发检查"按钮手动运行预警检测</p>
        </CardContent>
      </Card>
    </div>
  );
}
