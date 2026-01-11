'use client';

import { useEffect, useState, useCallback, useMemo } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import type {
  Contract,
  ContractCreate,
  ContractUpdate,
  Description,
  SchemaDefinition,
  SchemaProperty,
  Legal,
  Compliance,
  SLA,
  Access,
  Team,
  Server,
  Role,
  Governance,
  BreakingChangeInfo,
  ContractStatus,
  PhysicalType,
  SensitivityLevel,
  AccessLevel,
  LegalBasis,
  ReviewCadence,
} from '@/lib/types';
import api, { ApiClientError } from '@/lib/api';
import BreakingChangeWarning from '@/components/BreakingChangeWarning';
import {
  DEFAULT_COMPLIANCE,
  DEFAULT_SLA,
  DEFAULT_ACCESS,
  DEFAULT_GOVERNANCE,
  DEFAULT_LEGAL,
  DEFAULT_SCHEMA_PROPERTY,
  inferPrivacyFromFieldName,
  applyAuditReadyDefaults,
  COMPLIANCE_PRESETS,
  SLA_PRESETS,
  PII_PRIVACY_PRESETS,
} from '@/lib/defaults';

/**
 * Contract Studio Page (T-380, T-382, T-383)
 *
 * Complete redesign for Open Data Contract Standard (ODCS) with:
 * - Collapsible section editors for all ODCS sections
 * - Breaking change detection (T-384)
 * - Smart defaults for audit-ready contracts (T-382)
 * - Privacy-aligning defaults with auto-detection (T-383)
 * - Live YAML preview (always visible in side panel)
 * - Validation before save with field-specific errors
 * - Two-step approval workflow
 * - Security-first defaults with warnings for reducing security
 */

// =============================================================================
// Types
// =============================================================================

type SectionKey = 'basics' | 'description' | 'schema' | 'legal' | 'compliance' | 'sla' | 'access' | 'team' | 'servers' | 'governance';

interface SectionState {
  expanded: boolean;
}

// Validation error tracking
interface ValidationErrors {
  contractId?: string;
  contractName?: string;
  teamName?: string;
  schema?: Record<number, { name?: string; properties?: Record<number, { name?: string }> }>;
  general?: string[];
}

// Security override tracking
interface SecurityOverride {
  field: string;
  previousValue: string;
  newValue: string;
  reason: string;
}

// =============================================================================
// Helper Components
// =============================================================================

function SectionHeader({
  title,
  subtitle,
  expanded,
  onToggle,
  hasContent,
  hasErrors,
}: {
  title: string;
  subtitle?: string;
  expanded: boolean;
  onToggle: () => void;
  hasContent?: boolean;
  hasErrors?: boolean;
}) {
  return (
    <button
      onClick={onToggle}
      className="w-full flex items-center justify-between p-4 text-left hover:bg-slate-50 transition-colors"
    >
      <div className="flex items-center gap-3">
        <span
          className={`w-6 h-6 rounded flex items-center justify-center text-xs ${
            hasErrors
              ? 'bg-red-100 text-red-600'
              : hasContent
              ? 'bg-indigo-100 text-indigo-600'
              : 'bg-slate-100 text-slate-400'
          }`}
        >
          {expanded ? '−' : '+'}
        </span>
        <div>
          <h3 className="font-medium text-slate-800">{title}</h3>
          {subtitle && <p className="text-xs text-slate-500">{subtitle}</p>}
        </div>
      </div>
      <div className="flex items-center gap-2">
        {hasErrors && (
          <span className="px-2 py-0.5 bg-red-50 text-red-600 text-xs rounded">
            Has Errors
          </span>
        )}
        {hasContent && !hasErrors && (
          <span className="px-2 py-0.5 bg-indigo-50 text-indigo-600 text-xs rounded">
            Configured
          </span>
        )}
      </div>
    </button>
  );
}

function FormField({
  label,
  required,
  children,
  hint,
  error,
}: {
  label: string;
  required?: boolean;
  children: React.ReactNode;
  hint?: string;
  error?: string;
}) {
  return (
    <div>
      <label className="block text-sm font-medium text-slate-700 mb-1">
        {label} {required && <span className="text-red-500">*</span>}
      </label>
      {children}
      {error && <p className="mt-1 text-xs text-red-500">{error}</p>}
      {hint && !error && <p className="mt-1 text-xs text-slate-500">{hint}</p>}
    </div>
  );
}

function Input({
  value,
  onChange,
  placeholder,
  disabled,
  type = 'text',
  error,
}: {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
  type?: string;
  error?: boolean;
}) {
  return (
    <input
      type={type}
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      disabled={disabled}
      className={`w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 disabled:bg-slate-100 disabled:text-slate-500 ${
        error ? 'border-red-300 bg-red-50' : 'border-slate-300'
      }`}
    />
  );
}

function TextArea({
  value,
  onChange,
  placeholder,
  rows = 3,
}: {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  rows?: number;
}) {
  return (
    <textarea
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      rows={rows}
      className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
    />
  );
}

function Select<T extends string>({
  value,
  onChange,
  options,
  disabled,
}: {
  value: T;
  onChange: (value: T) => void;
  options: { value: T; label: string }[];
  disabled?: boolean;
}) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value as T)}
      disabled={disabled}
      className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 disabled:bg-slate-100 disabled:text-slate-500 disabled:cursor-not-allowed"
    >
      {options.map((opt) => (
        <option key={opt.value} value={opt.value}>
          {opt.label}
        </option>
      ))}
    </select>
  );
}

function TagInput({
  value,
  onChange,
  placeholder,
}: {
  value: string[];
  onChange: (value: string[]) => void;
  placeholder?: string;
}) {
  const [input, setInput] = useState('');

  const addTag = () => {
    if (input.trim() && !value.includes(input.trim())) {
      onChange([...value, input.trim()]);
      setInput('');
    }
  };

  const removeTag = (tag: string) => {
    onChange(value.filter((t) => t !== tag));
  };

  return (
    <div className="border border-slate-300 rounded-lg p-2">
      <div className="flex flex-wrap gap-1 mb-2">
        {value.map((tag) => (
          <span
            key={tag}
            className="px-2 py-1 bg-indigo-50 text-indigo-700 text-xs rounded flex items-center gap-1"
          >
            {tag}
            <button onClick={() => removeTag(tag)} className="hover:text-indigo-900">
              ×
            </button>
          </span>
        ))}
      </div>
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
        placeholder={placeholder}
        className="w-full text-sm border-none p-0 focus:ring-0"
      />
    </div>
  );
}

