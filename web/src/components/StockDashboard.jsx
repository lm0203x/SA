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
import AlertRules from '@/components/AlertRules';
import AlertRecords from '@/components/AlertRecords';


const StockDashboard = () => {


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

        {/* 标签页导航 */}
        <Tabs defaultValue="stocks" className="w-full">
          <TabsList className="grid w-full grid-cols-6">
            <TabsTrigger value="stocks" className="flex items-center space-x-2">
              <BarChart3 className="w-4 h-4" />
              <span>股票行情</span>
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
            <TabsTrigger value="webhook" className="flex items-center space-x-2">
              <Webhook className="w-4 h-4" />
              <span>Webhook</span>
            </TabsTrigger>
            <TabsTrigger value="strategy" className="flex items-center space-x-2">
              <Brain className="w-4 h-4" />
              <span>策略配置</span>
            </TabsTrigger>
          </TabsList>

          {/* 股票行情页面（自选股） */}
          <TabsContent value="stocks" className="space-y-6">
            <WatchlistManager />
          </TabsContent>

          {/* 预警规则页面 */}
          <TabsContent value="rules" className="space-y-6">
            <AlertRules />
          </TabsContent>

          {/* 数据源配置页面 */}
          <TabsContent value="datasource" className="space-y-6">
            <DataSourceConfig />
          </TabsContent>

          {/* 预警记录页面 */}
          <TabsContent value="alerts" className="space-y-6">
            <AlertRecords />
          </TabsContent>


          {/* 策略配置页面 */}
          <TabsContent value="strategy" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>策略配置</CardTitle>
                <CardDescription>配置智能分析策略和风险控制参数</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-12">
                  <Brain className="w-16 h-16 mx-auto text-gray-400 mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">策略配置功能开发中...</h3>
                  <p className="text-gray-500 mb-4">
                    将支持多种量化分析策略和智能预警算法
                  </p>
                  <div className="space-y-2 text-sm text-gray-600">
                    <div>• 价格动量策略</div>
                    <div>• 均值回归策略</div>
                    <div>• 成交量分析策略</div>
                    <div>• 技术指标策略</div>
                    <div>• 风险控制参数</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Webhook配置页面 */}
          <TabsContent value="webhook" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Webhook通知配置</CardTitle>
                <CardDescription>配置预警消息的推送渠道和格式</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-12">
                  <Webhook className="w-16 h-16 mx-auto text-gray-400 mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Webhook配置功能开发中...</h3>
                  <p className="text-gray-500 mb-4">
                    将支持多种通知渠道和自定义消息格式
                  </p>
                  <div className="space-y-2 text-sm text-gray-600">
                    <div>• 钉钉机器人通知</div>
                    <div>• 企业微信通知</div>
                    <div>• Slack通知</div>
                    <div>• Telegram通知</div>
                    <div>• 邮件通知</div>
                    <div>• 自定义Webhook</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default StockDashboard;

