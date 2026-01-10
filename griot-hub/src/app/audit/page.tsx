'use client';

import { useEffect, useState } from 'react';
import type { AuditReport, PIICategory, SensitivityLevel, LegalBasis } from '@/lib/types';
import api from '@/lib/api';

/**
 * Audit Dashboard Page (T-128)
 *
 * Displays comprehensive audit information:
 * - PII inventory across all contracts
 * - Sensitivity level breakdown
 * - Residency compliance status
 * - Legal basis coverage
 * - Retention policy compliance
 */
export default function AuditDashboardPage() {
  const [report, setReport] = useState<AuditReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchAuditReport() {
      try {
        setLoading(true);
        setError(null);
        const data = await api.getAuditReport({ include_details: true });
        setReport(data);
      } catch (err) {
        setError('Failed to load audit report. The report API may not be available yet.');
      } finally {
        setLoading(false);
      }
    }

    fetchAuditReport();
  }, []);

  const piiCategoryColors: Record<PIICategory, string> = {
    direct_identifier: 'bg-error-500',
    quasi_identifier: 'bg-warning-500',
    sensitive: 'bg-error-300',
    non_pii: 'bg-success-500',
  };

  const sensitivityColors: Record<SensitivityLevel, string> = {
    restricted: 'bg-error-500',
    confidential: 'bg-warning-500',
    internal: 'bg-primary-500',
    public: 'bg-success-500',
  };

  if (loading) {
    return (
      <div className="text-gray-500 text-center py-16">Loading audit report...</div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Audit Dashboard</h1>
          <p className="text-gray-500 mt-1">
            PII inventory, residency compliance, and data governance overview
          </p>
        </div>
        <button
          onClick={() => window.location.reload()}
          className="btn btn-secondary"
        >
          Refresh Report
        </button>
      </div>

      {error && (
        <div className="bg-warning-50 border border-warning-500 text-warning-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card">
          <div className="text-sm text-gray-500 mb-1">Contracts Scanned</div>
          <div className="text-3xl font-bold text-gray-900">
            {report?.contract_count ?? 0}
          </div>
        </div>
        <div className="card">
          <div className="text-sm text-gray-500 mb-1">Total Fields</div>
          <div className="text-3xl font-bold text-gray-900">
            {report?.field_count ?? 0}
          </div>
        </div>
        <div className="card">
          <div className="text-sm text-gray-500 mb-1">PII Fields</div>
          <div className="text-3xl font-bold text-warning-600">
            {report?.pii_inventory?.length ?? 0}
          </div>
        </div>
        <div className="card">
          <div className="text-sm text-gray-500 mb-1">Residency Compliance</div>
          <div
            className={`text-3xl font-bold ${
              (report?.residency_compliance_rate ?? 0) >= 90
                ? 'text-success-600'
                : (report?.residency_compliance_rate ?? 0) >= 70
                ? 'text-warning-600'
                : 'text-error-600'
            }`}
          >
            {((report?.residency_compliance_rate ?? 0) * 100).toFixed(1)}%
          </div>
        </div>
      </div>

      {/* PII by Category */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">PII by Category</h2>
        {report?.pii_by_category ? (
          <div className="space-y-3">
            {(Object.entries(report.pii_by_category) as [PIICategory, number][]).map(
              ([category, count]) => (
                <div key={category} className="flex items-center gap-4">
                  <div className="w-40 text-sm text-gray-600 capitalize">
                    {category.replace('_', ' ')}
                  </div>
                  <div className="flex-1 h-6 bg-gray-100 rounded overflow-hidden">
                    <div
                      className={`h-full ${piiCategoryColors[category]}`}
                      style={{
                        width: `${Math.min(
                          (count / (report.pii_inventory?.length || 1)) * 100,
                          100
                        )}%`,
                      }}
                    />
                  </div>
                  <div className="w-12 text-right text-sm font-medium text-gray-900">
                    {count}
                  </div>
                </div>
              )
            )}
          </div>
        ) : (
          <div className="text-gray-500 text-center py-8">
            No PII data available. Run the audit report to see results.
          </div>
        )}
      </div>

      {/* Sensitivity Level Distribution */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">
          Sensitivity Level Distribution
        </h2>
        {report?.pii_by_sensitivity ? (
          <div className="grid grid-cols-4 gap-4">
            {(
              Object.entries(report.pii_by_sensitivity) as [SensitivityLevel, number][]
            ).map(([level, count]) => (
              <div key={level} className="text-center">
                <div
                  className={`w-16 h-16 mx-auto rounded-full ${sensitivityColors[level]} flex items-center justify-center text-white text-xl font-bold`}
                >
                  {count}
                </div>
                <div className="mt-2 text-sm text-gray-600 capitalize">{level}</div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-gray-500 text-center py-8">
            No sensitivity data available.
          </div>
        )}
      </div>

      {/* Legal Basis Coverage */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">Legal Basis Coverage</h2>
        {report?.legal_basis_coverage ? (
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {(
              Object.entries(report.legal_basis_coverage) as [LegalBasis, number][]
            ).map(([basis, count]) => (
              <div key={basis} className="bg-gray-50 rounded-lg p-4">
                <div className="text-2xl font-bold text-gray-900">{count}</div>
                <div className="text-sm text-gray-600 capitalize">
                  {basis.replace('_', ' ')}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-gray-500 text-center py-8">
            No legal basis data available.
          </div>
        )}
      </div>

      {/* Residency Checks */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">Residency Compliance</h2>
        {report?.residency_checks && report.residency_checks.length > 0 ? (
          <div className="divide-y divide-gray-100">
            {report.residency_checks.map((check, idx) => (
              <div key={idx} className="py-4 flex items-center justify-between">
                <div>
                  <div className="font-medium text-gray-900">{check.contract_id}</div>
                  <div className="text-sm text-gray-500">
                    Region: {check.region.toUpperCase()} | {check.fields_checked} fields
                    checked
                  </div>
                </div>
                <span
                  className={`px-3 py-1 rounded text-sm font-medium ${
                    check.compliant
                      ? 'bg-success-50 text-success-700'
                      : 'bg-error-50 text-error-700'
                  }`}
                >
                  {check.compliant ? 'Compliant' : `${check.violations.length} Violations`}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-gray-500 text-center py-8">
            No residency checks performed yet.
          </div>
        )}
      </div>

      {/* PII Inventory Table */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">PII Inventory</h2>
        {report?.pii_inventory && report.pii_inventory.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Contract
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Field
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Category
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Sensitivity
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Masking
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Legal Basis
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {report.pii_inventory.slice(0, 20).map((item, idx) => (
                  <tr key={idx} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm">
                      <a
                        href={`/contracts/${item.contract_id}`}
                        className="text-primary-600 hover:underline"
                      >
                        {item.contract_name}
                      </a>
                    </td>
                    <td className="px-4 py-3 text-sm font-mono">{item.field_name}</td>
                    <td className="px-4 py-3 text-sm capitalize">
                      {item.pii_category.replace('_', ' ')}
                    </td>
                    <td className="px-4 py-3 text-sm capitalize">{item.sensitivity_level}</td>
                    <td className="px-4 py-3 text-sm capitalize">{item.masking_strategy}</td>
                    <td className="px-4 py-3 text-sm capitalize">
                      {item.legal_basis?.replace('_', ' ') ?? '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {report.pii_inventory.length > 20 && (
              <div className="text-center text-sm text-gray-500 py-4">
                Showing 20 of {report.pii_inventory.length} PII fields
              </div>
            )}
          </div>
        ) : (
          <div className="text-gray-500 text-center py-8">
            No PII fields detected in your contracts.
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
