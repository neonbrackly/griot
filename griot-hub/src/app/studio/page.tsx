'use client';

import { useEffect, useState, useCallback } from 'react';
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
 * - Live YAML preview
 * - Validation before save
 */

// =============================================================================
// Types
// =============================================================================

type SectionKey = 'basics' | 'description' | 'schema' | 'legal' | 'compliance' | 'sla' | 'access' | 'team' | 'servers' | 'governance';

interface SectionState {
  expanded: boolean;
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
}: {
  title: string;
  subtitle?: string;
  expanded: boolean;
  onToggle: () => void;
  hasContent?: boolean;
}) {
  return (
    <button
      onClick={onToggle}
      className="w-full flex items-center justify-between p-4 text-left hover:bg-slate-50 transition-colors"
    >
      <div className="flex items-center gap-3">
        <span
          className={`w-6 h-6 rounded flex items-center justify-center text-xs ${
            hasContent ? 'bg-indigo-100 text-indigo-600' : 'bg-slate-100 text-slate-400'
          }`}
        >
          {expanded ? '−' : '+'}
        </span>
        <div>
          <h3 className="font-medium text-slate-800">{title}</h3>
          {subtitle && <p className="text-xs text-slate-500">{subtitle}</p>}
        </div>
      </div>
      {hasContent && (
        <span className="px-2 py-0.5 bg-indigo-50 text-indigo-600 text-xs rounded">
          Configured
        </span>
      )}
    </button>
  );
}

function FormField({
  label,
  required,
  children,
  hint,
}: {
  label: string;
  required?: boolean;
  children: React.ReactNode;
  hint?: string;
}) {
  return (
    <div>
      <label className="block text-sm font-medium text-slate-700 mb-1">
        {label} {required && <span className="text-red-500">*</span>}
      </label>
      {children}
      {hint && <p className="mt-1 text-xs text-slate-500">{hint}</p>}
    </div>
  );
}

function Input({
  value,
  onChange,
  placeholder,
  disabled,
  type = 'text',
}: {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
  type?: string;
}) {
  return (
    <input
      type={type}
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      disabled={disabled}
      className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 disabled:bg-slate-100 disabled:text-slate-500"
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
}: {
  value: T;
  onChange: (value: T) => void;
  options: { value: T; label: string }[];
}) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value as T)}
      className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
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

// =============================================================================
// Schema Property Editor
// =============================================================================

