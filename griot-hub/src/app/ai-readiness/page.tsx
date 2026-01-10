'use client';

import { useEffect, useState } from 'react';
import type { AIReadinessReport, AIReadinessScore } from '@/lib/types';
import api from '@/lib/api';

/**
 * AI Readiness Page (T-130)
 *
 * Displays AI/LLM readiness metrics:
 * - Overall readiness score
 * - Documentation quality
 * - Semantic coverage (descriptions, units, glossary terms)
 * - Data quality indicators
 * - Per-contract readiness breakdown
 * - Recommendations for improvement
 */
export default function AIReadinessPage() {
  const [report, setReport] = useState<AIReadinessReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchAIReadinessReport() {
      try {
        setLoading(true);
        setError(null);
        const data = await api.getAIReadinessReport({ include_details: true });
        setReport(data);
      } catch (err) {
        setError(
          'Failed to load AI readiness report. The report API may not be available yet.'
        );
      } finally {
        setLoading(false);
      }
    }

    fetchAIReadinessReport();
  }, []);

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-success-600';
    if (score >= 60) return 'text-warning-600';
    return 'text-error-600';
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 80) return 'bg-success-500';
    if (score >= 60) return 'bg-warning-500';
    return 'bg-error-500';
  };

  const renderScoreRing = (score: number, size: 'sm' | 'lg' = 'lg') => {
    const radius = size === 'lg' ? 45 : 30;
    const circumference = 2 * Math.PI * radius;
    const progress = (score / 100) * circumference;

    return (
      <div className={`relative ${size === 'lg' ? 'w-32 h-32' : 'w-20 h-20'}`}>
        <svg className="w-full h-full transform -rotate-90">
          <circle
            cx="50%"
            cy="50%"
            r={radius}
            fill="none"
            stroke="#e5e7eb"
            strokeWidth={size === 'lg' ? 8 : 6}
          />
          <circle
            cx="50%"
            cy="50%"
            r={radius}
            fill="none"
            stroke={score >= 80 ? '#22c55e' : score >= 60 ? '#f59e0b' : '#ef4444'}
            strokeWidth={size === 'lg' ? 8 : 6}
            strokeDasharray={circumference}
            strokeDashoffset={circumference - progress}
            strokeLinecap="round"
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span
            className={`${size === 'lg' ? 'text-2xl' : 'text-lg'} font-bold ${getScoreColor(score)}`}
          >
            {score}
          </span>
        </div>
      </div>
    );
  };

  const renderScoreCard = (label: string, score: number) => (
    <div className="bg-gray-50 rounded-lg p-4 text-center">
      {renderScoreRing(score, 'sm')}
      <div className="text-sm text-gray-600 mt-2">{label}</div>
    </div>
  );

  if (loading) {
    return (
      <div className="text-gray-500 text-center py-16">
        Loading AI readiness report...
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">AI Readiness</h1>
          <p className="text-gray-500 mt-1">
            Measure how well your contracts are prepared for AI/LLM consumption
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

      {/* Overall Score */}
      <div className="card">
        <div className="flex flex-col md:flex-row items-center gap-8">
          <div className="text-center">
            {renderScoreRing(report?.overall_score?.overall_score ?? 0, 'lg')}
            <div className="text-lg font-semibold text-gray-800 mt-2">Overall Score</div>
          </div>

          <div className="flex-1 grid grid-cols-2 md:grid-cols-4 gap-4">
            {renderScoreCard(
              'Documentation',
              report?.overall_score?.documentation_score ?? 0
            )}
            {renderScoreCard(
              'Semantic Coverage',
              report?.overall_score?.semantic_coverage_score ?? 0
            )}
            {renderScoreCard('Data Quality', report?.overall_score?.data_quality_score ?? 0)}
            {renderScoreCard('Consistency', report?.overall_score?.consistency_score ?? 0)}
          </div>
        </div>
      </div>

      {/* Semantic Coverage Details */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">Semantic Coverage</h2>
        {report?.semantic_coverage ? (
          <div className="space-y-4">
            {[
              {
                label: 'Fields with Description',
                value: report.semantic_coverage.fields_with_description,
                total: report.semantic_coverage.total_fields,
              },
              {
                label: 'Fields with Unit',
                value: report.semantic_coverage.fields_with_unit,
                total: report.semantic_coverage.total_fields,
              },
              {
                label: 'Fields with Aggregation',
                value: report.semantic_coverage.fields_with_aggregation,
                total: report.semantic_coverage.total_fields,
              },
              {
                label: 'Fields with Glossary Term',
                value: report.semantic_coverage.fields_with_glossary_term,
                total: report.semantic_coverage.total_fields,
              },
            ].map((item, idx) => {
              const percentage =
                item.total > 0 ? (item.value / item.total) * 100 : 0;
              return (
                <div key={idx}>
                  <div className="flex items-center justify-between text-sm mb-1">
                    <span className="text-gray-600">{item.label}</span>
                    <span className="text-gray-900 font-medium">
                      {item.value} / {item.total} ({percentage.toFixed(0)}%)
                    </span>
                  </div>
                  <div className="h-3 bg-gray-100 rounded overflow-hidden">
                    <div
                      className={`h-full ${getScoreBgColor(percentage)}`}
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="text-gray-500 text-center py-8">
            No semantic coverage data available.
          </div>
        )}
      </div>

      {/* Top Recommendations */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">Top Recommendations</h2>
        {report?.top_recommendations && report.top_recommendations.length > 0 ? (
          <ul className="space-y-3">
            {report.top_recommendations.map((rec, idx) => (
              <li key={idx} className="flex items-start gap-3">
                <span className="flex-shrink-0 w-6 h-6 bg-primary-100 text-primary-700 rounded-full flex items-center justify-center text-sm font-medium">
                  {idx + 1}
                </span>
                <span className="text-gray-700">{rec}</span>
              </li>
            ))}
          </ul>
        ) : (
          <div className="text-gray-500 text-center py-8">
            No recommendations available. Your contracts may already be well-documented!
          </div>
        )}
      </div>

      {/* Contract Readiness Breakdown */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">
          Contract Readiness Breakdown
        </h2>
        {report?.readiness_by_contract && report.readiness_by_contract.length > 0 ? (
          <div className="space-y-3">
            {report.readiness_by_contract.slice(0, 15).map((contract, idx) => (
              <div key={idx} className="flex items-center gap-4">
                <div className="w-48 truncate">
                  <a
                    href={`/contracts/${contract.contract_id}`}
                    className="text-primary-600 hover:underline text-sm"
                  >
                    {contract.contract_id}
                  </a>
                </div>
                <div className="flex-1 h-4 bg-gray-100 rounded overflow-hidden">
                  <div
                    className={`h-full ${getScoreBgColor(contract.score)}`}
                    style={{ width: `${contract.score}%` }}
                  />
                </div>
                <div className={`w-12 text-right text-sm font-medium ${getScoreColor(contract.score)}`}>
                  {contract.score}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-gray-500 text-center py-8">
            No contract readiness data available.
          </div>
        )}
      </div>

      {/* Detailed Contract Analysis */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">
          Detailed Contract Analysis
        </h2>
        {report?.contracts && report.contracts.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Contract
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Overall
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Docs
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Semantic
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Quality
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Issues
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {report.contracts.slice(0, 10).map((contract, idx) => (
                  <tr key={idx} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm">
                      <a
                        href={`/contracts/${contract.contract_id}`}
                        className="text-primary-600 hover:underline"
                      >
                        {contract.contract_name}
                      </a>
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <span className={`font-medium ${getScoreColor(contract.score.overall_score)}`}>
                        {contract.score.overall_score}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <span className={getScoreColor(contract.score.documentation_score)}>
                        {contract.score.documentation_score}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <span className={getScoreColor(contract.score.semantic_coverage_score)}>
                        {contract.score.semantic_coverage_score}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <span className={getScoreColor(contract.score.data_quality_score)}>
                        {contract.score.data_quality_score}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500">
                      {contract.recommendations.length > 0 ? (
                        <span className="text-warning-600">
                          {contract.recommendations.length} issue
                          {contract.recommendations.length > 1 ? 's' : ''}
                        </span>
                      ) : (
                        <span className="text-success-600">None</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {report.contracts.length > 10 && (
              <div className="text-center text-sm text-gray-500 py-4">
                Showing 10 of {report.contracts.length} contracts
              </div>
            )}
          </div>
        ) : (
          <div className="text-gray-500 text-center py-8">
            No contract analysis available.
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
