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
  
  // 预警规则
  getAlertRules,
  createAlertRule,
  updateAlertRule,
  deleteAlertRule,
  getAlertRecords,
};