// Security Warning Component
function SecurityWarning({
  message,
  onConfirm,
  onCancel,
}: {
  message: string;
  onConfirm: (reason: string) => void;
  onCancel: () => void;
}) {
  const [reason, setReason] = useState('');

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
        <div className="flex items-start gap-3 mb-4">
          <div className="w-10 h-10 rounded-full bg-amber-100 flex items-center justify-center flex-shrink-0">
            <svg className="w-5 h-5 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <div>
            <h3 className="font-semibold text-slate-900">Security Setting Change</h3>
            <p className="text-sm text-slate-600 mt-1">{message}</p>
          </div>
        </div>
        <div className="mb-4">
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Reason for Override <span className="text-red-500">*</span>
          </label>
          <textarea
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            placeholder="Please provide a business justification for reducing this security setting..."
            rows={3}
            className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-amber-500 focus:border-amber-500"
          />
        </div>
        <div className="flex justify-end gap-3">
          <button
            onClick={onCancel}
            className="px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50"
          >
            Cancel
          </button>
          <button
            onClick={() => reason.trim() && onConfirm(reason)}
            disabled={!reason.trim()}
            className="px-4 py-2 text-sm font-medium text-white bg-amber-600 rounded-lg hover:bg-amber-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Confirm Override
          </button>
        </div>
      </div>
    </div>
  );
}

// Validation Summary Component
function ValidationSummary({
  errors,
  onDismiss,
}: {
  errors: ValidationErrors;
  onDismiss: () => void;
}) {
  const errorList: string[] = [];

  if (errors.contractId) errorList.push(`Contract ID: ${errors.contractId}`);
  if (errors.contractName) errorList.push(`Contract Name: ${errors.contractName}`);
  if (errors.teamName) errorList.push(`Team Name: ${errors.teamName}`);

  if (errors.schema) {
    Object.entries(errors.schema).forEach(([schemaIdx, schemaErrors]) => {
      if (schemaErrors.name) {
        errorList.push(`Schema ${parseInt(schemaIdx) + 1}: ${schemaErrors.name}`);
      }
      if (schemaErrors.properties) {
        Object.entries(schemaErrors.properties).forEach(([propIdx, propErrors]) => {
          if (propErrors.name) {
            errorList.push(`Schema ${parseInt(schemaIdx) + 1}, Property ${parseInt(propIdx) + 1}: ${propErrors.name}`);
          }
        });
      }
    });
  }

  if (errors.general) {
    errorList.push(...errors.general);
  }

  if (errorList.length === 0) return null;

  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
      <div className="flex items-start gap-3">
        <div className="w-5 h-5 rounded-full bg-red-100 flex items-center justify-center flex-shrink-0 mt-0.5">
          <svg className="w-3 h-3 text-red-600" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
        </div>
        <div className="flex-1">
          <h4 className="font-medium text-red-800 mb-2">Validation Errors</h4>
          <ul className="text-sm text-red-700 space-y-1">
            {errorList.map((error, idx) => (
              <li key={idx} className="flex items-start gap-2">
                <span className="text-red-400">•</span>
                <span>{error}</span>
              </li>
            ))}
          </ul>
        </div>
        <button onClick={onDismiss} className="text-red-400 hover:text-red-600">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  );
}

// Approval Workflow Component
function ApprovalWorkflow({
  contractId,
  contractVersion,
  status,
  onSendForApproval,
  onApprove,
  onReject,
  loading,
  approvalStatus,
}: {
  contractId: string;
  contractVersion: string;
  status: ContractStatus;
  onSendForApproval: () => void;
  onApprove: () => void;
  onReject: (reason: string) => void;
  loading: boolean;
  approvalStatus?: {
    status: 'pending' | 'approved' | 'rejected';
    approvedBy?: string;
    approvedAt?: string;
    rejectedBy?: string;
    rejectedAt?: string;
    rejectionReason?: string;
  };
}) {
  const [rejectReason, setRejectReason] = useState('');
  const [showRejectDialog, setShowRejectDialog] = useState(false);

  const handleReject = () => {
    if (rejectReason.trim()) {
      onReject(rejectReason);
      setShowRejectDialog(false);
      setRejectReason('');
    }
  };

  return (
    <div className="bg-white rounded-lg border border-slate-200 p-4">
      <h3 className="font-medium text-slate-800 mb-3">Approval Workflow</h3>

      {/* Status Badge */}
      <div className="flex items-center gap-2 mb-4">
        <span className="text-sm text-slate-600">Current Status:</span>
        <span
          className={`px-2 py-1 text-xs font-medium rounded ${
            status === 'draft'
              ? 'bg-slate-100 text-slate-600'
              : status === 'active'
              ? 'bg-emerald-100 text-emerald-700'
              : status === 'deprecated'
              ? 'bg-amber-100 text-amber-700'
              : 'bg-red-100 text-red-700'
          }`}
        >
          {status.charAt(0).toUpperCase() + status.slice(1)}
        </span>
      </div>

      {/* Approval Status */}
      {approvalStatus && (
        <div className="mb-4 p-3 rounded-lg bg-slate-50">
          {approvalStatus.status === 'pending' && (
            <div className="flex items-center gap-2 text-amber-600">
              <svg className="w-5 h-5 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="text-sm font-medium">Pending Approval</span>
            </div>
          )}
          {approvalStatus.status === 'approved' && (
            <div>
              <div className="flex items-center gap-2 text-emerald-600 mb-1">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span className="text-sm font-medium">Approved</span>
              </div>
              {approvalStatus.approvedBy && (
                <p className="text-xs text-slate-500">
                  by {approvalStatus.approvedBy} on {approvalStatus.approvedAt}
                </p>
              )}
            </div>
          )}
          {approvalStatus.status === 'rejected' && (
            <div>
              <div className="flex items-center gap-2 text-red-600 mb-1">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span className="text-sm font-medium">Rejected</span>
              </div>
              {approvalStatus.rejectedBy && (
                <p className="text-xs text-slate-500">
                  by {approvalStatus.rejectedBy} on {approvalStatus.rejectedAt}
                </p>
              )}
              {approvalStatus.rejectionReason && (
                <p className="text-xs text-red-600 mt-1">Reason: {approvalStatus.rejectionReason}</p>
              )}
            </div>
          )}
        </div>
      )}

      {/* Action Buttons */}
      {status === 'draft' && !approvalStatus && (
        <button
          onClick={onSendForApproval}
          disabled={loading}
          className="w-full px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              Sending...
            </>
          ) : (
            <>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
              Send for Approval
            </>
          )}
        </button>
      )}

      {approvalStatus?.status === 'pending' && (
        <div className="flex gap-2">
          <button
            onClick={onApprove}
            disabled={loading}
            className="flex-1 px-4 py-2 text-sm font-medium text-white bg-emerald-600 rounded-lg hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Approve
          </button>
          <button
            onClick={() => setShowRejectDialog(true)}
            disabled={loading}
            className="flex-1 px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Reject
          </button>
        </div>
      )}

      {/* Reject Dialog */}
      {showRejectDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
            <h3 className="font-semibold text-slate-900 mb-4">Reject Contract</h3>
            <div className="mb-4">
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Reason for Rejection <span className="text-red-500">*</span>
              </label>
              <textarea
                value={rejectReason}
                onChange={(e) => setRejectReason(e.target.value)}
                placeholder="Please provide a reason for rejecting this contract..."
                rows={3}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-red-500 focus:border-red-500"
              />
            </div>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setShowRejectDialog(false)}
                className="px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50"
              >
                Cancel
              </button>
              <button
                onClick={handleReject}
                disabled={!rejectReason.trim()}
                className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Reject Contract
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Schema Property Editor
// =============================================================================

