'use client';

import { useState, useEffect, useCallback } from 'react';
import yaml from 'js-yaml';
import type { BreakingChangeInfo, ContractStatus } from '@/lib/types';

/**
 * YAML Editor Component
 *
 * Features:
 * - Edit YAML content directly
 * - Syntax validation
 * - Parse YAML to form data
 * - Breaking change detection for live contracts
 * - Version control (auto-increment on breaking changes)
 */

interface YamlEditorProps {
  initialYaml: string;
  contractStatus: ContractStatus;
  currentVersion: string;
  onSave: (
    parsedData: Record<string, unknown>,
    isBreaking: boolean,
    newVersion?: string
  ) => Promise<void>;
  onCancel: () => void;
  detectBreakingChanges?: (newData: Record<string, unknown>) => Promise<BreakingChangeInfo[]>;
}

// Breaking change types that require version bump
const BREAKING_CHANGE_TYPES = [
  'field_removed',
  'type_changed_incompatible',
  'nullable_to_required',
  'enum_values_removed',
  'constraint_tightened',
  'required_field_added',
  'primary_key_changed',
];

export default function YamlEditor({
  initialYaml,
  contractStatus,
  currentVersion,
  onSave,
  onCancel,
  detectBreakingChanges,
}: YamlEditorProps) {
  const [yaml_content, setYamlContent] = useState(initialYaml);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [breakingChanges, setBreakingChanges] = useState<BreakingChangeInfo[]>([]);
  const [showBreakingWarning, setShowBreakingWarning] = useState(false);
  const [parsedData, setParsedData] = useState<Record<string, unknown> | null>(null);
  const [validationError, setValidationError] = useState<string | null>(null);

  // Parse YAML and validate
  const validateYaml = useCallback((content: string) => {
    try {
      const parsed = yaml.load(content) as Record<string, unknown>;
      setValidationError(null);
      return parsed;
    } catch (err) {
      if (err instanceof Error) {
        setValidationError(err.message);
      }
      return null;
    }
  }, []);

  // Real-time validation
  useEffect(() => {
    const parsed = validateYaml(yaml_content);
    setParsedData(parsed);
  }, [yaml_content, validateYaml]);

  // Calculate new version based on change type
  const calculateNewVersion = (current: string, isBreaking: boolean): string => {
    const parts = current.split('.');
    const major = parseInt(parts[0] || '1', 10);
    const minor = parseInt(parts[1] || '0', 10);
    const patch = parseInt(parts[2] || '0', 10);

    if (isBreaking) {
      // Major version bump for breaking changes
      return `${major + 1}.0.0`;
    } else {
      // Minor version bump for non-breaking changes
      return `${major}.${minor + 1}.${patch}`;
    }
  };

  // Check for breaking changes
  const handleCheckBreakingChanges = async () => {
    if (!parsedData) {
      setError('Invalid YAML. Please fix errors before saving.');
      return;
    }

    if (contractStatus === 'active' && detectBreakingChanges) {
      try {
        setSaving(true);
        const changes = await detectBreakingChanges(parsedData);
        const hasBreaking = changes.some((c) =>
          BREAKING_CHANGE_TYPES.includes(c.change_type)
        );

        if (hasBreaking) {
          setBreakingChanges(changes);
          setShowBreakingWarning(true);
        } else {
          // No breaking changes, save directly
          await handleSave(false);
        }
      } catch (err) {
        setError('Failed to check for breaking changes');
      } finally {
        setSaving(false);
      }
    } else {
      // Draft or other status - save directly
      await handleSave(false);
    }
  };

  // Save with version control
  const handleSave = async (isBreaking: boolean) => {
    if (!parsedData) {
      setError('Invalid YAML. Please fix errors before saving.');
      return;
    }

    try {
      setSaving(true);
      setError(null);

      const newVersion = isBreaking
        ? calculateNewVersion(currentVersion, true)
        : undefined;

      await onSave(parsedData, isBreaking, newVersion);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save');
    } finally {
      setSaving(false);
      setShowBreakingWarning(false);
    }
  };

  // Handle proceeding with breaking changes
  const handleProceedWithBreaking = () => {
    handleSave(true);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl mx-4 max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-slate-900">Edit YAML</h2>
            <p className="text-sm text-slate-500">
              Current version: {currentVersion} • Status: {contractStatus}
            </p>
          </div>
          <button
            onClick={onCancel}
            className="text-slate-400 hover:text-slate-600"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Editor */}
        <div className="flex-1 overflow-hidden p-6">
          <div className="h-full flex flex-col">
            {/* Validation Status */}
            {validationError && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                <div className="flex items-start gap-2">
                  <svg className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <div>
                    <p className="text-sm font-medium text-red-800">Invalid YAML Syntax</p>
                    <p className="text-xs text-red-600 mt-1 font-mono">{validationError}</p>
                  </div>
                </div>
              </div>
            )}

            {!validationError && parsedData && (
              <div className="mb-4 p-3 bg-emerald-50 border border-emerald-200 rounded-lg">
                <div className="flex items-center gap-2">
                  <svg className="w-5 h-5 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <p className="text-sm text-emerald-700">YAML is valid</p>
                </div>
              </div>
            )}

            {/* Error Alert */}
            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                {error}
              </div>
            )}

            {/* Textarea */}
            <textarea
              value={yaml_content}
              onChange={(e) => setYamlContent(e.target.value)}
              className={`flex-1 w-full font-mono text-sm p-4 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 resize-none ${
                validationError ? 'border-red-300 bg-red-50' : 'border-slate-300'
              }`}
              spellCheck={false}
            />
          </div>
        </div>

        {/* Live Contract Warning */}
        {contractStatus === 'active' && (
          <div className="px-6 py-3 bg-amber-50 border-t border-amber-200">
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <p className="text-sm text-amber-700">
                This is a <strong>live contract</strong>. Breaking changes will create a new major version.
              </p>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="px-6 py-4 border-t border-slate-200 flex justify-end gap-3">
          <button
            onClick={onCancel}
            className="px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50"
          >
            Cancel
          </button>
          <button
            onClick={handleCheckBreakingChanges}
            disabled={saving || !!validationError || !parsedData}
            className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {saving && (
              <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
            )}
            Save Changes
          </button>
        </div>

        {/* Breaking Changes Warning Modal */}
        {showBreakingWarning && (
          <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
            <div className="bg-white rounded-lg shadow-xl max-w-lg w-full mx-4 p-6">
              <div className="flex items-start gap-3 mb-4">
                <div className="w-10 h-10 rounded-full bg-red-100 flex items-center justify-center flex-shrink-0">
                  <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                </div>
                <div>
                  <h3 className="font-semibold text-slate-900">Breaking Changes Detected</h3>
                  <p className="text-sm text-slate-600 mt-1">
                    Your changes will break compatibility. A new major version ({calculateNewVersion(currentVersion, true)}) will be created.
                  </p>
                </div>
              </div>

              {/* Breaking Changes List */}
              <div className="mb-4 max-h-60 overflow-y-auto">
                <ul className="space-y-2">
                  {breakingChanges.map((change, idx) => (
                    <li
                      key={idx}
                      className="p-3 bg-red-50 rounded-lg border border-red-200"
                    >
                      <div className="flex items-start gap-2">
                        <span className="px-2 py-0.5 bg-red-100 text-red-700 text-xs font-medium rounded">
                          {change.change_type.replace(/_/g, ' ')}
                        </span>
                        {change.field && (
                          <span className="text-sm text-slate-600">
                            Field: <code className="font-mono">{change.field}</code>
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-slate-700 mt-1">{change.description}</p>
                      {change.migration_hint && (
                        <p className="text-xs text-slate-500 mt-1">
                          Hint: {change.migration_hint}
                        </p>
                      )}
                    </li>
                  ))}
                </ul>
              </div>

              <div className="flex justify-end gap-3">
                <button
                  onClick={() => setShowBreakingWarning(false)}
                  className="px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleProceedWithBreaking}
                  disabled={saving}
                  className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Proceed with Breaking Changes
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
