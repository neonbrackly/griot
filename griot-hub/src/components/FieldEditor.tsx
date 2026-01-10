'use client';

import type { FieldDefinition, FieldType } from '@/lib/types';

/**
 * FieldEditor Component
 *
 * Form for editing field definition.
 *
 * Features:
 * - Field name input
 * - Type selector
 * - Description textarea
 * - Constraint editors (contextual by type)
 * - Metadata editors (unit, aggregation)
 */
interface FieldEditorProps {
  field: FieldDefinition;
  onChange: (field: FieldDefinition) => void;
  onDelete: () => void;
}

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

export function FieldEditor({ field, onChange, onDelete }: FieldEditorProps) {
  const updateField = (updates: Partial<FieldDefinition>) => {
    onChange({ ...field, ...updates });
  };

  return (
    <div className="border border-gray-200 rounded-lg p-4 space-y-4">
      <div className="flex items-center justify-between">
        <span className="font-mono text-sm text-gray-600">
          {field.name || 'New Field'}
        </span>
        <button
          onClick={onDelete}
          className="text-error-500 hover:text-error-700 text-sm"
        >
          Remove
        </button>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Field Name
          </label>
          <input
            type="text"
            value={field.name}
            onChange={(e) =>
              updateField({
                name: e.target.value.toLowerCase().replace(/\s+/g, '_'),
              })
            }
            placeholder="field_name"
            className="input w-full"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Type
          </label>
          <select
            value={field.type}
            onChange={(e) => updateField({ type: e.target.value as FieldType })}
            className="input w-full"
          >
            {FIELD_TYPES.map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Description
        </label>
        <textarea
          value={field.description}
          onChange={(e) => updateField({ description: e.target.value })}
          placeholder="Describe what this field represents..."
          rows={2}
          className="input w-full"
        />
      </div>

      <div className="flex flex-wrap gap-4">
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={field.nullable || false}
            onChange={(e) => updateField({ nullable: e.target.checked })}
            className="text-primary-600"
          />
          <span className="text-sm text-gray-700">Nullable</span>
        </label>

        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={field.primary_key || false}
            onChange={(e) => updateField({ primary_key: e.target.checked })}
            className="text-primary-600"
          />
          <span className="text-sm text-gray-700">Primary Key</span>
        </label>

        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={field.unique || false}
            onChange={(e) => updateField({ unique: e.target.checked })}
            className="text-primary-600"
          />
          <span className="text-sm text-gray-700">Unique</span>
        </label>
      </div>

      {/* Constraints section - contextual based on field type */}
      {(field.type === 'string' || field.type === 'integer' || field.type === 'float') && (
        <div className="border-t border-gray-100 pt-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Constraints
          </label>
          <div className="grid grid-cols-2 gap-4 text-sm">
            {field.type === 'string' && (
              <>
                <div>
                  <label className="block text-gray-600 mb-1">Min Length</label>
                  <input
                    type="number"
                    value={field.constraints?.min_length || ''}
                    onChange={(e) =>
                      updateField({
                        constraints: {
                          ...field.constraints,
                          min_length: e.target.value
                            ? parseInt(e.target.value)
                            : undefined,
                        },
                      })
                    }
                    placeholder="0"
                    className="input w-full"
                  />
                </div>
                <div>
                  <label className="block text-gray-600 mb-1">Max Length</label>
                  <input
                    type="number"
                    value={field.constraints?.max_length || ''}
                    onChange={(e) =>
                      updateField({
                        constraints: {
                          ...field.constraints,
                          max_length: e.target.value
                            ? parseInt(e.target.value)
                            : undefined,
                        },
                      })
                    }
                    placeholder="255"
                    className="input w-full"
                  />
                </div>
                <div className="col-span-2">
                  <label className="block text-gray-600 mb-1">Pattern (Regex)</label>
                  <input
                    type="text"
                    value={field.constraints?.pattern || ''}
                    onChange={(e) =>
                      updateField({
                        constraints: {
                          ...field.constraints,
                          pattern: e.target.value || undefined,
                        },
                      })
                    }
                    placeholder="^[a-z]+$"
                    className="input w-full font-mono"
                  />
                </div>
              </>
            )}
            {(field.type === 'integer' || field.type === 'float') && (
              <>
                <div>
                  <label className="block text-gray-600 mb-1">Min (ge)</label>
                  <input
                    type="number"
                    value={field.constraints?.ge ?? ''}
                    onChange={(e) =>
                      updateField({
                        constraints: {
                          ...field.constraints,
                          ge: e.target.value ? parseFloat(e.target.value) : undefined,
                        },
                      })
                    }
                    placeholder="0"
                    className="input w-full"
                  />
                </div>
                <div>
                  <label className="block text-gray-600 mb-1">Max (le)</label>
                  <input
                    type="number"
                    value={field.constraints?.le ?? ''}
                    onChange={(e) =>
                      updateField({
                        constraints: {
                          ...field.constraints,
                          le: e.target.value ? parseFloat(e.target.value) : undefined,
                        },
                      })
                    }
                    placeholder="100"
                    className="input w-full"
                  />
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default FieldEditor;
