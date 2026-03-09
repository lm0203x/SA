import React, { useEffect, useState } from 'react';
import { BarChart3, CheckCircle2, Clock3, RefreshCw, TrendingUp } from 'lucide-react';

import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';

function getSignalClass(signal) {
  if (signal === 'buy') return 'bg-green-100 text-green-800';
  if (signal === 'watch') return 'bg-amber-100 text-amber-800';
  return 'bg-slate-200 text-slate-700';
}

export default function AnalysisRecords() {
  const [tasks, setTasks] = useState([]);
  const [selectedTask, setSelectedTask] = useState(null);
  const [stockCode, setStockCode] = useState('');
  const [stockHistory, setStockHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadTasks();
  }, []);

  async function loadTasks() {
    setLoading(true);
    setError('');
    try {
      const response = await fetch('/api/analysis/tasks');
      const payload = await response.json();

      if (!response.ok) {
        throw new Error(payload.message || '加载分析记录失败');
      }

      const nextTasks = payload.data?.tasks || [];
      setTasks(nextTasks);

      if (nextTasks.length > 0) {
        await loadTaskDetail(nextTasks[0].id, false);
      } else {
        setSelectedTask(null);
      }
    } catch (loadError) {
      console.error('Failed to load analysis tasks:', loadError);
      setError(loadError.message || '加载分析记录失败');
    } finally {
      setLoading(false);
    }
  }

  async function loadTaskDetail(taskId, resetError = true) {
    if (resetError) {
      setError('');
    }
    try {
      const response = await fetch(`/api/analysis/tasks/${taskId}`);
      const payload = await response.json();

      if (!response.ok) {
        throw new Error(payload.message || '加载分析记录详情失败');
      }

      setSelectedTask(payload.data);
    } catch (detailError) {
      console.error('Failed to load analysis task detail:', detailError);
      setError(detailError.message || '加载分析记录详情失败');
    }
  }

  async function searchStockHistory() {
    if (!stockCode.trim()) {
      setError('请输入股票代码');
      return;
    }

    setError('');
    try {
      const response = await fetch(`/api/analysis/stocks/${stockCode.trim()}/history`);
      const payload = await response.json();

      if (!response.ok) {
        throw new Error(payload.message || '加载股票分析历史失败');
      }

      setStockHistory(payload.data?.records || []);
    } catch (historyError) {
      console.error('Failed to load stock analysis history:', historyError);
      setError(historyError.message || '加载股票分析历史失败');
      setStockHistory([]);
    }
  }

  const summary = selectedTask?.task?.summary || {};

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">分析记录</h2>
          <p className="text-slate-600 mt-1">查看历史分析任务、策略输出和命中结果。</p>
        </div>
        <Button variant="outline" size="sm" onClick={loadTasks} disabled={loading}>
          <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          刷新
        </Button>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-500">分析任务</p>
                <h3 className="mt-1 text-2xl font-bold text-slate-900">{tasks.length}</h3>
              </div>
              <BarChart3 className="h-5 w-5 text-slate-500" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-500">最近扫描数</p>
                <h3 className="mt-1 text-2xl font-bold text-slate-900">{summary.total || 0}</h3>
              </div>
              <Clock3 className="h-5 w-5 text-slate-500" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-500">观察信号</p>
                <h3 className="mt-1 text-2xl font-bold text-amber-600">{summary.watch_count || 0}</h3>
              </div>
              <TrendingUp className="h-5 w-5 text-amber-500" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-500">买入信号</p>
                <h3 className="mt-1 text-2xl font-bold text-green-600">{summary.buy_count || 0}</h3>
              </div>
              <CheckCircle2 className="h-5 w-5 text-green-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-[360px_1fr]">
        <Card>
          <CardHeader>
            <CardTitle>任务历史</CardTitle>
            <CardDescription>按执行时间查看分析任务</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {tasks.length === 0 && !loading && (
              <div className="rounded-lg border border-dashed py-10 text-center text-sm text-slate-500">
                暂无分析记录
              </div>
            )}

            {tasks.map((task) => (
              <button
                key={task.id}
                type="button"
                className="w-full rounded-lg border p-4 text-left transition hover:border-slate-400"
                onClick={() => loadTaskDetail(task.id)}
              >
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-medium">{task.strategy_name || '未命名策略'}</span>
                      <Badge variant="outline">{task.status}</Badge>
                    </div>
                    <p className="mt-1 text-sm text-slate-600">
                      {task.task_date}，共扫描 {task.summary?.total || 0} 只股票
                    </p>
                  </div>
                  <span className="text-xs text-slate-400">#{task.id}</span>
                </div>
              </button>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>结果明细</CardTitle>
            <CardDescription>按任务查看本次策略命中的股票和结构化理由</CardDescription>
          </CardHeader>
          <CardContent>
            {!selectedTask ? (
              <div className="rounded-lg border border-dashed py-12 text-center text-sm text-slate-500">
                选择左侧任务后，这里会展示对应分析结果
              </div>
            ) : (
              <div className="space-y-4">
                <div className="rounded-lg bg-slate-50 p-4">
                  <div className="flex items-center gap-2">
                    <span className="font-medium">{selectedTask.task.strategy_name}</span>
                    <Badge variant="outline">{selectedTask.task.status}</Badge>
                  </div>
                  <p className="mt-1 text-sm text-slate-600">
                    任务日期: {selectedTask.task.task_date}，策略编码: {selectedTask.task.strategy_code || '-'}
                  </p>
                </div>

                {selectedTask.results?.length ? (
                  selectedTask.results.map((result) => (
                    <div key={result.id} className="rounded-lg border p-4">
                      <div className="flex items-center justify-between gap-4">
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="font-medium">{result.stock_name || result.ts_code}</span>
                            <span className="text-xs text-slate-500">{result.ts_code}</span>
                            <Badge className={getSignalClass(result.signal)}>{result.signal}</Badge>
                          </div>
                          <p className="mt-2 text-sm text-slate-600">
                            {result.reasons?.join('，') || '暂无分析理由'}
                          </p>
                        </div>
                        <div className="text-right">
                          <div className="text-2xl font-semibold text-slate-900">{result.score}</div>
                          <div className="text-xs text-slate-500">score</div>
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="rounded-lg border border-dashed py-10 text-center text-sm text-slate-500">
                    该任务暂无结果
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>按股票查看历史</CardTitle>
          <CardDescription>输入股票代码，查看这只股票在历史分析任务中的命中情况。</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-3">
            <Input
              value={stockCode}
              onChange={(event) => setStockCode(event.target.value)}
              placeholder="例如：000001.SZ"
            />
            <Button onClick={searchStockHistory}>查询</Button>
          </div>

          {stockHistory.length > 0 ? (
            <div className="space-y-3">
              {stockHistory.map((record) => (
                <div key={record.result_id} className="rounded-lg border p-4">
                  <div className="flex items-center justify-between gap-4">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{record.stock_name || record.ts_code}</span>
                        <span className="text-xs text-slate-500">{record.task_date}</span>
                        <span className="text-xs text-slate-500">{record.strategy_name}</span>
                        <Badge className={getSignalClass(record.signal)}>{record.signal}</Badge>
                      </div>
                      <p className="mt-2 text-sm text-slate-600">
                        {record.reasons?.join('，') || '暂无分析理由'}
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="text-xl font-semibold text-slate-900">{record.score}</div>
                      <div className="text-xs text-slate-500">score</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="rounded-lg border border-dashed py-8 text-center text-sm text-slate-500">
              输入股票代码后可查看历史分析记录
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
