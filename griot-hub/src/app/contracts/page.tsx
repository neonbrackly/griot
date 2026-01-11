'use client';

import { useEffect, useState } from 'react';
import type { Contract, ContractStatus } from '@/lib/types';
import api from '@/lib/api';

/**
 * Contract Browser Page
 *
 * Features:
 * - List all contracts with pagination
 * - Search by name, field, description
 * - Filter by status (active, draft, deprecated)
 * - Sort by name, updated_at, version
 * - Click to view contract details
 */
export default function ContractsPage() {
  const [contracts, setContracts] = useState<Contract[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<ContractStatus | ''>('');
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const limit = 20;

  useEffect(() => {
    async function fetchContracts() {
      try {
        setLoading(true);
        setError(null);

        if (searchQuery) {
          const results = await api.search({ q: searchQuery, limit, offset });
          // Convert search hits to contracts
          const contractIds = [...new Set(results.items.map((hit) => hit.contract_id))];
          const contractPromises = contractIds.map((id) => api.getContract(id));
          const fetchedContracts = await Promise.all(contractPromises);
          setContracts(fetchedContracts);
          setTotal(results.total);
        } else {
          const params: { limit: number; offset: number; status?: ContractStatus } = {
            limit,
            offset,
          };
          if (statusFilter) {
            params.status = statusFilter;
          }
          const result = await api.getContracts(params);
          setContracts(result.items);
          setTotal(result.total);
        }
      } catch (err) {
        setError('Failed to load contracts. Registry API may be unavailable.');
        setContracts([]);
      } finally {
        setLoading(false);
      }
    }

    fetchContracts();
  }, [searchQuery, statusFilter, offset]);

  const totalPages = Math.ceil(total / limit);
  const currentPage = Math.floor(offset / limit) + 1;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Contracts</h1>
        <a href="/studio" className="btn btn-primary">
          New Contract
        </a>
      </div>

      {/* Search and Filters */}
      <div className="flex gap-4">
        <input
          type="text"
          placeholder="Search contracts..."
          value={searchQuery}
          onChange={(e) => {
            setSearchQuery(e.target.value);
            setOffset(0);
          }}
          className="input flex-1"
        />
        <select
          value={statusFilter}
          onChange={(e) => {
            setStatusFilter(e.target.value as ContractStatus | '');
            setOffset(0);
          }}
          className="input w-40"
        >
          <option value="">All Status</option>
          <option value="active">Active</option>
          <option value="draft">Draft</option>
          <option value="deprecated">Deprecated</option>
        </select>
      </div>

      {error && (
        <div className="bg-warning-50 border border-warning-500 text-warning-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Contract List */}
      <div className="card">
        {loading ? (
          <div className="text-gray-500 text-center py-8">Loading contracts...</div>
        ) : contracts.length > 0 ? (
          <div className="divide-y divide-gray-100">
            {contracts.map((contract) => (
              <a
                key={contract.id}
                href={`/contracts/${contract.id}`}
                className="block py-4 hover:bg-gray-50 -mx-4 px-4"
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <span className="font-medium text-gray-900">{contract.name}</span>
                      <span
                        className={`px-2 py-0.5 rounded text-xs font-medium ${
                          contract.status === 'active'
                            ? 'bg-success-50 text-success-700'
                            : contract.status === 'draft'
                            ? 'bg-gray-100 text-gray-600'
                            : 'bg-warning-50 text-warning-700'
                        }`}
                      >
                        {contract.status}
                      </span>
                    </div>
                    <div className="text-sm text-gray-500 mt-1">
                      {contract.description || contract.id}
                    </div>
                    <div className="text-xs text-gray-400 mt-1">
                      {(contract.schema || []).reduce((count, s) => count + (s.properties?.length || 0), 0)} fields
                      {contract.owner && ` · Owner: ${contract.owner}`}
                    </div>
                  </div>
                  <div className="text-sm text-gray-400">v{contract.version}</div>
                </div>
              </a>
            ))}
          </div>
        ) : (
          <div className="text-gray-500 text-center py-8">
            {searchQuery || statusFilter
              ? 'No contracts match your search criteria.'
              : 'No contracts yet. Create your first contract to get started.'}
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
    </div>
  );
}
