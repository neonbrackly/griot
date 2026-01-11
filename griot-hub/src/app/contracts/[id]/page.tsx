'use client';

import { useEffect, useState, useMemo, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import type {
  Contract,
  VersionSummary,
  ValidationRecord,
  SchemaDefinition,
  SchemaProperty,
  PolicyCheck,
  PolicyCheckStatus,
  BreakingChangeInfo,
  ContractStatus,
} from '@/lib/types';
import api, { ApiClientError } from '@/lib/api';
import YamlEditor from '@/components/YamlEditor';

/**
 * Contract Detail Page (T-380)
 *
 * Redesigned for Open Data Contract Standard (ODCS) with:
 * - Modern UI inspired by reference design
 * - Interactive schema visualization
 * - Data Governance AI policy checks
 * - All ODCS sections display
 */

// =============================================================================
// Components
// =============================================================================

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    active: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    draft: 'bg-slate-50 text-slate-600 border-slate-200',
    deprecated: 'bg-amber-50 text-amber-700 border-amber-200',
    retired: 'bg-red-50 text-red-700 border-red-200',
  };
  return (
    <span className={`px-2.5 py-1 rounded-full text-xs font-medium border ${colors[status] || colors.draft}`}>
      {status}
    </span>
  );
}

function Tag({ children, variant = 'default' }: { children: React.ReactNode; variant?: 'default' | 'primary' }) {
  const base = 'px-2.5 py-1 rounded text-xs font-medium';
  const variants = {
    default: 'bg-slate-100 text-slate-600',
    primary: 'bg-indigo-50 text-indigo-700',
  };
  return <span className={`${base} ${variants[variant]}`}>{children}</span>;
}

function PolicyCheckCard({
  title,
  status,
  issueCount,
  issues,
}: {
  title: string;
  status: PolicyCheckStatus;
  issueCount?: number;
  issues?: { message: string }[];
}) {
  const statusConfig: Record<PolicyCheckStatus, { icon: string; color: string; bg: string }> = {
    pass: { icon: '✓', color: 'text-emerald-600', bg: 'bg-emerald-50' },
    fail: { icon: '!', color: 'text-red-600', bg: 'bg-red-50' },
    warning: { icon: '!', color: 'text-amber-600', bg: 'bg-amber-50' },
    info: { icon: 'i', color: 'text-blue-600', bg: 'bg-blue-50' },
  };

  const config = statusConfig[status];

  return (
    <div className="border border-slate-200 rounded-lg p-4 hover:border-slate-300 transition-colors">
      <div className="flex items-center justify-between mb-2">
        <span className="font-medium text-slate-800">{title}</span>
        {issueCount !== undefined && issueCount > 0 ? (
          <span className={`px-2 py-0.5 rounded text-xs font-medium ${config.bg} ${config.color}`}>
            {config.icon} {issueCount} issues
          </span>
        ) : (
          <span className={`w-5 h-5 rounded-full flex items-center justify-center text-xs ${config.bg} ${config.color}`}>
            {config.icon}
          </span>
        )}
      </div>
      {issues && issues.length > 0 && (
        <ul className="text-sm text-slate-500 space-y-1">
          {issues.slice(0, 3).map((issue, i) => (
            <li key={i} className="text-xs">{i + 1}. {issue.message}</li>
          ))}
        </ul>
      )}
    </div>
  );
}

