'use client';

import { useEffect, useState } from 'react';
import type {
  ContractDiff,
  VersionSummary,
  TypeChange,
  ConstraintChange,
  SectionChange,
} from '@/lib/types';
import api from '@/lib/api';

/**
 * Version Comparison Component (T-385)
 *
 * Displays a side-by-side comparison of contract versions with:
 * - Breaking change highlights
 * - Field additions/removals
 * - Type changes
 * - Constraint changes
 * - Section changes (ODCS)
 */

interface VersionComparisonProps {
  contractId: string;
  fromVersion?: string;
  toVersion?: string;
  onClose?: () => void;
}

export default function VersionComparison({
  contractId,
  fromVersion,
  toVersion,
  onClose,
}: VersionComparisonProps) {
  const [versions, setVersions] = useState<VersionSummary[]>([]);
  const [selectedFrom, setSelectedFrom] = useState(fromVersion || '');
  const [selectedTo, setSelectedTo] = useState(toVersion || '');
  const [diff, setDiff] = useState<ContractDiff | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load available versions
  useEffect(() => {
    async function loadVersions() {
      try {
        const response = await api.getVersions(contractId);
        setVersions(response.items);

        // Default to comparing latest two versions
        if (response.items.length >= 2 && !fromVersion && !toVersion) {
          setSelectedFrom(response.items[1].version);
          setSelectedTo(response.items[0].version);
        } else if (response.items.length === 1) {
          setSelectedTo(response.items[0].version);
        }
      } catch (err) {
        setError('Failed to load versions');
      }
    }

    loadVersions();
  }, [contractId, fromVersion, toVersion]);

  // Load diff when versions are selected
  useEffect(() => {
    async function loadDiff() {
      if (!selectedFrom || !selectedTo || selectedFrom === selectedTo) {
        setDiff(null);
        return;
      }

      try {
        setLoading(true);
        setError(null);
        const diffResult = await api.diffContract(contractId, selectedFrom, selectedTo);
        setDiff(diffResult);
      } catch (err) {
        setError('Failed to load diff');
      } finally {
        setLoading(false);
      }
    }

    loadDiff();
  }, [contractId, selectedFrom, selectedTo]);

  return (
    <div className="bg-white rounded-lg border border-slate-200 overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-slate-800">Version Comparison</h2>
          <p className="text-sm text-slate-500">Compare changes between contract versions</p>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>

      {/* Version Selectors */}
      <div className="px-6 py-4 bg-slate-50 border-b border-slate-200">
        <div className="flex items-center gap-4">
          <div className="flex-1">
            <label className="block text-xs font-medium text-slate-500 mb-1">From Version</label>
            <select
              value={selectedFrom}
              onChange={(e) => setSelectedFrom(e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
            >
              <option value="">Select version...</option>
              {versions.map((v) => (
                <option key={v.version} value={v.version}>
                  v{v.version} {v.is_breaking && '(breaking)'} - {v.created_at ? new Date(v.created_at).toLocaleDateString() : ''}
                </option>
              ))}
            </select>
          </div>

          <div className="pt-5">
            <svg className="w-5 h-5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </div>

          <div className="flex-1">
            <label className="block text-xs font-medium text-slate-500 mb-1">To Version</label>
            <select
              value={selectedTo}
              onChange={(e) => setSelectedTo(e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
            >
              <option value="">Select version...</option>
              {versions.map((v) => (
                <option key={v.version} value={v.version}>
                  v{v.version} {v.is_breaking && '(breaking)'} - {v.created_at ? new Date(v.created_at).toLocaleDateString() : ''}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="p-8 text-center text-slate-400">
          Loading comparison...
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="p-4 bg-red-50 text-red-600 text-sm">
          {error}
        </div>
      )}

      {/* No Selection */}
      {!loading && !error && !diff && selectedFrom && selectedTo && selectedFrom === selectedTo && (
        <div className="p-8 text-center text-slate-400">
          Select different versions to compare
        </div>
      )}

      {/* Diff Results */}
      {diff && (
        <div className="divide-y divide-slate-200">
          {/* Breaking Changes Warning */}
          {diff.has_breaking_changes && (
            <div className="px-6 py-4 bg-red-50 border-b border-red-200">
              <div className="flex items-center gap-2 text-red-700">
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <span className="font-medium">This version contains breaking changes</span>
              </div>
            </div>
          )}

          {/* Summary */}
          <div className="px-6 py-4">
            <h3 className="font-medium text-slate-800 mb-3">Summary</h3>
            <div className="grid grid-cols-4 gap-4 text-center">
              <div className="bg-emerald-50 rounded-lg p-3">
                <div className="text-2xl font-bold text-emerald-600">{diff.added_fields.length}</div>
                <div className="text-xs text-emerald-700">Added</div>
              </div>
              <div className="bg-red-50 rounded-lg p-3">
                <div className="text-2xl font-bold text-red-600">{diff.removed_fields.length}</div>
                <div className="text-xs text-red-700">Removed</div>
              </div>
              <div className="bg-amber-50 rounded-lg p-3">
                <div className="text-2xl font-bold text-amber-600">{diff.type_changes.length}</div>
                <div className="text-xs text-amber-700">Type Changes</div>
              </div>
              <div className="bg-blue-50 rounded-lg p-3">
                <div className="text-2xl font-bold text-blue-600">{diff.constraint_changes.length}</div>
                <div className="text-xs text-blue-700">Constraint Changes</div>
              </div>
            </div>
          </div>

          {/* Added Fields */}
          {diff.added_fields.length > 0 && (
            <div className="px-6 py-4">
              <h3 className="font-medium text-slate-800 mb-3 flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-emerald-500"></span>
                Added Fields
              </h3>
              <div className="space-y-2">
                {diff.added_fields.map((field) => (
                  <div
                    key={field}
                    className="px-3 py-2 bg-emerald-50 border border-emerald-200 rounded text-emerald-800 font-mono text-sm"
                  >
                    + {field}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Removed Fields */}
          {diff.removed_fields.length > 0 && (
            <div className="px-6 py-4">
              <h3 className="font-medium text-slate-800 mb-3 flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-red-500"></span>
                Removed Fields
                {diff.has_breaking_changes && (
                  <span className="px-2 py-0.5 bg-red-100 text-red-700 text-xs rounded">Breaking</span>
                )}
              </h3>
              <div className="space-y-2">
                {diff.removed_fields.map((field) => (
                  <div
                    key={field}
                    className="px-3 py-2 bg-red-50 border border-red-200 rounded text-red-800 font-mono text-sm"
                  >
                    - {field}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Type Changes */}
          {diff.type_changes.length > 0 && (
            <div className="px-6 py-4">
              <h3 className="font-medium text-slate-800 mb-3 flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-amber-500"></span>
                Type Changes
              </h3>
              <div className="space-y-2">
                {diff.type_changes.map((change, i) => (
                  <TypeChangeRow key={i} change={change} />
                ))}
              </div>
            </div>
          )}

          {/* Constraint Changes */}
          {diff.constraint_changes.length > 0 && (
            <div className="px-6 py-4">
              <h3 className="font-medium text-slate-800 mb-3 flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-blue-500"></span>
                Constraint Changes
              </h3>
              <div className="space-y-2">
                {diff.constraint_changes.map((change, i) => (
                  <ConstraintChangeRow key={i} change={change} />
                ))}
              </div>
            </div>
          )}

          {/* Section Changes (ODCS) */}
          {diff.section_changes && diff.section_changes.length > 0 && (
            <div className="px-6 py-4">
              <h3 className="font-medium text-slate-800 mb-3 flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-indigo-500"></span>
                Section Changes
              </h3>
              <div className="space-y-2">
                {diff.section_changes.map((change, i) => (
                  <SectionChangeRow key={i} change={change} />
                ))}
              </div>
            </div>
          )}

          {/* Schema Changes (ODCS) */}
          {(diff.added_schemas?.length || diff.removed_schemas?.length || diff.modified_schemas?.length) && (
            <div className="px-6 py-4">
              <h3 className="font-medium text-slate-800 mb-3 flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-purple-500"></span>
                Schema Changes
              </h3>
              <div className="grid grid-cols-3 gap-4">
                {diff.added_schemas && diff.added_schemas.length > 0 && (
                  <div>
                    <div className="text-xs text-slate-500 mb-2">Added</div>
                    {diff.added_schemas.map((s) => (
                      <div key={s} className="px-2 py-1 bg-emerald-50 text-emerald-700 rounded text-sm mb-1">
                        {s}
                      </div>
                    ))}
                  </div>
                )}
                {diff.removed_schemas && diff.removed_schemas.length > 0 && (
                  <div>
                    <div className="text-xs text-slate-500 mb-2">Removed</div>
                    {diff.removed_schemas.map((s) => (
                      <div key={s} className="px-2 py-1 bg-red-50 text-red-700 rounded text-sm mb-1">
                        {s}
                      </div>
                    ))}
                  </div>
                )}
                {diff.modified_schemas && diff.modified_schemas.length > 0 && (
                  <div>
                    <div className="text-xs text-slate-500 mb-2">Modified</div>
                    {diff.modified_schemas.map((s) => (
                      <div key={s} className="px-2 py-1 bg-amber-50 text-amber-700 rounded text-sm mb-1">
                        {s}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* No Changes */}
          {!diff.has_breaking_changes &&
            diff.added_fields.length === 0 &&
            diff.removed_fields.length === 0 &&
            diff.type_changes.length === 0 &&
            diff.constraint_changes.length === 0 && (
              <div className="px-6 py-8 text-center text-slate-400">
                No schema changes between these versions
              </div>
            )}
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Sub-components
// =============================================================================

function TypeChangeRow({ change }: { change: TypeChange }) {
  return (
    <div
      className={`px-3 py-2 border rounded ${
        change.is_breaking
          ? 'bg-red-50 border-red-200'
          : 'bg-amber-50 border-amber-200'
      }`}
    >
      <div className="flex items-center justify-between">
        <span className="font-mono text-sm text-slate-700">{change.field}</span>
        {change.is_breaking && (
          <span className="px-2 py-0.5 bg-red-100 text-red-700 text-xs rounded">Breaking</span>
        )}
      </div>
      <div className="flex items-center gap-2 mt-1 text-sm">
        <span className="px-2 py-0.5 bg-slate-100 rounded text-slate-600">{change.from_type}</span>
        <span className="text-slate-400">→</span>
        <span className="px-2 py-0.5 bg-slate-100 rounded text-slate-600">{change.to_type}</span>
      </div>
    </div>
  );
}

function ConstraintChangeRow({ change }: { change: ConstraintChange }) {
  return (
    <div
      className={`px-3 py-2 border rounded ${
        change.is_breaking
          ? 'bg-red-50 border-red-200'
          : 'bg-blue-50 border-blue-200'
      }`}
    >
      <div className="flex items-center justify-between">
        <span className="font-mono text-sm text-slate-700">
          {change.field}.{change.constraint}
        </span>
        {change.is_breaking && (
          <span className="px-2 py-0.5 bg-red-100 text-red-700 text-xs rounded">Breaking</span>
        )}
      </div>
      <div className="flex items-center gap-2 mt-1 text-sm">
        <span className="px-2 py-0.5 bg-slate-100 rounded text-slate-600">
          {JSON.stringify(change.from_value)}
        </span>
        <span className="text-slate-400">→</span>
        <span className="px-2 py-0.5 bg-slate-100 rounded text-slate-600">
          {JSON.stringify(change.to_value)}
        </span>
      </div>
    </div>
  );
}

function SectionChangeRow({ change }: { change: SectionChange }) {
  const colors = {
    added: { bg: 'bg-emerald-50', border: 'border-emerald-200', text: 'text-emerald-700', icon: '+' },
    removed: { bg: 'bg-red-50', border: 'border-red-200', text: 'text-red-700', icon: '-' },
    modified: { bg: 'bg-amber-50', border: 'border-amber-200', text: 'text-amber-700', icon: '~' },
  };
  const style = colors[change.change_type];

  return (
    <div className={`px-3 py-2 border rounded ${style.bg} ${style.border}`}>
      <div className="flex items-center justify-between">
        <span className={`font-medium ${style.text}`}>
          {style.icon} {change.section}
        </span>
        {change.is_breaking && (
          <span className="px-2 py-0.5 bg-red-100 text-red-700 text-xs rounded">Breaking</span>
        )}
      </div>
      {change.summary && (
        <div className="text-sm text-slate-600 mt-1">{change.summary}</div>
      )}
    </div>
  );
}

// =============================================================================
// Compact Version Badge
// =============================================================================

export function VersionBadge({
  version,
  isBreaking,
  onClick,
}: {
  version: string;
  isBreaking?: boolean;
  onClick?: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`px-2 py-1 rounded text-xs font-medium ${
        isBreaking
          ? 'bg-red-50 text-red-700 border border-red-200'
          : 'bg-slate-100 text-slate-600 border border-slate-200'
      } hover:bg-opacity-80 transition-colors`}
    >
      v{version}
      {isBreaking && ' (breaking)'}
    </button>
  );
}
