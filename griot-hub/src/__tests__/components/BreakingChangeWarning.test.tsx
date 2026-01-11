/**
 * Tests for BreakingChangeWarning Component (T-392)
 *
 * Tests the breaking change warning modal that displays when
 * a contract update contains breaking changes.
 */
import { render, screen, fireEvent } from '@testing-library/react';
import BreakingChangeWarning, { BreakingChangeBadge } from '@/components/BreakingChangeWarning';
import type { BreakingChangeInfo } from '@/lib/types';

// =============================================================================
// TEST DATA
// =============================================================================

const singleBreakingChange: BreakingChangeInfo[] = [
  {
    change_type: 'field_removed',
    field: 'customer_name',
    description: 'Field "customer_name" was removed',
    migration_hint: 'Use "full_name" field instead',
  },
];

const multipleBreakingChanges: BreakingChangeInfo[] = [
  {
    change_type: 'field_removed',
    field: 'customer_name',
    description: 'Field "customer_name" was removed',
  },
  {
    change_type: 'type_changed_incompatible',
    field: 'age',
    description: 'Type changed from string to integer',
    from_value: 'string',
    to_value: 'integer',
  },
  {
    change_type: 'required_field_added',
    field: 'email',
    description: 'New required field "email" was added',
  },
  {
    change_type: 'enum_value_removed',
    field: 'status',
    description: 'Enum value "pending" was removed',
    from_value: ['active', 'inactive', 'pending'],
    to_value: ['active', 'inactive'],
  },
  {
    change_type: 'constraint_tightened',
    field: 'description',
    description: 'max_length reduced from 500 to 255',
    from_value: 500,
    to_value: 255,
    migration_hint: 'Truncate descriptions longer than 255 characters',
  },
];

// =============================================================================
// BREAKING CHANGE WARNING TESTS
// =============================================================================

