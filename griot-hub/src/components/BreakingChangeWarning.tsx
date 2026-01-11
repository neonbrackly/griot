'use client';

import type { BreakingChangeInfo } from '@/lib/types';

/**
 * Breaking Change Warning Component (T-305, T-384)
 *
 * Displays breaking changes detected during contract update with:
 * - Clear warning banner
 * - Details about each breaking change
 * - Migration hints when available
 * - Options to proceed or cancel
 */

interface BreakingChangeWarningProps {
  changes: BreakingChangeInfo[];
  onProceed: () => void;
  onCancel: () => void;
  loading?: boolean;
}

export default function BreakingChangeWarning({
  changes,
  onProceed,
  onCancel,
  loading = false,
}: BreakingChangeWarningProps) {
  if (changes.length === 0) return null;

  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-6 mb-6">
      {/* Header */}
      <div className="flex items-start gap-3 mb-4">
        <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center flex-shrink-0">
          <span className="text-red-600 text-lg">⚠️</span>
        </div>
        <div>
          <h3 className="text-lg font-semibold text-red-800">
            Breaking Changes Detected
          </h3>
          <p className="text-red-700 text-sm mt-1">
            This update contains {changes.length} breaking change{changes.length !== 1 ? 's' : ''} that may affect downstream consumers.
          </p>
        </div>
      </div>

      {/* Changes List */}
      <div className="space-y-3 mb-6">
        {changes.map((change, index) => (
          <div
            key={index}
            className="bg-white border border-red-100 rounded-lg p-4"
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="px-2 py-0.5 bg-red-100 text-red-700 text-xs font-medium rounded">
                    {formatChangeType(change.change_type)}
                  </span>
                  {change.field && (
                    <span className="font-mono text-sm text-slate-600">
                      {change.field}
                    </span>
                  )}
                </div>
                <p className="text-slate-700 text-sm">{change.description}</p>
                {(change.from_value !== undefined || change.to_value !== undefined) && (
                  <div className="flex items-center gap-2 mt-2 text-xs">
                    {change.from_value !== undefined && (
                      <span className="px-2 py-1 bg-slate-100 rounded text-slate-600">
                        From: <code>{JSON.stringify(change.from_value)}</code>
                      </span>
                    )}
                    <span className="text-slate-400">→</span>
                    {change.to_value !== undefined && (
                      <span className="px-2 py-1 bg-slate-100 rounded text-slate-600">
                        To: <code>{JSON.stringify(change.to_value)}</code>
                      </span>
                    )}
                  </div>
                )}
              </div>
            </div>
            {change.migration_hint && (
              <div className="mt-3 p-3 bg-blue-50 rounded text-sm">
                <span className="font-medium text-blue-700">Migration hint: </span>
                <span className="text-blue-600">{change.migration_hint}</span>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Actions */}
      <div className="flex items-center justify-between pt-4 border-t border-red-200">
        <p className="text-sm text-red-600">
          Proceeding will create a new major version and notify consumers.
        </p>
        <div className="flex gap-3">
          <button
            onClick={onCancel}
            disabled={loading}
            className="px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            onClick={onProceed}
            disabled={loading}
            className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 disabled:opacity-50 flex items-center gap-2"
          >
            {loading && (
              <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                  fill="none"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                />
              </svg>
            )}
            Proceed with Breaking Changes
          </button>
        </div>
      </div>
    </div>
  );
}

/**
 * Compact inline warning for version tabs / history
 */
export function BreakingChangeBadge({ count }: { count: number }) {
  if (count === 0) return null;

  return (
    <span className="px-2 py-0.5 bg-red-50 text-red-700 text-xs font-medium rounded-full border border-red-200">
      {count} breaking
    </span>
  );
}

/**
 * Helper: Format breaking change type for display
 */
function formatChangeType(type: string): string {
  const typeMap: Record<string, string> = {
    field_removed: 'Field Removed',
    type_changed_incompatible: 'Type Changed',
    field_renamed: 'Field Renamed',
    required_field_added: 'Required Field Added',
    enum_value_removed: 'Enum Value Removed',
    constraint_tightened: 'Constraint Tightened',
    nullable_to_required: 'Now Required',
  };
  return typeMap[type] || type.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
}
