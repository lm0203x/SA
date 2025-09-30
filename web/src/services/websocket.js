/**
 * WebSocket服务 - 管理实时数据连接
 */

import { io } from 'socket.io-client';

const WS_URL = 'http://localhost:5000';

class WebSocketService {
  constructor() {
    this.socket = null;
    this.listeners = new Map();
    this.isConnected = false;
  }

  /**
   * 连接WebSocket服务器
   */
  connect() {
    if (this.socket && this.isConnected) {
      console.log('WebSocket已连接');
      return;
    }

    console.log('正在连接WebSocket...');
    
    this.socket = io(WS_URL, {
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: 5,
    });

    // 连接成功
    this.socket.on('connect', () => {
      console.log('✅ WebSocket连接成功');
      this.isConnected = true;
      this.notifyListeners('connected', { client_id: this.socket.id });
    });

    // 连接失败
    this.socket.on('connect_error', (error) => {
      console.error('❌ WebSocket连接失败:', error);
      this.isConnected = false;
      this.notifyListeners('connect_error', { error: error.message });
    });

    // 断开连接
    this.socket.on('disconnect', (reason) => {
      console.warn('⚠️ WebSocket断开连接:', reason);
      this.isConnected = false;
      this.notifyListeners('disconnected', { reason });
    });

    // 接收服务器消息
    this.socket.on('connected', (data) => {
      console.log('收到服务器欢迎消息:', data);
      this.notifyListeners('server_connected', data);
    });

    // 市场数据更新
    this.socket.on('market_data_update', (data) => {
      this.notifyListeners('market_data_update', data);
    });

    // 风险预警
    this.socket.on('risk_alert', (data) => {
      this.notifyListeners('risk_alert', data);
    });

    // 订阅确认
    this.socket.on('subscribed', (data) => {
      console.log('订阅成功:', data);
      this.notifyListeners('subscribed', data);
    });

    // 取消订阅确认
    this.socket.on('unsubscribed', (data) => {
      console.log('取消订阅成功:', data);
      this.notifyListeners('unsubscribed', data);
    });

    // Pong响应
    this.socket.on('pong', (data) => {
      this.notifyListeners('pong', data);
    });
  }

  /**
   * 断开连接
   */
  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.isConnected = false;
      console.log('WebSocket已断开');
    }
  }

  /**
   * 订阅数据
   * @param {string} type - 订阅类型 (market_data, indicators, signals, monitor, risk_alerts, portfolio, news)
   * @param {object} params - 订阅参数
   */
  subscribe(type, params = {}) {
    if (!this.isConnected) {
      console.warn('WebSocket未连接，无法订阅');
      return;
    }

    console.log(`订阅 ${type}:`, params);
    this.socket.emit('subscribe', { type, params });
  }

  /**
   * 取消订阅
   * @param {string} type - 订阅类型
   * @param {object} params - 订阅参数
   */
  unsubscribe(type, params = {}) {
    if (!this.isConnected) {
      return;
    }

    console.log(`取消订阅 ${type}:`, params);
    this.socket.emit('unsubscribe', { type, params });
  }

  /**
   * 发送心跳
   */
  ping() {
    if (this.isConnected) {
      this.socket.emit('ping');
    }
  }

  /**
   * 添加事件监听器
   * @param {string} event - 事件名称
   * @param {function} callback - 回调函数
   * @returns {function} 取消监听的函数
   */
  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event).add(callback);

    // 返回取消监听的函数
    return () => {
      const callbacks = this.listeners.get(event);
      if (callbacks) {
        callbacks.delete(callback);
      }
    };
  }

  /**
   * 移除事件监听器
   * @param {string} event - 事件名称
   * @param {function} callback - 回调函数（可选，不传则移除所有）
   */
  off(event, callback) {
    if (!callback) {
      this.listeners.delete(event);
    } else {
      const callbacks = this.listeners.get(event);
      if (callbacks) {
        callbacks.delete(callback);
      }
    }
  }

  /**
   * 通知所有监听器
   * @param {string} event - 事件名称
   * @param {any} data - 事件数据
   */
  notifyListeners(event, data) {
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      callbacks.forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`事件监听器执行错误 [${event}]:`, error);
        }
      });
    }
  }

  /**
   * 获取连接状态
   */
  getConnectionStatus() {
    return {
      isConnected: this.isConnected,
      socketId: this.socket?.id,
    };
  }
}

// 导出单例
const wsService = new WebSocketService();
export default wsService;
