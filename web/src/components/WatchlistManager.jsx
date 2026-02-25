/**
 * 自选股管理组件
 * 用户添加自选股，只获取关注的股票数据
 */

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Star, Plus, Trash2, RefreshCw, TrendingUp } from 'lucide-react';
import {
  getWatchlist,
  addToWatchlist,
  removeFromWatchlist,
  syncAllWatchlist,
  getStockDailyData,
  updatePushConfig
} from '@/services/api';
import StockChart from './StockChart';
import StockIndicators from './StockIndicators';

export default function WatchlistManager() {
  const [watchlist, setWatchlist] = useState([]);
  const [selectedStock, setSelectedStock] = useState(null);
  const [chartData, setChartData] = useState([]);
  const [chartLoading, setChartLoading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  
  // 添加自选股表单
  const [showAddForm, setShowAddForm] = useState(false);
  const [newStock, setNewStock] = useState({
    ts_code: '',
    name: '',
    note: ''
  });

  // 加载自选股列表
  const loadWatchlist = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await getWatchlist();
      
      if (response.success) {
        setWatchlist(response.data || []);
      } else {
        setError(response.message || '获取自选股失败');
      }
    } catch (err) {
      setError(err.message || '网络请求失败');
    } finally {
      setLoading(false);
    }
  };

  // 添加自选股
  const handleAdd = async () => {
    if (!newStock.ts_code.trim()) {
      setError('请输入股票代码');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      const response = await addToWatchlist(newStock);
      
      if (response.success) {
        setSuccess(`已添加 ${newStock.ts_code}`);
        setNewStock({ ts_code: '', name: '', note: '' });
        setShowAddForm(false);
        await loadWatchlist();
        
        // 3秒后清除成功提示
        setTimeout(() => setSuccess(null), 3000);
      } else {
        setError(response.message || '添加失败');
      }
    } catch (err) {
      setError(err.message || '添加失败');
    } finally {
      setLoading(false);
    }
  };

  // 删除自选股
  const handleRemove = async (id, tsCode) => {
    // 创建现代化确认对话框
    const confirmDelete = () => {
      return new Promise((resolve) => {
        // 创建模态框元素
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4';
        modal.innerHTML = `
          <div class="bg-white rounded-2xl p-6 max-w-sm w-full shadow-2xl transform transition-all">
            <div class="text-center">
              <h3 class="text-lg font-semibold text-gray-900 mb-2">确认删除 ${tsCode}</h3>
              <p class="text-gray-600 mb-6">此操作无法撤销</p>
              <div class="flex gap-3 justify-center">
                <button id="cancel-btn" class="px-6 py-2 bg-gray-100 text-gray-700 rounded-xl font-medium hover:bg-gray-200 transition-all duration-200 min-w-[80px]">
                  取消
                </button>
                <button id="confirm-btn" class="px-6 py-2 bg-blue-500 text-white rounded-xl font-medium hover:bg-blue-600 transition-all duration-200 min-w-[80px]">
                  删除
                </button>
              </div>
            </div>
          </div>
        `;
        
        document.body.appendChild(modal);
        
        // 绑定事件
        modal.querySelector('#cancel-btn').onclick = () => {
          document.body.removeChild(modal);
          resolve(false);
        };
        
        modal.querySelector('#confirm-btn').onclick = () => {
          document.body.removeChild(modal);
          resolve(true);
        };
        
        // 点击背景关闭
        modal.onclick = (e) => {
          if (e.target === modal) {
            document.body.removeChild(modal);
            resolve(false);
          }
        };
      });
    };
    
    const confirmed = await confirmDelete();
    if (!confirmed) return;
    
    try {
      const response = await removeFromWatchlist(id);
      
      if (response.success) {
        setSuccess(`已删除 ${tsCode}`);
        await loadWatchlist();
        
        // 如果删除的是当前选中的股票，清空图表
        if (selectedStock?.ts_code === tsCode) {
          setSelectedStock(null);
          setChartData([]);
        }
        
        setTimeout(() => setSuccess(null), 3000);
      } else {
        setError(response.message || '删除失败');
      }
    } catch (err) {
      setError(err.message || '删除失败');
    }
  };

  // 更新推送配置
  const handlePushConfigChange = async (stockId, field, value) => {
    try {
      const stock = watchlist.find(s => s.id === stockId);
      if (!stock) return;

      const config = {
        push_enabled: field === 'push_enabled' ? value : stock.push_enabled,
        push_time: field === 'push_time' ? value : stock.push_time
      };

      const response = await updatePushConfig(stockId, config);

      if (response.success) {
        // 更新本地状态
        setWatchlist(watchlist.map(s =>
          s.id === stockId ? { ...s, ...config } : s
        ));
      } else {
        setError(response.message || '更新推送配置失败');
      }
    } catch (err) {
      setError(err.message || '更新推送配置失败');
    }
  };

  // 同步所有自选股数据
  const handleSyncAll = async () => {
    setSyncing(true);
    setError(null);
    
    try {
      const response = await syncAllWatchlist({ limit: 60 });
      
      if (response.success) {
        setSuccess(response.message);
        setTimeout(() => setSuccess(null), 3000);
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
      const response = await getStockDailyData(stock.ts_code, { limit: 60 });
      
      if (response.success) {
        setChartData(response.data || []);
        
        if (!response.data || response.data.length === 0) {
          setError('暂无K线数据，请先同步该股票数据');
        }
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

  // 初始化加载
  useEffect(() => {
    loadWatchlist();
  }, []);

  return (
    <div className="space-y-6">
      {/* 错误和成功提示 */}
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

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 左侧：自选股列表 */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <Star className="h-5 w-5 text-yellow-500" />
                我的自选股
                {watchlist.length > 0 && (
                  <Badge variant="secondary">{watchlist.length}</Badge>
                )}
              </CardTitle>
              <div className="flex gap-2">
                <Button 
                  size="sm" 
                  variant="outline"
                  onClick={handleSyncAll}
                  disabled={syncing || watchlist.length === 0}
                >
                  <RefreshCw className={`h-4 w-4 mr-1 ${syncing ? 'animate-spin' : ''}`} />
                  同步
                </Button>
                <Button 
                  size="sm"
                  onClick={() => setShowAddForm(!showAddForm)}
                >
                  <Plus className="h-4 w-4 mr-1" />
                  添加
                </Button>
              </div>
            </div>
          </CardHeader>
          
          <CardContent>
            {/* 添加表单 */}
            {showAddForm && (
              <div className="mb-4 p-4 border rounded-lg bg-gray-50 space-y-3">
                <div>
                  <label className="text-sm font-medium">股票代码 *</label>
                  <Input
                    placeholder="例如: 000001.SZ"
                    value={newStock.ts_code}
                    onChange={(e) => setNewStock({...newStock, ts_code: e.target.value.toUpperCase()})}
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    格式：000001.SZ (深圳) 或 600000.SH (上海)
                  </p>
                </div>
                <div>
                  <label className="text-sm font-medium">股票名称（选填）</label>
                  <Input
                    placeholder="例如: 平安银行"
                    value={newStock.name}
                    onChange={(e) => setNewStock({...newStock, name: e.target.value})}
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">备注（选填）</label>
                  <Input
                    placeholder="个人备注"
                    value={newStock.note}
                    onChange={(e) => setNewStock({...newStock, note: e.target.value})}
                  />
                </div>
                <div className="flex gap-2">
                  <Button 
                    size="sm" 
                    onClick={handleAdd}
                    disabled={loading}
                  >
                    确认添加
                  </Button>
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => {
                      setShowAddForm(false);
                      setNewStock({ ts_code: '', name: '', note: '' });
                    }}
                  >
                    取消
                  </Button>
                </div>
              </div>
            )}

            {/* 自选股列表 */}
            {loading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
                <p className="text-sm text-gray-500">加载中...</p>
              </div>
            ) : watchlist.length === 0 ? (
              <div className="text-center py-12 text-gray-500">
                <Star className="h-12 w-12 mx-auto mb-3 text-gray-300" />
                <p className="text-sm">暂无自选股</p>
                <p className="text-xs mt-1">点击"添加"按钮添加您关注的股票</p>
              </div>
            ) : (
              <div className="space-y-2 max-h-[600px] overflow-y-auto">
                {watchlist.map((stock) => (
                  <div
                    key={stock.id}
                    className={`p-3 rounded-lg border transition-all ${
                      selectedStock?.ts_code === stock.ts_code
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:bg-gray-50'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div
                        className="flex-1 cursor-pointer"
                        onClick={() => loadChartData(stock)}
                      >
                        <div className="font-medium">{stock.name || stock.ts_code}</div>
                        <div className="text-sm text-gray-500">{stock.ts_code}</div>
                        {stock.note && (
                          <div className="text-xs text-gray-400 mt-1">💡 {stock.note}</div>
                        )}
                        {stock.last_sync && (
                          <div className="text-xs text-gray-400 mt-1">
                            🔄 {new Date(stock.last_sync).toLocaleString('zh-CN')}
                          </div>
                        )}
                      </div>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => handleRemove(stock.id, stock.ts_code)}
                      >
                        <Trash2 className="h-4 w-4 text-red-500" />
                      </Button>
                    </div>

                    {/* AI 推送配置 */}
                    <div className="mt-2 pt-2 border-t border-gray-100">
                      <div className="flex items-center gap-2">
                        <label className="flex items-center gap-2 text-xs cursor-pointer">
                          <input
                            type="checkbox"
                            checked={stock.push_enabled || false}
                            onChange={(e) => handlePushConfigChange(stock.id, 'push_enabled', e.target.checked)}
                            className="w-4 h-4 text-blue-600 rounded"
                          />
                          <span className={stock.push_enabled ? 'text-blue-600 font-medium' : 'text-gray-500'}>
                            AI推送
                          </span>
                        </label>
                        {stock.push_enabled && (
                          <input
                            type="time"
                            value={stock.push_time || '08:30'}
                            onChange={(e) => handlePushConfigChange(stock.id, 'push_time', e.target.value)}
                            className="text-xs px-2 py-1 border rounded"
                          />
                        )}
                        {stock.push_enabled && stock.last_push_at && (
                          <span className="text-xs text-gray-400">
                            已推送: {new Date(stock.last_push_at).toLocaleString('zh-CN')}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* 右侧：K线图和指标数据 */}
        <div className="lg:col-span-2 space-y-6">
          {/* K线图 */}
          <StockChart 
            data={chartData}
            stockInfo={selectedStock}
            loading={chartLoading}
          />
          
          {/* 股票指标 */}
          <StockIndicators 
            stockInfo={selectedStock}
            loading={chartLoading}
          />
        </div>
      </div>
    </div>
  );
}
