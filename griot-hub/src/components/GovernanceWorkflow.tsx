'use client';

import { useState } from 'react';
import type {
  Governance,
  ProducerInfo,
  ConsumerInfo,
  ApprovalEntry,
  ReviewConfig,
  ChangeManagement,
  ReviewCadence,
} from '@/lib/types';
import { DEFAULT_GOVERNANCE } from '@/lib/defaults';

/**
 * Governance & Approval Workflow UI (T-387)
 *
 * Comprehensive UI for managing:
 * - Producer/Consumer relationships
 * - Approval chains and workflows
 * - Review schedules
 * - Change management policies
 */

interface GovernanceWorkflowProps {
  value: Governance;
  onChange: (governance: Governance) => void;
  onClose?: () => void;
}

type TabKey = 'overview' | 'producer' | 'consumers' | 'approvals' | 'review' | 'changes';

export default function GovernanceWorkflow({ value, onChange, onClose }: GovernanceWorkflowProps) {
  const [activeTab, setActiveTab] = useState<TabKey>('overview');

  // Update helpers
  const updateProducer = (updates: Partial<ProducerInfo>) => {
    onChange({
      ...value,
      producer: {
        team: value.producer?.team || '',
        ...value.producer,
        ...updates,
      },
    });
  };

  const updateReview = (updates: Partial<ReviewConfig>) => {
    onChange({
      ...value,
      review: {
        cadence: value.review?.cadence || 'quarterly',
        ...value.review,
        ...updates,
      },
    });
  };

  const updateChangeManagement = (updates: Partial<ChangeManagement>) => {
    onChange({
      ...value,
      change_management: {
        breaking_change_notice: value.change_management?.breaking_change_notice || 'P30D',
        deprecation_notice: value.change_management?.deprecation_notice || 'P90D',
        migration_support: value.change_management?.migration_support ?? true,
        ...value.change_management,
        ...updates,
      },
    });
  };

  const addConsumer = () => {
    const newConsumer: ConsumerInfo = {
      team: '',
      use_case: '',
    };
    onChange({
      ...value,
      consumers: [...(value.consumers || []), newConsumer],
    });
  };

  const updateConsumer = (index: number, updates: Partial<ConsumerInfo>) => {
    const consumers = [...(value.consumers || [])];
    consumers[index] = { ...consumers[index], ...updates };
    onChange({ ...value, consumers });
  };

  const removeConsumer = (index: number) => {
    onChange({
      ...value,
      consumers: (value.consumers || []).filter((_, i) => i !== index),
    });
  };

  const addApproval = () => {
    const newApproval: ApprovalEntry = {
      role: '',
    };
    onChange({
      ...value,
      approval_chain: [...(value.approval_chain || []), newApproval],
    });
  };

  const updateApproval = (index: number, updates: Partial<ApprovalEntry>) => {
    const approvals = [...(value.approval_chain || [])];
    approvals[index] = { ...approvals[index], ...updates };
    onChange({ ...value, approval_chain: approvals });
  };

  const removeApproval = (index: number) => {
    onChange({
      ...value,
      approval_chain: (value.approval_chain || []).filter((_, i) => i !== index),
    });
  };

  return (
    <div className="bg-white rounded-lg border border-slate-200 overflow-hidden max-w-3xl">
      {/* Header */}
      <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-gradient-to-r from-slate-50 to-white">
        <div>
          <h2 className="text-lg font-semibold text-slate-800">Governance & Approval Workflow</h2>
          <p className="text-sm text-slate-500">Configure ownership, approvals, and change management</p>
        </div>
        {onClose && (
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>

      {/* Tabs */}
      <div className="border-b border-slate-200 px-6">
        <nav className="flex gap-6 -mb-px">
          {[
            { key: 'overview', label: 'Overview' },
            { key: 'producer', label: 'Producer' },
            { key: 'consumers', label: 'Consumers' },
            { key: 'approvals', label: 'Approvals' },
            { key: 'review', label: 'Review' },
            { key: 'changes', label: 'Change Mgmt' },
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as TabKey)}
              className={`py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.key
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-slate-500 hover:text-slate-700'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="p-6">
        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            <div className="grid grid-cols-2 gap-6">
              {/* Producer Card */}
              <div className="border border-slate-200 rounded-lg p-4">
                <h3 className="font-medium text-slate-700 mb-2 flex items-center gap-2">
                  <span className="w-6 h-6 bg-blue-100 rounded flex items-center justify-center text-blue-600">
                    P
                  </span>
                  Producer
                </h3>
                {value.producer?.team ? (
                  <div className="text-sm">
                    <div className="font-medium text-slate-800">{value.producer.team}</div>
                    {value.producer.contact && (
                      <div className="text-slate-500">{value.producer.contact}</div>
                    )}
                  </div>
                ) : (
                  <p className="text-sm text-slate-400">Not configured</p>
                )}
              </div>

              {/* Consumers Card */}
              <div className="border border-slate-200 rounded-lg p-4">
                <h3 className="font-medium text-slate-700 mb-2 flex items-center gap-2">
                  <span className="w-6 h-6 bg-emerald-100 rounded flex items-center justify-center text-emerald-600">
                    C
                  </span>
                  Consumers
                </h3>
                {(value.consumers?.length || 0) > 0 ? (
                  <div className="text-sm text-slate-600">
                    {value.consumers?.length} registered consumer(s)
                  </div>
                ) : (
                  <p className="text-sm text-slate-400">No consumers</p>
                )}
              </div>

              {/* Approval Chain Card */}
              <div className="border border-slate-200 rounded-lg p-4">
                <h3 className="font-medium text-slate-700 mb-2 flex items-center gap-2">
                  <span className="w-6 h-6 bg-amber-100 rounded flex items-center justify-center text-amber-600">
                    A
                  </span>
                  Approval Chain
                </h3>
                {(value.approval_chain?.length || 0) > 0 ? (
                  <div className="text-sm text-slate-600">
                    {value.approval_chain?.length} approver(s) required
                  </div>
                ) : (
                  <p className="text-sm text-slate-400">No approvals required</p>
                )}
              </div>

              {/* Review Schedule Card */}
              <div className="border border-slate-200 rounded-lg p-4">
                <h3 className="font-medium text-slate-700 mb-2 flex items-center gap-2">
                  <span className="w-6 h-6 bg-purple-100 rounded flex items-center justify-center text-purple-600">
                    R
                  </span>
                  Review Schedule
                </h3>
                <div className="text-sm">
                  <div className="text-slate-800 capitalize">
                    {value.review?.cadence || 'quarterly'}
                  </div>
                  {value.review?.next_review && (
                    <div className="text-slate-500">
                      Next: {new Date(value.review.next_review).toLocaleDateString()}
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Quick Stats */}
            <div className="bg-slate-50 rounded-lg p-4">
              <h3 className="text-sm font-medium text-slate-700 mb-3">Change Management</h3>
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <div className="text-lg font-bold text-slate-800">
                    {value.change_management?.breaking_change_notice || 'P30D'}
                  </div>
                  <div className="text-xs text-slate-500">Breaking Change Notice</div>
                </div>
                <div>
                  <div className="text-lg font-bold text-slate-800">
                    {value.change_management?.deprecation_notice || 'P90D'}
                  </div>
                  <div className="text-xs text-slate-500">Deprecation Notice</div>
                </div>
                <div>
                  <div className="text-lg font-bold text-slate-800">
                    {value.change_management?.migration_support ? 'Yes' : 'No'}
                  </div>
                  <div className="text-xs text-slate-500">Migration Support</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Producer Tab */}
        {activeTab === 'producer' && (
          <div className="space-y-4">
            <p className="text-sm text-slate-600">
              The producer is the team responsible for creating and maintaining this data contract.
            </p>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Team Name *</label>
                <input
                  type="text"
                  value={value.producer?.team || ''}
                  onChange={(e) => updateProducer({ team: e.target.value })}
                  placeholder="Data Platform Team"
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Contact Email</label>
                <input
                  type="email"
                  value={value.producer?.contact || ''}
                  onChange={(e) => updateProducer({ contact: e.target.value })}
                  placeholder="team@company.com"
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  Responsibilities
                </label>
                <textarea
                  value={(value.producer?.responsibilities || []).join('\n')}
                  onChange={(e) =>
                    updateProducer({
                      responsibilities: e.target.value.split('\n').filter((r) => r.trim()),
                    })
                  }
                  placeholder="Enter one responsibility per line"
                  rows={4}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                />
                <p className="text-xs text-slate-500 mt-1">
                  One responsibility per line (e.g., "Data quality assurance", "Schema maintenance")
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Consumers Tab */}
        {activeTab === 'consumers' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <p className="text-sm text-slate-600">
                Register teams that consume this data contract.
              </p>
              <button
                onClick={addConsumer}
                className="px-3 py-1 text-sm text-indigo-600 hover:text-indigo-700"
              >
                + Add Consumer
              </button>
            </div>

            {(value.consumers?.length || 0) === 0 ? (
              <div className="text-center py-8 text-slate-400">
                No consumers registered. Click "Add Consumer" to add one.
              </div>
            ) : (
              <div className="space-y-3">
                {value.consumers?.map((consumer, index) => (
                  <div
                    key={index}
                    className="border border-slate-200 rounded-lg p-4 space-y-3"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-slate-700">
                        Consumer #{index + 1}
                      </span>
                      <button
                        onClick={() => removeConsumer(index)}
                        className="text-red-500 hover:text-red-700 text-sm"
                      >
                        Remove
                      </button>
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="block text-xs text-slate-500 mb-1">Team Name *</label>
                        <input
                          type="text"
                          value={consumer.team}
                          onChange={(e) => updateConsumer(index, { team: e.target.value })}
                          placeholder="Analytics Team"
                          className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                        />
                      </div>
                      <div>
                        <label className="block text-xs text-slate-500 mb-1">Contact</label>
                        <input
                          type="text"
                          value={consumer.contact || ''}
                          onChange={(e) => updateConsumer(index, { contact: e.target.value })}
                          placeholder="team@company.com"
                          className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-xs text-slate-500 mb-1">Use Case</label>
                      <input
                        type="text"
                        value={consumer.use_case || ''}
                        onChange={(e) => updateConsumer(index, { use_case: e.target.value })}
                        placeholder="Dashboard reporting, ML model training"
                        className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                      />
                    </div>

                    {consumer.approved_date && (
                      <div className="text-xs text-slate-500">
                        Approved on {new Date(consumer.approved_date).toLocaleDateString()}
                        {consumer.approved_by && ` by ${consumer.approved_by}`}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Approvals Tab */}
        {activeTab === 'approvals' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <p className="text-sm text-slate-600">
                Configure the approval chain for contract changes.
              </p>
              <button
                onClick={addApproval}
                className="px-3 py-1 text-sm text-indigo-600 hover:text-indigo-700"
              >
                + Add Approver
              </button>
            </div>

            {(value.approval_chain?.length || 0) === 0 ? (
              <div className="text-center py-8 text-slate-400">
                No approvers configured. Changes will be auto-approved.
              </div>
            ) : (
              <div className="space-y-3">
                {value.approval_chain?.map((approval, index) => (
                  <div
                    key={index}
                    className="border border-slate-200 rounded-lg p-4 flex items-center gap-4"
                  >
                    {/* Step Number */}
                    <div className="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-600 font-medium">
                      {index + 1}
                    </div>

                    {/* Fields */}
                    <div className="flex-1 grid grid-cols-2 gap-3">
                      <div>
                        <label className="block text-xs text-slate-500 mb-1">Role *</label>
                        <input
                          type="text"
                          value={approval.role}
                          onChange={(e) => updateApproval(index, { role: e.target.value })}
                          placeholder="Data Steward, Manager, etc."
                          className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                        />
                      </div>
                      <div>
                        <label className="block text-xs text-slate-500 mb-1">Approver</label>
                        <input
                          type="text"
                          value={approval.approver || ''}
                          onChange={(e) => updateApproval(index, { approver: e.target.value })}
                          placeholder="john.doe@company.com"
                          className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                        />
                      </div>
                    </div>

                    {/* Status */}
                    {approval.approved_date && (
                      <div className="px-2 py-1 bg-emerald-50 text-emerald-700 rounded text-xs">
                        Approved
                      </div>
                    )}

                    {/* Remove */}
                    <button
                      onClick={() => removeApproval(index)}
                      className="text-red-500 hover:text-red-700"
                    >
                      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                ))}
              </div>
            )}

            {/* Approval Flow Visualization */}
            {(value.approval_chain?.length || 0) > 0 && (
              <div className="bg-slate-50 rounded-lg p-4 mt-4">
                <h4 className="text-sm font-medium text-slate-700 mb-2">Approval Flow</h4>
                <div className="flex items-center gap-2 overflow-x-auto">
                  <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs">
                    Submit
                  </span>
                  {value.approval_chain?.map((approval, index) => (
                    <div key={index} className="flex items-center gap-2">
                      <span className="text-slate-300">→</span>
                      <span className="px-2 py-1 bg-amber-100 text-amber-700 rounded text-xs">
                        {approval.role || `Step ${index + 1}`}
                      </span>
                    </div>
                  ))}
                  <span className="text-slate-300">→</span>
                  <span className="px-2 py-1 bg-emerald-100 text-emerald-700 rounded text-xs">
                    Approved
                  </span>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Review Tab */}
        {activeTab === 'review' && (
          <div className="space-y-4">
            <p className="text-sm text-slate-600">
              Configure the review schedule for this data contract.
            </p>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  Review Cadence
                </label>
                <select
                  value={value.review?.cadence || 'quarterly'}
                  onChange={(e) => updateReview({ cadence: e.target.value as ReviewCadence })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                >
                  <option value="monthly">Monthly</option>
                  <option value="quarterly">Quarterly</option>
                  <option value="annually">Annually</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">
                    Last Review
                  </label>
                  <input
                    type="date"
                    value={value.review?.last_review?.split('T')[0] || ''}
                    onChange={(e) => updateReview({ last_review: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">
                    Next Review
                  </label>
                  <input
                    type="date"
                    value={value.review?.next_review?.split('T')[0] || ''}
                    onChange={(e) => updateReview({ next_review: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  Reviewers
                </label>
                <textarea
                  value={(value.review?.reviewers || []).join('\n')}
                  onChange={(e) =>
                    updateReview({
                      reviewers: e.target.value.split('\n').filter((r) => r.trim()),
                    })
                  }
                  placeholder="Enter one reviewer email per line"
                  rows={3}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                />
              </div>
            </div>
          </div>
        )}

        {/* Change Management Tab */}
        {activeTab === 'changes' && (
          <div className="space-y-4">
            <p className="text-sm text-slate-600">
              Configure how changes to this contract are managed and communicated.
            </p>

            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">
                    Breaking Change Notice Period
                  </label>
                  <select
                    value={value.change_management?.breaking_change_notice || 'P30D'}
                    onChange={(e) =>
                      updateChangeManagement({ breaking_change_notice: e.target.value })
                    }
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                  >
                    <option value="P7D">7 days</option>
                    <option value="P14D">14 days</option>
                    <option value="P30D">30 days</option>
                    <option value="P60D">60 days</option>
                    <option value="P90D">90 days</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">
                    Deprecation Notice Period
                  </label>
                  <select
                    value={value.change_management?.deprecation_notice || 'P90D'}
                    onChange={(e) =>
                      updateChangeManagement({ deprecation_notice: e.target.value })
                    }
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                  >
                    <option value="P30D">30 days</option>
                    <option value="P60D">60 days</option>
                    <option value="P90D">90 days</option>
                    <option value="P180D">180 days</option>
                    <option value="P365D">1 year</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="flex items-center gap-2 text-sm font-medium text-slate-700">
                  <input
                    type="checkbox"
                    checked={value.change_management?.migration_support ?? true}
                    onChange={(e) =>
                      updateChangeManagement({ migration_support: e.target.checked })
                    }
                    className="rounded"
                  />
                  Provide migration support for breaking changes
                </label>
                <p className="text-xs text-slate-500 ml-6 mt-1">
                  When enabled, consumers will receive migration guides and tooling support
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  Communication Channels
                </label>
                <div className="flex flex-wrap gap-2">
                  {['email', 'slack', 'teams', 'webhook'].map((channel) => (
                    <label
                      key={channel}
                      className={`flex items-center gap-2 px-3 py-2 rounded-lg border cursor-pointer ${
                        (value.change_management?.communication_channels || []).includes(channel)
                          ? 'border-indigo-500 bg-indigo-50'
                          : 'border-slate-200'
                      }`}
                    >
                      <input
                        type="checkbox"
                        checked={(value.change_management?.communication_channels || []).includes(
                          channel
                        )}
                        onChange={(e) => {
                          const current = value.change_management?.communication_channels || [];
                          updateChangeManagement({
                            communication_channels: e.target.checked
                              ? [...current, channel]
                              : current.filter((c) => c !== channel),
                          });
                        }}
                        className="sr-only"
                      />
                      <span className="text-sm capitalize">{channel}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="px-6 py-4 border-t border-slate-200 bg-slate-50 flex justify-end">
        <button
          onClick={onClose}
          className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700"
        >
          Done
        </button>
      </div>
    </div>
  );
}

// =============================================================================
// Compact Governance Summary
// =============================================================================

export function GovernanceSummary({ governance }: { governance?: Governance }) {
  if (!governance) return <span className="text-slate-400">No governance configured</span>;

  return (
    <div className="flex flex-wrap gap-2 text-xs">
      {governance.producer?.team && (
        <span className="px-2 py-1 bg-blue-50 text-blue-700 rounded">
          Producer: {governance.producer.team}
        </span>
      )}
      {(governance.consumers?.length || 0) > 0 && (
        <span className="px-2 py-1 bg-emerald-50 text-emerald-700 rounded">
          {governance.consumers?.length} consumer(s)
        </span>
      )}
      {(governance.approval_chain?.length || 0) > 0 && (
        <span className="px-2 py-1 bg-amber-50 text-amber-700 rounded">
          {governance.approval_chain?.length} approver(s)
        </span>
      )}
      {governance.review?.cadence && (
        <span className="px-2 py-1 bg-purple-50 text-purple-700 rounded capitalize">
          {governance.review.cadence} review
        </span>
      )}
    </div>
  );
}
