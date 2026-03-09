import React, { useEffect, useState } from 'react';
import { Brain, Play, Plus, RefreshCcw, Target } from 'lucide-react';

import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

const strategyTypes = [
  { id: 'value', name: '估值修复', description: '结合估值、安全边际和资金流的日线分析策略。' },
  { id: 'trend', name: '趋势观察', description: '更关注涨跌幅、换手和量能结构的观察型策略。' },
  { id: 'fund_flow', name: '资金流改善', description: '更关注最新资金净流入和结构信号。' },
];

const emptyStrategy = {
  name: '',
  code: '',
  strategy_type: 'value',
  description: '',
  schedule_type: 'manual',
};

export default function AnalysisRules() {
  const [strategies, setStrategies] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [selectedTask, setSelectedTask] = useState(null);
  const [newStrategy, setNewStrategy] = useState(emptyStrategy);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [runningId, setRunningId] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    setLoading(true);
    setError('');
    try {
      const [strategyRes, taskRes] = await Promise.all([
        fetch('/api/analysis/strategies'),
        fetch('/api/analysis/tasks'),
      ]);
      const strategyPayload = await strategyRes.json();
      const taskPayload = await taskRes.json();

      if (!strategyRes.ok) {
        throw new Error(strategyPayload.message || '加载分析策略失败');
      }
      if (!taskRes.ok) {
        throw new Error(taskPayload.message || '加载分析任务失败');
      }

      setStrategies(strategyPayload.data || []);
      setTasks(taskPayload.data?.tasks || []);
    } catch (loadError) {
      console.error('Failed to load analysis data:', loadError);
      setError(loadError.message || '加载分析数据失败');
    } finally {
      setLoading(false);
    }
  }

  async function createStrategy() {
    if (!newStrategy.name || !newStrategy.code || !newStrategy.strategy_type) {
      setError('请填写策略名称、编码和类型');
      return;
    }

    setSubmitting(true);
    setError('');
    try {
      const response = await fetch('/api/analysis/strategies', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...newStrategy,
          conditions: { stock_scope_type: 'watchlist' },
        }),
      });
      const payload = await response.json();

      if (!response.ok) {
        throw new Error(payload.message || '创建分析策略失败');
      }

      setStrategies((prev) => [payload.data, ...prev]);
      setNewStrategy(emptyStrategy);
    } catch (createError) {
      console.error('Failed to create strategy:', createError);
      setError(createError.message || '创建分析策略失败');
    } finally {
      setSubmitting(false);
    }
  }

  async function runStrategy(strategyId) {
    setRunningId(strategyId);
    setError('');
    try {
      const response = await fetch(`/api/analysis/strategies/${strategyId}/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({}),
      });
      const payload = await response.json();

      if (!response.ok) {
        throw new Error(payload.message || '执行分析策略失败');
      }

      setSelectedTask(payload.data);
      await loadData();
    } catch (runError) {
      console.error('Failed to run strategy:', runError);
      setError(runError.message || '执行分析策略失败');
    } finally {
      setRunningId(null);
    }
  }

  async function loadTaskDetail(taskId) {
    setError('');
    try {
      const response = await fetch(`/api/analysis/tasks/${taskId}`);
      const payload = await response.json();

      if (!response.ok) {
        throw new Error(payload.message || '加载任务详情失败');
      }

      setSelectedTask(payload.data);
    } catch (detailError) {
      console.error('Failed to load task detail:', detailError);
      setError(detailError.message || '加载任务详情失败');
    }
  }

  function getSignalClass(signal) {
    if (signal === 'buy') return 'bg-green-100 text-green-800';
    if (signal === 'watch') return 'bg-amber-100 text-amber-800';
    return 'bg-slate-200 text-slate-700';
  }

  const currentType = strategyTypes.find((item) => item.id === newStrategy.strategy_type);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">分析策略</h2>
          <p className="text-slate-600 mt-1">定义分析策略，执行日线扫描，并查看结构化结果。</p>
        </div>
        <Badge variant="outline" className="flex items-center gap-2">
          <Brain className="h-4 w-4" />
          <span>策略数: {strategies.length}</span>
        </Badge>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <Tabs defaultValue="create" className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="create">创建策略</TabsTrigger>
          <TabsTrigger value="manage">策略列表</TabsTrigger>
          <TabsTrigger value="tasks">任务结果</TabsTrigger>
        </TabsList>

        <TabsContent value="create" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Plus className="h-5 w-5" />
                <span>创建新策略</span>
              </CardTitle>
              <CardDescription>先以自选股为扫描范围，后续再逐步扩展更复杂的分析条件。</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="strategy-name">策略名称</Label>
                  <Input
                    id="strategy-name"
                    placeholder="例如：低估值观察策略"
                    value={newStrategy.name}
                    onChange={(event) => setNewStrategy((prev) => ({ ...prev, name: event.target.value }))}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="strategy-code">策略编码</Label>
                  <Input
                    id="strategy-code"
                    placeholder="例如：value_watch"
                    value={newStrategy.code}
                    onChange={(event) => setNewStrategy((prev) => ({ ...prev, code: event.target.value }))}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="strategy-type">策略类型</Label>
                  <Select
                    value={newStrategy.strategy_type}
                    onValueChange={(value) => setNewStrategy((prev) => ({ ...prev, strategy_type: value }))}
                  >
                    <SelectTrigger id="strategy-type">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {strategyTypes.map((item) => (
                        <SelectItem key={item.id} value={item.id}>
                          {item.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="schedule-type">调度方式</Label>
                  <Select
                    value={newStrategy.schedule_type}
                    onValueChange={(value) => setNewStrategy((prev) => ({ ...prev, schedule_type: value }))}
                  >
                    <SelectTrigger id="schedule-type">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="manual">手动执行</SelectItem>
                      <SelectItem value="daily_close">收盘后执行</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="strategy-description">策略描述</Label>
                <textarea
                  id="strategy-description"
                  placeholder="描述这个策略重点关注什么信号和适用场景"
                  value={newStrategy.description}
                  onChange={(event) => setNewStrategy((prev) => ({ ...prev, description: event.target.value }))}
                  className="min-h-[120px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                />
              </div>

              <Card className="border-dashed">
                <CardHeader>
                  <CardTitle className="text-lg">当前类型说明</CardTitle>
                  <CardDescription>{currentType?.description}</CardDescription>
                </CardHeader>
              </Card>

              <Button onClick={createStrategy} className="w-full" disabled={submitting}>
                <Plus className="h-4 w-4 mr-2" />
                {submitting ? '创建中...' : '创建策略'}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="manage" className="space-y-4">
          <div className="flex justify-end">
            <Button variant="outline" size="sm" onClick={loadData} disabled={loading}>
              <RefreshCcw className="h-4 w-4 mr-2" />
              刷新
            </Button>
          </div>

          {strategies.map((strategy) => (
            <Card key={strategy.id}>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <Target className="h-4 w-4 text-slate-500" />
                      <h3 className="font-medium">{strategy.name}</h3>
                      <Badge variant="outline">{strategy.strategy_type}</Badge>
                      <Badge variant={strategy.is_active ? 'default' : 'secondary'}>
                        {strategy.is_active ? '启用' : '停用'}
                      </Badge>
                    </div>
                    <p className="text-sm text-slate-600">{strategy.description || '暂无描述'}</p>
                    <p className="text-xs text-slate-500">编码: {strategy.code}</p>
                  </div>
                  <Button onClick={() => runStrategy(strategy.id)} disabled={runningId === strategy.id}>
                    <Play className="h-4 w-4 mr-2" />
                    {runningId === strategy.id ? '执行中...' : '执行分析'}
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}

          {strategies.length === 0 && (
            <Card>
              <CardContent className="py-12 text-center">
                <Brain className="h-12 w-12 text-slate-400 mx-auto mb-4" />
                <p className="text-slate-600">暂无分析策略</p>
                <p className="text-sm text-slate-500 mt-2">创建第一条策略后即可执行日线分析。</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="tasks" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>分析任务</CardTitle>
              <CardDescription>查看最近执行的分析任务和命中的结构化结果。</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {tasks.map((task) => (
                  <button
                    key={task.id}
                    type="button"
                    className="w-full rounded-lg border p-4 text-left transition hover:border-slate-400"
                    onClick={() => loadTaskDetail(task.id)}
                  >
                    <div className="flex items-center justify-between gap-4">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-medium">{task.strategy_name || '未命名策略'}</span>
                          <Badge variant="outline">{task.status}</Badge>
                        </div>
                        <p className="text-sm text-slate-600 mt-1">
                          任务日期: {task.task_date}，共扫描 {task.summary?.total || 0} 只股票
                        </p>
                      </div>
                      <span className="text-xs text-slate-500">#{task.id}</span>
                    </div>
                  </button>
                ))}

                {tasks.length === 0 && (
                  <div className="rounded-lg border border-dashed py-8 text-center text-sm text-slate-500">
                    暂无分析任务
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          <Card className="min-h-[240px]">
            <CardHeader>
              <CardTitle>任务详情</CardTitle>
            </CardHeader>
            <CardContent>
              {!selectedTask ? (
                <div className="rounded-lg border border-dashed py-10 text-center text-sm text-slate-500">
                  选择一条任务后，这里会展示分析结果明细
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="rounded-lg bg-slate-50 p-4">
                    <div className="flex items-center gap-2">
                      <span className="font-medium">{selectedTask.task.strategy_name}</span>
                      <Badge variant="outline">{selectedTask.task.status}</Badge>
                    </div>
                    <p className="text-sm text-slate-600 mt-1">
                      扫描股票数: {selectedTask.task.summary?.total || 0}，观察信号:
                      {' '}{selectedTask.task.summary?.watch_count || 0}，买入信号:
                      {' '}{selectedTask.task.summary?.buy_count || 0}
                    </p>
                  </div>

                  {selectedTask.results.map((result) => (
                    <div key={result.id} className="rounded-lg border p-4">
                      <div className="flex items-center justify-between gap-4">
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="font-medium">{result.stock_name || result.ts_code}</span>
                            <span className="text-xs text-slate-500">{result.ts_code}</span>
                            <Badge className={getSignalClass(result.signal)}>{result.signal}</Badge>
                          </div>
                          <p className="text-sm text-slate-600 mt-2">
                            {result.reasons?.join('，') || '暂无分析理由'}
                          </p>
                        </div>
                        <div className="text-right">
                          <div className="text-2xl font-semibold text-slate-900">{result.score}</div>
                          <div className="text-xs text-slate-500">score</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
