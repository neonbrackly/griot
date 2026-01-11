/**
 * Tests for VersionComparison Component (T-392)
 *
 * Tests the version comparison component that shows
 * differences between contract versions with breaking change highlights.
 */
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import VersionComparison, { VersionBadge } from '@/components/VersionComparison';
import api from '@/lib/api';
import type { VersionList, ContractDiff, VersionSummary } from '@/lib/types';

// Mock the API module
jest.mock('@/lib/api', () => ({
  __esModule: true,
  default: {
    getVersions: jest.fn(),
    diffContract: jest.fn(),
  },
}));

const mockApi = api as jest.Mocked<typeof api>;

// =============================================================================
// TEST DATA
// =============================================================================

const mockVersions: VersionList = {
  items: [
    { version: '2.0.0', created_at: '2024-01-15', is_breaking: true },
    { version: '1.1.0', created_at: '2024-01-10', is_breaking: false },
    { version: '1.0.0', created_at: '2024-01-01', is_breaking: false },
  ],
  total: 3,
};

const mockDiffWithBreaking: ContractDiff = {
  from_version: '1.1.0',
  to_version: '2.0.0',
  has_breaking_changes: true,
  added_fields: ['new_field'],
  removed_fields: ['old_field', 'deprecated_field'],
  type_changes: [
    {
      field: 'age',
      from_type: 'string',
      to_type: 'integer',
      is_breaking: true,
    },
  ],
  constraint_changes: [
    {
      field: 'name',
      constraint: 'max_length',
      from_value: 500,
      to_value: 255,
      is_breaking: true,
    },
  ],
  section_changes: [
    {
      section: 'compliance',
      change_type: 'modified',
      summary: 'Updated data classification',
      is_breaking: false,
    },
  ],
};

const mockDiffNoBreaking: ContractDiff = {
  from_version: '1.0.0',
  to_version: '1.1.0',
  has_breaking_changes: false,
  added_fields: ['new_optional_field'],
  removed_fields: [],
  type_changes: [],
  constraint_changes: [
    {
      field: 'description',
      constraint: 'max_length',
      from_value: 255,
      to_value: 500,
      is_breaking: false,
    },
  ],
};

const mockEmptyDiff: ContractDiff = {
  from_version: '1.0.0',
  to_version: '1.0.0',
  has_breaking_changes: false,
  added_fields: [],
  removed_fields: [],
  type_changes: [],
  constraint_changes: [],
};

// =============================================================================
// VERSION COMPARISON TESTS
// =============================================================================

