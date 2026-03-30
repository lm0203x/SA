import React, { useState, useEffect } from 'react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { AlertTriangle, Settings, Database, Brain, Shield, BarChart3 } from 'lucide-react';
import WatchlistManager from '@/components/WatchlistManager';
import AnalysisRecords from '@/components/AnalysisRecords';
import AIRecommendation from '@/components/AIRecommendation';
import AnalysisRules from '@/components/AnalysisRules';

import { useNavigate } from 'react-router-dom';

const StockDashboard = () => {
  const navigate = useNavigate();
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    const rawUser = window.localStorage.getItem('user');
    const user = rawUser ? JSON.parse(rawUser) : null;
    setIsAdmin(user?.username === 'admin');
  }, []);


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
              {isAdmin && (
                <Button variant="outline" size="sm" onClick={() => navigate('/admin')}>
                  <Shield className="w-4 h-4 mr-1" />
                  管理员页面
                </Button>
              )}
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
          <TabsList className="grid w-full grid-cols-4">
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

