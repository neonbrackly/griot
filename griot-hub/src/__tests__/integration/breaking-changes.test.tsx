/**
 * Integration Tests for Breaking Change Flow (T-392)
 *
 * Tests the complete breaking change detection and handling flow
 * in the Contract Studio page, from update attempt through
 * warning display and resolution.
 */
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import StudioPage from '@/app/studio/page';
import api, { ApiClientError } from '@/lib/api';
import type { Contract, BreakingChangeInfo } from '@/lib/types';

// Mock the API module
jest.mock('@/lib/api', () => ({
  __esModule: true,
  default: {
    getContract: jest.fn(),
    createContract: jest.fn(),
    updateContract: jest.fn(),
  },
  ApiClientError: class MockApiClientError extends Error {
    code: string;
    status: number;
    breakingChanges?: BreakingChangeInfo[];

    constructor(
      code: string,
      message: string,
      status: number,
      breakingChanges?: BreakingChangeInfo[]
    ) {
      super(message);
      this.code = code;
      this.status = status;
      this.breakingChanges = breakingChanges;
      this.name = 'ApiClientError';
    }

    isBreakingChangeError() {
      return this.code === 'BREAKING_CHANGES_DETECTED' && this.status === 409;
    }
  },
}));

// Mock next/navigation
const mockPush = jest.fn();
const mockSearchParams = new URLSearchParams();

jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
    replace: jest.fn(),
    back: jest.fn(),
  }),
  useSearchParams: () => mockSearchParams,
}));

const mockApi = api as jest.Mocked<typeof api>;
const MockApiClientError = ApiClientError as jest.MockedClass<typeof ApiClientError>;

// =============================================================================
// TEST DATA
// =============================================================================

const existingContract: Contract = {
  id: 'customer-contract',
  name: 'Customer Contract',
  api_version: 'v1.0.0',
  kind: 'DataContract',
  version: '1.0.0',
  status: 'active',
  fields: [
    { name: 'customer_id', type: 'string', description: 'Customer ID' },
    { name: 'customer_name', type: 'string', description: 'Customer name' },
    { name: 'email', type: 'string', description: 'Email address' },
  ],
};

const breakingChanges: BreakingChangeInfo[] = [
  {
    change_type: 'field_removed',
    field: 'customer_name',
    description: 'Field "customer_name" was removed',
    migration_hint: 'Use "full_name" field instead',
  },
  {
    change_type: 'type_changed_incompatible',
    field: 'age',
    description: 'Type changed from string to integer',
    from_value: 'string',
    to_value: 'integer',
  },
];

// =============================================================================
// HELPER FUNCTIONS
// =============================================================================

function setupEditMode() {
  mockSearchParams.set('edit', 'customer-contract');
}

function clearEditMode() {
  mockSearchParams.delete('edit');
}

// =============================================================================
// INTEGRATION TESTS
// =============================================================================

