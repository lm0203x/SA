/**
 * K线图组件
 * 使用Recharts实现股票K线图展示
 */

import React from 'react';
import {
  ComposedChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { Card } from '@/components/ui/card';

/**
 * 自定义Tooltip
 */
const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;

    return (
      <div className="bg-white border border-gray-300 p-3 rounded shadow-lg">
        <p className="font-semibold mb-2">{data.trade_date}</p>
        <div className="space-y-1 text-sm">
          <p className="text-gray-700">开盘: <span className="font-medium">{data.open?.toFixed(2)}</span></p>
          <p className="text-gray-700">收盘: <span className="font-medium">{data.close?.toFixed(2)}</span></p>
          <p className="text-gray-700">最高: <span className="font-medium text-red-600">{data.high?.toFixed(2)}</span></p>
          <p className="text-gray-700">最低: <span className="font-medium text-green-600">{data.low?.toFixed(2)}</span></p>
          <p className="text-gray-700">成交量: <span className="font-medium">{(data.vol / 100)?.toFixed(0)}手</span></p>
          <p className={`font-medium ${data.pct_chg >= 0 ? 'text-red-600' : 'text-green-600'}`}>
            涨跌幅: {data.pct_chg >= 0 ? '+' : ''}{data.pct_chg?.toFixed(2)}%
          </p>
        </div>
      </div>
    );
  }
  return null;
};

/**
 * K线图组件
 */
export default function StockChart({ data, stockInfo, loading }) {
  // ... existing loading check ...

  if (loading) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center h-96">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">加载K线数据中...</p>
          </div>
        </div>
      </Card>
    );
  }

  if (!data || data.length === 0) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center h-96">
          <div className="text-center text-gray-500">
            <p className="text-lg mb-2">📊 暂无K线数据</p>
            <p className="text-sm">请选择股票查看K线图</p>
          </div>
        </div>
      </Card>
    );
  }

  // ... existing data processing ...

  // 数据预处理：按日期排序（从旧到新）
  const sortedData = [...data].sort((a, b) => {
    return a.trade_date.localeCompare(b.trade_date);
  });

  // 格式化日期显示
  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    // YYYYMMDD -> MM-DD
    return `${dateStr.slice(4, 6)}-${dateStr.slice(6, 8)}`;
  };

  // 计算成交量的最大值，用于调整Y轴范围
  const maxVolume = Math.max(...sortedData.map(d => d.vol || 0));

  return (
    <Card className="p-6">
      {/* 股票信息标题 */}
      {stockInfo && (
        <div className="mb-4 pb-4 border-b space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-xl font-bold">{stockInfo.name}</h3>
              <p className="text-sm text-gray-500">{stockInfo.ts_code}</p>
            </div>
            {sortedData.length > 0 && (
              <div className="text-right">
                <p className="text-2xl font-bold">
                  {sortedData[sortedData.length - 1]?.close?.toFixed(2)}
                </p>
                <p className={`text-sm font-medium ${sortedData[sortedData.length - 1]?.pct_chg >= 0
                  ? 'text-red-600'
                  : 'text-green-600'
                  }`}>
                  {sortedData[sortedData.length - 1]?.pct_chg >= 0 ? '+' : ''}
                  {sortedData[sortedData.length - 1]?.pct_chg?.toFixed(2)}%
                </p>
              </div>
            )}
          </div>

          <div className="flex items-center justify-between">
            <p className="text-sm font-medium text-slate-600">日K走势</p>
          </div>
        </div>
      )}

      {/* K线图 */}
      <ResponsiveContainer width="100%" height={400}>
        <ComposedChart
          data={sortedData}
          margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />

          <XAxis
            dataKey="trade_date"
            tickFormatter={formatDate}
            tick={{ fontSize: 12 }}
            interval="preserveStartEnd"
          />

          {/* 价格Y轴 */}
          <YAxis
            yAxisId="price"
            domain={['auto', 'auto']}
            tick={{ fontSize: 12 }}
            tickFormatter={(value) => value.toFixed(2)}
          />

          {/* 成交量Y轴 */}
          <YAxis
            yAxisId="volume"
            orientation="right"
            domain={[0, maxVolume * 1.2]}
            tick={{ fontSize: 12 }}
            tickFormatter={(value) => `${(value / 10000).toFixed(0)}万`}
          />

          <Tooltip content={<CustomTooltip />} />

          <Legend
            wrapperStyle={{ paddingTop: '20px' }}
            iconType="line"
          />

          {/* 成交量柱状图 */}
          <Bar
            yAxisId="volume"
            dataKey="vol"
            name="成交量"
            fill="#94a3b8"
            opacity={0.3}
            radius={[4, 4, 0, 0]}
          />

          {/* 收盘价折线 */}
          <Line
            yAxisId="price"
            type="monotone"
            dataKey="close"
            name="收盘价"
            stroke="#3b82f6"
            strokeWidth={2}
            dot={false}
          />

          {/* 最高价折线 */}
          <Line
            yAxisId="price"
            type="monotone"
            dataKey="high"
            name="最高价"
            stroke="#ef4444"
            strokeWidth={1}
            strokeDasharray="3 3"
            dot={false}
          />

          {/* 最低价折线 */}
          <Line
            yAxisId="price"
            type="monotone"
            dataKey="low"
            name="最低价"
            stroke="#10b981"
            strokeWidth={1}
            strokeDasharray="3 3"
            dot={false}
          />
        </ComposedChart>
      </ResponsiveContainer>

      {/* 图表说明 */}
      <div className="mt-4 pt-4 border-t text-sm text-gray-500 space-y-1">
        <p>📊 数据范围: {formatDate(sortedData[0]?.trade_date)} 至 {formatDate(sortedData[sortedData.length - 1]?.trade_date)}</p>
        <p>📈 共 {sortedData.length} 个交易日 (日K)</p>
        <p>💾 数据来源: Tushare Pro (2120积分权限)</p>
      </div>
    </Card>
  );
}