function SchemaPropertyEditor({
  property,
  onChange,
  onRemove,
}: {
  property: SchemaProperty;
  onChange: (property: SchemaProperty) => void;
  onRemove: () => void;
}) {
  return (
    <div className="border border-slate-200 rounded-lg p-4 space-y-3">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-slate-700">Property</span>
        <button onClick={onRemove} className="text-red-500 hover:text-red-700 text-sm">
          Remove
        </button>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <FormField label="Name" required>
          <Input
            value={property.name}
            onChange={(name) => onChange({ ...property, name })}
            placeholder="field_name"
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
  const [showYaml, setShowYaml] = useState(false);

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
    const data = buildContractData();
    const yamlContent = `# Data Contract: ${contractName || 'Untitled'}
apiVersion: v1.0.0
kind: DataContract
id: ${contractId || 'my-contract'}
name: "${contractName || 'Untitled'}"
status: ${status}
${description.purpose ? `\ndescription:\n  purpose: "${description.purpose}"${description.usage ? `\n  usage: "${description.usage}"` : ''}${description.limitations ? `\n  limitations: "${description.limitations}"` : ''}` : ''}
${schema.length > 0 ? `\nschema:\n${schema.map(s => `  - name: ${s.name}\n    physicalType: ${s.physicalType}${s.properties && s.properties.length > 0 ? `\n    properties:\n${s.properties.map(p => `      - name: ${p.name}\n        logicalType: ${p.logicalType}\n        nullable: ${p.nullable}${p.primary_key ? '\n        primaryKey: true' : ''}${p.description ? `\n        description: "${p.description}"` : ''}`).join('\n')}` : ''}`).join('\n')}` : ''}
${team.name ? `\nteam:\n  name: "${team.name}"${team.department ? `\n  department: "${team.department}"` : ''}${team.steward?.name ? `\n  steward:\n    name: "${team.steward.name}"${team.steward.email ? `\n    email: "${team.steward.email}"` : ''}` : ''}` : ''}
${compliance.data_classification ? `\ncompliance:\n  dataClassification: ${compliance.data_classification}${compliance.regulatory_scope && compliance.regulatory_scope.length > 0 ? `\n  regulatoryScope:\n${compliance.regulatory_scope.map(r => `    - ${r}`).join('\n')}` : ''}` : ''}
`;
    return yamlContent;
  }, [buildContractData, contractId, contractName, status, description, schema, team, compliance]);

  // Save contract
  const handleSave = async (force: boolean = false) => {
    setError(null);
    setSuccess(null);
    setBreakingChanges([]);

    // Validation
    if (!contractId.trim()) {
      setError('Contract ID is required');
      return;
    }
    if (!contractName.trim()) {
      setError('Contract name is required');
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

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16">
        <div className="animate-pulse text-slate-400">Loading contract...</div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
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
            onClick={() => setShowYaml(!showYaml)}
            className="px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50"
          >
            {showYaml ? 'Hide YAML' : 'Show YAML'}
          </button>
          <button
            onClick={() => handleSave(false)}
            disabled={saving}
            className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 disabled:opacity-50 flex items-center gap-2"
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
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {success && (
        <div className="bg-emerald-50 border border-emerald-200 text-emerald-700 px-4 py-3 rounded-lg">
          {success}
        </div>
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

      {/* Main Content */}
      <div className="grid grid-cols-3 gap-6">
        {/* Form Sections (2/3) */}
        <div className="col-span-2 space-y-4">
          {/* Basics Section */}
          <div className="bg-white rounded-lg border border-slate-200 overflow-hidden">
            <SectionHeader
              title="Basic Information"
              subtitle="Required contract metadata"
              expanded={sections.basics.expanded}
              onToggle={() => toggleSection('basics')}
              hasContent={!!contractId && !!contractName}
            />
            {sections.basics.expanded && (
              <div className="p-4 border-t border-slate-200 space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <FormField label="Contract ID" required hint="Unique identifier (lowercase, hyphens)">
                    <Input
                      value={contractId}
                      onChange={(v) => setContractId(v.toLowerCase().replace(/\s+/g, '-'))}
                      placeholder="my-contract"
                      disabled={!!editId}
                    />
                  </FormField>

                  <FormField label="Contract Name" required>
                    <Input
                      value={contractName}
                      onChange={setContractName}
                      placeholder="My Contract"
                    />
                  </FormField>
                </div>

                <FormField label="Status">
                  <Select
                    value={status}
                    onChange={setStatus}
                    options={[
                      { value: 'draft', label: 'Draft' },
                      { value: 'active', label: 'Active' },
                      { value: 'deprecated', label: 'Deprecated' },
                      { value: 'retired', label: 'Retired' },
                    ]}
                  />
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
            />
            {sections.schema.expanded && (
              <div className="p-4 border-t border-slate-200 space-y-4">
                {schema.map((s, schemaIndex) => (
                  <div key={schemaIndex} className="border border-slate-200 rounded-lg p-4 space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="grid grid-cols-2 gap-4 flex-1">
                        <FormField label="Schema Name">
                          <Input
                            value={s.name}
                            onChange={(name) => updateSchema(schemaIndex, { name })}
                            placeholder="schema_name"
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
                <FormField label="Data Classification">
                  <Select
                    value={compliance.data_classification}
                    onChange={(data_classification) => setCompliance({ ...compliance, data_classification })}
                    options={[
                      { value: 'public', label: 'Public' },
                      { value: 'internal', label: 'Internal' },
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
                  <FormField label="Availability Target (%)" hint="e.g., 99.9">
                    <Input
                      value={sla.availability?.target_percent?.toString() || ''}
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
                      placeholder="99.9"
                      type="number"
                    />
                  </FormField>

                  <FormField label="Freshness Target" hint="ISO 8601 duration (e.g., PT4H)">
                    <Input
                      value={sla.freshness?.target || ''}
                      onChange={(target) =>
                        setSLA({
                          ...sla,
                          freshness: { ...sla.freshness, target },
                        })
                      }
                      placeholder="PT4H"
                    />
                  </FormField>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <FormField label="Completeness Target (%)" hint="e.g., 99.5">
                    <Input
                      value={sla.completeness?.target_percent?.toString() || ''}
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

                  <FormField label="Error Rate Target" hint="e.g., 0.001 (0.1%)">
                    <Input
                      value={sla.accuracy?.error_rate_target?.toString() || ''}
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
                <FormField label="Default Access Level">
                  <Select
                    value={access.default_level}
                    onChange={(default_level) => setAccess({ ...access, default_level })}
                    options={[
                      { value: 'read', label: 'Read' },
                      { value: 'write', label: 'Write' },
                      { value: 'admin', label: 'Admin' },
                    ]}
                  />
                </FormField>

                <FormField label="Approval Required">
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={access.approval?.required || false}
                      onChange={(e) =>
                        setAccess({
                          ...access,
                          approval: { ...access.approval, required: e.target.checked },
                        })
                      }
                      className="rounded"
                    />
                    <span className="text-sm text-slate-600">Require approval for access requests</span>
                  </label>
                </FormField>
              </div>
            )}
          </div>
        </div>

        {/* YAML Preview Sidebar (1/3) */}
        <div className="space-y-4">
          {showYaml && (
            <div className="bg-white rounded-lg border border-slate-200 overflow-hidden sticky top-4">
              <div className="px-4 py-3 border-b border-slate-200 flex items-center justify-between">
                <span className="font-medium text-slate-800">YAML Preview</span>
                <button
                  onClick={() => navigator.clipboard.writeText(generateYaml())}
                  className="text-sm text-indigo-600 hover:text-indigo-700"
                >
                  Copy
                </button>
              </div>
              <pre className="p-4 text-xs font-mono text-slate-700 overflow-auto max-h-[600px] bg-slate-50">
                {generateYaml()}
              </pre>
            </div>
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
