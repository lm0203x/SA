// WebhookConfig.jsx - 管理Webhook配置的前端组件
// 采用与 AlertRules 类似的风格，实现列表、添加、编辑、删除、测试等功能

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import {
  getWebhookConfigs,
  createWebhookConfig,
  updateWebhookConfig,
  deleteWebhookConfig,
  testWebhookConfig,
  enableWebhookConfig,
  disableWebhookConfig,
  getWebhookTypes,
} from '@/services/api';
import {
  Webhook,
  MessageSquare,
  Mail,
  Settings,
  Plus,
  Edit,
  Trash2,
  CheckCircle,
  XCircle,
  TestTube,
  AlertTriangle,
} from 'lucide-react';

export default function WebhookConfig() {
  const [configs, setConfigs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState(null); // null 为新增
  const [form, setForm] = useState({
    webhook_type: 'dingtalk',
    webhook_name: '',
    config_data: {},
    is_enabled: true,
    is_default: false,
  });

  const loadConfigs = async () => {
    setLoading(true);
    try {
      const resp = await getWebhookConfigs();
      if (resp.success) {
        setConfigs(resp.data?.configs || resp.data || []);
      } else {
        setError(resp.message || '加载Webhook配置失败');
      }
    } catch (e) {
      setError(e.message || '加载Webhook配置异常');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadConfigs();
  }, []);

  const resetForm = () => {
    setForm({
      webhook_type: 'dingtalk',
      webhook_name: '',
      config_data: {},
      is_enabled: true,
      is_default: false,
    });
    setEditing(null);
  };

  const handleSubmit = async () => {
    const payload = {
      webhook_type: form.webhook_type,
      webhook_name: form.webhook_name,
      config_data: form.config_data,
      is_enabled: form.is_enabled,
      is_default: form.is_default,
    };
    setLoading(true);
    try {
      const resp = editing
        ? await updateWebhookConfig(editing.id, payload)
        : await createWebhookConfig(payload);
      if (resp.success) {
        setSuccess(editing ? '更新成功' : '创建成功');
        await loadConfigs();
        resetForm();
        setShowForm(false);
        setTimeout(() => setSuccess(null), 3000);
      } else {
        setError(resp.message || '操作失败');
      }
    } catch (e) {
      setError(e.message || '请求异常');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id, name) => {
    if (!window.confirm(`确认删除 ${name}？此操作不可恢复`)) return;
    setLoading(true);
    try {
      const resp = await deleteWebhookConfig(id);
      if (resp.success) {
        setSuccess('删除成功');
        await loadConfigs();
        setTimeout(() => setSuccess(null), 3000);
      } else {
        setError(resp.message || '删除失败');
      }
    } catch (e) {
      setError(e.message || '请求异常');
    } finally {
      setLoading(false);
    }
  };

  const handleTest = async (id) => {
    setLoading(true);
    try {
      const resp = await testWebhookConfig(id);
      if (resp.success) {
        setSuccess('连接测试成功');
      } else {
        setError(resp.message || '测试失败');
      }
    } catch (e) {
      setError(e.message || '请求异常');
    } finally {
      setLoading(false);
      setTimeout(() => { setSuccess(null); setError(null); }, 4000);
    }
  };

  const toggleEnable = async (cfg) => {
    const fn = cfg.is_enabled ? disableWebhookConfig : enableWebhookConfig;
    setLoading(true);
    try {
      const resp = await fn(cfg.id);
      if (resp.success) {
        setSuccess(cfg.is_enabled ? '已禁用' : '已启用');
        await loadConfigs();
        setTimeout(() => setSuccess(null), 2000);
      } else {
        setError(resp.message || '操作失败');
      }
    } catch (e) {
      setError(e.message || '请求异常');
    } finally {
      setLoading(false);
    }
  };

  const openEdit = (cfg) => {
    setEditing(cfg);
    setForm({
      webhook_type: cfg.webhook_type,
      webhook_name: cfg.webhook_name,
      config_data: cfg.config_data || {},
      is_enabled: cfg.is_enabled,
      is_default: cfg.is_default,
    });
    setShowForm(true);
  };

  const renderConfigFields = () => {
    const fields = [];
    if (['dingtalk', 'wechat_work', 'feishu', 'webhook', 'custom'].includes(form.webhook_type)) {
      fields.push(
        <div key="url" className="grid gap-2" >
          <Label>Webhook URL</Label>
          <Input
            placeholder="https://..."
            value={form.config_data.webhook_url || ''}
            onChange={e => setForm(prev => ({ ...prev, config_data: { ...prev.config_data, webhook_url: e.target.value } }))}
          />
        </div>
      );
    }
    if (form.webhook_type === 'dingtalk') {
      fields.push(
        <div key="secret" className="grid gap-2" >
          <Label>Secret（可选）</Label>
          <Input
            placeholder="SEC..."
            value={form.config_data.secret || ''}
            onChange={e => setForm(prev => ({ ...prev, config_data: { ...prev.config_data, secret: e.target.value } }))}
          />
        </div>
      );
    }
    if (form.webhook_type === 'email') {
      fields.push(
        <div key="smtp" className="grid gap-2" >
          <Label>SMTP Host</Label>
          <Input
            placeholder="smtp.example.com"
            value={form.config_data.smtp_host || ''}
            onChange={e => setForm(prev => ({ ...prev, config_data: { ...prev.config_data, smtp_host: e.target.value } }))}
          />
        </div>
      );
    }
    return fields;
  };

  return (
    <div className="space-y-6">
      {/* 错误/成功提示 */}
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

      {/* 列表卡片 */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Webhook className="h-5 w-5 text-blue-500" />
              <span>Webhook 配置</span>
              {configs.length > 0 && <Badge variant="secondary">{configs.length}</Badge>}
            </CardTitle>
            <Button size="sm" onClick={() => { resetForm(); setShowForm(true); }}>
              + 添加配置
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">加载中...</div>
          ) : configs.length === 0 ? (
            <div className="text-center text-gray-500 py-8">暂无Webhook配置</div>
          ) : (
            <div className="space-y-4">
              {configs.map(cfg => (
                <div key={cfg.id} className={`p-4 rounded-lg border ${cfg.is_enabled ? 'border-blue-200 bg-blue-50' : 'border-gray-200 bg-gray-50'}`}>
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <h4 className="font-medium">{cfg.webhook_name}</h4>
                        <Badge>{cfg.webhook_type}</Badge>
                        {cfg.is_enabled ? (
                          <Badge className="bg-green-500 text-white">启用</Badge>
                        ) : (
                          <Badge variant="secondary">禁用</Badge>
                        )}
                        {cfg.is_default && <Badge variant="outline">默认</Badge>}
                      </div>
                      <p className="text-sm text-gray-600 break-all">{cfg.config_data?.webhook_url || ''}</p>
                    </div>
                    <div className="flex gap-2">
                      <Button size="sm" variant="outline" onClick={() => toggleEnable(cfg)}>
                        {cfg.is_enabled ? '禁用' : '启用'}
                      </Button>
                      <Button size="sm" variant="outline" onClick={() => handleTest(cfg.id)}>
                        测试
                      </Button>
                      <Button size="sm" variant="outline" onClick={() => openEdit(cfg)}>
                        编辑
                      </Button>
                      <Button size="sm" variant="ghost" onClick={() => handleDelete(cfg.id, cfg.webhook_name)}>
                        删除
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* 添加/编辑表单弹窗 */}
      <Dialog open={showForm} onOpenChange={setShowForm}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>{editing ? '编辑Webhook' : '添加Webhook'}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="grid gap-2">
              <Label>名称</Label>
              <Input
                placeholder="如：钉钉机器人-默认"
                value={form.webhook_name}
                onChange={e => setForm(prev => ({ ...prev, webhook_name: e.target.value }))}
              />
            </div>
            <div className="grid gap-2">
              <Label>类型</Label>
              <Select value={form.webhook_type} onValueChange={v => setForm(prev => ({ ...prev, webhook_type: v }))}>
                <SelectTrigger>
                  <SelectValue placeholder="选择类型" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="dingtalk">钉钉机器人</SelectItem>
                  <SelectItem value="wechat_work">企业微信机器人</SelectItem>
                  <SelectItem value="feishu">飞书机器人</SelectItem>
                  <SelectItem value="email">邮件通知</SelectItem>
                  <SelectItem value="webhook">通用Webhook</SelectItem>
                  <SelectItem value="custom">自定义接口</SelectItem>
                </SelectContent>
              </Select>
            </div>
            {/* 动态字段 */}
            {renderConfigFields()}
            <div className="flex items-center gap-2 mt-4 justify-end">
              <Button variant="outline" onClick={() => setShowForm(false)} disabled={loading}>
                取消
              </Button>
              <Button onClick={handleSubmit} disabled={loading}>
                {editing ? '更新' : '创建'}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
