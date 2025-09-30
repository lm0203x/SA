/**
 * 股票列表组件
 * 显示股票列表并支持选择查看K线图
 */

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Search, RefreshCw, TrendingUp, Activity } from 'lucide-react';
import { getStocks, syncStockList, getStockDailyData } from '@/services/api';
import StockChart from './StockChart';

export default function StockList() {
  const [stocks, setStocks] = useState([]);
  const [filteredStocks, setFilteredStocks] = useState([]);
  const [selectedStock, setSelectedStock] = useState(null);
  const [chartData, setChartData] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);
  const [chartLoading, setChartLoading] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const pageSize = 50;

  // 加载股票列表
  const loadStocks = async (pageNum = 1) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await getStocks({ 
        page: pageNum, 
        page_size: pageSize 
      });
      
      if (response.success) {
        setStocks(response.data || []);
        setFilteredStocks(response.data || []);
        setTotalPages(response.total_pages || 1);
        setPage(pageNum);
      } else {
        setError(response.message || '获取股票列表失败');
      }
    } catch (err) {
      setError(err.message || '网络请求失败');
      
      // 如果是数据源未配置的错误，提供友好提示
      if (err.message?.includes('没有激活的数据源')) {
        setError('请先在"数据源"标签页配置并激活Tushare数据源');
      }
    } finally {
      setLoading(false);
    }
  };

  // 同步股票列表
  const handleSync = async () => {
    setSyncing(true);
    setError(null);
    
    try {
      const response = await syncStockList(false);
      
      if (response.success) {
        // 同步成功后重新加载列表
        await loadStocks(1);
      } else {
        setError(response.message || '同步失败');
      }
    } catch (err) {
      setError(err.message || '同步失败');
    } finally {
      setSyncing(false);
    }
  };

  // 加载K线数据
  const loadChartData = async (stock) => {
    setSelectedStock(stock);
    setChartLoading(true);
    setError(null);
    
    try {
      const response = await getStockDailyData(stock.ts_code, { 
        limit: 60  // 最近60个交易日
      });
      
      if (response.success) {
        setChartData(response.data || []);
      } else {
        setError(response.message || '获取K线数据失败');
        setChartData([]);
      }
    } catch (err) {
      setError(err.message || '加载K线数据失败');
      setChartData([]);
    } finally {
      setChartLoading(false);
    }
  };

  // 搜索过滤
  useEffect(() => {
    if (!searchTerm.trim()) {
      setFilteredStocks(stocks);
      return;
    }

    const term = searchTerm.toLowerCase();
    const filtered = stocks.filter(stock => 
      stock.name?.toLowerCase().includes(term) ||
      stock.ts_code?.toLowerCase().includes(term) ||
      stock.symbol?.toLowerCase().includes(term) ||
      stock.industry?.toLowerCase().includes(term)
    );
    setFilteredStocks(filtered);
  }, [searchTerm, stocks]);

  // 初始化加载
  useEffect(() => {
    loadStocks(1);
  }, []);

  return (
    <div className="space-y-6">
      {/* 错误提示 */}
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 左侧：股票列表 */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <Activity className="h-5 w-5" />
                股票列表
              </CardTitle>
              <Button 
                size="sm" 
                variant="outline"
                onClick={handleSync}
                disabled={syncing}
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${syncing ? 'animate-spin' : ''}`} />
                {syncing ? '同步中...' : '同步'}
              </Button>
            </div>
          </CardHeader>
          
          <CardContent>
            {/* 搜索框 */}
            <div className="relative mb-4">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="搜索股票代码、名称、行业..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>

            {/* 股票列表 */}
            {loading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
                <p className="text-sm text-gray-500">加载中...</p>
              </div>
            ) : (
              <>
                <div className="space-y-2 max-h-[600px] overflow-y-auto">
                  {filteredStocks.map((stock) => (
                    <div
                      key={stock.ts_code}
                      onClick={() => loadChartData(stock)}
                      className={`p-3 rounded-lg cursor-pointer transition-all hover:bg-gray-50 border ${
                        selectedStock?.ts_code === stock.ts_code 
                          ? 'border-blue-500 bg-blue-50' 
                          : 'border-transparent'
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="font-medium">{stock.name}</div>
                          <div className="text-sm text-gray-500">{stock.ts_code}</div>
                        </div>
                        <Badge variant="outline" className="text-xs">
                          {stock.industry || '其他'}
                        </Badge>
                      </div>
                      {stock.area && (
                        <div className="text-xs text-gray-400 mt-1">📍 {stock.area}</div>
                      )}
                    </div>
                  ))}
                </div>

                {/* 分页 */}
                {totalPages > 1 && (
                  <div className="mt-4 flex items-center justify-between border-t pt-4">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => loadStocks(page - 1)}
                      disabled={page <= 1}
                    >
                      上一页
                    </Button>
                    <span className="text-sm text-gray-600">
                      {page} / {totalPages}
                    </span>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => loadStocks(page + 1)}
                      disabled={page >= totalPages}
                    >
                      下一页
                    </Button>
                  </div>
                )}
              </>
            )}
          </CardContent>
        </Card>

        {/* 右侧：K线图 */}
        <div className="lg:col-span-2">
          <StockChart 
            data={chartData}
            stockInfo={selectedStock}
            loading={chartLoading}
          />
        </div>
      </div>
    </div>
  );
}
