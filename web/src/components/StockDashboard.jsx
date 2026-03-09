import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { TrendingUp, TrendingDown, AlertTriangle, Activity, Plus, Settings, Database, Brain, Webhook, BarChart3, UserPlus } from 'lucide-react';
import DataSourceConfig from '@/components/DataSourceConfig';
import WatchlistManager from '@/components/WatchlistManager';
import AnalysisRecords from '@/components/AnalysisRecords';
import AIRecommendation from '@/components/AIRecommendation';
import AnalysisRules from '@/components/AnalysisRules';
import WebhookConfig from '@/components/WebhookConfig';


import { useNavigate } from 'react-router-dom';

const StockDashboard = () => {
  const navigate = useNavigate();
  const [showCreateUser, setShowCreateUser] = useState(false);
  const [showWebhookConfig, setShowWebhookConfig] = useState(false);
  const [newUsername, setNewUsername] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [createLoading, setCreateLoading] = useState(false);
  const [createMsg, setCreateMsg] = useState('');

  const handleCreateUser = async () => {
    if (!newUsername || !newPassword) {
      setCreateMsg('请填写用户名和密码');
      return;
    }
    setCreateLoading(true);
    setCreateMsg('');
    try {
      const res = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: newUsername, password: newPassword }),
      });
      const data = await res.json();
      if (data.success) {
        setCreateMsg('创建成功！');
        setNewUsername('');
        setNewPassword('');
        setTimeout(() => setShowCreateUser(false), 1000);
      } else {
        setCreateMsg(data.message || '创建失败');
      }
    } catch (e) {
      setCreateMsg('网络错误');
    } finally {
      setCreateLoading(false);
    }
  };


  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-7xl mx-auto">
        {/* 头部 */}
        <div className="mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">股票异动检测与智能预警系统</h1>
              <p className="text-gray-600 mt-1">实时监控股票异动，智能预警系统助您把握投资机会</p>
            </div>
            <div className="flex items-center space-x-4">
              <Button variant="ghost" size="sm" onClick={() => navigate('/')}>
                返回首页
              </Button>
              <Button variant="outline" size="sm" onClick={() => setShowWebhookConfig(true)}>
                <Webhook className="w-4 h-4 mr-1" />
                Webhook配置
              </Button>
              <Button variant="outline" size="sm" onClick={() => setShowCreateUser(true)}>
                <UserPlus className="w-4 h-4 mr-1" />
                创建用户
              </Button>
              <div className="flex items-center space-x-2">
                <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
                  <Database className="w-3 h-3 mr-1" />
                  API模式
                </Badge>
                <div className="flex items-center space-x-1">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="text-sm text-gray-600">前后端已连接</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* 创建用户弹窗 */}
        <Dialog open={showCreateUser} onOpenChange={setShowCreateUser}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>创建新用户</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label>用户名</Label>
                <Input
                  value={newUsername}
                  onChange={(e) => setNewUsername(e.target.value)}
                  placeholder="输入用户名"
                />
              </div>
              <div className="space-y-2">
                <Label>密码</Label>
                <Input
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder="输入密码"
                />
              </div>
              {createMsg && <p className="text-sm text-center text-red-500">{createMsg}</p>}
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setShowCreateUser(false)}>取消</Button>
              <Button onClick={handleCreateUser} disabled={createLoading}>
                {createLoading ? '创建中...' : '创建'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        <Dialog open={showWebhookConfig} onOpenChange={setShowWebhookConfig}>
          <DialogContent className="max-w-5xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Webhook配置</DialogTitle>
            </DialogHeader>
            <WebhookConfig />
          </DialogContent>
        </Dialog>

        {/* 标签页导航 */}
        <Tabs defaultValue="stocks" className="w-full">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="stocks" className="flex items-center space-x-2">
              <BarChart3 className="w-4 h-4" />
              <span>股票行情</span>
            </TabsTrigger>
            <TabsTrigger value="strategy" className="flex items-center space-x-2">
              <Brain className="w-4 h-4" />
              <span>智能推荐</span>
            </TabsTrigger>
            <TabsTrigger value="rules" className="flex items-center space-x-2">
              <Settings className="w-4 h-4" />
              <span>分析策略</span>
            </TabsTrigger>
            <TabsTrigger value="alerts" className="flex items-center space-x-2">
              <AlertTriangle className="w-4 h-4" />
              <span>分析记录</span>
            </TabsTrigger>
            <TabsTrigger value="datasource" className="flex items-center space-x-2">
              <Database className="w-4 h-4" />
              <span>数据源</span>
            </TabsTrigger>
          </TabsList>

          {/* 股票行情页面（自选股） */}
          <TabsContent
            value="stocks"
            className="space-y-6 data-[state=inactive]:hidden"
            forceMount={true}
          >
            <WatchlistManager />
          </TabsContent>

          {/* 分析策略页面 */}
          <TabsContent value="rules" className="space-y-6">
            <AnalysisRules />
          </TabsContent>

          {/* 数据源配置页面 */}
          <TabsContent value="datasource" className="space-y-6">
            <DataSourceConfig />
          </TabsContent>

          {/* 分析记录页面 */}
          <TabsContent value="alerts" className="space-y-6">
            <AnalysisRecords />
          </TabsContent>


          {/* 智能推荐页面 */}
          <TabsContent value="strategy" className="space-y-6">
            <AIRecommendation />
          </TabsContent>


        </Tabs>
      </div>
    </div>
  );
};

export default StockDashboard;

