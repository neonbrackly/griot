'use client';

import type { ValidationRecord } from '@/lib/types';

/**
 * ErrorTrendChart Component
 *
 * Line chart showing validation error trends over time.
 * Uses Recharts for rendering (placeholder implementation).
 */
interface ErrorTrendChartProps {
  data: ValidationRecord[];
  contractId?: string;
}

export function ErrorTrendChart({ data, contractId }: ErrorTrendChartProps) {
  // Filter by contract if specified
  const filteredData = contractId
    ? data.filter((d) => d.contract_id === contractId)
    : data;

  // Sort by date
  const sortedData = [...filteredData].sort(
    (a, b) => new Date(a.recorded_at).getTime() - new Date(b.recorded_at).getTime()
  );

  // Prepare chart data
  const chartData = sortedData.map((record) => ({
    date: new Date(record.recorded_at).toLocaleDateString(),
    errorRate:
      record.error_count !== undefined && record.row_count > 0
        ? (record.error_count / record.row_count) * 100
        : 0,
    passed: record.passed ? 1 : 0,
    rowCount: record.row_count,
  }));

  // Calculate summary stats
  const avgErrorRate =
    chartData.length > 0
      ? chartData.reduce((sum, d) => sum + d.errorRate, 0) / chartData.length
      : 0;
  const passRate =
    chartData.length > 0
      ? (chartData.filter((d) => d.passed).length / chartData.length) * 100
      : 0;

  if (chartData.length === 0) {
    return (
      <div className="bg-gray-50 h-64 rounded-lg flex items-center justify-center text-gray-400">
        No validation data available for chart
      </div>
    );
  }

  // Placeholder for actual Recharts implementation
  // TODO: Implement with Recharts when the package is properly set up
  return (
    <div className="space-y-4">
      {/* Summary Stats */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-gray-50 rounded-lg p-3">
          <div className="text-sm text-gray-500">Data Points</div>
          <div className="text-xl font-semibold text-gray-900">
            {chartData.length}
          </div>
        </div>
        <div className="bg-gray-50 rounded-lg p-3">
          <div className="text-sm text-gray-500">Avg Error Rate</div>
          <div className="text-xl font-semibold text-gray-900">
            {avgErrorRate.toFixed(2)}%
          </div>
        </div>
        <div className="bg-gray-50 rounded-lg p-3">
          <div className="text-sm text-gray-500">Pass Rate</div>
          <div className="text-xl font-semibold text-gray-900">
            {passRate.toFixed(1)}%
          </div>
        </div>
      </div>

      {/* Chart placeholder */}
      <div className="bg-gray-50 h-48 rounded-lg p-4">
        <div className="text-sm text-gray-500 mb-2">Error Rate Trend</div>
        <div className="flex items-end h-32 gap-1">
          {chartData.slice(-20).map((d, i) => (
            <div
              key={i}
              className="flex-1 bg-primary-200 hover:bg-primary-400 transition-colors rounded-t"
              style={{ height: `${Math.max(d.errorRate * 2, 4)}%` }}
              title={`${d.date}: ${d.errorRate.toFixed(2)}%`}
            />
          ))}
        </div>
        <div className="text-xs text-gray-400 mt-2 text-center">
          Last {Math.min(20, chartData.length)} validations
        </div>
      </div>

      {/* Note about full implementation */}
      <p className="text-xs text-gray-400 text-center">
        Full interactive chart with Recharts will be available after npm install
      </p>
    </div>
  );
}

export default ErrorTrendChart;
