'use client';

import { useEffect, useState } from 'react';
import type { ValidationRecord } from '@/lib/types';
import api from '@/lib/api';

/**
 * Validation Monitor Page
 *
 * Features:
 * - Real-time validation feed
 * - Filter by contract, status, date range
 * - Error rate trends (chart)
 * - Drill down to individual validation
 * - Sample errors display
 */
export default function MonitorPage() {
  const [validations, setValidations] = useState<ValidationRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [contractFilter, setContractFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'passed' | 'failed'>('all');
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const limit = 20;

  useEffect(() => {
    async function fetchValidations() {
      try {
        setLoading(true);
        setError(null);

        const params: {
          limit: number;
          offset: number;
          contract_id?: string;
          passed?: boolean;
        } = { limit, offset };

        if (contractFilter) {
          params.contract_id = contractFilter;
        }
        if (statusFilter !== 'all') {
          params.passed = statusFilter === 'passed';
        }

        const result = await api.getValidations(params);
        setValidations(result.items);
        setTotal(result.total);
      } catch (err) {
        setError('Failed to load validations. Registry API may be unavailable.');
        setValidations([]);
      } finally {
        setLoading(false);
      }
    }

    fetchValidations();
  }, [contractFilter, statusFilter, offset]);

  // Calculate stats
  const passedCount = validations.filter((v) => v.passed).length;
  const failedCount = validations.filter((v) => !v.passed).length;
  const totalRows = validations.reduce((sum, v) => sum + v.row_count, 0);
  const totalErrors = validations.reduce((sum, v) => sum + (v.error_count || 0), 0);

  const totalPages = Math.ceil(total / limit);
  const currentPage = Math.floor(offset / limit) + 1;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Validation Monitor</h1>
        <button
          onClick={() => {
            setOffset(0);
            setLoading(true);
          }}
          className="btn btn-secondary"
        >
          Refresh
        </button>
      </div>

      {error && (
        <div className="bg-warning-50 border border-warning-500 text-warning-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card">
          <div className="text-sm text-gray-500 mb-1">Total Validations</div>
          <div className="text-3xl font-bold text-gray-900">
            {loading ? '...' : validations.length}
          </div>
        </div>
        <div className="card">
          <div className="text-sm text-gray-500 mb-1">Passed</div>
          <div className="text-3xl font-bold text-success-600">
            {loading ? '...' : passedCount}
          </div>
        </div>
        <div className="card">
          <div className="text-sm text-gray-500 mb-1">Failed</div>
          <div className="text-3xl font-bold text-error-600">
            {loading ? '...' : failedCount}
          </div>
        </div>
        <div className="card">
          <div className="text-sm text-gray-500 mb-1">Total Errors</div>
          <div className="text-3xl font-bold text-gray-900">
            {loading ? '...' : totalErrors.toLocaleString()}
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-4">
        <input
          type="text"
          placeholder="Filter by contract ID..."
          value={contractFilter}
          onChange={(e) => {
            setContractFilter(e.target.value);
            setOffset(0);
          }}
          className="input flex-1"
        />
        <select
          value={statusFilter}
          onChange={(e) => {
            setStatusFilter(e.target.value as 'all' | 'passed' | 'failed');
            setOffset(0);
          }}
          className="input w-40"
        >
          <option value="all">All Status</option>
          <option value="passed">Passed</option>
          <option value="failed">Failed</option>
        </select>
      </div>

      {/* Validation List */}
      <div className="card">
        {loading ? (
          <div className="text-gray-500 text-center py-8">Loading validations...</div>
        ) : validations.length > 0 ? (
          <div className="divide-y divide-gray-100">
            {validations.map((validation) => (
              <div key={validation.id} className="py-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <span
                        className={`px-2 py-0.5 rounded text-sm font-medium ${
                          validation.passed
                            ? 'bg-success-50 text-success-700'
                            : 'bg-error-50 text-error-700'
                        }`}
                      >
                        {validation.passed ? 'Passed' : 'Failed'}
                      </span>
                      <a
                        href={`/contracts/${validation.contract_id}`}
                        className="font-medium text-gray-900 hover:text-primary-600"
                      >
                        {validation.contract_id}
                      </a>
                      {validation.contract_version && (
                        <span className="text-xs text-gray-400">
                          v{validation.contract_version}
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-4 mt-2 text-sm text-gray-500">
                      <span>{validation.row_count.toLocaleString()} rows</span>
                      {validation.error_count !== undefined && validation.error_count > 0 && (
                        <span className="text-error-600">
                          {validation.error_count.toLocaleString()} errors (
                          {((validation.error_count / validation.row_count) * 100).toFixed(2)}%)
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="text-sm text-gray-400">
                    {new Date(validation.recorded_at).toLocaleString()}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-gray-500 text-center py-8">
            {contractFilter || statusFilter !== 'all'
              ? 'No validations match your filters.'
              : 'No validations recorded yet.'}
          </div>
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-500">
            Showing {offset + 1}-{Math.min(offset + limit, total)} of {total}
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setOffset(Math.max(0, offset - limit))}
              disabled={offset === 0}
              className="btn btn-secondary disabled:opacity-50"
            >
              Previous
            </button>
            <button
              onClick={() => setOffset(offset + limit)}
              disabled={currentPage >= totalPages}
              className="btn btn-secondary disabled:opacity-50"
            >
              Next
            </button>
          </div>
        </div>
      )}

      {/* Chart placeholder */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">Error Rate Trend</h2>
        <div className="bg-gray-50 h-64 rounded flex items-center justify-center text-gray-400">
          Chart will be rendered here when data is available.
          <br />
          (Requires recharts component implementation)
        </div>
      </div>
    </div>
  );
}
