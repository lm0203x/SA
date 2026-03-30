import React, { useEffect, useState } from 'react';

import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { getOperationLogs } from '@/services/api';

const defaultPagination = {
  page: 1,
  per_page: 10,
  total: 0,
  pages: 0,
  has_next: false,
  has_prev: false,
};

export default function OperationLogList() {
  const [records, setRecords] = useState([]);
  const [pagination, setPagination] = useState(defaultPagination);
  const [filters, setFilters] = useState({
    page: 1,
    module: '',
    action_type: '',
    username: '',
    status: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadLogs(filters.page);
  }, [filters.page]);

  async function loadLogs(page = 1) {
    setLoading(true);
    setError('');
    try {
      const response = await getOperationLogs({
        page,
        per_page: pagination.per_page,
        module: filters.module,
        action_type: filters.action_type,
        username: filters.username,
        status: filters.status,
      });
      setRecords(response.data?.records || []);
      setPagination(response.data?.pagination || defaultPagination);
    } catch (loadError) {
      setError(loadError.message || '加载操作日志失败');
    } finally {
      setLoading(false);
    }
  }

  function handleFilterChange(field, value) {
    setFilters((prev) => ({
      ...prev,
      [field]: value,
      page: 1,
    }));
  }

  const statusClassMap = {
    success: 'bg-green-100 text-green-800',
    failed: 'bg-red-100 text-red-800',
  };

  return (
    <div className="space-y-4">
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <Card>
        <CardHeader>
          <CardTitle>操作日志</CardTitle>
          <CardDescription>记录登录、配置、同步、分析和结果查看等关键操作。</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-3 md:grid-cols-5">
            <Input
              placeholder="模块，如 watchlist"
              value={filters.module}
              onChange={(event) => handleFilterChange('module', event.target.value)}
            />
            <Input
              placeholder="操作类型，如 analyze"
              value={filters.action_type}
              onChange={(event) => handleFilterChange('action_type', event.target.value)}
            />
            <Input
              placeholder="用户名"
              value={filters.username}
              onChange={(event) => handleFilterChange('username', event.target.value)}
            />
            <select
              className="h-10 rounded-md border border-slate-200 bg-white px-3 text-sm"
              value={filters.status}
              onChange={(event) => handleFilterChange('status', event.target.value)}
            >
              <option value="">全部状态</option>
              <option value="success">success</option>
              <option value="failed">failed</option>
            </select>
            <Button onClick={() => loadLogs(1)} disabled={loading}>
              {loading ? '查询中...' : '查询'}
            </Button>
          </div>

          {loading ? (
            <div className="py-8 text-center text-sm text-slate-500">加载中...</div>
          ) : records.length === 0 ? (
            <div className="rounded-lg border border-dashed py-8 text-center text-sm text-slate-500">
              暂无操作日志
            </div>
          ) : (
            <div className="space-y-3">
              {records.map((record) => (
                <div key={record.id} className="rounded-lg border p-4">
                  <div className="flex items-start justify-between gap-4">
                    <div className="space-y-2">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="font-medium text-slate-900">{record.action_name}</span>
                        <Badge variant="outline">{record.module}</Badge>
                        <Badge variant="outline">{record.action_type}</Badge>
                        <Badge className={statusClassMap[record.status] || 'bg-slate-100 text-slate-700'}>
                          {record.status}
                        </Badge>
                      </div>
                      <div className="text-sm text-slate-600">
                        用户: {record.username || '匿名'} | 对象: {record.target_name || '--'}
                      </div>
                      <div className="text-sm text-slate-600">
                        {record.message || '--'}
                      </div>
                      <div className="text-xs text-slate-500">
                        {record.request_method || '--'} {record.request_path || '--'}
                      </div>
                    </div>
                    <div className="text-right text-xs text-slate-500">
                      {record.created_at ? new Date(record.created_at).toLocaleString('zh-CN') : '--'}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          <div className="flex items-center justify-between text-sm text-slate-500">
            <span>
              第 {pagination.page || 1} / {pagination.pages || 1} 页，共 {pagination.total || 0} 条
            </span>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                disabled={!pagination.has_prev || loading}
                onClick={() => setFilters((prev) => ({ ...prev, page: prev.page - 1 }))}
              >
                上一页
              </Button>
              <Button
                variant="outline"
                size="sm"
                disabled={!pagination.has_next || loading}
                onClick={() => setFilters((prev) => ({ ...prev, page: prev.page + 1 }))}
              >
                下一页
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
