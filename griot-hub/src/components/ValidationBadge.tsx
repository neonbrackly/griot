/**
 * ValidationBadge Component
 *
 * Badge showing validation status.
 */
interface ValidationBadgeProps {
  passed: boolean;
  errorRate?: number;
  size?: 'sm' | 'md' | 'lg';
}

export function ValidationBadge({
  passed,
  errorRate,
  size = 'md',
}: ValidationBadgeProps) {
  const sizeClasses = {
    sm: 'px-1.5 py-0.5 text-xs',
    md: 'px-2 py-1 text-sm',
    lg: 'px-3 py-1.5 text-base',
  };

  const statusClasses = passed
    ? 'bg-success-50 text-success-700'
    : 'bg-error-50 text-error-700';

  return (
    <span
      className={`inline-flex items-center gap-1 rounded font-medium ${sizeClasses[size]} ${statusClasses}`}
    >
      <span
        className={`inline-block rounded-full ${
          size === 'sm' ? 'w-1.5 h-1.5' : size === 'md' ? 'w-2 h-2' : 'w-2.5 h-2.5'
        } ${passed ? 'bg-success-500' : 'bg-error-500'}`}
      />
      <span>{passed ? 'Passed' : 'Failed'}</span>
      {errorRate !== undefined && !passed && (
        <span className="text-error-500">({(errorRate * 100).toFixed(1)}%)</span>
      )}
    </span>
  );
}

export default ValidationBadge;
