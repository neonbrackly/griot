import type { Contract } from '@/lib/types';

/**
 * ContractCard Component
 *
 * Displays a contract summary in card format.
 *
 * Shows:
 * - Contract name
 * - Description (truncated)
 * - Version
 * - Status badge
 * - Field count
 * - Last updated
 */
interface ContractCardProps {
  contract: Contract;
  onClick?: () => void;
}

export function ContractCard({ contract, onClick }: ContractCardProps) {
  const statusColors = {
    active: 'bg-success-50 text-success-700',
    draft: 'bg-gray-100 text-gray-600',
    deprecated: 'bg-warning-50 text-warning-700',
  };

  return (
    <div
      onClick={onClick}
      className={`card hover:shadow-md transition-shadow ${
        onClick ? 'cursor-pointer' : ''
      }`}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="font-semibold text-gray-900 truncate">{contract.name}</h3>
            <span
              className={`px-2 py-0.5 rounded text-xs font-medium ${
                statusColors[contract.status]
              }`}
            >
              {contract.status}
            </span>
          </div>

          {contract.description && (
            <p className="text-sm text-gray-600 mt-1 line-clamp-2">
              {contract.description}
            </p>
          )}

          <div className="flex items-center gap-4 mt-3 text-xs text-gray-400">
            <span>{(contract.schema || []).reduce((count, s) => count + (s.properties?.length || 0), 0)} fields</span>
            <span>v{contract.version}</span>
            {contract.updated_at && (
              <span>
                Updated {new Date(contract.updated_at).toLocaleDateString()}
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default ContractCard;