describe('BreakingChangeWarning', () => {
  const mockOnProceed = jest.fn();
  const mockOnCancel = jest.fn();

  beforeEach(() => {
    mockOnProceed.mockClear();
    mockOnCancel.mockClear();
  });

  describe('Rendering', () => {
    it('renders nothing when no breaking changes', () => {
      const { container } = render(
        <BreakingChangeWarning
          changes={[]}
          onProceed={mockOnProceed}
          onCancel={mockOnCancel}
        />
      );

      expect(container.firstChild).toBeNull();
    });

    it('renders warning header for single breaking change', () => {
      render(
        <BreakingChangeWarning
          changes={singleBreakingChange}
          onProceed={mockOnProceed}
          onCancel={mockOnCancel}
        />
      );

      expect(screen.getByText('Breaking Changes Detected')).toBeInTheDocument();
      expect(
        screen.getByText(/This update contains 1 breaking change/)
      ).toBeInTheDocument();
    });

    it('renders warning header for multiple breaking changes', () => {
      render(
        <BreakingChangeWarning
          changes={multipleBreakingChanges}
          onProceed={mockOnProceed}
          onCancel={mockOnCancel}
        />
      );

      expect(screen.getByText('Breaking Changes Detected')).toBeInTheDocument();
      expect(
        screen.getByText(/This update contains 5 breaking changes/)
      ).toBeInTheDocument();
    });

    it('displays all breaking change items', () => {
      render(
        <BreakingChangeWarning
          changes={multipleBreakingChanges}
          onProceed={mockOnProceed}
          onCancel={mockOnCancel}
        />
      );

      // Check all fields are displayed
      expect(screen.getByText('customer_name')).toBeInTheDocument();
      expect(screen.getByText('age')).toBeInTheDocument();
      expect(screen.getByText('email')).toBeInTheDocument();
      expect(screen.getByText('status')).toBeInTheDocument();
      expect(screen.getByText('description')).toBeInTheDocument();

      // Check descriptions
      expect(screen.getByText('Field "customer_name" was removed')).toBeInTheDocument();
      expect(screen.getByText('Type changed from string to integer')).toBeInTheDocument();
    });

    it('displays migration hints when available', () => {
      render(
        <BreakingChangeWarning
          changes={multipleBreakingChanges}
          onProceed={mockOnProceed}
          onCancel={mockOnCancel}
        />
      );

      expect(
        screen.getByText('Truncate descriptions longer than 255 characters')
      ).toBeInTheDocument();
    });

    it('displays from/to values for changes', () => {
      render(
        <BreakingChangeWarning
          changes={multipleBreakingChanges}
          onProceed={mockOnProceed}
          onCancel={mockOnCancel}
        />
      );

      // Type change from/to
      expect(screen.getByText(/From:.*"string"/)).toBeInTheDocument();
      expect(screen.getByText(/To:.*"integer"/)).toBeInTheDocument();
    });

    it('formats change types correctly', () => {
      render(
        <BreakingChangeWarning
          changes={multipleBreakingChanges}
          onProceed={mockOnProceed}
          onCancel={mockOnCancel}
        />
      );

      expect(screen.getByText('Field Removed')).toBeInTheDocument();
      expect(screen.getByText('Type Changed')).toBeInTheDocument();
      expect(screen.getByText('Required Field Added')).toBeInTheDocument();
      expect(screen.getByText('Enum Value Removed')).toBeInTheDocument();
      expect(screen.getByText('Constraint Tightened')).toBeInTheDocument();
    });
  });

  describe('Actions', () => {
    it('calls onCancel when Cancel button is clicked', () => {
      render(
        <BreakingChangeWarning
          changes={singleBreakingChange}
          onProceed={mockOnProceed}
          onCancel={mockOnCancel}
        />
      );

      fireEvent.click(screen.getByText('Cancel'));

      expect(mockOnCancel).toHaveBeenCalledTimes(1);
      expect(mockOnProceed).not.toHaveBeenCalled();
    });

    it('calls onProceed when Proceed button is clicked', () => {
      render(
        <BreakingChangeWarning
          changes={singleBreakingChange}
          onProceed={mockOnProceed}
          onCancel={mockOnCancel}
        />
      );

      fireEvent.click(screen.getByText('Proceed with Breaking Changes'));

      expect(mockOnProceed).toHaveBeenCalledTimes(1);
      expect(mockOnCancel).not.toHaveBeenCalled();
    });

    it('disables buttons when loading', () => {
      render(
        <BreakingChangeWarning
          changes={singleBreakingChange}
          onProceed={mockOnProceed}
          onCancel={mockOnCancel}
          loading={true}
        />
      );

      const cancelButton = screen.getByText('Cancel');
      const proceedButton = screen.getByText('Proceed with Breaking Changes');

      expect(cancelButton).toBeDisabled();
      expect(proceedButton).toBeDisabled();
    });

    it('shows loading spinner when loading', () => {
      const { container } = render(
        <BreakingChangeWarning
          changes={singleBreakingChange}
          onProceed={mockOnProceed}
          onCancel={mockOnCancel}
          loading={true}
        />
      );

      // Check for spinner SVG with animate-spin class
      const spinner = container.querySelector('.animate-spin');
      expect(spinner).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('has proper warning styling', () => {
      const { container } = render(
        <BreakingChangeWarning
          changes={singleBreakingChange}
          onProceed={mockOnProceed}
          onCancel={mockOnCancel}
        />
      );

      // Check for red/warning themed container
      const warningContainer = container.querySelector('.bg-red-50');
      expect(warningContainer).toBeInTheDocument();
    });

    it('contains clickable buttons', () => {
      render(
        <BreakingChangeWarning
          changes={singleBreakingChange}
          onProceed={mockOnProceed}
          onCancel={mockOnCancel}
        />
      );

      const cancelButton = screen.getByRole('button', { name: 'Cancel' });
      const proceedButton = screen.getByRole('button', {
        name: /Proceed with Breaking Changes/,
      });

      expect(cancelButton).toBeInTheDocument();
      expect(proceedButton).toBeInTheDocument();
    });
  });
});

// =============================================================================
// BREAKING CHANGE BADGE TESTS
// =============================================================================

describe('BreakingChangeBadge', () => {
  it('renders nothing when count is 0', () => {
    const { container } = render(<BreakingChangeBadge count={0} />);
    expect(container.firstChild).toBeNull();
  });

  it('renders badge with count for single breaking change', () => {
    render(<BreakingChangeBadge count={1} />);
    expect(screen.getByText('1 breaking')).toBeInTheDocument();
  });

  it('renders badge with count for multiple breaking changes', () => {
    render(<BreakingChangeBadge count={5} />);
    expect(screen.getByText('5 breaking')).toBeInTheDocument();
  });

  it('has proper styling', () => {
    const { container } = render(<BreakingChangeBadge count={3} />);

    const badge = container.querySelector('span');
    expect(badge).toHaveClass('bg-red-50');
    expect(badge).toHaveClass('text-red-700');
  });
});
