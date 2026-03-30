import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import UserManagement from '@/components/UserManagement';
import WebhookConfig from '@/components/WebhookConfig';
import DataSourceConfig from '@/components/DataSourceConfig';
import OperationLogList from '@/components/OperationLogList';

export default function AdminPage() {
  const navigate = useNavigate();

  useEffect(() => {
    const rawUser = window.localStorage.getItem('user');
    const user = rawUser ? JSON.parse(rawUser) : null;
    if (!user || user.username !== 'admin') {
      navigate('/dashboard');
    }
  }, [navigate]);

  return (
    <div className="min-h-screen bg-slate-50 p-4">
      <div className="mx-auto max-w-7xl space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-slate-900">管理员页面</h1>
            <p className="mt-1 text-slate-600">集中管理用户、Webhook、数据源，并查看系统操作日志。</p>
          </div>
          <Button variant="outline" onClick={() => navigate('/dashboard')}>
            返回工作台
          </Button>
        </div>

        <Tabs defaultValue="users" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="users">用户管理</TabsTrigger>
            <TabsTrigger value="webhooks">Webhook配置</TabsTrigger>
            <TabsTrigger value="datasources">数据源配置</TabsTrigger>
            <TabsTrigger value="logs">操作日志</TabsTrigger>
          </TabsList>

          <TabsContent value="users">
            <UserManagement />
          </TabsContent>
          <TabsContent value="webhooks">
            <WebhookConfig />
          </TabsContent>
          <TabsContent value="datasources">
            <DataSourceConfig />
          </TabsContent>
          <TabsContent value="logs">
            <OperationLogList />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