function SchemaPropertyEditor({
  property,
  onChange,
  onRemove,
  error,
}: {
  property: SchemaProperty;
  onChange: (property: SchemaProperty) => void;
  onRemove: () => void;
  error?: { name?: string };
}) {
  return (
    <div className={`border rounded-lg p-4 space-y-3 ${error?.name ? 'border-red-300 bg-red-50' : 'border-slate-200'}`}>
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-slate-700">Property</span>
        <button onClick={onRemove} className="text-red-500 hover:text-red-700 text-sm">
          Remove
        </button>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <FormField label="Name" required error={error?.name}>
          <Input
            value={property.name}
            onChange={(name) => onChange({ ...property, name })}
            placeholder="field_name"
            error={!!error?.name}
          />
        </FormField>

        <FormField label="Logical Type">
          <Select
            value={property.logicalType}
            onChange={(logicalType) => onChange({ ...property, logicalType })}
            options={[
              { value: 'string', label: 'String' },
              { value: 'integer', label: 'Integer' },
              { value: 'number', label: 'Number' },
              { value: 'boolean', label: 'Boolean' },
              { value: 'date', label: 'Date' },
              { value: 'datetime', label: 'DateTime' },
              { value: 'array', label: 'Array' },
              { value: 'object', label: 'Object' },
            ]}
          />
        </FormField>
      </div>

      <FormField label="Description">
        <Input
          value={property.description || ''}
          onChange={(description) => onChange({ ...property, description })}
          placeholder="Describe this field"
        />
      </FormField>

      <div className="flex gap-4">
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={property.nullable}
            onChange={(e) => onChange({ ...property, nullable: e.target.checked })}
            className="rounded"
          />
          <span className="text-sm text-slate-600">Nullable</span>
        </label>

        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={property.primary_key}
            onChange={(e) => onChange({ ...property, primary_key: e.target.checked })}
            className="rounded"
          />
          <span className="text-sm text-slate-600">Primary Key</span>
        </label>

        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={property.privacy?.contains_pii || false}
            onChange={(e) =>
              onChange({
                ...property,
                privacy: {
                  ...property.privacy,
                  contains_pii: e.target.checked,
                  sensitivity_level: property.privacy?.sensitivity_level || 'internal',
                  masking: property.privacy?.masking || 'none',
                },
              })
            }
            className="rounded"
          />
          <span className="text-sm text-slate-600">Contains PII</span>
        </label>
      </div>
    </div>
  );
}

// =============================================================================
// YAML Preview Panel
// =============================================================================