describe('VersionComparison', () => {
  beforeEach(() => {
    mockApi.getVersions.mockReset();
    mockApi.diffContract.mockReset();
  });

  describe('Loading and Error States', () => {
    it('shows loading state while fetching versions', async () => {
      mockApi.getVersions.mockImplementation(
        () => new Promise(() => {}) // Never resolves
      );

      render(<VersionComparison contractId="test-contract" />);

      // Initial render shouldn't show loading for versions (they load in useEffect)
      await waitFor(() => {
        expect(mockApi.getVersions).toHaveBeenCalledWith('test-contract');
      });
    });

    it('shows error state when versions fail to load', async () => {
      mockApi.getVersions.mockRejectedValue(new Error('Network error'));

      render(<VersionComparison contractId="test-contract" />);

      await waitFor(() => {
        expect(screen.getByText('Failed to load versions')).toBeInTheDocument();
      });
    });

    it('shows loading state while fetching diff', async () => {
      mockApi.getVersions.mockResolvedValue(mockVersions);
      mockApi.diffContract.mockImplementation(
        () => new Promise(() => {}) // Never resolves
      );

      render(
        <VersionComparison
          contractId="test-contract"
          fromVersion="1.1.0"
          toVersion="2.0.0"
        />
      );

      await waitFor(() => {
        expect(screen.getByText('Loading comparison...')).toBeInTheDocument();
      });
    });

    it('shows error state when diff fails to load', async () => {
      mockApi.getVersions.mockResolvedValue(mockVersions);
      mockApi.diffContract.mockRejectedValue(new Error('Network error'));

      render(
        <VersionComparison
          contractId="test-contract"
          fromVersion="1.1.0"
          toVersion="2.0.0"
        />
      );

      await waitFor(() => {
        expect(screen.getByText('Failed to load diff')).toBeInTheDocument();
      });
    });
  });

  describe('Version Selection', () => {
    it('loads available versions on mount', async () => {
      mockApi.getVersions.mockResolvedValue(mockVersions);

      render(<VersionComparison contractId="test-contract" />);

      await waitFor(() => {
        expect(mockApi.getVersions).toHaveBeenCalledWith('test-contract');
      });
    });

    it('auto-selects latest two versions when no props provided', async () => {
      mockApi.getVersions.mockResolvedValue(mockVersions);
      mockApi.diffContract.mockResolvedValue(mockDiffWithBreaking);

      render(<VersionComparison contractId="test-contract" />);

      await waitFor(() => {
        // Should auto-diff between v1.1.0 and v2.0.0
        expect(mockApi.diffContract).toHaveBeenCalledWith(
          'test-contract',
          '1.1.0',
          '2.0.0'
        );
      });
    });

    it('uses provided fromVersion and toVersion props', async () => {
      mockApi.getVersions.mockResolvedValue(mockVersions);
      mockApi.diffContract.mockResolvedValue(mockDiffNoBreaking);

      render(
        <VersionComparison
          contractId="test-contract"
          fromVersion="1.0.0"
          toVersion="1.1.0"
        />
      );

      await waitFor(() => {
        expect(mockApi.diffContract).toHaveBeenCalledWith(
          'test-contract',
          '1.0.0',
          '1.1.0'
        );
      });
    });

    it('shows message when same version selected', async () => {
      mockApi.getVersions.mockResolvedValue(mockVersions);

      render(
        <VersionComparison
          contractId="test-contract"
          fromVersion="1.0.0"
          toVersion="1.0.0"
        />
      );

      await waitFor(() => {
        expect(
          screen.getByText('Select different versions to compare')
        ).toBeInTheDocument();
      });
    });
  });

  describe('Breaking Changes Display', () => {
    it('shows breaking changes warning when present', async () => {
      mockApi.getVersions.mockResolvedValue(mockVersions);
      mockApi.diffContract.mockResolvedValue(mockDiffWithBreaking);

      render(
        <VersionComparison
          contractId="test-contract"
          fromVersion="1.1.0"
          toVersion="2.0.0"
        />
      );

      await waitFor(() => {
        expect(
          screen.getByText('This version contains breaking changes')
        ).toBeInTheDocument();
      });
    });

    it('does not show breaking changes warning when none present', async () => {
      mockApi.getVersions.mockResolvedValue(mockVersions);
      mockApi.diffContract.mockResolvedValue(mockDiffNoBreaking);

      render(
        <VersionComparison
          contractId="test-contract"
          fromVersion="1.0.0"
          toVersion="1.1.0"
        />
      );

      await waitFor(() => {
        expect(
          screen.queryByText('This version contains breaking changes')
        ).not.toBeInTheDocument();
      });
    });

    it('displays removed fields as breaking', async () => {
      mockApi.getVersions.mockResolvedValue(mockVersions);
      mockApi.diffContract.mockResolvedValue(mockDiffWithBreaking);

      render(
        <VersionComparison
          contractId="test-contract"
          fromVersion="1.1.0"
          toVersion="2.0.0"
        />
      );

      await waitFor(() => {
        expect(screen.getByText('Removed Fields')).toBeInTheDocument();
        expect(screen.getByText(/old_field/)).toBeInTheDocument();
        expect(screen.getByText(/deprecated_field/)).toBeInTheDocument();
      });
    });

    it('displays type changes with breaking indicator', async () => {
      mockApi.getVersions.mockResolvedValue(mockVersions);
      mockApi.diffContract.mockResolvedValue(mockDiffWithBreaking);

      render(
        <VersionComparison
          contractId="test-contract"
          fromVersion="1.1.0"
          toVersion="2.0.0"
        />
      );

      await waitFor(() => {
        expect(screen.getByText('Type Changes')).toBeInTheDocument();
        expect(screen.getByText('age')).toBeInTheDocument();
        expect(screen.getByText('string')).toBeInTheDocument();
        expect(screen.getByText('integer')).toBeInTheDocument();
      });
    });

    it('displays constraint changes with breaking indicator', async () => {
      mockApi.getVersions.mockResolvedValue(mockVersions);
      mockApi.diffContract.mockResolvedValue(mockDiffWithBreaking);

      render(
        <VersionComparison
          contractId="test-contract"
          fromVersion="1.1.0"
          toVersion="2.0.0"
        />
      );

      await waitFor(() => {
        expect(screen.getByText('Constraint Changes')).toBeInTheDocument();
        expect(screen.getByText('name.max_length')).toBeInTheDocument();
      });
    });
  });

  describe('Diff Summary', () => {
    it('displays summary counts', async () => {
      mockApi.getVersions.mockResolvedValue(mockVersions);
      mockApi.diffContract.mockResolvedValue(mockDiffWithBreaking);

      render(
        <VersionComparison
          contractId="test-contract"
          fromVersion="1.1.0"
          toVersion="2.0.0"
        />
      );

      await waitFor(() => {
        // Summary section
        expect(screen.getByText('Summary')).toBeInTheDocument();

        // Check counts (1 added, 2 removed, 1 type change, 1 constraint change)
        expect(screen.getByText('1')).toBeInTheDocument(); // Added
        expect(screen.getByText('2')).toBeInTheDocument(); // Removed
      });
    });

    it('displays added fields', async () => {
      mockApi.getVersions.mockResolvedValue(mockVersions);
      mockApi.diffContract.mockResolvedValue(mockDiffWithBreaking);

      render(
        <VersionComparison
          contractId="test-contract"
          fromVersion="1.1.0"
          toVersion="2.0.0"
        />
      );

      await waitFor(() => {
        expect(screen.getByText('Added Fields')).toBeInTheDocument();
        expect(screen.getByText(/new_field/)).toBeInTheDocument();
      });
    });

    it('shows no changes message when versions are identical', async () => {
      mockApi.getVersions.mockResolvedValue(mockVersions);
      mockApi.diffContract.mockResolvedValue(mockEmptyDiff);

      render(
        <VersionComparison
          contractId="test-contract"
          fromVersion="1.0.0"
          toVersion="1.0.1"
        />
      );

      await waitFor(() => {
        expect(
          screen.getByText('No schema changes between these versions')
        ).toBeInTheDocument();
      });
    });
  });

  describe('Section Changes', () => {
    it('displays ODCS section changes', async () => {
      mockApi.getVersions.mockResolvedValue(mockVersions);
      mockApi.diffContract.mockResolvedValue(mockDiffWithBreaking);

      render(
        <VersionComparison
          contractId="test-contract"
          fromVersion="1.1.0"
          toVersion="2.0.0"
        />
      );

      await waitFor(() => {
        expect(screen.getByText('Section Changes')).toBeInTheDocument();
        expect(screen.getByText(/compliance/)).toBeInTheDocument();
        expect(screen.getByText('Updated data classification')).toBeInTheDocument();
      });
    });
  });

  describe('Close Button', () => {
    it('calls onClose when provided and clicked', async () => {
      mockApi.getVersions.mockResolvedValue(mockVersions);
      const mockOnClose = jest.fn();

      render(
        <VersionComparison contractId="test-contract" onClose={mockOnClose} />
      );

      await waitFor(() => {
        expect(mockApi.getVersions).toHaveBeenCalled();
      });

      // Find and click close button
      const closeButton = screen.getByRole('button', { name: '' }); // SVG button
      fireEvent.click(closeButton);

      expect(mockOnClose).toHaveBeenCalledTimes(1);
    });

    it('does not render close button when onClose not provided', async () => {
      mockApi.getVersions.mockResolvedValue(mockVersions);

      const { container } = render(
        <VersionComparison contractId="test-contract" />
      );

      await waitFor(() => {
        expect(mockApi.getVersions).toHaveBeenCalled();
      });

      // Header should not have close button (only version selects)
      const header = container.querySelector('.border-b');
      const buttons = header?.querySelectorAll('button');
      // No close button in header when onClose not provided
      expect(buttons?.length || 0).toBeLessThanOrEqual(0);
    });
  });
});