function SchemaVisualization({ schemas }: { schemas?: SchemaDefinition[] }) {
  if (!schemas || schemas.length === 0) return null;

  return (
    <div className="bg-slate-50 rounded-lg p-4">
      <div className="flex items-center gap-2 mb-4">
        <button className="px-2 py-1 text-xs bg-white border border-slate-200 rounded hover:bg-slate-50">
          enlarge
        </button>
        <button className="px-2 py-1 text-xs bg-white border border-slate-200 rounded hover:bg-slate-50">
          apply layout
        </button>
      </div>
      <div className="flex justify-center">
        {schemas.map((schema) => (
          <div key={schema.name} className="bg-white rounded-lg border border-slate-200 shadow-sm min-w-[240px]">
            <div className="bg-indigo-600 text-white px-4 py-2 rounded-t-lg font-medium text-sm flex items-center gap-2">
              <span className="text-xs opacity-75">≡</span>
              {schema.name}
            </div>
            <div className="divide-y divide-slate-100">
              {schema.properties?.slice(0, 8).map((prop) => (
                <div key={prop.name} className="px-4 py-2 flex items-center justify-between text-sm">
                  <span className="font-mono text-slate-700">{prop.name}</span>
                  <span className="text-slate-400 text-xs">{prop.logicalType || 'string'}</span>
                </div>
              ))}
              {(schema.properties?.length || 0) > 8 && (
                <div className="px-4 py-2 text-xs text-slate-400 text-center">
                  +{(schema.properties?.length || 0) - 8} more fields
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
      <div className="text-right text-xs text-slate-400 mt-2">React Flow</div>
    </div>
  );
}

function InfoGrid({ items }: { items: { label: string; value: string | React.ReactNode }[] }) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
      {items.map((item) => (
        <div key={item.label}>
          <div className="text-xs text-slate-500 mb-1">{item.label}</div>
          <div className="font-medium text-slate-800">{item.value}</div>
        </div>
      ))}
    </div>
  );
}

function Section({ title, subtitle, children }: { title: string; subtitle?: string; children: React.ReactNode }) {
  return (
    <div className="mb-8">
      <div className="mb-4">
        <h2 className="text-lg font-semibold text-slate-800">{title}</h2>
        {subtitle && <p className="text-sm text-slate-500">{subtitle}</p>}
      </div>
      {children}
    </div>
  );
}

function SchemaTable({ properties }: { properties?: SchemaProperty[] }) {
  if (!properties || properties.length === 0) {
    return <div className="text-slate-400 text-sm">No properties defined</div>;
  }

  return (
    <div className="border border-slate-200 rounded-lg overflow-hidden">
      <table className="w-full text-sm">
        <thead className="bg-slate-50 border-b border-slate-200">
          <tr>
            <th className="text-left px-4 py-3 font-medium text-slate-600">Name</th>
            <th className="text-left px-4 py-3 font-medium text-slate-600">Type</th>
            <th className="text-left px-4 py-3 font-medium text-slate-600">Description</th>
            <th className="text-left px-4 py-3 font-medium text-slate-600">Details</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {properties.map((prop) => (
            <tr key={prop.name} className="hover:bg-slate-50">
              <td className="px-4 py-3">
                <div className="flex items-center gap-2">
                  <span className="font-mono font-medium text-slate-800">{prop.name}</span>
                  {prop.primary_key && (
                    <span className="px-1.5 py-0.5 bg-amber-50 text-amber-700 text-xs rounded">
                      primaryKey
                    </span>
                  )}
                </div>
              </td>
              <td className="px-4 py-3">
                <div className="flex items-center gap-2">
                  <Tag>{prop.logicalType || 'string'}</Tag>
                  {prop.physicalType && (
                    <Tag variant="primary">{prop.physicalType}</Tag>
                  )}
                </div>
              </td>
              <td className="px-4 py-3 text-slate-600 max-w-md">
                <div>{prop.semantic?.description || prop.description || '—'}</div>
                {prop.examples && prop.examples.length > 0 && (
                  <div className="text-xs text-slate-400 mt-1 italic">
                    Example(s): {prop.examples.slice(0, 2).map(e => String(e)).join(', ')}
                  </div>
                )}
              </td>
              <td className="px-4 py-3">
                <div className="flex flex-wrap gap-1">
                  {prop.nullable && <Tag>nullable</Tag>}
                  {prop.constraints?.unique && <Tag>unique</Tag>}
                  {prop.privacy?.contains_pii && (
                    <Tag variant="primary">PII</Tag>
                  )}
                  {prop.foreign_key && (
                    <Tag variant="primary">FK</Tag>
                  )}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export default function ContractDetailPage() {
  const params = useParams();
  const router = useRouter();
  const contractId = params.id as string;

  const [contract, setContract] = useState<Contract | null>(null);
  const [versions, setVersions] = useState<VersionSummary[]>([]);
  const [validations, setValidations] = useState<ValidationRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'schema' | 'governance' | 'versions' | 'validations'>('overview');

  // YAML Editor state
  const [showYamlEditor, setShowYamlEditor] = useState(false);
  const [yamlContent, setYamlContent] = useState<string>('');

  // Approval workflow state
  const [approvalLoading, setApprovalLoading] = useState(false);
  const [approvalStatus, setApprovalStatus] = useState<{
    status: 'pending' | 'approved' | 'rejected';
    approvedBy?: string;
    approvedAt?: string;
  } | null>(null);

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

  // Load YAML content for editing
  const handleEditYaml = useCallback(async () => {
    try {
      const yaml = await api.getContractYaml(contractId);
      setYamlContent(yaml);
      setShowYamlEditor(true);
    } catch (err) {
      // Generate YAML from current contract if API fails
      if (contract) {
        const generatedYaml = `# Data Contract: ${contract.name}
apiVersion: ${contract.api_version || 'v1.0.0'}
kind: DataContract
id: ${contract.id}
name: "${contract.name}"
version: "${contract.version}"
status: ${contract.status}
${contract.description_odcs?.purpose ? `\ndescription:\n  purpose: "${contract.description_odcs.purpose}"` : ''}
${contract.schema?.length ? `\nschema:\n${contract.schema.map(s => `  - name: ${s.name}\n    physicalType: ${s.physicalType}`).join('\n')}` : ''}
`;
        setYamlContent(generatedYaml);
        setShowYamlEditor(true);
      }
    }
  }, [contractId, contract]);

  // Detect breaking changes for YAML editor
  const detectBreakingChanges = useCallback(async (newData: Record<string, unknown>): Promise<BreakingChangeInfo[]> => {
    try {
      const response = await api.checkBreakingChanges(contractId, newData as any);
      return response.breaking_changes || [];
    } catch (err) {
      if (err instanceof ApiClientError && err.isBreakingChangeError()) {
        return err.breakingChanges || [];
      }
      return [];
    }
  }, [contractId]);

  // Save YAML changes
  const handleSaveYaml = useCallback(async (
    parsedData: Record<string, unknown>,
    isBreaking: boolean,
    newVersion?: string
  ) => {
    try {
      await api.updateContract(contractId, parsedData as any, { allowBreaking: isBreaking });
      setShowYamlEditor(false);
      // Refresh contract data
      const updatedContract = await api.getContract(contractId);
      setContract(updatedContract);
      // Refresh versions
      const versionsRes = await api.getVersions(contractId, { limit: 10 });
      setVersions(versionsRes.items);
    } catch (err) {
      throw err;
    }
  }, [contractId]);

  // Send for approval
  const handleSendForApproval = useCallback(async () => {
    if (!contract) return;

    try {
      setApprovalLoading(true);
      await api.createApprovalChain(contractId, contract.version, {
        approvers: [
          {
            user_id: 'data-producer',
            email: 'producer@company.com',
            name: 'Data Producer',
            role: 'producer',
          },
        ],
      });
      setApprovalStatus({ status: 'pending' });
    } catch (err) {
      console.error('Failed to send for approval:', err);
    } finally {
      setApprovalLoading(false);
    }
  }, [contractId, contract]);

  // Approve contract
  const handleApprove = useCallback(async () => {
    if (!contract) return;

    try {
      setApprovalLoading(true);
      await api.updateContractStatus(contractId, 'active');
      setApprovalStatus({
        status: 'approved',
        approvedBy: 'Current User',
        approvedAt: new Date().toISOString(),
      });
      // Refresh contract
      const updatedContract = await api.getContract(contractId);
      setContract(updatedContract);
    } catch (err) {
      console.error('Failed to approve:', err);
    } finally {
      setApprovalLoading(false);
    }
  }, [contractId, contract]);

  // Compute governance checks from contract data
  const governanceChecks = useMemo(() => {
    if (!contract) return null;

    const checks: { title: string; status: PolicyCheckStatus; issueCount?: number; issues?: { message: string }[] }[] = [];

    // Ownership check
    const ownershipIssues: { message: string }[] = [];
    if (!contract.team?.name) {
      ownershipIssues.push({ message: 'The data contract does not specify a team as an owner.' });
    }
    if (!contract.team?.steward?.email) {
      ownershipIssues.push({ message: 'The data contract does not include contact details for the team.' });
    }
    checks.push({
      title: 'Ownership',
      status: ownershipIssues.length > 0 ? 'warning' : 'pass',
      issueCount: ownershipIssues.length,
      issues: ownershipIssues,
    });

    // Data Classification check
    const hasClassification = contract.compliance?.data_classification;
    checks.push({
      title: 'Data Classification',
      status: hasClassification ? 'pass' : 'warning',
      issueCount: hasClassification ? 0 : 1,
      issues: hasClassification ? [] : [{ message: 'Data classification is not specified.' }],
    });

    // Mandatory fields check
    const mandatoryIssues: { message: string }[] = [];
    if (!contract.description_odcs?.purpose && !contract.description) {
      mandatoryIssues.push({ message: "The mandatory field 'description.purpose' is missing." });
    }
    checks.push({
      title: 'Mandatory fields',
      status: mandatoryIssues.length > 0 ? 'fail' : 'pass',
      issueCount: mandatoryIssues.length,
      issues: mandatoryIssues,
    });

    // SLA check
    const hasSLA = contract.sla && (contract.sla.availability || contract.sla.freshness);
    checks.push({
      title: 'SLA Defined',
      status: hasSLA ? 'pass' : 'info',
      issueCount: hasSLA ? 0 : 1,
      issues: hasSLA ? [] : [{ message: 'No SLA targets are defined.' }],
    });

    // PII Compliance check
    const hasPrivacyConfig = contract.schema?.some(s =>
      s.properties?.some(p => p.privacy?.contains_pii !== undefined)
    );
    checks.push({
      title: 'PII Compliance',
      status: hasPrivacyConfig ? 'pass' : 'info',
      issueCount: hasPrivacyConfig ? 0 : 1,
      issues: hasPrivacyConfig ? [] : [{ message: 'Privacy configuration not specified for fields.' }],
    });

    return checks;
  }, [contract]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16">
        <div className="animate-pulse text-slate-400">Loading contract details...</div>
      </div>
    );
  }

  if (error || !contract) {
    return (
      <div className="text-center py-16">
        <div className="text-red-500 mb-4">{error || 'Contract not found'}</div>
        <a href="/contracts" className="text-indigo-600 hover:underline">
          Back to contracts
        </a>
      </div>
    );
  }

  // Determine domain from team/governance
  const domain = contract.team?.department || contract.governance?.producer?.team || 'General';

  // Get total field count from ODCS schema
  const totalFields = (contract.schema || []).reduce((acc, s) => acc + (s.properties?.length || 0), 0);

  return (
    <div className="space-y-6">
      {/* Breadcrumb */}
      <nav className="text-sm text-slate-500">
        <a href="/" className="hover:text-slate-700">Home</a>
        <span className="mx-2">›</span>
        <a href="/contracts" className="hover:text-slate-700">Data Contracts</a>
        <span className="mx-2">›</span>
        <span className="text-slate-800">{contract.name}</span>
      </nav>

      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <h1 className="text-2xl font-bold text-slate-900">Data Contract</h1>
          </div>
          <div className="flex items-center gap-2 mb-3">
            <span className="font-mono text-slate-600">{contract.id}</span>
            <Tag variant="primary">{contract.version}</Tag>
          </div>
          <div className="flex items-center gap-2">
            <Tag>{domain}</Tag>
            <Tag variant="primary">Open Data Contract Standard {contract.api_version || 'v1.0.0'}</Tag>
            <StatusBadge status={contract.status} />
          </div>
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleEditYaml}
            className="px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
            Edit YAML
          </button>
          {contract.status === 'draft' && !approvalStatus && (
            <button
              onClick={handleSendForApproval}
              disabled={approvalLoading}
              className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {approvalLoading ? (
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
              ) : (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              )}
              Send for Approval
            </button>
          )}
          {approvalStatus?.status === 'pending' && (
            <button
              onClick={handleApprove}
              disabled={approvalLoading}
              className="px-4 py-2 text-sm font-medium text-white bg-emerald-600 rounded-lg hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {approvalLoading ? (
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
              ) : (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              )}
              Approve & Activate
            </button>
          )}
          {contract.status !== 'draft' && (
            <button className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700">
              Request Access
            </button>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-slate-200">
        <nav className="flex gap-8">
          {(['overview', 'schema', 'governance', 'versions', 'validations'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`py-3 border-b-2 font-medium text-sm capitalize transition-colors ${
                activeTab === tab
                  ? 'border-indigo-600 text-indigo-600'
                  : 'border-transparent text-slate-500 hover:text-slate-700'
              }`}
            >
              {tab}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-3 gap-8">
          {/* Main Content (2/3) */}
          <div className="col-span-2 space-y-8">
            {/* Schema Visualization */}
            {contract.schema && contract.schema.length > 0 && (
              <SchemaVisualization schemas={contract.schema} />
            )}

            {/* Fundamentals */}
            <Section title="Fundamentals" subtitle="Information about the data contract">
              <div className="bg-white rounded-lg border border-slate-200 p-6">
                <InfoGrid
                  items={[
                    { label: 'Version', value: contract.version },
                    { label: 'Status', value: <StatusBadge status={contract.status} /> },
                    { label: 'Domain', value: domain },
                    {
                      label: 'Purpose',
                      value: contract.description_odcs?.purpose || contract.description || 'Not specified',
                    },
                  ]}
                />
              </div>
            </Section>

            {/* Schema Preview */}
            <Section title="Schema" subtitle="Schema supports both a business representation and physical implementation">
              {contract.schema?.map((schema) => (
                <div key={schema.name} className="mb-6">
                  <div className="flex items-center gap-2 mb-3">
                    <span className="font-mono font-medium text-slate-800">{schema.name}</span>
                    <Tag>{schema.physicalType}</Tag>
                  </div>
                  <SchemaTable properties={schema.properties} />
                </div>
              ))}
            </Section>
          </div>

          {/* Sidebar (1/3) */}
          <div className="space-y-6">
            {/* Implementation */}
            {contract.servers && contract.servers.length > 0 && (
              <div className="bg-white rounded-lg border border-slate-200 p-6">
                <h3 className="font-semibold text-slate-800 mb-2">Implementation</h3>
                <p className="text-xs text-slate-500 mb-4">Data product output port implementing this contract</p>
                {contract.servers.map((server) => (
                  <div key={server.server} className="flex items-center gap-3 p-3 bg-slate-50 rounded-lg">
                    <div className="w-8 h-8 bg-blue-100 rounded flex items-center justify-center text-blue-600">
                      ❄️
                    </div>
                    <div>
                      <div className="font-medium text-slate-800">{server.dataset}</div>
                      <div className="text-xs text-slate-500">{server.type} • {server.environment}</div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Data Governance AI */}
            <div className="bg-white rounded-lg border border-slate-200 p-6">
              <h3 className="font-semibold text-slate-800 mb-2">Data Governance AI</h3>
              <p className="text-xs text-slate-500 mb-4">Automated policy checks</p>
              <div className="space-y-3">
                {governanceChecks?.map((check) => (
                  <PolicyCheckCard
                    key={check.title}
                    title={check.title}
                    status={check.status}
                    issueCount={check.issueCount}
                    issues={check.issues}
                  />
                ))}
              </div>
            </div>

            {/* Quick Stats */}
            <div className="bg-white rounded-lg border border-slate-200 p-6">
              <h3 className="font-semibold text-slate-800 mb-4">Quick Stats</h3>
              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-slate-500">Total Fields</span>
                  <span className="font-medium text-slate-800">{totalFields}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-500">Schemas</span>
                  <span className="font-medium text-slate-800">{contract.schema?.length || 0}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-500">Versions</span>
                  <span className="font-medium text-slate-800">{versions.length}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-500">Validations</span>
                  <span className="font-medium text-slate-800">{validations.length}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'schema' && (
        <div className="space-y-6">
          {contract.schema?.map((schema) => (
            <Section
              key={schema.name}
              title={schema.name}
              subtitle={`${schema.physicalType} • ${schema.properties?.length || 0} properties`}
            >
              <SchemaTable properties={schema.properties} />

              {/* Quality Rules */}
              {schema.quality && (
                <div className="mt-4 bg-slate-50 rounded-lg p-4">
                  <h4 className="font-medium text-slate-700 mb-3">Quality Rules</h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    {schema.quality.completeness && (
                      <div className="bg-white rounded p-3 border border-slate-200">
                        <div className="text-xs text-slate-500 mb-1">Completeness</div>
                        <div className="font-medium">{schema.quality.completeness.min_percent}%</div>
                      </div>
                    )}
                    {schema.quality.accuracy && (
                      <div className="bg-white rounded p-3 border border-slate-200">
                        <div className="text-xs text-slate-500 mb-1">Accuracy</div>
                        <div className="font-medium">{(1 - schema.quality.accuracy.max_error_rate) * 100}%</div>
                      </div>
                    )}
                    {schema.quality.freshness && (
                      <div className="bg-white rounded p-3 border border-slate-200">
                        <div className="text-xs text-slate-500 mb-1">Freshness</div>
                        <div className="font-medium">{schema.quality.freshness.max_age}</div>
                      </div>
                    )}
                    {schema.quality.volume && (
                      <div className="bg-white rounded p-3 border border-slate-200">
                        <div className="text-xs text-slate-500 mb-1">Volume</div>
                        <div className="font-medium">
                          {schema.quality.volume.min_rows?.toLocaleString() || '0'} - {schema.quality.volume.max_rows?.toLocaleString() || '∞'}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </Section>
          ))}

        </div>
      )}

      {activeTab === 'governance' && (
        <div className="grid grid-cols-2 gap-6">
          {/* Team & Ownership */}
          <Section title="Team & Ownership">
            <div className="bg-white rounded-lg border border-slate-200 p-6 space-y-4">
              {contract.team && (
                <>
                  <div>
                    <div className="text-xs text-slate-500 mb-1">Team</div>
                    <div className="font-medium text-slate-800">{contract.team.name}</div>
                    {contract.team.department && (
                      <div className="text-sm text-slate-500">{contract.team.department}</div>
                    )}
                  </div>
                  {contract.team.steward && (
                    <div>
                      <div className="text-xs text-slate-500 mb-1">Data Steward</div>
                      <div className="font-medium text-slate-800">{contract.team.steward.name}</div>
                      {contract.team.steward.email && (
                        <div className="text-sm text-indigo-600">{contract.team.steward.email}</div>
                      )}
                    </div>
                  )}
                </>
              )}
              {!contract.team && (
                <div className="text-slate-400 text-sm">No team information available</div>
              )}
            </div>
          </Section>

          {/* Compliance */}
          <Section title="Compliance">
            <div className="bg-white rounded-lg border border-slate-200 p-6 space-y-4">
              {contract.compliance && (
                <>
                  <div>
                    <div className="text-xs text-slate-500 mb-1">Data Classification</div>
                    <Tag variant="primary">{contract.compliance.data_classification}</Tag>
                  </div>
                  {contract.compliance.regulatory_scope && contract.compliance.regulatory_scope.length > 0 && (
                    <div>
                      <div className="text-xs text-slate-500 mb-1">Regulations</div>
                      <div className="flex flex-wrap gap-1">
                        {contract.compliance.regulatory_scope.map((reg) => (
                          <Tag key={reg}>{reg}</Tag>
                        ))}
                      </div>
                    </div>
                  )}
                  {contract.compliance.audit_requirements && (
                    <div>
                      <div className="text-xs text-slate-500 mb-1">Audit Logging</div>
                      <div className="text-sm text-slate-700">
                        {contract.compliance.audit_requirements.logging ? 'Enabled' : 'Disabled'}
                        {contract.compliance.audit_requirements.log_retention && (
                          <span className="text-slate-500"> • Retention: {contract.compliance.audit_requirements.log_retention}</span>
                        )}
                      </div>
                    </div>
                  )}
                </>
              )}
              {!contract.compliance && (
                <div className="text-slate-400 text-sm">No compliance information available</div>
              )}
            </div>
          </Section>

          {/* Legal */}
          <Section title="Legal">
            <div className="bg-white rounded-lg border border-slate-200 p-6 space-y-4">
              {contract.legal && (
                <>
                  {contract.legal.jurisdiction && contract.legal.jurisdiction.length > 0 && (
                    <div>
                      <div className="text-xs text-slate-500 mb-1">Jurisdiction</div>
                      <div className="flex flex-wrap gap-1">
                        {contract.legal.jurisdiction.map((j) => (
                          <Tag key={j}>{j}</Tag>
                        ))}
                      </div>
                    </div>
                  )}
                  {contract.legal.basis && (
                    <div>
                      <div className="text-xs text-slate-500 mb-1">Legal Basis</div>
                      <div className="font-medium text-slate-800 capitalize">
                        {contract.legal.basis.replace(/_/g, ' ')}
                      </div>
                    </div>
                  )}
                  {contract.legal.regulations && contract.legal.regulations.length > 0 && (
                    <div>
                      <div className="text-xs text-slate-500 mb-1">Regulations</div>
                      <div className="flex flex-wrap gap-1">
                        {contract.legal.regulations.map((reg) => (
                          <Tag key={reg} variant="primary">{reg}</Tag>
                        ))}
                      </div>
                    </div>
                  )}
                </>
              )}
              {!contract.legal && (
                <div className="text-slate-400 text-sm">No legal information available</div>
              )}
            </div>
          </Section>

          {/* SLA */}
          <Section title="Service Level Agreements">
            <div className="bg-white rounded-lg border border-slate-200 p-6 space-y-4">
              {contract.sla && (
                <div className="grid grid-cols-2 gap-4">
                  {contract.sla.availability && (
                    <div className="bg-slate-50 rounded p-3">
                      <div className="text-xs text-slate-500 mb-1">Availability</div>
                      <div className="font-medium text-slate-800">{contract.sla.availability.target_percent}%</div>
                      <div className="text-xs text-slate-500">Window: {contract.sla.availability.measurement_window}</div>
                    </div>
                  )}
                  {contract.sla.freshness && (
                    <div className="bg-slate-50 rounded p-3">
                      <div className="text-xs text-slate-500 mb-1">Freshness</div>
                      <div className="font-medium text-slate-800">{contract.sla.freshness.target}</div>
                    </div>
                  )}
                  {contract.sla.completeness && (
                    <div className="bg-slate-50 rounded p-3">
                      <div className="text-xs text-slate-500 mb-1">Completeness</div>
                      <div className="font-medium text-slate-800">{contract.sla.completeness.target_percent}%</div>
                    </div>
                  )}
                  {contract.sla.accuracy && (
                    <div className="bg-slate-50 rounded p-3">
                      <div className="text-xs text-slate-500 mb-1">Accuracy</div>
                      <div className="font-medium text-slate-800">
                        {(1 - contract.sla.accuracy.error_rate_target) * 100}%
                      </div>
                    </div>
                  )}
                </div>
              )}
              {!contract.sla && (
                <div className="text-slate-400 text-sm">No SLA defined</div>
              )}
            </div>
          </Section>

          {/* Access Control */}
          <Section title="Access Control">
            <div className="bg-white rounded-lg border border-slate-200 p-6 space-y-4">
              {contract.access && (
                <>
                  <div>
                    <div className="text-xs text-slate-500 mb-1">Default Access Level</div>
                    <Tag variant="primary">{contract.access.default_level}</Tag>
                  </div>
                  {contract.access.grants && contract.access.grants.length > 0 && (
                    <div>
                      <div className="text-xs text-slate-500 mb-2">Grants</div>
                      <div className="space-y-2">
                        {contract.access.grants.map((grant, i) => (
                          <div key={i} className="flex items-center justify-between bg-slate-50 rounded p-2">
                            <span className="font-mono text-sm text-slate-700">{grant.principal}</span>
                            <Tag>{grant.level}</Tag>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </>
              )}
              {!contract.access && (
                <div className="text-slate-400 text-sm">No access control configured</div>
              )}
            </div>
          </Section>

          {/* Roles */}
          {contract.roles && contract.roles.length > 0 && (
            <Section title="Roles">
              <div className="bg-white rounded-lg border border-slate-200 p-6">
                <div className="space-y-2">
                  {contract.roles.map((role) => (
                    <div key={role.role} className="flex items-center justify-between bg-slate-50 rounded p-3">
                      <span className="font-medium text-slate-700">{role.role}</span>
                      <Tag variant="primary">{role.access}</Tag>
                    </div>
                  ))}
                </div>
              </div>
            </Section>
          )}
        </div>
      )}

      {activeTab === 'versions' && (
        <div className="bg-white rounded-lg border border-slate-200">
          {versions.length > 0 ? (
            <div className="divide-y divide-slate-100">
              {versions.map((version) => (
                <div key={version.version} className="px-6 py-4 flex items-center justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-slate-800">v{version.version}</span>
                      {version.is_breaking && (
                        <span className="px-2 py-0.5 bg-red-50 text-red-700 rounded text-xs font-medium">
                          breaking
                        </span>
                      )}
                      {version.change_type && (
                        <Tag>{version.change_type}</Tag>
                      )}
                    </div>
                    {version.change_notes && (
                      <div className="text-sm text-slate-500 mt-1">{version.change_notes}</div>
                    )}
                  </div>
                  <div className="text-sm text-slate-400">
                    {version.created_at && new Date(version.created_at).toLocaleDateString()}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-slate-400 text-center py-8">No version history</div>
          )}
        </div>
      )}

      {activeTab === 'validations' && (
        <div className="bg-white rounded-lg border border-slate-200">
          {validations.length > 0 ? (
            <div className="divide-y divide-slate-100">
              {validations.map((validation) => (
                <div key={validation.id} className="px-6 py-4 flex items-center justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <span
                        className={`px-2 py-0.5 rounded text-sm font-medium ${
                          validation.passed
                            ? 'bg-emerald-50 text-emerald-700'
                            : 'bg-red-50 text-red-700'
                        }`}
                      >
                        {validation.passed ? 'Passed' : 'Failed'}
                      </span>
                      <span className="text-slate-600">
                        {validation.row_count.toLocaleString()} rows
                      </span>
                      {validation.error_count !== undefined && validation.error_count > 0 && (
                        <span className="text-red-600">
                          ({validation.error_count.toLocaleString()} errors)
                        </span>
                      )}
                    </div>
                    <div className="text-sm text-slate-500 mt-1">
                      v{validation.contract_version || contract.version}
                    </div>
                  </div>
                  <div className="text-sm text-slate-400">
                    {new Date(validation.recorded_at).toLocaleString()}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-slate-400 text-center py-8">No validations recorded</div>
          )}
        </div>
      )}

      {/* YAML Editor Modal */}
      {showYamlEditor && (
        <YamlEditor
          initialYaml={yamlContent}
          contractStatus={contract.status as 'draft' | 'active' | 'deprecated' | 'retired'}
          currentVersion={contract.version}
          onSave={handleSaveYaml}
          onCancel={() => setShowYamlEditor(false)}
          detectBreakingChanges={detectBreakingChanges}
        />
      )}

      {/* Approval Status Banner */}
      {approvalStatus && (
        <div className={`fixed bottom-4 right-4 p-4 rounded-lg shadow-lg max-w-sm ${
          approvalStatus.status === 'pending'
            ? 'bg-amber-50 border border-amber-200'
            : approvalStatus.status === 'approved'
            ? 'bg-emerald-50 border border-emerald-200'
            : 'bg-red-50 border border-red-200'
        }`}>
          <div className="flex items-center gap-3">
            {approvalStatus.status === 'pending' && (
              <>
                <svg className="w-6 h-6 text-amber-500 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div>
                  <p className="font-medium text-amber-800">Pending Approval</p>
                  <p className="text-sm text-amber-600">Waiting for producer approval</p>
                </div>
              </>
            )}
            {approvalStatus.status === 'approved' && (
              <>
                <svg className="w-6 h-6 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div>
                  <p className="font-medium text-emerald-800">Approved!</p>
                  <p className="text-sm text-emerald-600">
                    {approvalStatus.approvedBy && `by ${approvalStatus.approvedBy}`}
                  </p>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
