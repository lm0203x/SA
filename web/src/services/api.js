/**
 * API服务层 - 封装所有后端API调用
 */

const API_BASE_URL = 'http://localhost:5000/api';

/**
 * 通用的API请求函数
 */
async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
    },
    ...options,
  };

  try {
    const response = await fetch(url, defaultOptions);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`API请求失败 [${endpoint}]:`, error);
    throw error;
  }
}

// ==================== 数据源管理API ====================

/**
 * 获取所有数据源配置
 */
export async function getDataSources() {
  return apiRequest('/datasources');
}

/**
 * 创建数据源配置
 */
export async function createDataSource(data) {
  return apiRequest('/datasources', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

/**
 * 更新数据源配置
 */
export async function updateDataSource(id, data) {
  return apiRequest(`/datasources/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

/**
 * 删除数据源配置
 */
export async function deleteDataSource(id) {
  return apiRequest(`/datasources/${id}`, {
    method: 'DELETE',
  });
}

/**
 * 测试数据源连接
 */
export async function testDataSourceConnection(id) {
  return apiRequest(`/datasources/${id}/test`, {
    method: 'POST',
  });
}

/**
 * 获取激活的数据源
 */
export async function getActiveDataSource() {
  return apiRequest('/datasources/active');
}

// ==================== 股票数据API ====================

/**
 * 获取股票列表
 */
export async function getStocks(params = {}) {
  const queryString = new URLSearchParams(params).toString();
  const endpoint = queryString ? `/stocks?${queryString}` : '/stocks';
  return apiRequest(endpoint);
}

/**
 * 获取实时行情
 */
export async function getRealtimeQuotes(symbols) {
  return apiRequest('/stocks/realtime', {
    method: 'POST',
    body: JSON.stringify({ symbols }),
  });
}

/**
 * 获取股票日线数据
 */
export async function getStockDailyData(tsCode, params = {}) {
  const queryString = new URLSearchParams(params).toString();
  const endpoint = queryString 
    ? `/stocks/${tsCode}/daily?${queryString}` 
    : `/stocks/${tsCode}/daily`;
  return apiRequest(endpoint);
}

/**
 * 同步股票列表
 */
export async function syncStockList(forceUpdate = false) {
  return apiRequest('/stocks/sync', {
    method: 'POST',
    body: JSON.stringify({ force_update: forceUpdate }),
  });
}

/**
 * 同步股票日线数据
 */
export async function syncStockDailyData(tsCode, params = {}) {
  return apiRequest(`/stocks/${tsCode}/daily/sync`, {
    method: 'POST',
    body: JSON.stringify(params),
  });
}

// ==================== 自选股API ====================

/**
 * 获取自选股列表
 */
export async function getWatchlist() {
  return apiRequest('/watchlist');
}

/**
 * 添加自选股
 */
export async function addToWatchlist(data) {
  return apiRequest('/watchlist', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

/**
 * 删除自选股
 */
export async function removeFromWatchlist(id) {
  return apiRequest(`/watchlist/${id}`, {
    method: 'DELETE',
  });
}

/**
 * 更新自选股备注
 */
export async function updateWatchlist(id, data) {
  return apiRequest(`/watchlist/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

/**
 * 同步单个自选股数据
 */
export async function syncWatchlistStock(id, params = {}) {
  return apiRequest(`/watchlist/${id}/sync`, {
    method: 'POST',
    body: JSON.stringify(params),
  });
}

/**
 * 同步所有自选股数据
 */
export async function syncAllWatchlist(params = {}) {
  return apiRequest('/watchlist/sync-all', {
    method: 'POST',
    body: JSON.stringify(params),
  });
}

// ==================== 预警规则API ====================

/**
 * 获取所有预警规则
 */
export async function getAlertRules() {
  return apiRequest('/rules');
}

/**
 * 创建预警规则
 */
export async function createAlertRule(data) {
  return apiRequest('/rules', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

/**
 * 更新预警规则
 */
export async function updateAlertRule(id, data) {
  return apiRequest(`/rules/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

/**
 * 删除预警规则
 */
export async function deleteAlertRule(id) {
  return apiRequest(`/rules/${id}`, {
    method: 'DELETE',
  });
}

/**
 * 获取预警记录
 */
export async function getAlertRecords(limit = 50) {
  return apiRequest(`/alerts?limit=${limit}`);
}

// ==================== 导出所有API ====================

export default {
  // 数据源
  getDataSources,
  createDataSource,
  updateDataSource,
  deleteDataSource,
  testDataSourceConnection,
  getActiveDataSource,
  
  // 股票数据
  getStocks,
  getRealtimeQuotes,
  getStockDailyData,
  syncStockList,
  syncStockDailyData,
  
  // 自选股
  getWatchlist,
  addToWatchlist,
  removeFromWatchlist,
  updateWatchlist,
  syncWatchlistStock,
  syncAllWatchlist,
  
  // 预警规则
  getAlertRules,
  createAlertRule,
  updateAlertRule,
  deleteAlertRule,
  getAlertRecords,
};
