'use client';

import type { FieldConstraints, FieldFormat } from '@/lib/types';

/**
 * ConstraintEditor Component
 *
 * Dynamic constraint editor based on field type.
 * Shows relevant constraint inputs based on the selected field type.
 */
interface ConstraintEditorProps {
  fieldType: string;
  constraints: FieldConstraints;
  onChange: (constraints: FieldConstraints) => void;
}

const FORMAT_OPTIONS: FieldFormat[] = [
  'email',
  'uri',
  'uuid',
  'date',
  'datetime',
  'ipv4',
  'ipv6',
  'hostname',
];

export function ConstraintEditor({
  fieldType,
  constraints,
  onChange,
}: ConstraintEditorProps) {
  const updateConstraint = <K extends keyof FieldConstraints>(
    key: K,
    value: FieldConstraints[K]
  ) => {
    onChange({ ...constraints, [key]: value });
  };

  return (
    <div className="space-y-4">
      {/* String constraints */}
      {fieldType === 'string' && (
        <>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Min Length
              </label>
              <input
                type="number"
                value={constraints.min_length ?? ''}
                onChange={(e) =>
                  updateConstraint(
                    'min_length',
                    e.target.value ? parseInt(e.target.value) : undefined
                  )
                }
                min={0}
                className="input w-full"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Max Length
              </label>
              <input
                type="number"
                value={constraints.max_length ?? ''}
                onChange={(e) =>
                  updateConstraint(
                    'max_length',
                    e.target.value ? parseInt(e.target.value) : undefined
                  )
                }
                min={0}
                className="input w-full"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Pattern (Regex)
            </label>
            <input
              type="text"
              value={constraints.pattern ?? ''}
              onChange={(e) =>
                updateConstraint('pattern', e.target.value || undefined)
              }
              placeholder="^[a-zA-Z0-9]+$"
              className="input w-full font-mono"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Format
            </label>
            <select
              value={constraints.format ?? ''}
              onChange={(e) =>
                updateConstraint(
                  'format',
                  (e.target.value as FieldFormat) || undefined
                )
              }
              className="input w-full"
            >
              <option value="">None</option>
              {FORMAT_OPTIONS.map((format) => (
                <option key={format} value={format}>
                  {format}
                </option>
              ))}
            </select>
          </div>
        </>
      )}

      {/* Numeric constraints */}
      {(fieldType === 'integer' || fieldType === 'float') && (
        <>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Greater than or equal (ge)
              </label>
              <input
                type="number"
                value={constraints.ge ?? ''}
                onChange={(e) =>
                  updateConstraint(
                    'ge',
                    e.target.value ? parseFloat(e.target.value) : undefined
                  )
                }
                className="input w-full"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Less than or equal (le)
              </label>
              <input
                type="number"
                value={constraints.le ?? ''}
                onChange={(e) =>
                  updateConstraint(
                    'le',
                    e.target.value ? parseFloat(e.target.value) : undefined
                  )
                }
                className="input w-full"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Greater than (gt)
              </label>
              <input
                type="number"
                value={constraints.gt ?? ''}
                onChange={(e) =>
                  updateConstraint(
                    'gt',
                    e.target.value ? parseFloat(e.target.value) : undefined
                  )
                }
                className="input w-full"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Less than (lt)
              </label>
              <input
                type="number"
                value={constraints.lt ?? ''}
                onChange={(e) =>
                  updateConstraint(
                    'lt',
                    e.target.value ? parseFloat(e.target.value) : undefined
                  )
                }
                className="input w-full"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Multiple of
            </label>
            <input
              type="number"
              value={constraints.multiple_of ?? ''}
              onChange={(e) =>
                updateConstraint(
                  'multiple_of',
                  e.target.value ? parseFloat(e.target.value) : undefined
                )
              }
              className="input w-full"
            />
          </div>
        </>
      )}

      {/* Enum constraint (all types) */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Allowed Values (enum)
        </label>
        <input
          type="text"
          value={constraints.enum?.join(', ') ?? ''}
          onChange={(e) =>
            updateConstraint(
              'enum',
              e.target.value
                ? e.target.value.split(',').map((v) => v.trim())
                : undefined
            )
          }
          placeholder="value1, value2, value3"
          className="input w-full"
        />
        <p className="text-xs text-gray-500 mt-1">
          Comma-separated list of allowed values
        </p>
      </div>
    </div>
  );
}

export default ConstraintEditor;
