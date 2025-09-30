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
import { 
  Webhook, 
  MessageSquare, 
  Mail, 
  Bell, 
  Smartphone, 
  Send, 
  TestTube, 
  Plus, 
  Edit, 
  Trash2,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Settings
} from 'lucide-react';

const WebhookConfig = () => {
  const [webhooks, setWebhooks] = useState([]);
  const [testResults, setTestResults] = useState({});
  const [newWebhook, setNewWebhook] = useState({
    name: '',
    type: 'generic',
    url: '',
    method: 'POST',
    headers: {},
    payload_template: '',
    enabled: true,
    retry_count: 3,
    timeout: 30
  });

  const webhookTypes = [
    {
      id: 'generic',
      name: '通用Webhook',
      description: '自定义HTTP请求',
      icon: Webhook,
      defaultTemplate: JSON.stringify({
        message: '{{message}}',
        symbol: '{{symbol}}',
        price: '{{price}}',
        change: '{{change}}',
        timestamp: '{{timestamp}}'
      }, null, 2)
    },
    {
      id: 'dingtalk',
      name: '钉钉机器人',
      description: '发送消息到钉钉群',
      icon: MessageSquare,
      defaultTemplate: JSON.stringify({
        msgtype: 'text',
        text: {
          content: '股票预警：{{symbol}} 当前价格 {{price}}，变化 {{change}}%。{{message}}'
        }
      }, null, 2)
    },
    {
      id: 'wechat_work',
      name: '企业微信',
      description: '发送消息到企业微信群',
      icon: MessageSquare,
      defaultTemplate: JSON.stringify({
        msgtype: 'text',
        text: {
          content: '📈 股票异动提醒\n股票代码：{{symbol}}\n当前价格：{{price}}\n涨跌幅：{{change}}%\n预警信息：{{message}}\n时间：{{timestamp}}'
        }
      }, null, 2)
    },
    {
      id: 'slack',
      name: 'Slack',
      description: '发送消息到Slack频道',
      icon: MessageSquare,
      defaultTemplate: JSON.stringify({
        text: '股票预警：{{symbol}}',
        attachments: [
          {
            color: 'warning',
            fields: [
              { title: '股票代码', value: '{{symbol}}', short: true },
              { title: '当前价格', value: '{{price}}', short: true },
              { title: '涨跌幅', value: '{{change}}%', short: true },
              { title: '预警信息', value: '{{message}}', short: false }
            ]
          }
        ]
      }, null, 2)
    },
    {
      id: 'email',
      name: '邮件通知',
      description: '发送邮件通知',
      icon: Mail,
      defaultTemplate: JSON.stringify({
        subject: '股票预警：{{symbol}} - {{message}}',
        body: '您好，\n\n股票 {{symbol}} 触发了预警条件：\n\n当前价格：{{price}}\n涨跌幅：{{change}}%\n预警信息：{{message}}\n触发时间：{{timestamp}}\n\n请及时关注市场动态。'
      }, null, 2)
    },
    {
      id: 'telegram',
      name: 'Telegram',
      description: '发送消息到Telegram',
      icon: Send,
      defaultTemplate: JSON.stringify({
        chat_id: '{{chat_id}}',
        text: '🚨 *股票预警通知*\n\n📊 股票代码：`{{symbol}}`\n💰 当前价格：`{{price}}`\n📈 涨跌幅：`{{change}}%`\n⚠️ 预警信息：{{message}}\n🕐 时间：{{timestamp}}',
        parse_mode: 'Markdown'
      }, null, 2)
    }
  ];

  useEffect(() => {
    loadWebhooks();
  }, []);

  const loadWebhooks = async () => {
    try {
      const response = await fetch('/api/webhooks');
      if (response.ok) {
        const data = await response.json();
        setWebhooks(data);
      }
    } catch (error) {
      console.error('Failed to load webhooks:', error);
    }
  };

  const createWebhook = async () => {
    if (!newWebhook.name || !newWebhook.url) {
      alert('请填写Webhook名称和URL');
      return;
    }

    try {
      const response = await fetch('/api/webhooks', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newWebhook),
      });

      if (response.ok) {
        const webhook = await response.json();
        setWebhooks(prev => [...prev, webhook]);
        setNewWebhook({
          name: '',
          type: 'generic',
          url: '',
          method: 'POST',
          headers: {},
          payload_template: '',
          enabled: true,
          retry_count: 3,
          timeout: 30
        });
      }
    } catch (error) {
      console.error('Failed to create webhook:', error);
    }
  };

  const testWebhook = async (webhookId) => {
    try {
      setTestResults(prev => ({ ...prev, [webhookId]: 'testing' }));
      
      const response = await fetch(`/api/webhooks/${webhookId}/test`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          symbol: 'AAPL',
          price: 175.50,
          change: 2.35,
          message: '测试预警消息',
          timestamp: new Date().toISOString()
        }),
      });

      const result = await response.json();
      
      if (response.ok && result.success) {
        setTestResults(prev => ({ ...prev, [webhookId]: 'success' }));
      } else {
        setTestResults(prev => ({ ...prev, [webhookId]: 'failed' }));
      }
    } catch (error) {
      console.error('Failed to test webhook:', error);
      setTestResults(prev => ({ ...prev, [webhookId]: 'failed' }));
    }
  };

  const toggleWebhook = async (webhookId, enabled) => {
    try {
      const response = await fetch(`/api/webhooks/${webhookId}/toggle`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ enabled }),
      });

      if (response.ok) {
        setWebhooks(prev => 
          prev.map(w => w.id === webhookId ? { ...w, enabled } : w)
        );
      }
    } catch (error) {
      console.error('Failed to toggle webhook:', error);
    }
  };

  const deleteWebhook = async (webhookId) => {
    if (!confirm('确定要删除这个Webhook吗？')) return;

    try {
      const response = await fetch(`/api/webhooks/${webhookId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        setWebhooks(prev => prev.filter(w => w.id !== webhookId));
      }
    } catch (error) {
      console.error('Failed to delete webhook:', error);
    }
  };

  const getWebhookTypeInfo = (type) => {
    return webhookTypes.find(wt => wt.id === type) || webhookTypes[0];
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-500" />;
      case 'testing':
        return <TestTube className="h-4 w-4 text-blue-500 animate-pulse" />;
      default:
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
    }
  };

  const updateWebhookType = (type) => {
    const typeInfo = getWebhookTypeInfo(type);
    setNewWebhook(prev => ({
      ...prev,
      type,
      payload_template: typeInfo.defaultTemplate
    }));
  };

  const addHeader = () => {
    const key = prompt('请输入Header名称:');
    if (key) {
      const value = prompt('请输入Header值:');
      if (value) {
        setNewWebhook(prev => ({
          ...prev,
          headers: {
            ...prev.headers,
            [key]: value
          }
        }));
      }
    }
  };

  const removeHeader = (key) => {
    setNewWebhook(prev => {
      const newHeaders = { ...prev.headers };
      delete newHeaders[key];
      return {
        ...prev,
        headers: newHeaders
      };
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Webhook配置</h2>
          <p className="text-slate-600 mt-1">配置预警通知的发送方式</p>
        </div>
        <Badge variant="outline" className="flex items-center space-x-2">
          <Webhook className="h-4 w-4" />
          <span>活跃Webhook: {webhooks.filter(w => w.enabled).length}</span>
        </Badge>
      </div>

      <Tabs defaultValue="create" className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="create">创建Webhook</TabsTrigger>
          <TabsTrigger value="manage">管理Webhook</TabsTrigger>
          <TabsTrigger value="logs">发送日志</TabsTrigger>
        </TabsList>

        {/* 创建Webhook */}
        <TabsContent value="create" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Plus className="h-5 w-5" />
                <span>创建新Webhook</span>
              </CardTitle>
              <CardDescription>
                配置Webhook以接收股票预警通知
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* 基本信息 */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="webhook-name">Webhook名称</Label>
                  <Input
                    id="webhook-name"
                    placeholder="例如：钉钉群通知"
                    value={newWebhook.name}
                    onChange={(e) => setNewWebhook(prev => ({ ...prev, name: e.target.value }))}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="webhook-type">Webhook类型</Label>
                  <Select 
                    value={newWebhook.type} 
                    onValueChange={updateWebhookType}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {webhookTypes.map((type) => {
                        const Icon = type.icon;
                        return (
                          <SelectItem key={type.id} value={type.id}>
                            <div className="flex items-center space-x-2">
                              <Icon className="h-4 w-4" />
                              <span>{type.name}</span>
                            </div>
                          </SelectItem>
                        );
                      })}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="webhook-url">Webhook URL</Label>
                <Input
                  id="webhook-url"
                  placeholder="https://oapi.dingtalk.com/robot/send?access_token=..."
                  value={newWebhook.url}
                  onChange={(e) => setNewWebhook(prev => ({ ...prev, url: e.target.value }))}
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="webhook-method">HTTP方法</Label>
                  <Select 
                    value={newWebhook.method} 
                    onValueChange={(value) => setNewWebhook(prev => ({ ...prev, method: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="POST">POST</SelectItem>
                      <SelectItem value="PUT">PUT</SelectItem>
                      <SelectItem value="PATCH">PATCH</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="webhook-timeout">超时时间(秒)</Label>
                  <Input
                    id="webhook-timeout"
                    type="number"
                    min="5"
                    max="300"
                    value={newWebhook.timeout}
                    onChange={(e) => setNewWebhook(prev => ({ ...prev, timeout: parseInt(e.target.value) }))}
                  />
                </div>
              </div>

              {/* HTTP Headers */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label>HTTP Headers</Label>
                  <Button variant="outline" size="sm" onClick={addHeader}>
                    <Plus className="h-4 w-4 mr-1" />
                    添加Header
                  </Button>
                </div>
                <div className="space-y-2">
                  {Object.entries(newWebhook.headers).map(([key, value]) => (
                    <div key={key} className="flex items-center space-x-2">
                      <Input value={key} readOnly className="flex-1" />
                      <Input value={value} readOnly className="flex-1" />
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => removeHeader(key)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              </div>

              {/* 消息模板 */}
              <div className="space-y-2">
                <Label htmlFor="payload-template">消息模板</Label>
                <Textarea
                  id="payload-template"
                  rows={10}
                  placeholder="JSON格式的消息模板..."
                  value={newWebhook.payload_template}
                  onChange={(e) => setNewWebhook(prev => ({ ...prev, payload_template: e.target.value }))}
                />
                <p className="text-sm text-slate-500">
                  可用变量：{{`{{symbol}}`}}, {{`{{price}}`}}, {{`{{change}}`}}, {{`{{message}}`}}, {{`{{timestamp}}`}}
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="retry-count">重试次数</Label>
                  <Input
                    id="retry-count"
                    type="number"
                    min="0"
                    max="10"
                    value={newWebhook.retry_count}
                    onChange={(e) => setNewWebhook(prev => ({ ...prev, retry_count: parseInt(e.target.value) }))}
                  />
                </div>
                <div className="flex items-center space-x-2 mt-6">
                  <Switch
                    id="webhook-enabled"
                    checked={newWebhook.enabled}
                    onCheckedChange={(checked) => setNewWebhook(prev => ({ ...prev, enabled: checked }))}
                  />
                  <Label htmlFor="webhook-enabled">创建后立即启用</Label>
                </div>
              </div>

              <Button onClick={createWebhook} className="w-full">
                <Plus className="h-4 w-4 mr-2" />
                创建Webhook
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 管理Webhook */}
        <TabsContent value="manage" className="space-y-4">
          {webhooks.map((webhook) => {
            const typeInfo = getWebhookTypeInfo(webhook.type);
            const Icon = typeInfo.icon;

            return (
              <Card key={webhook.id}>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className="p-2 bg-slate-100 rounded-lg">
                        <Icon className="h-6 w-6 text-slate-600" />
                      </div>
                      <div>
                        <h3 className="font-medium">{webhook.name}</h3>
                        <p className="text-sm text-slate-600">{typeInfo.name}</p>
                        <p className="text-xs text-slate-500 mt-1">{webhook.url}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(testResults[webhook.id])}
                      <Badge variant={webhook.enabled ? 'default' : 'secondary'}>
                        {webhook.enabled ? '启用' : '禁用'}
                      </Badge>
                      <div className="flex items-center space-x-1">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => testWebhook(webhook.id)}
                          disabled={testResults[webhook.id] === 'testing'}
                        >
                          <TestTube className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => toggleWebhook(webhook.id, !webhook.enabled)}
                        >
                          <Settings className="h-4 w-4" />
                        </Button>
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => deleteWebhook(webhook.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}

          {webhooks.length === 0 && (
            <Card>
              <CardContent className="text-center py-12">
                <Webhook className="h-12 w-12 text-slate-400 mx-auto mb-4" />
                <p className="text-slate-600">暂无Webhook配置</p>
                <p className="text-sm text-slate-500 mt-2">创建第一个Webhook开始接收通知</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* 发送日志 */}
        <TabsContent value="logs" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>发送统计</CardTitle>
              <CardDescription>查看Webhook发送统计信息</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">1,234</div>
                  <div className="text-sm text-slate-600">总发送次数</div>
                </div>
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-green-600">1,156</div>
                  <div className="text-sm text-slate-600">成功发送</div>
                </div>
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-red-600">78</div>
                  <div className="text-sm text-slate-600">发送失败</div>
                </div>
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-purple-600">93.7%</div>
                  <div className="text-sm text-slate-600">成功率</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>最近发送记录</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {[1,2,3,4,5].map((i) => (
                  <div key={i} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      <CheckCircle className="h-5 w-5 text-green-500" />
                      <div>
                        <p className="font-medium">钉钉群通知</p>
                        <p className="text-sm text-slate-600">AAPL 价格异动预警</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-slate-600">2分钟前</p>
                      <Badge variant="default">成功</Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default WebhookConfig;

