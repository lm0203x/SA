import React, { useEffect, useState } from 'react';
import { BarChart3, CheckCircle2, Clock3, RefreshCw, TrendingUp } from 'lucide-react';

import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { apiRequest } from '@/services/api';

function getSignalClass(signal) {
  if (signal === 'buy') return 'bg-green-100 text-green-800';
  if (signal === 'watch') return 'bg-amber-100 text-amber-800';
  return 'bg-slate-200 text-slate-700';
}

function getStatusLabel(status) {
  if (status === 'completed') return 'completed';
  if (status === 'running') return 'running';
  if (status === 'failed') return 'failed';
  return status || 'unknown';
}

const DEFAULT_TASK_PAGINATION = {
  page: 1,
  per_page: 8,
  total: 0,
  pages: 0,
  has_next: false,
  has_prev: false,
};

const DEFAULT_STOCK_PAGINATION = {
  page: 1,
  per_page: 5,
  total: 0,
  pages: 0,
  has_next: false,
  has_prev: false,
};

export default function AnalysisRecords() {
  const [strategies, setStrategies] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [taskPagination, setTaskPagination] = useState(DEFAULT_TASK_PAGINATION);
  const [taskFilters, setTaskFilters] = useState({
    strategyId: '',
    status: '',
    page: 1,
  });
  const [selectedTask, setSelectedTask] = useState(null);
  const [stockCode, setStockCode] = useState('');
  const [submittedStockCode, setSubmittedStockCode] = useState('');
  const [stockStrategyId, setStockStrategyId] = useState('');
  const [stockHistory, setStockHistory] = useState([]);
  const [stockPagination, setStockPagination] = useState(DEFAULT_STOCK_PAGINATION);
  const [loading, setLoading] = useState(true);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadStrategies();
  }, []);

  useEffect(() => {
    loadTasks(taskFilters.page);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [taskFilters.page, taskFilters.status, taskFilters.strategyId]);

  async function loadStrategies() {
    try {
      const payload = await apiRequest('/analysis/strategies');

      setStrategies(payload.data || []);
    } catch (loadError) {
      console.error('Failed to load strategies:', loadError);
      setError(loadError.message || '加载分析策略失败');
    }
  }

  async function loadTasks(page = 1) {
    setLoading(true);
    setError('');
    try {
      const params = new URLSearchParams({
        page: String(page),
        per_page: String(taskPagination.per_page),
      });

      if (taskFilters.strategyId) {
        params.set('strategy_id', taskFilters.strategyId);
      }
      if (taskFilters.status) {
        params.set('status', taskFilters.status);
      }

      const payload = await apiRequest(`/analysis/tasks?${params.toString()}`);

      const nextTasks = payload.data?.tasks || [];
      const nextPagination = payload.data?.pagination || DEFAULT_TASK_PAGINATION;
      setTasks(nextTasks);
      setTaskPagination(nextPagination);

      if (nextTasks.length === 0) {
        setSelectedTask(null);
        return;
      }

      const selectedId = selectedTask?.task?.id;
      const matchedTask = selectedId ? nextTasks.find((task) => task.id === selectedId) : null;
      const taskToLoad = matchedTask || nextTasks[0];
      await loadTaskDetail(taskToLoad.id, false);
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
      const payload = await apiRequest(`/analysis/tasks/${taskId}`);

      setSelectedTask(payload.data);
    } catch (detailError) {
      console.error('Failed to load analysis task detail:', detailError);
      setError(detailError.message || '加载分析记录详情失败');
    }
  }

  async function searchStockHistory(page = 1) {
    const nextStockCode = stockCode.trim().toUpperCase();
    if (!nextStockCode) {
      setError('请输入股票代码');
      return;
    }

    setError('');
    setHistoryLoading(true);
    try {
      const params = new URLSearchParams({
        page: String(page),
        per_page: String(stockPagination.per_page),
      });

      if (stockStrategyId) {
        params.set('strategy_id', stockStrategyId);
      }

      const payload = await apiRequest(`/analysis/stocks/${nextStockCode}/history?${params.toString()}`);

      setSubmittedStockCode(nextStockCode);
      setStockHistory(payload.data?.records || []);
      setStockPagination(payload.data?.pagination || DEFAULT_STOCK_PAGINATION);
    } catch (historyError) {
      console.error('Failed to load stock analysis history:', historyError);
      setError(historyError.message || '加载股票分析历史失败');
      setStockHistory([]);
      setStockPagination(DEFAULT_STOCK_PAGINATION);
    } finally {
      setHistoryLoading(false);
    }
  }

  function handleTaskFilterChange(field, value) {
    setTaskFilters((prev) => ({
      ...prev,
      [field]: value,
      page: 1,
    }));
  }

  function handleTaskPageChange(page) {
    setTaskFilters((prev) => ({
      ...prev,
      page,
    }));
  }

  const summary = selectedTask?.task?.summary || {};

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">分析记录</h2>
          <p className="text-slate-600 mt-1">按任务和按股票查看历史分析结果，支持基础筛选和分页。</p>
        </div>
        <Button variant="outline" size="sm" onClick={() => loadTasks(taskFilters.page)} disabled={loading}>
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
                <p className="text-sm font-medium text-slate-500">任务总数</p>
                <h3 className="mt-1 text-2xl font-bold text-slate-900">{taskPagination.total || 0}</h3>
              </div>
              <BarChart3 className="h-5 w-5 text-slate-500" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-500">本次扫描</p>
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
            <CardDescription>按执行时间查看分析任务，支持策略和状态筛选。</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-3">
              <select
                className="h-10 rounded-md border border-slate-200 bg-white px-3 text-sm"
                value={taskFilters.strategyId}
                onChange={(event) => handleTaskFilterChange('strategyId', event.target.value)}
              >
                <option value="">全部策略</option>
                {strategies.map((strategy) => (
                  <option key={strategy.id} value={strategy.id}>
                    {strategy.name}
                  </option>
                ))}
              </select>
              <select
                className="h-10 rounded-md border border-slate-200 bg-white px-3 text-sm"
                value={taskFilters.status}
                onChange={(event) => handleTaskFilterChange('status', event.target.value)}
              >
                <option value="">全部状态</option>
                <option value="completed">completed</option>
                <option value="running">running</option>
                <option value="failed">failed</option>
              </select>
            </div>

            {tasks.length === 0 && !loading && (
              <div className="rounded-lg border border-dashed py-10 text-center text-sm text-slate-500">
                暂无分析记录
              </div>
            )}

            {tasks.map((task) => (
              <button
                key={task.id}
                type="button"
                className={`w-full rounded-lg border p-4 text-left transition hover:border-slate-400 ${
                  selectedTask?.task?.id === task.id ? 'border-slate-900 bg-slate-50' : ''
                }`}
                onClick={() => loadTaskDetail(task.id)}
              >
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-medium">{task.strategy_name || '未命名策略'}</span>
                      <Badge variant="outline">{getStatusLabel(task.status)}</Badge>
                    </div>
                    <p className="mt-1 text-sm text-slate-600">
                      {task.task_date}，共扫描 {task.summary?.total || 0} 只股票
                    </p>
                  </div>
                  <span className="text-xs text-slate-400">#{task.id}</span>
                </div>
              </button>
            ))}

            <div className="flex items-center justify-between pt-2 text-sm text-slate-500">
              <span>
                第 {taskPagination.page || 1} / {taskPagination.pages || 1} 页
              </span>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  disabled={!taskPagination.has_prev || loading}
                  onClick={() => handleTaskPageChange(taskPagination.page - 1)}
                >
                  上一页
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={!taskPagination.has_next || loading}
                  onClick={() => handleTaskPageChange(taskPagination.page + 1)}
                >
                  下一页
                </Button>
              </div>
            </div>
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
                    <Badge variant="outline">{getStatusLabel(selectedTask.task.status)}</Badge>
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
          <CardDescription>输入股票代码后，可按策略筛选并分页查看历史分析记录。</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-3 md:grid-cols-[1fr_220px_120px]">
            <Input
              value={stockCode}
              onChange={(event) => setStockCode(event.target.value)}
              placeholder="例如：000001.SZ"
            />
            <select
              className="h-10 rounded-md border border-slate-200 bg-white px-3 text-sm"
              value={stockStrategyId}
              onChange={(event) => setStockStrategyId(event.target.value)}
            >
              <option value="">全部策略</option>
              {strategies.map((strategy) => (
                <option key={strategy.id} value={strategy.id}>
                  {strategy.name}
                </option>
              ))}
            </select>
            <Button onClick={() => searchStockHistory(1)} disabled={historyLoading}>
              {historyLoading ? '查询中' : '查询'}
            </Button>
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

              <div className="flex items-center justify-between pt-2 text-sm text-slate-500">
                <span>
                  {submittedStockCode || stockCode.trim().toUpperCase()} 第 {stockPagination.page || 1} / {stockPagination.pages || 1} 页
                </span>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={!stockPagination.has_prev || historyLoading}
                    onClick={() => searchStockHistory(stockPagination.page - 1)}
                  >
                    上一页
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={!stockPagination.has_next || historyLoading}
                    onClick={() => searchStockHistory(stockPagination.page + 1)}
                  >
                    下一页
                  </Button>
                </div>
              </div>
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