describe('Contract Studio Breaking Change Flow', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    clearEditMode();
  });

  describe('New Contract Creation', () => {
    it('creates contract successfully without breaking changes', async () => {
      mockApi.createContract.mockResolvedValue({
        ...existingContract,
        id: 'new-contract',
        version: '1.0.0',
      });

      render(<StudioPage />);

      // Fill in required fields
      const idInput = screen.getByPlaceholderText('my-contract');
      const nameInput = screen.getByPlaceholderText('My Contract');

      await userEvent.type(idInput, 'new-contract');
      await userEvent.type(nameInput, 'New Contract');

      // Submit
      fireEvent.click(screen.getByText('Create Contract'));

      await waitFor(() => {
        expect(mockApi.createContract).toHaveBeenCalled();
      });

      // Should show success message
      await waitFor(() => {
        expect(screen.getByText('Contract created successfully')).toBeInTheDocument();
      });
    });

    it('shows validation error for missing required fields', async () => {
      render(<StudioPage />);

      // Try to submit without filling fields
      fireEvent.click(screen.getByText('Create Contract'));

      await waitFor(() => {
        expect(screen.getByText('Contract ID is required')).toBeInTheDocument();
      });

      expect(mockApi.createContract).not.toHaveBeenCalled();
    });
  });

  describe('Contract Update with Breaking Changes', () => {
    beforeEach(() => {
      setupEditMode();
      mockApi.getContract.mockResolvedValue(existingContract);
    });

    it('loads existing contract for editing', async () => {
      render(<StudioPage />);

      await waitFor(() => {
        expect(mockApi.getContract).toHaveBeenCalledWith('customer-contract');
      });

      // Contract data should be loaded
      await waitFor(() => {
        const nameInput = screen.getByPlaceholderText('My Contract');
        expect(nameInput).toHaveValue('Customer Contract');
      });
    });

    it('shows breaking change warning when update has breaking changes', async () => {
      const breakingError = new MockApiClientError(
        'BREAKING_CHANGES_DETECTED',
        'Breaking changes detected',
        409,
        breakingChanges
      );
      mockApi.updateContract.mockRejectedValue(breakingError);

      render(<StudioPage />);

      // Wait for contract to load
      await waitFor(() => {
        expect(mockApi.getContract).toHaveBeenCalled();
      });

      // Try to save changes
      fireEvent.click(screen.getByText('Save Changes'));

      // Should show breaking change warning
      await waitFor(() => {
        expect(screen.getByText('Breaking Changes Detected')).toBeInTheDocument();
      });

      // Should show details of breaking changes
      expect(screen.getByText('Field Removed')).toBeInTheDocument();
      expect(screen.getByText('customer_name')).toBeInTheDocument();
      expect(screen.getByText('Type Changed')).toBeInTheDocument();
    });

    it('shows migration hints in breaking change warning', async () => {
      const breakingError = new MockApiClientError(
        'BREAKING_CHANGES_DETECTED',
        'Breaking changes detected',
        409,
        breakingChanges
      );
      mockApi.updateContract.mockRejectedValue(breakingError);

      render(<StudioPage />);

      await waitFor(() => {
        expect(mockApi.getContract).toHaveBeenCalled();
      });

      fireEvent.click(screen.getByText('Save Changes'));

      await waitFor(() => {
        expect(
          screen.getByText('Use "full_name" field instead')
        ).toBeInTheDocument();
      });
    });

    it('cancels breaking change warning and returns to editing', async () => {
      const breakingError = new MockApiClientError(
        'BREAKING_CHANGES_DETECTED',
        'Breaking changes detected',
        409,
        breakingChanges
      );
      mockApi.updateContract.mockRejectedValue(breakingError);

      render(<StudioPage />);

      await waitFor(() => {
        expect(mockApi.getContract).toHaveBeenCalled();
      });

      fireEvent.click(screen.getByText('Save Changes'));

      await waitFor(() => {
        expect(screen.getByText('Breaking Changes Detected')).toBeInTheDocument();
      });

      // Click Cancel
      fireEvent.click(screen.getByText('Cancel'));

      // Warning should be dismissed
      await waitFor(() => {
        expect(
          screen.queryByText('Breaking Changes Detected')
        ).not.toBeInTheDocument();
      });

      // Should still be in edit mode
      expect(screen.getByText('Save Changes')).toBeInTheDocument();
    });

    it('proceeds with breaking changes when user confirms', async () => {
      const breakingError = new MockApiClientError(
        'BREAKING_CHANGES_DETECTED',
        'Breaking changes detected',
        409,
        breakingChanges
      );

      // First call fails, second call (with allowBreaking) succeeds
      mockApi.updateContract
        .mockRejectedValueOnce(breakingError)
        .mockResolvedValueOnce({
          ...existingContract,
          version: '2.0.0',
        });

      render(<StudioPage />);

      await waitFor(() => {
        expect(mockApi.getContract).toHaveBeenCalled();
      });

      // First save attempt
      fireEvent.click(screen.getByText('Save Changes'));

      await waitFor(() => {
        expect(screen.getByText('Breaking Changes Detected')).toBeInTheDocument();
      });

      // Proceed with breaking changes
      fireEvent.click(screen.getByText('Proceed with Breaking Changes'));

      // Should call updateContract with allowBreaking: true
      await waitFor(() => {
        expect(mockApi.updateContract).toHaveBeenCalledTimes(2);
        expect(mockApi.updateContract).toHaveBeenLastCalledWith(
          'customer-contract',
          expect.any(Object),
          { allowBreaking: true }
        );
      });

      // Should show success message
      await waitFor(() => {
        expect(screen.getByText('Contract updated successfully')).toBeInTheDocument();
      });
    });

    it('shows loading state during save operation', async () => {
      // Make updateContract hang
      mockApi.updateContract.mockImplementation(
        () => new Promise(() => {}) // Never resolves
      );

      render(<StudioPage />);

      await waitFor(() => {
        expect(mockApi.getContract).toHaveBeenCalled();
      });

      fireEvent.click(screen.getByText('Save Changes'));

      // Button should be disabled during save
      await waitFor(() => {
        const saveButton = screen.getByText('Save Changes');
        expect(saveButton).toBeDisabled();
      });
    });

    it('handles API errors gracefully', async () => {
      mockApi.updateContract.mockRejectedValue(new Error('Network error'));

      render(<StudioPage />);

      await waitFor(() => {
        expect(mockApi.getContract).toHaveBeenCalled();
      });

      fireEvent.click(screen.getByText('Save Changes'));

      await waitFor(() => {
        expect(
          screen.getByText(/Failed to save contract/)
        ).toBeInTheDocument();
      });
    });
  });

  describe('Breaking Change Count Display', () => {
    beforeEach(() => {
      setupEditMode();
      mockApi.getContract.mockResolvedValue(existingContract);
    });

    it('shows correct count for single breaking change', async () => {
      const singleBreakingError = new MockApiClientError(
        'BREAKING_CHANGES_DETECTED',
        'Breaking changes detected',
        409,
        [breakingChanges[0]]
      );
      mockApi.updateContract.mockRejectedValue(singleBreakingError);

      render(<StudioPage />);

      await waitFor(() => {
        expect(mockApi.getContract).toHaveBeenCalled();
      });

      fireEvent.click(screen.getByText('Save Changes'));

      await waitFor(() => {
        expect(
          screen.getByText(/This update contains 1 breaking change/)
        ).toBeInTheDocument();
      });
    });

    it('shows correct count for multiple breaking changes', async () => {
      const breakingError = new MockApiClientError(
        'BREAKING_CHANGES_DETECTED',
        'Breaking changes detected',
        409,
        breakingChanges
      );
      mockApi.updateContract.mockRejectedValue(breakingError);

      render(<StudioPage />);

      await waitFor(() => {
        expect(mockApi.getContract).toHaveBeenCalled();
      });

      fireEvent.click(screen.getByText('Save Changes'));

      await waitFor(() => {
        expect(
          screen.getByText(/This update contains 2 breaking changes/)
        ).toBeInTheDocument();
      });
    });
  });

  describe('Breaking Change Type Formatting', () => {
    beforeEach(() => {
      setupEditMode();
      mockApi.getContract.mockResolvedValue(existingContract);
    });

    const allBreakingChangeTypes: BreakingChangeInfo[] = [
      { change_type: 'field_removed', field: 'f1', description: 'Removed' },
      { change_type: 'field_renamed', field: 'f2', description: 'Renamed' },
      { change_type: 'type_changed_incompatible', field: 'f3', description: 'Type changed' },
      { change_type: 'required_field_added', field: 'f4', description: 'Required added' },
      { change_type: 'enum_value_removed', field: 'f5', description: 'Enum removed' },
      { change_type: 'constraint_tightened', field: 'f6', description: 'Constraint tight' },
      { change_type: 'nullable_to_required', field: 'f7', description: 'Now required' },
    ];

    it('formats all breaking change types correctly', async () => {
      const breakingError = new MockApiClientError(
        'BREAKING_CHANGES_DETECTED',
        'Breaking changes detected',
        409,
        allBreakingChangeTypes
      );
      mockApi.updateContract.mockRejectedValue(breakingError);

      render(<StudioPage />);

      await waitFor(() => {
        expect(mockApi.getContract).toHaveBeenCalled();
      });

      fireEvent.click(screen.getByText('Save Changes'));

      await waitFor(() => {
        expect(screen.getByText('Field Removed')).toBeInTheDocument();
        expect(screen.getByText('Field Renamed')).toBeInTheDocument();
        expect(screen.getByText('Type Changed')).toBeInTheDocument();
        expect(screen.getByText('Required Field Added')).toBeInTheDocument();
        expect(screen.getByText('Enum Value Removed')).toBeInTheDocument();
        expect(screen.getByText('Constraint Tightened')).toBeInTheDocument();
        expect(screen.getByText('Now Required')).toBeInTheDocument();
      });
    });
  });
});
