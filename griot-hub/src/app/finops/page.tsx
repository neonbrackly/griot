'use client';

import { useEffect, useState } from 'react';
import type { AnalyticsReport } from '@/lib/types';
import api from '@/lib/api';

/**
 * FinOps Dashboard Page (T-129)
 *
 * Displays analytics and operational metrics:
 * - Contract usage statistics
 * - Validation trends over time
 * - Top failing contracts
 * - Error type distribution
 * - Field usage patterns
 */
export default function FinOpsDashboardPage() {
  const [report, setReport] = useState<AnalyticsReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dateRange, setDateRange] = useState<'7d' | '30d' | '90d'>('30d');

  useEffect(() => {
    async function fetchAnalyticsReport() {
      try {
        setLoading(true);
        setError(null);

        const toDate = new Date().toISOString().split('T')[0];
        const fromDate = new Date();
        fromDate.setDate(
          fromDate.getDate() - (dateRange === '7d' ? 7 : dateRange === '30d' ? 30 : 90)
        );

        const data = await api.getAnalyticsReport({
          from_date: fromDate.toISOString().split('T')[0],
          to_date: toDate,
          include_details: true,
        });
        setReport(data);
      } catch (err) {
        setError('Failed to load analytics report. The report API may not be available yet.');
      } finally {
        setLoading(false);
      }
    }

    fetchAnalyticsReport();
  }, [dateRange]);

  if (loading) {
    return (
      <div className="text-gray-500 text-center py-16">Loading analytics report...</div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">FinOps Dashboard</h1>
          <p className="text-gray-500 mt-1">
            Analytics, usage metrics, and operational insights
          </p>
        </div>
        <div className="flex gap-2">
          {(['7d', '30d', '90d'] as const).map((range) => (
            <button
              key={range}
              onClick={() => setDateRange(range)}
              className={`px-4 py-2 rounded-md text-sm font-medium ${
                dateRange === range
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {range === '7d' ? '7 Days' : range === '30d' ? '30 Days' : '90 Days'}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div className="bg-warning-50 border border-warning-500 text-warning-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card">
          <div className="text-sm text-gray-500 mb-1">Total Contracts</div>
          <div className="text-3xl font-bold text-gray-900">
            {report?.total_contracts ?? 0}
          </div>
        </div>
        <div className="card">
          <div className="text-sm text-gray-500 mb-1">Total Fields</div>
          <div className="text-3xl font-bold text-gray-900">
            {report?.total_fields ?? 0}
          </div>
        </div>
        <div className="card">
          <div className="text-sm text-gray-500 mb-1">Total Validations</div>
          <div className="text-3xl font-bold text-primary-600">
            {report?.total_validations?.toLocaleString() ?? 0}
          </div>
        </div>
        <div className="card">
          <div className="text-sm text-gray-500 mb-1">Overall Pass Rate</div>
          <div
            className={`text-3xl font-bold ${
              (report?.overall_pass_rate ?? 0) >= 95
                ? 'text-success-600'
                : (report?.overall_pass_rate ?? 0) >= 80
                ? 'text-warning-600'
                : 'text-error-600'
            }`}
          >
            {((report?.overall_pass_rate ?? 0) * 100).toFixed(1)}%
          </div>
        </div>
      </div>

      {/* Validations Over Time */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">Validations Over Time</h2>
        {report?.validations_by_day && report.validations_by_day.length > 0 ? (
          <div className="space-y-4">
            {/* Simple bar chart representation */}
            <div className="flex items-end h-48 gap-1">
              {report.validations_by_day.slice(-30).map((day, idx) => {
                const maxCount = Math.max(
                  ...report.validations_by_day.map((d) => d.count),
                  1
                );
                const height = (day.count / maxCount) * 100;
                return (
                  <div
                    key={idx}
                    className="flex-1 flex flex-col items-center justify-end"
                    title={`${day.date}: ${day.count} validations (${(day.pass_rate * 100).toFixed(0)}% pass)`}
                  >
                    <div
                      className={`w-full rounded-t ${
                        day.pass_rate >= 0.95
                          ? 'bg-success-400'
                          : day.pass_rate >= 0.8
                          ? 'bg-warning-400'
                          : 'bg-error-400'
                      }`}
                      style={{ height: `${Math.max(height, 4)}%` }}
                    />
                  </div>
                );
              })}
            </div>
            <div className="flex justify-between text-xs text-gray-400">
              <span>{report.validations_by_day[0]?.date}</span>
              <span>
                {report.validations_by_day[report.validations_by_day.length - 1]?.date}
              </span>
            </div>
          </div>
        ) : (
          <div className="text-gray-500 text-center py-8">
            No validation history available for the selected period.
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Top Failing Contracts */}
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Top Failing Contracts</h2>
          {report?.top_failing_contracts && report.top_failing_contracts.length > 0 ? (
            <div className="space-y-3">
              {report.top_failing_contracts.slice(0, 10).map((contract, idx) => (
                <div key={idx} className="flex items-center justify-between">
                  <a
                    href={`/contracts/${contract.contract_id}`}
                    className="text-primary-600 hover:underline truncate"
                  >
                    {contract.contract_id}
                  </a>
                  <span className="text-error-600 font-medium">
                    {contract.fail_count} failures
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-gray-500 text-center py-8">
              No validation failures recorded.
            </div>
          )}
        </div>

        {/* Top Error Types */}
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Top Error Types</h2>
          {report?.top_error_types && report.top_error_types.length > 0 ? (
            <div className="space-y-3">
              {report.top_error_types.slice(0, 10).map((errorType, idx) => {
                const maxCount = Math.max(...report.top_error_types.map((e) => e.count), 1);
                const percentage = (errorType.count / maxCount) * 100;
                return (
                  <div key={idx}>
                    <div className="flex items-center justify-between text-sm mb-1">
                      <span className="text-gray-600 capitalize">
                        {errorType.constraint.replace('_', ' ')}
                      </span>
                      <span className="text-gray-900 font-medium">
                        {errorType.count.toLocaleString()}
                      </span>
                    </div>
                    <div className="h-2 bg-gray-100 rounded overflow-hidden">
                      <div
                        className="h-full bg-primary-500"
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="text-gray-500 text-center py-8">No error data available.</div>
          )}
        </div>
      </div>

      {/* Contract Metrics Table */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">Contract Metrics</h2>
        {report?.contract_metrics && report.contract_metrics.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Contract
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Fields
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Validations
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Pass Rate
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Avg Error Rate
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Last Validation
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {report.contract_metrics.slice(0, 20).map((metric, idx) => (
                  <tr key={idx} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm">
                      <a
                        href={`/contracts/${metric.contract_id}`}
                        className="text-primary-600 hover:underline"
                      >
                        {metric.contract_name}
                      </a>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900">{metric.field_count}</td>
                    <td className="px-4 py-3 text-sm text-gray-900">
                      {metric.validation_count.toLocaleString()}
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <span
                        className={`font-medium ${
                          metric.pass_rate >= 0.95
                            ? 'text-success-600'
                            : metric.pass_rate >= 0.8
                            ? 'text-warning-600'
                            : 'text-error-600'
                        }`}
                      >
                        {(metric.pass_rate * 100).toFixed(1)}%
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {(metric.avg_error_rate * 100).toFixed(2)}%
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500">
                      {metric.last_validation
                        ? new Date(metric.last_validation).toLocaleDateString()
                        : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {report.contract_metrics.length > 20 && (
              <div className="text-center text-sm text-gray-500 py-4">
                Showing 20 of {report.contract_metrics.length} contracts
              </div>
            )}
          </div>
        ) : (
          <div className="text-gray-500 text-center py-8">
            No contract metrics available.
          </div>
        )}
      </div>

      {/* Field Usage */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">Field Usage Patterns</h2>
        {report?.field_usage && report.field_usage.length > 0 ? (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {report.field_usage.slice(0, 8).map((field, idx) => (
              <div key={idx} className="bg-gray-50 rounded-lg p-4">
                <div className="font-mono text-sm text-gray-900 truncate">
                  {field.field_name}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {field.contract_count} contracts
                </div>
                <div className="text-xs text-gray-500">
                  {(field.avg_null_rate * 100).toFixed(1)}% null rate
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-gray-500 text-center py-8">
            No field usage data available.
          </div>
        )}
      </div>

      {/* Report Metadata */}
      {report && (
        <div className="text-sm text-gray-400 text-center">
          Report generated at {new Date(report.generated_at).toLocaleString()}
        </div>
      )}
    </div>
  );
}