function YamlPreviewPanel({
  yaml,
  onCopy,
  onEdit,
  canEdit,
}: {
  yaml: string;
  onCopy: () => void;
  onEdit?: () => void;
  canEdit?: boolean;
}) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    onCopy();
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bg-white rounded-lg border border-slate-200 overflow-hidden sticky top-4">
      <div className="px-4 py-3 border-b border-slate-200 flex items-center justify-between bg-slate-50">
        <span className="font-medium text-slate-800">Live YAML Preview</span>
        <div className="flex items-center gap-2">
          {canEdit && onEdit && (
            <button
              onClick={onEdit}
              className="text-sm text-indigo-600 hover:text-indigo-700 flex items-center gap-1"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
              Edit YAML
            </button>
          )}
          <button
            onClick={handleCopy}
            className="text-sm text-indigo-600 hover:text-indigo-700 flex items-center gap-1"
          >
            {copied ? (
              <>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                Copied!
              </>
            ) : (
              <>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                Copy
              </>
            )}
          </button>
        </div>
      </div>
      <pre className="p-4 text-xs font-mono text-slate-700 overflow-auto max-h-[500px] bg-slate-50 whitespace-pre-wrap">
        {yaml}
      </pre>
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export default function StudioPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const editId = searchParams.get('edit');

  // Form state
  const [contractId, setContractId] = useState('');
  const [contractName, setContractName] = useState('');
  const [status, setStatus] = useState<ContractStatus>('draft');
  const [description, setDescription] = useState<Description>({});
  const [schema, setSchema] = useState<SchemaDefinition[]>([]);
  // Initialize with audit-ready smart defaults (T-382)
  const [legal, setLegal] = useState<Legal>(DEFAULT_LEGAL);
  const [compliance, setCompliance] = useState<Compliance>(DEFAULT_COMPLIANCE);
  const [sla, setSLA] = useState<SLA>(DEFAULT_SLA);
  const [access, setAccess] = useState<Access>(DEFAULT_ACCESS);
  const [team, setTeam] = useState<Team>({ name: '' });
  const [servers, setServers] = useState<Server[]>([]);
  const [governance, setGovernance] = useState<Governance>(DEFAULT_GOVERNANCE);

  // Section state
  const [sections, setSections] = useState<Record<SectionKey, SectionState>>({
    basics: { expanded: true },
    description: { expanded: false },
    schema: { expanded: true },
    legal: { expanded: false },
    compliance: { expanded: false },
    sla: { expanded: false },
    access: { expanded: false },
    team: { expanded: false },
    servers: { expanded: false },
    governance: { expanded: false },
  });

  // UI state
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [breakingChanges, setBreakingChanges] = useState<BreakingChangeInfo[]>([]);
  const [validationErrors, setValidationErrors] = useState<ValidationErrors>({});
  const [showValidationSummary, setShowValidationSummary] = useState(false);

  // Security override state
  const [securityWarning, setSecurityWarning] = useState<{
    message: string;
    pendingChange: () => void;
  } | null>(null);
  const [securityOverrides, setSecurityOverrides] = useState<SecurityOverride[]>([]);

  // Approval workflow state
  const [approvalStatus, setApprovalStatus] = useState<{
    status: 'pending' | 'approved' | 'rejected';
    approvedBy?: string;
    approvedAt?: string;
    rejectedBy?: string;
    rejectedAt?: string;
    rejectionReason?: string;
  } | undefined>(undefined);
  const [sendingForApproval, setSendingForApproval] = useState(false);

  // =============================================================================
  // Validation Logic
  // =============================================================================

  // Real-time validation
  const validateForm = useCallback((): ValidationErrors => {
    const errors: ValidationErrors = {};

    // Contract ID validation
    if (!contractId.trim()) {
      errors.contractId = 'Contract ID is required';
    } else if (!/^[a-z0-9-]+$/.test(contractId)) {
      errors.contractId = 'Contract ID must be lowercase letters, numbers, and hyphens only';
    }

    // Contract Name validation
    if (!contractName.trim()) {
      errors.contractName = 'Contract name is required';
    }

    // Schema validation
    if (schema.length > 0) {
      const schemaErrors: Record<number, { name?: string; properties?: Record<number, { name?: string }> }> = {};

      schema.forEach((s, schemaIdx) => {
        if (!s.name.trim()) {
          schemaErrors[schemaIdx] = { ...schemaErrors[schemaIdx], name: 'Schema name is required' };
        }

        if (s.properties && s.properties.length > 0) {
          const propErrors: Record<number, { name?: string }> = {};
          s.properties.forEach((prop, propIdx) => {
            if (!prop.name.trim()) {
              propErrors[propIdx] = { name: 'Property name is required' };
            }
          });
          if (Object.keys(propErrors).length > 0) {
            schemaErrors[schemaIdx] = { ...schemaErrors[schemaIdx], properties: propErrors };
          }
        }
      });

      if (Object.keys(schemaErrors).length > 0) {
        errors.schema = schemaErrors;
      }
    }

    return errors;
  }, [contractId, contractName, schema]);

  // Check if form is valid
  const isFormValid = useMemo(() => {
    const errors = validateForm();
    return Object.keys(errors).length === 0;
  }, [validateForm]);

  // =============================================================================
  // Security Check Functions
  // =============================================================================

  const checkSecurityReduction = (
    field: string,
    previousValue: SensitivityLevel | string,
    newValue: SensitivityLevel | string,
    onChange: () => void
  ) => {
    const sensitivityOrder: Record<string, number> = {
      restricted: 4,
      confidential: 3,
      internal: 2,
      public: 1,
    };

    const prevLevel = sensitivityOrder[previousValue] || 0;
    const newLevel = sensitivityOrder[newValue] || 0;

    if (newLevel < prevLevel) {
      setSecurityWarning({
        message: `You are reducing the ${field} from "${previousValue}" to "${newValue}". This may expose sensitive data. Are you sure you want to proceed?`,
        pendingChange: onChange,
      });
    } else {
      onChange();
    }
  };

  const handleSecurityOverrideConfirm = (reason: string) => {
    if (securityWarning) {
      const override: SecurityOverride = {
        field: 'data_classification',
        previousValue: compliance.data_classification,
        newValue: '',
        reason,
      };
      setSecurityOverrides([...securityOverrides, override]);
      securityWarning.pendingChange();
      setSecurityWarning(null);
    }
  };

  // =============================================================================
  // Form Handlers
  // =============================================================================

  // Toggle section
  const toggleSection = (key: SectionKey) => {
    setSections((prev) => ({
      ...prev,
      [key]: { ...prev[key], expanded: !prev[key].expanded },
    }));
  };

  // Load contract for editing
  useEffect(() => {
    async function loadContract() {
      if (!editId) return;

      try {
        setLoading(true);
        const contract = await api.getContract(editId);
        setContractId(contract.id);
        setContractName(contract.name);
        setStatus(contract.status);

        // ODCS sections
        if (contract.description_odcs) setDescription(contract.description_odcs);
        if (contract.schema) setSchema(contract.schema);
        if (contract.legal) setLegal(contract.legal);
        if (contract.compliance) setCompliance(contract.compliance);
        if (contract.sla) setSLA(contract.sla);
        if (contract.access) setAccess(contract.access);
        if (contract.team) setTeam(contract.team);
        if (contract.servers) setServers(contract.servers);
        if (contract.governance) setGovernance(contract.governance);
      } catch (err) {
        setError('Failed to load contract for editing');
      } finally {
        setLoading(false);
      }
    }

    loadContract();
  }, [editId]);

  // Add new schema
  const addSchema = () => {
    setSchema([
      ...schema,
      {
        name: `schema_${schema.length + 1}`,
        physicalType: 'table',
        properties: [],
      },
    ]);
  };

  // Update schema
  const updateSchema = (index: number, updates: Partial<SchemaDefinition>) => {
    setSchema(schema.map((s, i) => (i === index ? { ...s, ...updates } : s)));
  };

  // Add property to schema with smart defaults (T-382, T-383)
  const addProperty = (schemaIndex: number) => {
    const newProperty: SchemaProperty = {
      name: '',
      logicalType: DEFAULT_SCHEMA_PROPERTY.logicalType || 'string',
      nullable: DEFAULT_SCHEMA_PROPERTY.nullable ?? true,
      primary_key: DEFAULT_SCHEMA_PROPERTY.primary_key ?? false,
      privacy: DEFAULT_SCHEMA_PROPERTY.privacy,
    };
    updateSchema(schemaIndex, {
      properties: [...(schema[schemaIndex].properties || []), newProperty],
    });
  };

  // Auto-detect privacy settings when field name changes (T-383)
  const updatePropertyWithPrivacyDetection = (
    schemaIndex: number,
    propIndex: number,
    property: SchemaProperty,
    oldName?: string
  ) => {
    // If the name changed and no privacy was manually set, auto-detect
    if (property.name !== oldName && property.name) {
      const detectedPrivacy = inferPrivacyFromFieldName(property.name);
      // Only apply if privacy wasn't manually configured
      if (!property.privacy?.contains_pii || property.privacy.contains_pii === false) {
        property = {
          ...property,
          privacy: {
            ...property.privacy,
            ...detectedPrivacy,
          },
        };
      }
    }
    updateProperty(schemaIndex, propIndex, property);
  };

  // Update property
  const updateProperty = (schemaIndex: number, propIndex: number, property: SchemaProperty) => {
    const props = [...(schema[schemaIndex].properties || [])];
    props[propIndex] = property;
    updateSchema(schemaIndex, { properties: props });
  };

  // Remove property
  const removeProperty = (schemaIndex: number, propIndex: number) => {
    const props = (schema[schemaIndex].properties || []).filter((_, i) => i !== propIndex);
    updateSchema(schemaIndex, { properties: props });
  };

  // Build contract data
  const buildContractData = useCallback((): ContractCreate | ContractUpdate => {
    const data: ContractCreate = {
      id: contractId,
      name: contractName,
      description_odcs: description,
      schema: schema.length > 0 ? schema : undefined,
      legal: Object.keys(legal).length > 0 ? legal : undefined,
      compliance: compliance,
      sla: Object.keys(sla).length > 0 ? sla : undefined,
      access: access,
      team: team.name ? team : undefined,
      servers: servers.length > 0 ? servers : undefined,
      governance: Object.keys(governance).length > 0 ? governance : undefined,
    };

    return data;
  }, [contractId, contractName, description, schema, legal, compliance, sla, access, team, servers, governance]);

  // Generate YAML preview
  const generateYaml = useCallback(() => {
    const yamlContent = `# Data Contract: ${contractName || 'Untitled'}
apiVersion: v1.0.0
kind: DataContract
id: ${contractId || 'my-contract'}
name: "${contractName || 'Untitled'}"
status: ${status}
${description.purpose ? `\ndescription:\n  purpose: "${description.purpose}"${description.usage ? `\n  usage: "${description.usage}"` : ''}${description.limitations ? `\n  limitations: "${description.limitations}"` : ''}` : ''}
${schema.length > 0 ? `\nschema:\n${schema.map(s => `  - name: ${s.name}\n    physicalType: ${s.physicalType}${s.properties && s.properties.length > 0 ? `\n    properties:\n${s.properties.map(p => `      - name: ${p.name}\n        logicalType: ${p.logicalType}\n        nullable: ${p.nullable}${p.primary_key ? '\n        primaryKey: true' : ''}${p.description ? `\n        description: "${p.description}"` : ''}`).join('\n')}` : ''}`).join('\n')}` : ''}
${team.name ? `\nteam:\n  name: "${team.name}"${team.department ? `\n  department: "${team.department}"` : ''}${team.steward?.name ? `\n  steward:\n    name: "${team.steward.name}"${team.steward.email ? `\n    email: "${team.steward.email}"` : ''}` : ''}` : ''}
${compliance.data_classification ? `\ncompliance:\n  dataClassification: ${compliance.data_classification}${compliance.regulatory_scope && compliance.regulatory_scope.length > 0 ? `\n  regulatoryScope:\n${compliance.regulatory_scope.map(r => `    - ${r}`).join('\n')}` : ''}${compliance.audit_requirements ? `\n  auditRequirements:\n    logging: ${compliance.audit_requirements.logging}\n    logRetention: ${compliance.audit_requirements.log_retention}` : ''}` : ''}
${sla.availability ? `\nsla:\n  availability:\n    targetPercent: ${sla.availability.target_percent}\n    measurementWindow: ${sla.availability.measurement_window}${sla.freshness ? `\n  freshness:\n    target: ${sla.freshness.target}` : ''}${sla.completeness ? `\n  completeness:\n    targetPercent: ${sla.completeness.target_percent}` : ''}${sla.accuracy ? `\n  accuracy:\n    errorRateTarget: ${sla.accuracy.error_rate_target}` : ''}` : ''}
${access.default_level ? `\naccess:\n  defaultLevel: ${access.default_level}${access.approval?.required ? `\n  approval:\n    required: ${access.approval.required}` : ''}` : ''}
`;
    return yamlContent;
  }, [contractId, contractName, status, description, schema, team, compliance, sla, access]);

  // Validate form and show errors
  const handleValidate = () => {
    const errors = validateForm();
    setValidationErrors(errors);
    setShowValidationSummary(true);

    if (Object.keys(errors).length === 0) {
      setSuccess('All fields are valid!');
      setTimeout(() => setSuccess(null), 3000);
    }
  };

  // Save contract
  const handleSave = async (force: boolean = false) => {
    setError(null);
    setSuccess(null);
    setBreakingChanges([]);

    // Run validation
    const errors = validateForm();
    if (Object.keys(errors).length > 0) {
      setValidationErrors(errors);
      setShowValidationSummary(true);
      setError('Please fix the validation errors before saving');
      return;
    }

    try {
      setSaving(true);
      const data = buildContractData();

      if (editId) {
        // Update existing contract
        await api.updateContract(editId, data as ContractUpdate, { allowBreaking: force });
        setSuccess('Contract updated successfully');
      } else {
        // Create new contract
        await api.createContract(data as ContractCreate);
        setSuccess('Contract created successfully');
        // Redirect to contract detail
        setTimeout(() => router.push(`/contracts/${contractId}`), 1500);
      }
    } catch (err) {
      if (err instanceof ApiClientError && err.isBreakingChangeError()) {
        setBreakingChanges(err.breakingChanges || []);
      } else {
        setError('Failed to save contract. Registry API may be unavailable.');
      }
    } finally {
      setSaving(false);
    }
  };

  // Handle proceeding with breaking changes
  const handleProceedWithBreaking = () => {
    handleSave(true);
  };

  // Send for approval
  const handleSendForApproval = async () => {
    // Validate first
    const errors = validateForm();
    if (Object.keys(errors).length > 0) {
      setValidationErrors(errors);
      setShowValidationSummary(true);
      setError('Please fix the validation errors before sending for approval');
      return;
    }

    try {
      setSendingForApproval(true);

      // Save the contract first if it's new
      if (!editId) {
        const data = buildContractData();
        await api.createContract(data as ContractCreate);
      }

      // Create approval chain
      await api.createApprovalChain(contractId, '1.0.0', {
        approvers: [
          {
            user_id: 'data-producer',
            email: 'producer@company.com',
            name: 'Data Producer',
            role: 'producer',
          },
        ],
      });

      setApprovalStatus({
        status: 'pending',
      });
      setSuccess('Contract sent for approval successfully');
    } catch (err) {
      setError('Failed to send contract for approval');
    } finally {
      setSendingForApproval(false);
    }
  };

  // Handle approval
  const handleApprove = async () => {
    try {
      setSendingForApproval(true);
      // Update status to active
      await api.updateContract(contractId, { name: contractName }, { allowBreaking: false });
      setApprovalStatus({
        status: 'approved',
        approvedBy: 'Current User',
        approvedAt: new Date().toISOString(),
      });
      setStatus('active');
      setSuccess('Contract approved and activated');
    } catch (err) {
      setError('Failed to approve contract');
    } finally {
      setSendingForApproval(false);
    }
  };

  // Handle rejection
  const handleReject = async (reason: string) => {
    try {
      setSendingForApproval(true);
      setApprovalStatus({
        status: 'rejected',
        rejectedBy: 'Current User',
        rejectedAt: new Date().toISOString(),
        rejectionReason: reason,
      });
      setSuccess('Contract rejected');
    } catch (err) {
      setError('Failed to reject contract');
    } finally {
      setSendingForApproval(false);
    }
  };

  // Copy YAML to clipboard
  const handleCopyYaml = () => {
    navigator.clipboard.writeText(generateYaml());
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16">
        <div className="animate-pulse text-slate-400">Loading contract...</div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">
            {editId ? 'Edit Contract' : 'New Contract'}
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Create or edit data contracts using the Open Data Contract Standard
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleValidate}
            className="px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Validate Contract
          </button>
          <button
            onClick={() => handleSave(false)}
            disabled={saving || !isFormValid}
            className={`px-4 py-2 text-sm font-medium text-white rounded-lg flex items-center gap-2 ${
              isFormValid
                ? 'bg-indigo-600 hover:bg-indigo-700'
                : 'bg-slate-400 cursor-not-allowed'
            } disabled:opacity-50`}
            title={!isFormValid ? 'Please fill in all required fields' : ''}
          >
            {saving && (
              <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
            )}
            {editId ? 'Save Changes' : 'Create Contract'}
          </button>
        </div>
      </div>

      {/* Alerts */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center justify-between">
          <span>{error}</span>
          <button onClick={() => setError(null)} className="text-red-400 hover:text-red-600">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      )}

      {success && (
        <div className="bg-emerald-50 border border-emerald-200 text-emerald-700 px-4 py-3 rounded-lg flex items-center justify-between">
          <span>{success}</span>
          <button onClick={() => setSuccess(null)} className="text-emerald-400 hover:text-emerald-600">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      )}

      {/* Validation Summary */}
      {showValidationSummary && Object.keys(validationErrors).length > 0 && (
        <ValidationSummary
          errors={validationErrors}
          onDismiss={() => setShowValidationSummary(false)}
        />
      )}

      {/* Breaking Changes Warning */}
      {breakingChanges.length > 0 && (
        <BreakingChangeWarning
          changes={breakingChanges}
          onProceed={handleProceedWithBreaking}
          onCancel={() => setBreakingChanges([])}
          loading={saving}
        />
      )}

      {/* Security Warning Modal */}
      {securityWarning && (
        <SecurityWarning
          message={securityWarning.message}
          onConfirm={handleSecurityOverrideConfirm}
          onCancel={() => setSecurityWarning(null)}
        />
      )}

      {/* Main Content - Split Pane Layout */}
      <div className="grid grid-cols-12 gap-6">
        {/* Form Sections (8/12 = 2/3) */}
        <div className="col-span-8 space-y-4">
          {/* Basics Section */}
          <div className="bg-white rounded-lg border border-slate-200 overflow-hidden">
            <SectionHeader
              title="Basic Information"
              subtitle="Required contract metadata"
              expanded={sections.basics.expanded}
              onToggle={() => toggleSection('basics')}
              hasContent={!!contractId && !!contractName}
              hasErrors={!!validationErrors.contractId || !!validationErrors.contractName}
            />
            {sections.basics.expanded && (
              <div className="p-4 border-t border-slate-200 space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <FormField
                    label="Contract ID"
                    required
                    hint="Unique identifier (lowercase, hyphens)"
                    error={validationErrors.contractId}
                  >
                    <Input
                      value={contractId}
                      onChange={(v) => setContractId(v.toLowerCase().replace(/\s+/g, '-'))}
                      placeholder="my-contract"
                      disabled={!!editId}
                      error={!!validationErrors.contractId}
                    />
                  </FormField>

                  <FormField label="Contract Name" required error={validationErrors.contractName}>
                    <Input
                      value={contractName}
                      onChange={setContractName}
                      placeholder="My Contract"
                      error={!!validationErrors.contractName}
                    />
                  </FormField>
                </div>

                <FormField label="Status" hint="New contracts start as Draft and must be approved to go Live">
                  <Select
                    value={status}
                    onChange={setStatus}
                    disabled={!editId || status === 'draft'}
                    options={[
                      { value: 'draft', label: 'Draft' },
                      { value: 'active', label: 'Active (Live)' },
                      { value: 'deprecated', label: 'Deprecated' },
                      { value: 'retired', label: 'Retired' },
                    ]}
                  />
                  {(!editId || status === 'draft') && (
                    <p className="mt-1 text-xs text-amber-600">
                      Status is locked to "Draft" until the contract is approved by a producer.
                    </p>
                  )}
                </FormField>
              </div>
            )}
          </div>

          {/* Description Section */}
          <div className="bg-white rounded-lg border border-slate-200 overflow-hidden">
            <SectionHeader
              title="Description"
              subtitle="Purpose, usage, and limitations"
              expanded={sections.description.expanded}
              onToggle={() => toggleSection('description')}
              hasContent={!!description.purpose}
            />
            {sections.description.expanded && (
              <div className="p-4 border-t border-slate-200 space-y-4">
                <FormField label="Purpose" hint="What is this data used for?">
                  <TextArea
                    value={description.purpose || ''}
                    onChange={(purpose) => setDescription({ ...description, purpose })}
                    placeholder="Describe the purpose of this data contract..."
                  />
                </FormField>

                <FormField label="Usage" hint="How should this data be used?">
                  <TextArea
                    value={description.usage || ''}
                    onChange={(usage) => setDescription({ ...description, usage })}
                    placeholder="Describe expected usage patterns..."
                  />
                </FormField>

                <FormField label="Limitations" hint="What are the limitations?">
                  <TextArea
                    value={description.limitations || ''}
                    onChange={(limitations) => setDescription({ ...description, limitations })}
                    placeholder="Describe any limitations or caveats..."
                  />
                </FormField>
              </div>
            )}
          </div>

          {/* Schema Section */}
          <div className="bg-white rounded-lg border border-slate-200 overflow-hidden">
            <SectionHeader
              title="Schema"
              subtitle="Define datasets and fields"
              expanded={sections.schema.expanded}
              onToggle={() => toggleSection('schema')}
              hasContent={schema.length > 0}
              hasErrors={!!validationErrors.schema}
            />
            {sections.schema.expanded && (
              <div className="p-4 border-t border-slate-200 space-y-4">
                {schema.map((s, schemaIndex) => (
                  <div key={schemaIndex} className="border border-slate-200 rounded-lg p-4 space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="grid grid-cols-2 gap-4 flex-1">
                        <FormField
                          label="Schema Name"
                          error={validationErrors.schema?.[schemaIndex]?.name}
                        >
                          <Input
                            value={s.name}
                            onChange={(name) => updateSchema(schemaIndex, { name })}
                            placeholder="schema_name"
                            error={!!validationErrors.schema?.[schemaIndex]?.name}
                          />
                        </FormField>
                        <FormField label="Physical Type">
                          <Select
                            value={s.physicalType}
                            onChange={(physicalType) => updateSchema(schemaIndex, { physicalType })}
                            options={[
                              { value: 'table', label: 'Table' },
                              { value: 'view', label: 'View' },
                              { value: 'file', label: 'File' },
                              { value: 'stream', label: 'Stream' },
                            ]}
                          />
                        </FormField>
                      </div>
                      <button
                        onClick={() => setSchema(schema.filter((_, i) => i !== schemaIndex))}
                        className="ml-4 text-red-500 hover:text-red-700"
                      >
                        Remove
                      </button>
                    </div>

                    {/* Properties */}
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-slate-700">Properties</span>
                        <button
                          onClick={() => addProperty(schemaIndex)}
                          className="text-sm text-indigo-600 hover:text-indigo-700"
                        >
                          + Add Property
                        </button>
                      </div>

                      {s.properties?.map((prop, propIndex) => (
                        <SchemaPropertyEditor
                          key={propIndex}
                          property={prop}
                          onChange={(p) => updateProperty(schemaIndex, propIndex, p)}
                          onRemove={() => removeProperty(schemaIndex, propIndex)}
                          error={validationErrors.schema?.[schemaIndex]?.properties?.[propIndex]}
                        />
                      ))}

                      {(!s.properties || s.properties.length === 0) && (
                        <p className="text-sm text-slate-400 text-center py-4">
                          No properties defined. Click "Add Property" to start.
                        </p>
                      )}
                    </div>
                  </div>
                ))}

                <button
                  onClick={addSchema}
                  className="w-full py-3 border-2 border-dashed border-slate-300 rounded-lg text-slate-500 hover:border-indigo-500 hover:text-indigo-600 transition-colors"
                >
                  + Add Schema
                </button>
              </div>
            )}
          </div>

          {/* Team Section */}
          <div className="bg-white rounded-lg border border-slate-200 overflow-hidden">
            <SectionHeader
              title="Team"
              subtitle="Ownership and contact information"
              expanded={sections.team.expanded}
              onToggle={() => toggleSection('team')}
              hasContent={!!team.name}
            />
            {sections.team.expanded && (
              <div className="p-4 border-t border-slate-200 space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <FormField label="Team Name">
                    <Input
                      value={team.name}
                      onChange={(name) => setTeam({ ...team, name })}
                      placeholder="Data Platform Team"
                    />
                  </FormField>

                  <FormField label="Department">
                    <Input
                      value={team.department || ''}
                      onChange={(department) => setTeam({ ...team, department })}
                      placeholder="Engineering"
                    />
                  </FormField>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <FormField label="Steward Name">
                    <Input
                      value={team.steward?.name || ''}
                      onChange={(name) => setTeam({ ...team, steward: { ...team.steward, name } })}
                      placeholder="John Doe"
                    />
                  </FormField>

                  <FormField label="Steward Email">
                    <Input
                      value={team.steward?.email || ''}
                      onChange={(email) => setTeam({ ...team, steward: { ...team.steward, name: team.steward?.name || '', email } })}
                      placeholder="john.doe@company.com"
                      type="email"
                    />
                  </FormField>
                </div>
              </div>
            )}
          </div>

          {/* Compliance Section */}
          <div className="bg-white rounded-lg border border-slate-200 overflow-hidden">
            <SectionHeader
              title="Compliance"
              subtitle="Data classification and regulations"
              expanded={sections.compliance.expanded}
              onToggle={() => toggleSection('compliance')}
              hasContent={!!compliance.data_classification}
            />
            {sections.compliance.expanded && (
              <div className="p-4 border-t border-slate-200 space-y-4">
                <FormField
                  label="Data Classification"
                  hint="Security-first default: Internal. Reducing classification requires justification."
                >
                  <Select
                    value={compliance.data_classification}
                    onChange={(newValue) => {
                      checkSecurityReduction(
                        'Data Classification',
                        compliance.data_classification,
                        newValue,
                        () => setCompliance({ ...compliance, data_classification: newValue })
                      );
                    }}
                    options={[
                      { value: 'public', label: 'Public' },
                      { value: 'internal', label: 'Internal (Default)' },
                      { value: 'confidential', label: 'Confidential' },
                      { value: 'restricted', label: 'Restricted' },
                    ]}
                  />
                </FormField>

                <FormField label="Regulatory Scope" hint="Press Enter to add">
                  <TagInput
                    value={compliance.regulatory_scope || []}
                    onChange={(regulatory_scope) => setCompliance({ ...compliance, regulatory_scope })}
                    placeholder="GDPR, CCPA, HIPAA..."
                  />
                </FormField>

                <div className="grid grid-cols-2 gap-4">
                  <FormField label="Audit Logging">
                    <label className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={compliance.audit_requirements?.logging ?? true}
                        onChange={(e) =>
                          setCompliance({
                            ...compliance,
                            audit_requirements: {
                              ...compliance.audit_requirements,
                              logging: e.target.checked,
                              log_retention: compliance.audit_requirements?.log_retention || 'P365D',
                            },
                          })
                        }
                        className="rounded"
                      />
                      <span className="text-sm text-slate-600">Enable audit logging (Recommended)</span>
                    </label>
                  </FormField>

                  <FormField label="Log Retention" hint="ISO 8601 duration (default: 1 year)">
                    <Input
                      value={compliance.audit_requirements?.log_retention || 'P365D'}
                      onChange={(log_retention) =>
                        setCompliance({
                          ...compliance,
                          audit_requirements: {
                            ...compliance.audit_requirements,
                            logging: compliance.audit_requirements?.logging ?? true,
                            log_retention,
                          },
                        })
                      }
                      placeholder="P365D"
                    />
                  </FormField>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <FormField label="Allow Download">
                    <label className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={compliance.export_restrictions?.allow_download ?? false}
                        onChange={(e) =>
                          setCompliance({
                            ...compliance,
                            export_restrictions: {
                              ...compliance.export_restrictions,
                              allow_download: e.target.checked,
                              allow_external_transfer: compliance.export_restrictions?.allow_external_transfer ?? false,
                            },
                          })
                        }
                        className="rounded"
                      />
                      <span className="text-sm text-slate-600">Allow data download (Default: No)</span>
                    </label>
                  </FormField>

                  <FormField label="Allow External Transfer">
                    <label className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={compliance.export_restrictions?.allow_external_transfer ?? false}
                        onChange={(e) =>
                          setCompliance({
                            ...compliance,
                            export_restrictions: {
                              ...compliance.export_restrictions,
                              allow_download: compliance.export_restrictions?.allow_download ?? false,
                              allow_external_transfer: e.target.checked,
                            },
                          })
                        }
                        className="rounded"
                      />
                      <span className="text-sm text-slate-600">Allow external transfer (Default: No)</span>
                    </label>
                  </FormField>
                </div>
              </div>
            )}
          </div>

          {/* SLA Section */}
          <div className="bg-white rounded-lg border border-slate-200 overflow-hidden">
            <SectionHeader
              title="Service Level Agreements"
              subtitle="Define quality targets"
              expanded={sections.sla.expanded}
              onToggle={() => toggleSection('sla')}
              hasContent={!!sla.availability || !!sla.freshness}
            />
            {sections.sla.expanded && (
              <div className="p-4 border-t border-slate-200 space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <FormField label="Availability Target (%)" hint="Default: 99.0%">
                    <Input
                      value={sla.availability?.target_percent?.toString() || '99.0'}
                      onChange={(v) =>
                        setSLA({
                          ...sla,
                          availability: {
                            ...sla.availability,
                            target_percent: parseFloat(v) || 99,
                            measurement_window: sla.availability?.measurement_window || 'P30D',
                          },
                        })
                      }
                      placeholder="99.0"
                      type="number"
                    />
                  </FormField>

                  <FormField label="Freshness Target" hint="Default: P1D (daily)">
                    <Input
                      value={sla.freshness?.target || 'P1D'}
                      onChange={(target) =>
                        setSLA({
                          ...sla,
                          freshness: { ...sla.freshness, target },
                        })
                      }
                      placeholder="P1D"
                    />
                  </FormField>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <FormField label="Completeness Target (%)" hint="Default: 99.5%">
                    <Input
                      value={sla.completeness?.target_percent?.toString() || '99.5'}
                      onChange={(v) =>
                        setSLA({
                          ...sla,
                          completeness: {
                            ...sla.completeness,
                            target_percent: parseFloat(v) || 99.5,
                          },
                        })
                      }
                      placeholder="99.5"
                      type="number"
                    />
                  </FormField>

                  <FormField label="Error Rate Target" hint="Default: 0.001 (99.9% accuracy)">
                    <Input
                      value={sla.accuracy?.error_rate_target?.toString() || '0.001'}
                      onChange={(v) =>
                        setSLA({
                          ...sla,
                          accuracy: {
                            ...sla.accuracy,
                            error_rate_target: parseFloat(v) || 0.001,
                          },
                        })
                      }
                      placeholder="0.001"
                      type="number"
                    />
                  </FormField>
                </div>
              </div>
            )}
          </div>

          {/* Access Section */}
          <div className="bg-white rounded-lg border border-slate-200 overflow-hidden">
            <SectionHeader
              title="Access Control"
              subtitle="Configure access levels and grants"
              expanded={sections.access.expanded}
              onToggle={() => toggleSection('access')}
              hasContent={!!access.default_level}
            />
            {sections.access.expanded && (
              <div className="p-4 border-t border-slate-200 space-y-4">
                <FormField label="Default Access Level" hint="Security-first default: Read (least privilege)">
                  <Select
                    value={access.default_level}
                    onChange={(default_level) => setAccess({ ...access, default_level })}
                    options={[
                      { value: 'read', label: 'Read (Default - Least Privilege)' },
                      { value: 'write', label: 'Write' },
                      { value: 'admin', label: 'Admin' },
                    ]}
                  />
                </FormField>

                <FormField label="Approval Required" hint="Security-first default: Yes">
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={access.approval?.required ?? true}
                      onChange={(e) =>
                        setAccess({
                          ...access,
                          approval: { ...access.approval, required: e.target.checked },
                        })
                      }
                      className="rounded"
                    />
                    <span className="text-sm text-slate-600">Require approval for access requests (Recommended)</span>
                  </label>
                </FormField>
              </div>
            )}
          </div>
        </div>

        {/* Right Sidebar (4/12 = 1/3) */}
        <div className="col-span-4 space-y-4">
          {/* YAML Preview - Always Visible */}
          <YamlPreviewPanel
            yaml={generateYaml()}
            onCopy={handleCopyYaml}
            canEdit={!!editId}
          />

          {/* Approval Workflow - Only show for editing */}
          {editId && (
            <ApprovalWorkflow
              contractId={contractId}
              contractVersion="1.0.0"
              status={status}
              onSendForApproval={handleSendForApproval}
              onApprove={handleApprove}
              onReject={handleReject}
              loading={sendingForApproval}
              approvalStatus={approvalStatus}
            />
          )}

          {/* Quick Help */}
          <div className="bg-white rounded-lg border border-slate-200 p-4">
            <h3 className="font-medium text-slate-800 mb-3">Quick Help</h3>
            <ul className="text-sm text-slate-600 space-y-2">
              <li className="flex gap-2">
                <span className="text-indigo-500">•</span>
                <span>Fill out <strong>Basic Information</strong> first</span>
              </li>
              <li className="flex gap-2">
                <span className="text-indigo-500">•</span>
                <span>Add <strong>Schema</strong> with properties</span>
              </li>
              <li className="flex gap-2">
                <span className="text-indigo-500">•</span>
                <span>Configure <strong>Compliance</strong> for data classification</span>
              </li>
              <li className="flex gap-2">
                <span className="text-indigo-500">•</span>
                <span>Set <strong>SLA</strong> targets for quality</span>
              </li>
              <li className="flex gap-2">
                <span className="text-amber-500">•</span>
                <span>New contracts start as <strong>Draft</strong> and require approval</span>
              </li>
            </ul>
          </div>

          {/* Security Defaults Info */}
          <div className="bg-amber-50 rounded-lg border border-amber-200 p-4">
            <h3 className="font-medium text-amber-800 mb-2">Security-First Defaults</h3>
            <p className="text-sm text-amber-700 mb-2">
              This contract uses security-first defaults:
            </p>
            <ul className="text-xs text-amber-600 space-y-1">
              <li>• Data Classification: Internal</li>
              <li>• Audit Logging: Enabled</li>
              <li>• Access Level: Read (Least Privilege)</li>
              <li>• Approval Required: Yes</li>
              <li>• Data Download: Disabled</li>
              <li>• External Transfer: Disabled</li>
            </ul>
          </div>

          {/* ODCS Reference */}
          <div className="bg-indigo-50 rounded-lg border border-indigo-200 p-4">
            <h3 className="font-medium text-indigo-800 mb-2">ODCS Reference</h3>
            <p className="text-sm text-indigo-700 mb-2">
              This editor follows the Open Data Contract Standard (ODCS) specification.
            </p>
            <a
              href="https://bitol.io/open-data-contract-standard/"
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-indigo-600 hover:underline"
            >
              Learn more about ODCS →
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
