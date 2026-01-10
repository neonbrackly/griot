'use client';

import { useEffect, useState } from 'react';
import type { Contract, ValidationRecord, HealthResponse } from '@/lib/types';
import api from '@/lib/api';

/**
 * Home / Dashboard Page
 *
 * Displays:
 * - Contract count and status breakdown
 * - Recent validation results
 * - Quick actions (create contract, run validation)
 * - Health status of registry
 */
export default function HomePage() {
  const [contracts, setContracts] = useState<Contract[]>([]);
  const [validations, setValidations] = useState<ValidationRecord[]>([]);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchDashboardData() {
      try {
        setLoading(true);
        // These will fail until the registry API is available
        const [contractsRes, validationsRes, healthRes] = await Promise.allSettled([
          api.getContracts({ limit: 5 }),
          api.getValidations({ limit: 10 }),
          api.health(),
        ]);

        if (contractsRes.status === 'fulfilled') {
          setContracts(contractsRes.value.items);
        }
        if (validationsRes.status === 'fulfilled') {
          setValidations(validationsRes.value.items);
        }
        if (healthRes.status === 'fulfilled') {
          setHealth(healthRes.value);
        }
      } catch (err) {
        setError('Failed to load dashboard data. Registry API may be unavailable.');
      } finally {
        setLoading(false);
      }
    }

    fetchDashboardData();
  }, []);

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <div className="flex gap-3">
          <a href="/studio" className="btn btn-primary">
            New Contract
          </a>
        </div>
      </div>

      {error && (
        <div className="bg-warning-50 border border-warning-500 text-warning-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Health Status */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">Registry Status</h2>
        {loading ? (
          <div className="text-gray-500">Loading...</div>
        ) : health ? (
          <div className="flex items-center gap-4">
            <span
              className={`inline-block w-3 h-3 rounded-full ${
                health.status === 'healthy'
                  ? 'bg-success-500'
                  : health.status === 'degraded'
                  ? 'bg-warning-500'
                  : 'bg-error-500'
              }`}
            />
            <span className="capitalize">{health.status}</span>
            <span className="text-gray-500 text-sm">v{health.version}</span>
          </div>
        ) : (
          <div className="text-gray-500">Registry API not available</div>
        )}
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card">
          <div className="text-sm text-gray-500 mb-1">Total Contracts</div>
          <div className="text-3xl font-bold text-gray-900">
            {loading ? '...' : contracts.length}
          </div>
        </div>
        <div className="card">
          <div className="text-sm text-gray-500 mb-1">Recent Validations</div>
          <div className="text-3xl font-bold text-gray-900">
            {loading ? '...' : validations.length}
          </div>
        </div>
        <div className="card">
          <div className="text-sm text-gray-500 mb-1">Pass Rate</div>
          <div className="text-3xl font-bold text-gray-900">
            {loading
              ? '...'
              : validations.length > 0
              ? `${Math.round((validations.filter((v) => v.passed).length / validations.length) * 100)}%`
              : 'N/A'}
          </div>
        </div>
      </div>

      {/* Recent Contracts */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-800">Recent Contracts</h2>
          <a href="/contracts" className="text-primary-600 hover:text-primary-700 text-sm">
            View all
          </a>
        </div>
        {loading ? (
          <div className="text-gray-500">Loading contracts...</div>
        ) : contracts.length > 0 ? (
          <div className="divide-y divide-gray-100">
            {contracts.map((contract) => (
              <a
                key={contract.id}
                href={`/contracts/${contract.id}`}
                className="block py-3 hover:bg-gray-50 -mx-4 px-4"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium text-gray-900">{contract.name}</div>
                    <div className="text-sm text-gray-500">{contract.id}</div>
                  </div>
                  <div className="text-sm text-gray-400">v{contract.version}</div>
                </div>
              </a>
            ))}
          </div>
        ) : (
          <div className="text-gray-500 text-center py-8">
            No contracts yet.{' '}
            <a href="/studio" className="text-primary-600 hover:underline">
              Create your first contract
            </a>
          </div>
        )}
      </div>

      {/* Recent Validations */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-800">Recent Validations</h2>
          <a href="/monitor" className="text-primary-600 hover:text-primary-700 text-sm">
            View all
          </a>
        </div>
        {loading ? (
          <div className="text-gray-500">Loading validations...</div>
        ) : validations.length > 0 ? (
          <div className="divide-y divide-gray-100">
            {validations.map((validation) => (
              <div key={validation.id} className="py-3 flex items-center justify-between">
                <div>
                  <div className="font-medium text-gray-900">{validation.contract_id}</div>
                  <div className="text-sm text-gray-500">
                    {new Date(validation.recorded_at).toLocaleString()}
                  </div>
                </div>
                <span
                  className={`px-2 py-1 rounded text-sm font-medium ${
                    validation.passed
                      ? 'bg-success-50 text-success-700'
                      : 'bg-error-50 text-error-700'
                  }`}
                >
                  {validation.passed ? 'Passed' : 'Failed'}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-gray-500 text-center py-8">No validations recorded yet.</div>
        )}
      </div>
    </div>
  );
}
