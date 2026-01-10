'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import type { Contract, VersionSummary, ValidationRecord } from '@/lib/types';
import api from '@/lib/api';

/**
 * Contract Detail Page
 *
 * Features:
 * - Contract metadata (name, description, owner)
 * - Field list with constraints
 * - Version history
 * - Recent validations for this contract
 * - Diff between versions
 * - Download as YAML
 */
export default function ContractDetailPage() {
  const params = useParams();
  const contractId = params.id as string;

  const [contract, setContract] = useState<Contract | null>(null);
  const [versions, setVersions] = useState<VersionSummary[]>([]);
  const [validations, setValidations] = useState<ValidationRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'fields' | 'versions' | 'validations'>('fields');

  useEffect(() => {
    async function fetchContractData() {
      try {
        setLoading(true);
        setError(null);

        const [contractRes, versionsRes, validationsRes] = await Promise.allSettled([
          api.getContract(contractId),
          api.getVersions(contractId, { limit: 10 }),
          api.getContractValidations(contractId, { limit: 10 }),
        ]);

        if (contractRes.status === 'fulfilled') {
          setContract(contractRes.value);
        } else {
          throw new Error('Contract not found');
        }

        if (versionsRes.status === 'fulfilled') {
          setVersions(versionsRes.value.items);
        }

        if (validationsRes.status === 'fulfilled') {
          setValidations(validationsRes.value.items);
        }
      } catch (err) {
        setError('Failed to load contract. It may not exist or the API is unavailable.');
      } finally {
        setLoading(false);
      }
    }

    if (contractId) {
      fetchContractData();
    }
  }, [contractId]);

  if (loading) {
    return (
      <div className="text-gray-500 text-center py-16">Loading contract details...</div>
    );
  }

  if (error || !contract) {
    return (
      <div className="text-center py-16">
        <div className="text-error-500 mb-4">{error || 'Contract not found'}</div>
        <a href="/contracts" className="text-primary-600 hover:underline">
          Back to contracts
        </a>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-gray-900">{contract.name}</h1>
            <span
              className={`px-2 py-0.5 rounded text-sm font-medium ${
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
          <div className="text-gray-500 mt-1">{contract.id}</div>
          {contract.description && (
            <div className="text-gray-600 mt-2">{contract.description}</div>
          )}
        </div>
        <div className="flex gap-3">
          <a href={`/studio?edit=${contract.id}`} className="btn btn-secondary">
            Edit
          </a>
          <button className="btn btn-secondary">Download YAML</button>
        </div>
      </div>

      {/* Metadata */}
      <div className="card">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <div className="text-sm text-gray-500">Version</div>
            <div className="font-medium">{contract.version}</div>
          </div>
          <div>
            <div className="text-sm text-gray-500">Owner</div>
            <div className="font-medium">{contract.owner || 'Unassigned'}</div>
          </div>
          <div>
            <div className="text-sm text-gray-500">Fields</div>
            <div className="font-medium">{contract.fields.length}</div>
          </div>
          <div>
            <div className="text-sm text-gray-500">Updated</div>
            <div className="font-medium">
              {contract.updated_at
                ? new Date(contract.updated_at).toLocaleDateString()
                : 'N/A'}
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex gap-8">
          {(['fields', 'versions', 'validations'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`py-3 border-b-2 font-medium text-sm capitalize ${
                activeTab === tab
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              {tab}
              {tab === 'fields' && ` (${contract.fields.length})`}
              {tab === 'versions' && ` (${versions.length})`}
              {tab === 'validations' && ` (${validations.length})`}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="card">
        {activeTab === 'fields' && (
          <div className="space-y-4">
            {contract.fields.map((field, index) => (
              <div
                key={field.name}
                className={`py-4 ${index > 0 ? 'border-t border-gray-100' : ''}`}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-mono font-medium text-gray-900">
                        {field.name}
                      </span>
                      <span className="px-2 py-0.5 bg-gray-100 rounded text-xs text-gray-600">
                        {field.type}
                      </span>
                      {field.nullable && (
                        <span className="text-xs text-gray-400">nullable</span>
                      )}
                      {field.primary_key && (
                        <span className="px-2 py-0.5 bg-primary-50 text-primary-700 rounded text-xs">
                          PK
                        </span>
                      )}
                      {field.unique && (
                        <span className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs">
                          unique
                        </span>
                      )}
                    </div>
                    <div className="text-sm text-gray-600 mt-1">{field.description}</div>
                  </div>
                </div>
                {field.constraints && Object.keys(field.constraints).length > 0 && (
                  <div className="mt-2 text-sm">
                    <span className="text-gray-500">Constraints: </span>
                    <span className="text-gray-700">
                      {Object.entries(field.constraints)
                        .filter(([, v]) => v !== undefined)
                        .map(([k, v]) => `${k}=${JSON.stringify(v)}`)
                        .join(', ')}
                    </span>
                  </div>
                )}
              </div>
            ))}
            {contract.fields.length === 0 && (
              <div className="text-gray-500 text-center py-8">No fields defined</div>
            )}
          </div>
        )}

        {activeTab === 'versions' && (
          <div className="space-y-4">
            {versions.map((version, index) => (
              <div
                key={version.version}
                className={`py-4 ${index > 0 ? 'border-t border-gray-100' : ''}`}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-gray-900">v{version.version}</span>
                      {version.is_breaking && (
                        <span className="px-2 py-0.5 bg-error-50 text-error-700 rounded text-xs">
                          breaking
                        </span>
                      )}
                      {version.change_type && (
                        <span className="text-xs text-gray-400">{version.change_type}</span>
                      )}
                    </div>
                    {version.change_notes && (
                      <div className="text-sm text-gray-600 mt-1">{version.change_notes}</div>
                    )}
                  </div>
                  <div className="text-sm text-gray-400">
                    {version.created_at
                      ? new Date(version.created_at).toLocaleDateString()
                      : ''}
                  </div>
                </div>
              </div>
            ))}
            {versions.length === 0 && (
              <div className="text-gray-500 text-center py-8">No version history</div>
            )}
          </div>
        )}

        {activeTab === 'validations' && (
          <div className="space-y-4">
            {validations.map((validation, index) => (
              <div
                key={validation.id}
                className={`py-4 ${index > 0 ? 'border-t border-gray-100' : ''}`}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <span
                        className={`px-2 py-0.5 rounded text-sm font-medium ${
                          validation.passed
                            ? 'bg-success-50 text-success-700'
                            : 'bg-error-50 text-error-700'
                        }`}
                      >
                        {validation.passed ? 'Passed' : 'Failed'}
                      </span>
                      <span className="text-gray-600">
                        {validation.row_count.toLocaleString()} rows
                      </span>
                      {validation.error_count !== undefined && validation.error_count > 0 && (
                        <span className="text-error-600">
                          ({validation.error_count.toLocaleString()} errors)
                        </span>
                      )}
                    </div>
                    <div className="text-sm text-gray-500 mt-1">
                      v{validation.contract_version || contract.version}
                    </div>
                  </div>
                  <div className="text-sm text-gray-400">
                    {new Date(validation.recorded_at).toLocaleString()}
                  </div>
                </div>
              </div>
            ))}
            {validations.length === 0 && (
              <div className="text-gray-500 text-center py-8">No validations recorded</div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
