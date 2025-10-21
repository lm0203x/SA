/**
 * 股票指标展示组件
 * 显示每日指标和资金流向数据
 */

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { TrendingUp, TrendingDown, RefreshCw, DollarSign, BarChart3 } from 'lucide-react';
import { 
  getStockDailyBasic, 
  getStockMoneyflow,
  syncStockDailyBasic,
  syncStockMoneyflow
} from '@/services/api';

export default function StockIndicators({ stockInfo, loading: parentLoading }) {
  const [basicData, setBasicData] = useState([]);
  const [moneyflowData, setMoneyflowData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [error, setError] = useState(null);

  // 加载指标数据
  const loadIndicatorData = async (stock) => {
    if (!stock?.ts_code) return;
    
    setLoading(true);
    setError(null);
    
    try {
      // 并行获取每日指标和资金流向数据
      const [basicResponse, moneyflowResponse] = await Promise.all([
        getStockDailyBasic(stock.ts_code, { limit: 30 }),
        getStockMoneyflow(stock.ts_code, { limit: 30 })
      ]);
      
      if (basicResponse.success) {
        setBasicData(basicResponse.data || []);
      } else {
        console.warn('获取每日指标失败:', basicResponse.message);
      }
      
      if (moneyflowResponse.success) {
        setMoneyflowData(moneyflowResponse.data || []);
      } else {
        console.warn('获取资金流向失败:', moneyflowResponse.message);
      }
      
      // 如果两个都没有数据，显示提示
      if ((!basicResponse.success || !basicResponse.data?.length) && 
          (!moneyflowResponse.success || !moneyflowResponse.data?.length)) {
        setError('暂无指标数据，请先同步该股票的指标数据');
      }
      
    } catch (err) {
      setError(err.message || '加载指标数据失败');
    } finally {
      setLoading(false);
    }
  };

  // 同步指标数据
  const handleSyncData = async () => {
    if (!stockInfo?.ts_code) return;
    
    setSyncing(true);
    setError(null);
    
    try {
      // 并行同步两种数据
      const [basicResult, moneyflowResult] = await Promise.all([
        syncStockDailyBasic(stockInfo.ts_code, { limit: 30 }),
        syncStockMoneyflow(stockInfo.ts_code, { limit: 30 })
      ]);
      
      let successCount = 0;
      let messages = [];
      
      if (basicResult.success) {
        successCount++;
        messages.push(`每日指标: 新增${basicResult.added || 0}条`);
      }
      
      if (moneyflowResult.success) {
        successCount++;
        messages.push(`资金流向: 新增${moneyflowResult.added || 0}条`);
      }
      
      if (successCount > 0) {
        // 重新加载数据
        await loadIndicatorData(stockInfo);
      } else {
        setError('同步失败，请检查数据源配置');
      }
      
    } catch (err) {
      setError(err.message || '同步失败');
    } finally {
      setSyncing(false);
    }
  };

  // 当股票信息变化时加载数据
  useEffect(() => {
    if (stockInfo) {
      loadIndicatorData(stockInfo);
    } else {
      setBasicData([]);
      setMoneyflowData([]);
      setError(null);
    }
  }, [stockInfo]);

  // 格式化数值
  const formatNumber = (num, decimals = 2) => {
    if (num === null || num === undefined) return '--';
    if (typeof num !== 'number') return num;
    
    if (Math.abs(num) >= 1e8) {
      return (num / 1e8).toFixed(decimals) + '亿';
    } else if (Math.abs(num) >= 1e4) {
      return (num / 1e4).toFixed(decimals) + '万';
    }
    return num.toFixed(decimals);
  };

  // 获取最新数据
  const latestBasic = basicData[0] || {};
  const latestMoneyflow = moneyflowData[0] || {};

  if (parentLoading || loading) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
            <p className="text-gray-600">加载指标数据中...</p>
          </div>
        </div>
      </Card>
    );
  }

  if (!stockInfo) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-center text-gray-500">
            <BarChart3 className="w-12 h-12 mx-auto mb-3 text-gray-300" />
            <p className="text-lg mb-2">📊 股票指标</p>
            <p className="text-sm">请选择股票查看指标数据</p>
          </div>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {/* 错误提示 */}
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* 每日指标卡片 */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5 text-blue-500" />
              每日指标
              {basicData.length > 0 && (
                <Badge variant="secondary">{basicData.length}天</Badge>
              )}
            </CardTitle>
            <Button 
              size="sm" 
              variant="outline"
              onClick={handleSyncData}
              disabled={syncing}
            >
              <RefreshCw className={`h-4 w-4 mr-1 ${syncing ? 'animate-spin' : ''}`} />
              同步数据
            </Button>
          </div>
        </CardHeader>
        
        <CardContent>
          {basicData.length > 0 ? (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-3 bg-gray-50 rounded-lg">
                <div className="text-sm text-gray-500 mb-1">换手率</div>
                <div className="text-lg font-semibold text-blue-600">
                  {formatNumber(latestBasic.turnover_rate)}%
                </div>
              </div>
              
              <div className="text-center p-3 bg-gray-50 rounded-lg">
                <div className="text-sm text-gray-500 mb-1">量比</div>
                <div className="text-lg font-semibold text-green-600">
                  {formatNumber(latestBasic.volume_ratio)}
                </div>
              </div>
              
              <div className="text-center p-3 bg-gray-50 rounded-lg">
                <div className="text-sm text-gray-500 mb-1">市盈率</div>
                <div className="text-lg font-semibold text-purple-600">
                  {formatNumber(latestBasic.pe)}
                </div>
              </div>
              
              <div className="text-center p-3 bg-gray-50 rounded-lg">
                <div className="text-sm text-gray-500 mb-1">市净率</div>
                <div className="text-lg font-semibold text-orange-600">
                  {formatNumber(latestBasic.pb)}
                </div>
              </div>
              
              <div className="text-center p-3 bg-gray-50 rounded-lg">
                <div className="text-sm text-gray-500 mb-1">总市值</div>
                <div className="text-lg font-semibold text-red-600">
                  {formatNumber(latestBasic.total_mv)}
                </div>
              </div>
              
              <div className="text-center p-3 bg-gray-50 rounded-lg">
                <div className="text-sm text-gray-500 mb-1">流通市值</div>
                <div className="text-lg font-semibold text-indigo-600">
                  {formatNumber(latestBasic.circ_mv)}
                </div>
              </div>
              
              <div className="text-center p-3 bg-gray-50 rounded-lg">
                <div className="text-sm text-gray-500 mb-1">市销率</div>
                <div className="text-lg font-semibold text-teal-600">
                  {formatNumber(latestBasic.ps)}
                </div>
              </div>
              
              <div className="text-center p-3 bg-gray-50 rounded-lg">
                <div className="text-sm text-gray-500 mb-1">股息率</div>
                <div className="text-lg font-semibold text-pink-600">
                  {formatNumber(latestBasic.dv_ratio)}%
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <p>暂无每日指标数据</p>
              <p className="text-sm mt-1">点击"同步数据"获取最新指标</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 资金流向卡片 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <DollarSign className="h-5 w-5 text-green-500" />
            资金流向
            {moneyflowData.length > 0 && (
              <Badge variant="secondary">{moneyflowData.length}天</Badge>
            )}
          </CardTitle>
        </CardHeader>
        
        <CardContent>
          {moneyflowData.length > 0 ? (
            <div className="space-y-4">
              {/* 净流入总览 */}
              <div className="flex items-center justify-center p-4 bg-gradient-to-r from-green-50 to-blue-50 rounded-lg">
                <div className="text-center">
                  <div className="text-sm text-gray-600 mb-1">净流入额</div>
                  <div className={`text-2xl font-bold flex items-center gap-1 ${
                    latestMoneyflow.net_mf_amount >= 0 ? 'text-red-600' : 'text-green-600'
                  }`}>
                    {latestMoneyflow.net_mf_amount >= 0 ? (
                      <TrendingUp className="w-5 h-5" />
                    ) : (
                      <TrendingDown className="w-5 h-5" />
                    )}
                    {formatNumber(latestMoneyflow.net_mf_amount)}万
                  </div>
                </div>
              </div>
              
              {/* 资金流向详情 */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-3">
                  <h4 className="font-medium text-gray-700">买入资金</h4>
                  
                  <div className="flex justify-between items-center p-2 bg-red-50 rounded">
                    <span className="text-sm text-gray-600">特大单</span>
                    <span className="font-medium text-red-600">
                      {formatNumber(latestMoneyflow.buy_elg_amount)}万
                    </span>
                  </div>
                  
                  <div className="flex justify-between items-center p-2 bg-orange-50 rounded">
                    <span className="text-sm text-gray-600">大单</span>
                    <span className="font-medium text-orange-600">
                      {formatNumber(latestMoneyflow.buy_lg_amount)}万
                    </span>
                  </div>
                  
                  <div className="flex justify-between items-center p-2 bg-yellow-50 rounded">
                    <span className="text-sm text-gray-600">中单</span>
                    <span className="font-medium text-yellow-600">
                      {formatNumber(latestMoneyflow.buy_md_amount)}万
                    </span>
                  </div>
                  
                  <div className="flex justify-between items-center p-2 bg-blue-50 rounded">
                    <span className="text-sm text-gray-600">小单</span>
                    <span className="font-medium text-blue-600">
                      {formatNumber(latestMoneyflow.buy_sm_amount)}万
                    </span>
                  </div>
                </div>
                
                <div className="space-y-3">
                  <h4 className="font-medium text-gray-700">卖出资金</h4>
                  
                  <div className="flex justify-between items-center p-2 bg-gray-50 rounded">
                    <span className="text-sm text-gray-600">特大单</span>
                    <span className="font-medium text-gray-600">
                      {formatNumber(latestMoneyflow.sell_elg_amount)}万
                    </span>
                  </div>
                  
                  <div className="flex justify-between items-center p-2 bg-gray-50 rounded">
                    <span className="text-sm text-gray-600">大单</span>
                    <span className="font-medium text-gray-600">
                      {formatNumber(latestMoneyflow.sell_lg_amount)}万
                    </span>
                  </div>
                  
                  <div className="flex justify-between items-center p-2 bg-gray-50 rounded">
                    <span className="text-sm text-gray-600">中单</span>
                    <span className="font-medium text-gray-600">
                      {formatNumber(latestMoneyflow.sell_md_amount)}万
                    </span>
                  </div>
                  
                  <div className="flex justify-between items-center p-2 bg-gray-50 rounded">
                    <span className="text-sm text-gray-600">小单</span>
                    <span className="font-medium text-gray-600">
                      {formatNumber(latestMoneyflow.sell_sm_amount)}万
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <p>暂无资金流向数据</p>
              <p className="text-sm mt-1">点击"同步数据"获取最新资金流向</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 数据说明 */}
      {(basicData.length > 0 || moneyflowData.length > 0) && (
        <div className="text-xs text-gray-500 space-y-1">
          {basicData.length > 0 && (
            <p>📊 每日指标数据: 最近{basicData.length}个交易日</p>
          )}
          {moneyflowData.length > 0 && (
            <p>💰 资金流向数据: 最近{moneyflowData.length}个交易日</p>
          )}
          <p>💾 数据来源: Tushare Pro (2120积分权限)</p>
        </div>
      )}
    </div>
  );
}
