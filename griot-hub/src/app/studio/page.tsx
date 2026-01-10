'use client';

import { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import type { Contract, FieldDefinition, FieldType } from '@/lib/types';
import api from '@/lib/api';

/**
 * Contract Studio (Editor) Page
 *
 * Features:
 * - Create new contract
 * - Edit existing contract
 * - Add/remove/edit fields
 * - Visual constraint editor
 * - YAML preview
 * - Validation preview (dry run)
 * - Save draft / publish
 */

const FIELD_TYPES: FieldType[] = [
  'string',
  'integer',
  'float',
  'boolean',
  'date',
  'datetime',
  'array',
  'object',
];

function createEmptyField(): FieldDefinition {
  return {
    name: '',
    type: 'string',
    description: '',
    nullable: false,
    primary_key: false,
    unique: false,
    constraints: {},
  };
}

export default function StudioPage() {
  const searchParams = useSearchParams();
  const editId = searchParams.get('edit');

  const [contractId, setContractId] = useState('');
  const [contractName, setContractName] = useState('');
  const [description, setDescription] = useState('');
  const [owner, setOwner] = useState('');
  const [fields, setFields] = useState<FieldDefinition[]>([createEmptyField()]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    async function loadContract() {
      if (!editId) return;

      try {
        setLoading(true);
        const contract = await api.getContract(editId);
        setContractId(contract.id);
        setContractName(contract.name);
        setDescription(contract.description || '');
        setOwner(contract.owner || '');
        setFields(contract.fields.length > 0 ? contract.fields : [createEmptyField()]);
      } catch (err) {
        setError('Failed to load contract for editing');
      } finally {
        setLoading(false);
      }
    }

    loadContract();
  }, [editId]);

  const addField = () => {
    setFields([...fields, createEmptyField()]);
  };

  const removeField = (index: number) => {
    if (fields.length > 1) {
      setFields(fields.filter((_, i) => i !== index));
    }
  };

  const updateField = (index: number, updates: Partial<FieldDefinition>) => {
    setFields(
      fields.map((field, i) => (i === index ? { ...field, ...updates } : field))
    );
  };

  const handleSave = async (publish: boolean = false) => {
    setError(null);
    setSuccess(null);

    // Validation
    if (!contractId.trim()) {
      setError('Contract ID is required');
      return;
    }
    if (!contractName.trim()) {
      setError('Contract name is required');
      return;
    }
    const validFields = fields.filter((f) => f.name.trim() && f.description.trim());
    if (validFields.length === 0) {
      setError('At least one field with name and description is required');
      return;
    }

    try {
      setSaving(true);

      const contractData = {
        id: contractId,
        name: contractName,
        description: description || undefined,
        owner: owner || undefined,
        fields: validFields,
      };

      if (editId) {
        await api.updateContract(editId, {
          name: contractName,
          description: description || undefined,
          fields: validFields,
          change_type: 'minor',
        });
        setSuccess('Contract updated successfully');
      } else {
        await api.createContract(contractData);
        setSuccess('Contract created successfully');
      }
    } catch (err) {
      setError('Failed to save contract. Registry API may be unavailable.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="text-gray-500 text-center py-16">Loading contract...</div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">
          {editId ? 'Edit Contract' : 'New Contract'}
        </h1>
        <div className="flex gap-3">
          <button
            onClick={() => handleSave(false)}
            disabled={saving}
            className="btn btn-secondary"
          >
            {saving ? 'Saving...' : 'Save Draft'}
          </button>
          <button
            onClick={() => handleSave(true)}
            disabled={saving}
            className="btn btn-primary"
          >
            {saving ? 'Publishing...' : 'Publish'}
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-error-50 border border-error-500 text-error-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {success && (
        <div className="bg-success-50 border border-success-500 text-success-700 px-4 py-3 rounded">
          {success}
        </div>
      )}

      {/* Contract Metadata */}
      <div className="card space-y-4">
        <h2 className="text-lg font-semibold text-gray-800">Contract Details</h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Contract ID *
            </label>
            <input
              type="text"
              value={contractId}
              onChange={(e) => setContractId(e.target.value.toLowerCase().replace(/\s+/g, '-'))}
              placeholder="my-contract"
              disabled={!!editId}
              className="input w-full"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Contract Name *
            </label>
            <input
              type="text"
              value={contractName}
              onChange={(e) => setContractName(e.target.value)}
              placeholder="My Contract"
              className="input w-full"
            />
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Description
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Describe what this contract defines..."
            rows={2}
            className="input w-full"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Owner
          </label>
          <input
            type="text"
            value={owner}
            onChange={(e) => setOwner(e.target.value)}
            placeholder="team-name or email"
            className="input w-full"
          />
        </div>
      </div>

      {/* Fields */}
      <div className="card space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-800">Fields</h2>
          <button onClick={addField} className="btn btn-secondary text-sm">
            + Add Field
          </button>
        </div>

        <div className="space-y-4">
          {fields.map((field, index) => (
            <div key={index} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-start justify-between mb-4">
                <span className="text-sm font-medium text-gray-500">
                  Field {index + 1}
                </span>
                {fields.length > 1 && (
                  <button
                    onClick={() => removeField(index)}
                    className="text-error-500 hover:text-error-700 text-sm"
                  >
                    Remove
                  </button>
                )}
              </div>

              <div className="grid grid-cols-3 gap-4 mb-4">
                <div>
                  <label className="block text-sm text-gray-600 mb-1">Name *</label>
                  <input
                    type="text"
                    value={field.name}
                    onChange={(e) =>
                      updateField(index, {
                        name: e.target.value.toLowerCase().replace(/\s+/g, '_'),
                      })
                    }
                    placeholder="field_name"
                    className="input w-full text-sm"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-600 mb-1">Type *</label>
                  <select
                    value={field.type}
                    onChange={(e) =>
                      updateField(index, { type: e.target.value as FieldType })
                    }
                    className="input w-full text-sm"
                  >
                    {FIELD_TYPES.map((type) => (
                      <option key={type} value={type}>
                        {type}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="flex items-end gap-4">
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={field.nullable || false}
                      onChange={(e) => updateField(index, { nullable: e.target.checked })}
                    />
                    <span className="text-sm text-gray-600">Nullable</span>
                  </label>
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={field.primary_key || false}
                      onChange={(e) =>
                        updateField(index, { primary_key: e.target.checked })
                      }
                    />
                    <span className="text-sm text-gray-600">PK</span>
                  </label>
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={field.unique || false}
                      onChange={(e) => updateField(index, { unique: e.target.checked })}
                    />
                    <span className="text-sm text-gray-600">Unique</span>
                  </label>
                </div>
              </div>

              <div>
                <label className="block text-sm text-gray-600 mb-1">
                  Description *
                </label>
                <input
                  type="text"
                  value={field.description}
                  onChange={(e) => updateField(index, { description: e.target.value })}
                  placeholder="Describe this field..."
                  className="input w-full text-sm"
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* YAML Preview (placeholder) */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">YAML Preview</h2>
        <pre className="bg-gray-50 p-4 rounded text-sm overflow-x-auto text-gray-700">
          {`# Contract: ${contractName || 'Untitled'}
id: ${contractId || 'my-contract'}
name: "${contractName || 'Untitled'}"
${description ? `description: "${description}"` : ''}
${owner ? `owner: "${owner}"` : ''}
fields:
${fields
  .filter((f) => f.name)
  .map(
    (f) => `  - name: ${f.name}
    type: ${f.type}
    description: "${f.description}"
    nullable: ${f.nullable || false}${f.primary_key ? '\n    primary_key: true' : ''}${f.unique ? '\n    unique: true' : ''}`
  )
  .join('\n')}`}
        </pre>
      </div>
    </div>
  );
}