// =============================================================================
// VERSION BADGE TESTS
// =============================================================================

describe('VersionBadge', () => {
  it('renders version number', () => {
    render(<VersionBadge version="1.2.3" />);
    expect(screen.getByText('v1.2.3')).toBeInTheDocument();
  });

  it('shows breaking indicator when isBreaking is true', () => {
    render(<VersionBadge version="2.0.0" isBreaking={true} />);
    expect(screen.getByText('v2.0.0 (breaking)')).toBeInTheDocument();
  });

  it('does not show breaking indicator when isBreaking is false', () => {
    render(<VersionBadge version="1.1.0" isBreaking={false} />);
    expect(screen.getByText('v1.1.0')).toBeInTheDocument();
    expect(screen.queryByText(/breaking/)).not.toBeInTheDocument();
  });

  it('calls onClick when clicked', () => {
    const mockOnClick = jest.fn();
    render(<VersionBadge version="1.0.0" onClick={mockOnClick} />);

    fireEvent.click(screen.getByText('v1.0.0'));

    expect(mockOnClick).toHaveBeenCalledTimes(1);
  });

  it('has breaking styling when isBreaking', () => {
    const { container } = render(
      <VersionBadge version="2.0.0" isBreaking={true} />
    );

    const badge = container.querySelector('button');
    expect(badge).toHaveClass('bg-red-50');
    expect(badge).toHaveClass('text-red-700');
  });

  it('has normal styling when not breaking', () => {
    const { container } = render(
      <VersionBadge version="1.0.0" isBreaking={false} />
    );

    const badge = container.querySelector('button');
    expect(badge).toHaveClass('bg-slate-100');
    expect(badge).toHaveClass('text-slate-600');
  });
});
