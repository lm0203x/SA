import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Database, CheckCircle, XCircle, Loader2, Plus, Trash2, Edit, RefreshCw } from 'lucide-react';
import {
  getDataSources,
  createDataSource,
  updateDataSource,
  deleteDataSource,
  testDataSourceConnection,
  syncStockList
} from '@/services/api';

export default function DataSourceConfig() {
  const [dataSources, setDataSources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [testingId, setTestingId] = useState(null);
  const [editingId, setEditingId] = useState(null);
  const [message, setMessage] = useState({ type: '', text: '' });

  // Tushare配置表单
  const [tushareForm, setTushareForm] = useState({
    source_name: 'Tushare Pro',
    token: '',
  });

  // 新增数据源对话框
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [newDataSource, setNewDataSource] = useState({
    source_type: 'tushare',
    source_name: '',
    config_data: { token: '' },
    is_active: false,
    is_default: false,
  });
  const [saving, setSaving] = useState(false);

  // 加载数据源列表
  useEffect(() => {
    loadDataSources();
  }, []);

  const loadDataSources = async () => {
    try {
      setLoading(true);
      const response = await getDataSources();
      setDataSources(response.data || response || []);
      setMessage({ type: '', text: '' });
    } catch (error) {
      console.error('加载数据源失败:', error);
      setMessage({ type: 'error', text: `加载失败: ${error.message}` });
    } finally {
      setLoading(false);
    }
  };

  // 同步股票列表
  const handleSyncStocks = async () => {
    try {
      setSyncing(true);
      setMessage({ type: 'info', text: '正在同步股票列表，这可能需要几分钟...' });

      const response = await syncStockList(true);

      if (response.success) {
        setMessage({ type: 'success', text: `✅ 同步成功: ${response.message}` });
      } else {
        setMessage({ type: 'error', text: `❌ 同步失败: ${response.message}` });
      }
    } catch (error) {
      console.error('同步股票列表失败:', error);
      setMessage({ type: 'error', text: `❌ 同步失败: ${error.message}` });
    } finally {
      setSyncing(false);
    }
  };

  // 测试连接
  const handleTestConnection = async (id) => {
    try {
      setTestingId(id);
      setMessage({ type: '', text: '' });

      const response = await testDataSourceConnection(id);

      if (response.status === 'success' || response.success) {
        setMessage({ type: 'success', text: '✅ 连接测试成功！' });
        loadDataSources(); // 重新加载以更新状态
      } else {
        setMessage({ type: 'error', text: `❌ 连接测试失败: ${response.message}` });
      }
    } catch (error) {
      console.error('测试连接失败:', error);
      setMessage({ type: 'error', text: `❌ 测试失败: ${error.message}` });
    } finally {
      setTestingId(null);
    }
  };

  // 更新数据源（激活/停用）
  const handleToggleActive = async (dataSource) => {
    try {
      setMessage({ type: '', text: '' });

      await updateDataSource(dataSource.id, {
        is_active: !dataSource.is_active,
        is_default: !dataSource.is_active, // 激活时设为默认
      });

      setMessage({
        type: 'success',
        text: `✅ 数据源已${!dataSource.is_active ? '激活' : '停用'}`
      });
      loadDataSources();
    } catch (error) {
      console.error('更新数据源失败:', error);
      setMessage({ type: 'error', text: `❌ 更新失败: ${error.message}` });
    }
  };

  // 设置默认数据源
  const handleSetDefault = async (dataSource) => {
    try {
      setMessage({ type: '', text: '' });

      await updateDataSource(dataSource.id, {
        is_default: true,
      });

      setMessage({
        type: 'success',
        text: '✅ 已设为默认数据源'
      });
      loadDataSources();
    } catch (error) {
      console.error('设置默认数据源失败:', error);
      setMessage({ type: 'error', text: `❌ 设置失败: ${error.message}` });
    }
  };

  // 更新Token
  const handleUpdateToken = async (dataSource) => {
    if (!tushareForm.token.trim()) {
      setMessage({ type: 'error', text: '请输入Tushare Token' });
      return;
    }

    try {
      setMessage({ type: '', text: '' });

      await updateDataSource(dataSource.id, {
        config_data: { token: tushareForm.token },
        source_name: tushareForm.source_name || dataSource.source_name,
      });

      setMessage({ type: 'success', text: '✅ Token更新成功' });
      setEditingId(null);
      setTushareForm({ source_name: 'Tushare Pro', token: '' });
      loadDataSources();
    } catch (error) {
      console.error('更新Token失败:', error);
      setMessage({ type: 'error', text: `❌ 更新失败: ${error.message}` });
    }
  };

  // 新增数据源
  const handleAddDataSource = async () => {
    if (!newDataSource.source_name.trim()) {
      setMessage({ type: 'error', text: '请输入数据源名称' });
      return;
    }
    if (!newDataSource.config_data.token.trim()) {
      setMessage({ type: 'error', text: '请输入Token' });
      return;
    }

    try {
      setSaving(true);
      setMessage({ type: '', text: '' });

      await createDataSource({
        source_type: newDataSource.source_type,
        source_name: newDataSource.source_name,
        config_data: newDataSource.config_data,
        is_active: newDataSource.is_active,
        is_default: newDataSource.is_default,
      });

      setMessage({ type: 'success', text: '✅ 数据源创建成功' });
      setShowAddDialog(false);
      setNewDataSource({
        source_type: 'tushare',
        source_name: '',
        config_data: { token: '' },
        is_active: false,
        is_default: false,
      });
      loadDataSources();
    } catch (error) {
      console.error('创建数据源失败:', error);
      setMessage({ type: 'error', text: `❌ 创建失败: ${error.message}` });
    } finally {
      setSaving(false);
    }
  };

  // 删除数据源
  const handleDelete = async (id) => {
    if (!confirm('确定要删除此数据源吗？')) return;

    try {
      setMessage({ type: '', text: '' });
      await deleteDataSource(id);
      setMessage({ type: 'success', text: '✅ 数据源已删除' });
      loadDataSources();
    } catch (error) {
      console.error('删除数据源失败:', error);
      setMessage({ type: 'error', text: `❌ 删除失败: ${error.message}` });
    }
  };

  // 渲染状态徽章
  const renderStatusBadge = (dataSource) => {
    const badges = [];
    if (dataSource.is_default) {
      badges.push(<Badge key="default" className="bg-purple-500">默认</Badge>);
    }
    if (dataSource.is_active) {
      badges.push(<Badge key="active" className="bg-green-500">已激活</Badge>);
    } else if (dataSource.status === '成功') {
      badges.push(<Badge key="tested" className="bg-blue-500">已测试</Badge>);
    } else {
      badges.push(<Badge key="untested" variant="outline">未测试</Badge>);
    }
    return <div className="flex gap-1">{badges}</div>;
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="h-5 w-5" />
            数据源配置
          </CardTitle>
        </CardHeader>
        <CardContent className="flex justify-center items-center py-8">
          <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
          <span className="ml-2 text-gray-500">加载中...</span>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {/* 消息提示 */}
      {message.text && (
        <Alert className={message.type === 'error' ? 'border-red-500' : 'border-green-500'}>
          <AlertDescription>{message.text}</AlertDescription>
        </Alert>
      )}

      {/* 数据源列表 */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Database className="h-5 w-5" />
                数据源配置
              </CardTitle>
              <CardDescription>
                配置和管理股票数据源，支持Tushare Pro等多种数据源
              </CardDescription>
            </div>
            <Button
              onClick={() => setShowAddDialog(true)}
              size="sm"
            >
              <Plus className="h-4 w-4 mr-1" />
              新增数据源
            </Button>
            <Button
              onClick={handleSyncStocks}
              disabled={syncing || dataSources.length === 0}
              variant="outline"
              size="sm"
            >
              <RefreshCw className={`h-4 w-4 mr-1 ${syncing ? 'animate-spin' : ''}`} />
              {syncing ? '同步中...' : '同步股票列表'}
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {dataSources.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              暂无数据源配置
            </div>
          ) : (
            dataSources.map((ds) => (
              <Card key={ds.id} className="border-2">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Database className="h-5 w-5 text-blue-500" />
                      <div>
                        <CardTitle className="text-lg">{ds.source_name}</CardTitle>
                        <CardDescription className="text-sm">
                          类型: {ds.source_type} |
                          {ds.last_test_time && ` 最后测试: ${new Date(ds.last_test_time).toLocaleString()}`}
                        </CardDescription>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {renderStatusBadge(ds)}
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* 编辑Token表单 */}
                  {editingId === ds.id ? (
                    <div className="space-y-3 p-4 bg-gray-50 rounded-lg">
                      <div>
                        <Label htmlFor={`token-${ds.id}`}>Tushare Token</Label>
                        <Input
                          id={`token-${ds.id}`}
                          type="text"
                          placeholder="输入您的Tushare Token"
                          value={tushareForm.token}
                          onChange={(e) => setTushareForm({ ...tushareForm, token: e.target.value })}
                          className="mt-1"
                        />
                        <p className="text-xs text-gray-500 mt-1">
                          在 <a href="https://tushare.pro/" target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">Tushare官网</a> 注册获取Token
                        </p>
                      </div>
                      <div className="flex gap-2">
                        <Button
                          onClick={() => handleUpdateToken(ds)}
                          size="sm"
                        >
                          <CheckCircle className="h-4 w-4 mr-1" />
                          保存
                        </Button>
                        <Button
                          onClick={() => {
                            setEditingId(null);
                            setTushareForm({ source_name: 'Tushare Pro', token: '' });
                          }}
                          variant="outline"
                          size="sm"
                        >
                          取消
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <div className="flex items-center gap-2">
                      <Button
                        onClick={() => {
                          setEditingId(ds.id);
                          setTushareForm({
                            source_name: ds.source_name,
                            token: ds.config_data?.token || '',
                          });
                        }}
                        variant="outline"
                        size="sm"
                      >
                        <Edit className="h-4 w-4 mr-1" />
                        配置Token
                      </Button>

                      <Button
                        onClick={() => handleTestConnection(ds.id)}
                        variant="outline"
                        size="sm"
                        disabled={testingId === ds.id || !ds.config_data?.token}
                      >
                        {testingId === ds.id ? (
                          <>
                            <Loader2 className="h-4 w-4 mr-1 animate-spin" />
                            测试中...
                          </>
                        ) : (
                          <>
                            <Database className="h-4 w-4 mr-1" />
                            测试连接
                          </>
                        )}
                      </Button>

                      {!ds.is_default && (
                        <Button
                          onClick={() => handleSetDefault(ds)}
                          variant="outline"
                          size="sm"
                        >
                          <CheckCircle className="h-4 w-4 mr-1" />
                          设为默认
                        </Button>
                      )}

                      <Button
                        onClick={() => handleToggleActive(ds)}
                        variant={ds.is_active ? "default" : "outline"}
                        size="sm"
                        disabled={!ds.config_data?.token}
                      >
                        {ds.is_active ? (
                          <>
                            <XCircle className="h-4 w-4 mr-1" />
                            停用
                          </>
                        ) : (
                          <>
                            <CheckCircle className="h-4 w-4 mr-1" />
                            激活
                          </>
                        )}
                      </Button>

                      {!ds.is_active && (
                        <Button
                          onClick={() => handleDelete(ds.id)}
                          variant="destructive"
                          size="sm"
                        >
                          <Trash2 className="h-4 w-4 mr-1" />
                          删除
                        </Button>
                      )}
                    </div>
                  )}

                  {/* Token状态提示 */}
                  {!ds.config_data?.token && (
                    <Alert>
                      <AlertDescription className="text-sm">
                        ⚠️ 请先配置Token才能使用此数据源
                      </AlertDescription>
                    </Alert>
                  )}
                </CardContent>
              </Card>
            ))
          )}
        </CardContent>
      </Card>

      {/* 新增数据源对话框 */}
      <Dialog open={showAddDialog} onOpenChange={setShowAddDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>新增数据源</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="source_type">数据源类型</Label>
              <select
                id="source_type"
                className="w-full mt-1 p-2 border rounded"
                value={newDataSource.source_type}
                onChange={(e) => setNewDataSource({ ...newDataSource, source_type: e.target.value })}
              >
                <option value="tushare">Tushare Pro</option>
                <option value="baostock">Baostock</option>
                <option value="tushare_pro">Tushare Pro (新)</option>
              </select>
            </div>
            <div>
              <Label htmlFor="source_name">数据源名称</Label>
              <Input
                id="source_name"
                value={newDataSource.source_name}
                onChange={(e) => setNewDataSource({ ...newDataSource, source_name: e.target.value })}
                placeholder="请输入数据源名称"
              />
            </div>
            <div>
              <Label htmlFor="token">Token</Label>
              <Input
                id="token"
                type="password"
                value={newDataSource.config_data.token}
                onChange={(e) => setNewDataSource({
                  ...newDataSource,
                  config_data: { token: e.target.value }
                })}
                placeholder="请输入API Token"
              />
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="is_default"
                checked={newDataSource.is_default}
                onChange={(e) => setNewDataSource({ ...newDataSource, is_default: e.target.checked })}
              />
              <Label htmlFor="is_default" className="font-normal">设为默认数据源</Label>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowAddDialog(false)}>
              取消
            </Button>
            <Button onClick={handleAddDataSource} disabled={saving}>
              {saving ? '保存中...' : '保存'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}