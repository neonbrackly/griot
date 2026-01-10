'use client';

import { useEffect, useState } from 'react';
import type { Region, ResidencyStatus, AuditReport } from '@/lib/types';
import api from '@/lib/api';

/**
 * Residency Map Page (T-131)
 *
 * Displays data residency information:
 * - Geographic distribution of contracts/data
 * - Residency compliance by region
 * - Violations and their details
 * - Interactive region selection
 */

const REGIONS: { id: Region; name: string; description: string }[] = [
  { id: 'us', name: 'United States', description: 'North America' },
  { id: 'eu', name: 'European Union', description: 'EU/EEA member states' },
  { id: 'uk', name: 'United Kingdom', description: 'UK post-Brexit' },
  { id: 'apac', name: 'Asia Pacific', description: 'APAC region' },
  { id: 'latam', name: 'Latin America', description: 'Central & South America' },
  { id: 'mea', name: 'Middle East & Africa', description: 'MEA region' },
  { id: 'global', name: 'Global', description: 'No residency restrictions' },
];

export default function ResidencyMapPage() {
  const [residencyMap, setResidencyMap] = useState<Record<Region, string[]> | null>(null);
  const [auditReport, setAuditReport] = useState<AuditReport | null>(null);
  const [selectedRegion, setSelectedRegion] = useState<Region | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchResidencyData() {
      try {
        setLoading(true);
        setError(null);

        const [mapData, auditData] = await Promise.allSettled([
          api.getResidencyMap(),
          api.getAuditReport({ include_details: true }),
        ]);

        if (mapData.status === 'fulfilled') {
          setResidencyMap(mapData.value);
        }
        if (auditData.status === 'fulfilled') {
          setAuditReport(auditData.value);
        }
      } catch (err) {
        setError('Failed to load residency data. The API may not be available yet.');
      } finally {
        setLoading(false);
      }
    }

    fetchResidencyData();
  }, []);

  const getRegionStats = (region: Region) => {
    const contracts = residencyMap?.[region] ?? [];
    const checks = auditReport?.residency_checks?.filter((c) => c.region === region) ?? [];
    const violations = checks.flatMap((c) => c.violations);
    const compliant = checks.filter((c) => c.compliant).length;

    return {
      contractCount: contracts.length,
      checksCount: checks.length,
      violationsCount: violations.length,
      complianceRate: checks.length > 0 ? (compliant / checks.length) * 100 : 100,
    };
  };

  const getTotalStats = () => {
    let totalContracts = 0;
    let totalViolations = 0;

    if (residencyMap) {
      Object.values(residencyMap).forEach((contracts) => {
        totalContracts += contracts.length;
      });
    }

    if (auditReport?.residency_checks) {
      auditReport.residency_checks.forEach((check) => {
        totalViolations += check.violations.length;
      });
    }

    return {
      totalContracts,
      totalViolations,
      complianceRate: (auditReport?.residency_compliance_rate ?? 1) * 100,
    };
  };

  if (loading) {
    return (
      <div className="text-gray-500 text-center py-16">Loading residency data...</div>
    );
  }

  const totalStats = getTotalStats();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Residency Map</h1>
          <p className="text-gray-500 mt-1">
            Data residency requirements and compliance by geographic region
          </p>
        </div>
        <button
          onClick={() => window.location.reload()}
          className="btn btn-secondary"
        >
          Refresh Data
        </button>
      </div>

      {error && (
        <div className="bg-warning-50 border border-warning-500 text-warning-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Global Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card">
          <div className="text-sm text-gray-500 mb-1">Total Contracts with Residency</div>
          <div className="text-3xl font-bold text-gray-900">
            {totalStats.totalContracts}
          </div>
        </div>
        <div className="card">
          <div className="text-sm text-gray-500 mb-1">Total Violations</div>
          <div
            className={`text-3xl font-bold ${
              totalStats.totalViolations === 0 ? 'text-success-600' : 'text-error-600'
            }`}
          >
            {totalStats.totalViolations}
          </div>
        </div>
        <div className="card">
          <div className="text-sm text-gray-500 mb-1">Overall Compliance</div>
          <div
            className={`text-3xl font-bold ${
              totalStats.complianceRate >= 95
                ? 'text-success-600'
                : totalStats.complianceRate >= 80
                ? 'text-warning-600'
                : 'text-error-600'
            }`}
          >
            {totalStats.complianceRate.toFixed(1)}%
          </div>
        </div>
      </div>

      {/* Region Map (Visual Grid) */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">Regional Overview</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
          {REGIONS.map((region) => {
            const stats = getRegionStats(region.id);
            const isSelected = selectedRegion === region.id;

            return (
              <button
                key={region.id}
                onClick={() => setSelectedRegion(isSelected ? null : region.id)}
                className={`p-4 rounded-lg border-2 transition-all ${
                  isSelected
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-200 hover:border-gray-300 bg-white'
                }`}
              >
                <div className="text-center">
                  <div
                    className={`text-2xl font-bold ${
                      stats.violationsCount > 0
                        ? 'text-error-600'
                        : stats.contractCount > 0
                        ? 'text-success-600'
                        : 'text-gray-400'
                    }`}
                  >
                    {stats.contractCount}
                  </div>
                  <div className="text-xs text-gray-600 font-medium mt-1">
                    {region.name}
                  </div>
                  {stats.violationsCount > 0 && (
                    <div className="text-xs text-error-500 mt-1">
                      {stats.violationsCount} violation{stats.violationsCount > 1 ? 's' : ''}
                    </div>
                  )}
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Selected Region Details */}
      {selectedRegion && (
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">
            {REGIONS.find((r) => r.id === selectedRegion)?.name} Details
          </h2>

          {/* Contracts in Region */}
          <div className="mb-6">
            <h3 className="text-sm font-medium text-gray-700 mb-2">
              Contracts in this Region
            </h3>
            {residencyMap?.[selectedRegion] && residencyMap[selectedRegion].length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {residencyMap[selectedRegion].map((contractId) => (
                  <a
                    key={contractId}
                    href={`/contracts/${contractId}`}
                    className="px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded-full text-sm text-gray-700"
                  >
                    {contractId}
                  </a>
                ))}
              </div>
            ) : (
              <div className="text-gray-500 text-sm">
                No contracts assigned to this region.
              </div>
            )}
          </div>

          {/* Residency Checks */}
          <div>
            <h3 className="text-sm font-medium text-gray-700 mb-2">Compliance Checks</h3>
            {auditReport?.residency_checks?.filter((c) => c.region === selectedRegion)
              .length ? (
              <div className="space-y-3">
                {auditReport.residency_checks
                  .filter((c) => c.region === selectedRegion)
                  .map((check, idx) => (
                    <div
                      key={idx}
                      className={`p-4 rounded-lg ${
                        check.compliant ? 'bg-success-50' : 'bg-error-50'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <a
                          href={`/contracts/${check.contract_id}`}
                          className="font-medium text-gray-900 hover:text-primary-600"
                        >
                          {check.contract_id}
                        </a>
                        <span
                          className={`px-2 py-1 rounded text-sm font-medium ${
                            check.compliant
                              ? 'bg-success-100 text-success-700'
                              : 'bg-error-100 text-error-700'
                          }`}
                        >
                          {check.compliant ? 'Compliant' : 'Non-Compliant'}
                        </span>
                      </div>
                      <div className="text-sm text-gray-500 mt-1">
                        {check.fields_checked} fields checked
                      </div>
                      {check.violations.length > 0 && (
                        <div className="mt-3 space-y-2">
                          {check.violations.map((v, vidx) => (
                            <div
                              key={vidx}
                              className="text-sm bg-white p-2 rounded border border-error-200"
                            >
                              <span className="font-mono text-error-600">
                                {v.field_name ?? 'Contract level'}
                              </span>
                              : {v.violation_reason}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
              </div>
            ) : (
              <div className="text-gray-500 text-sm">
                No compliance checks performed for this region.
              </div>
            )}
          </div>
        </div>
      )}

      {/* All Violations */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">All Residency Violations</h2>
        {auditReport?.residency_checks?.some((c) => c.violations.length > 0) ? (
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
                    Current Region
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Required Region
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Reason
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {auditReport.residency_checks
                  .flatMap((check) =>
                    check.violations.map((v) => ({ ...v, contract_id: check.contract_id }))
                  )
                  .map((violation, idx) => (
                    <tr key={idx} className="hover:bg-gray-50">
                      <td className="px-4 py-3 text-sm">
                        <a
                          href={`/contracts/${violation.contract_id}`}
                          className="text-primary-600 hover:underline"
                        >
                          {violation.contract_id}
                        </a>
                      </td>
                      <td className="px-4 py-3 text-sm font-mono">
                        {violation.field_name ?? '—'}
                      </td>
                      <td className="px-4 py-3 text-sm uppercase">
                        {violation.current_region}
                      </td>
                      <td className="px-4 py-3 text-sm uppercase">
                        {violation.required_region}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600">
                        {violation.violation_reason ?? 'Region mismatch'}
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-success-600 text-center py-8">
            No residency violations detected. All data is compliant with residency
            requirements.
          </div>
        )}
      </div>

      {/* Region Legend */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">Region Reference</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {REGIONS.map((region) => (
            <div key={region.id} className="flex items-center gap-3">
              <div className="w-12 h-8 bg-gray-100 rounded flex items-center justify-center text-xs font-bold text-gray-600 uppercase">
                {region.id}
              </div>
              <div>
                <div className="text-sm font-medium text-gray-900">{region.name}</div>
                <div className="text-xs text-gray-500">{region.description}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
