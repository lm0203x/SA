import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { TrendingUp, TrendingDown, AlertTriangle, Activity, Plus, Settings, Database, Brain, Webhook, BarChart3 } from 'lucide-react';
import DataSourceConfig from '@/components/DataSourceConfig';
import WatchlistManager from '@/components/WatchlistManager';
import AlertManagement from '@/components/AlertManagement';
import AlertRecords from '@/components/AlertRecords';
import AIRecommendation from '@/components/AIRecommendation';


import { useNavigate } from 'react-router-dom';

const StockDashboard = () => {
  const navigate = useNavigate();


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
              <span>预警规则</span>
            </TabsTrigger>
            <TabsTrigger value="alerts" className="flex items-center space-x-2">
              <AlertTriangle className="w-4 h-4" />
              <span>预警记录</span>
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

          {/* 预警规则页面 */}
          <TabsContent value="rules" className="space-y-6">
            <AlertManagement />
          </TabsContent>

          {/* 数据源配置页面 */}
          <TabsContent value="datasource" className="space-y-6">
            <DataSourceConfig />
          </TabsContent>

          {/* 预警记录页面 */}
          <TabsContent value="alerts" className="space-y-6">
            <AlertRecords />
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

