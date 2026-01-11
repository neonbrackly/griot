/**
 * Tests for API Client Breaking Change Handling (T-392)
 *
 * Tests the API client's handling of breaking change responses from
 * the Registry API, including error detection and response parsing.
 */
import api, { ApiClientError } from '@/lib/api';
import type { BreakingChangeInfo, BreakingChangesResponse } from '@/lib/types';

// =============================================================================
// MOCK SETUP
// =============================================================================

// Store original fetch
const originalFetch = global.fetch;

// Mock response helper
function mockResponse(status: number, data: unknown) {
  return Promise.resolve({
    ok: status >= 200 && status < 300,
    status,
    json: () => Promise.resolve(data),
  } as Response);
}

// =============================================================================
// TEST DATA
// =============================================================================

const breakingChangesResponse: BreakingChangesResponse = {
  code: 'BREAKING_CHANGES_DETECTED',
  message: 'Contract update contains breaking changes',
  breaking_changes: [
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
  ],
  allow_breaking_hint: 'Use ?allow_breaking=true to force update',
};

const mockContract = {
  id: 'test-contract',
  name: 'Test Contract',
  api_version: 'v1.0.0',
  kind: 'DataContract' as const,
  version: '1.0.0',
  status: 'active' as const,
  fields: [],
};

const mockUpdate = {
  name: 'Updated Contract',
  fields: [{ name: 'new_field', type: 'string' as const, description: 'New field' }],
};

// =============================================================================
// API CLIENT ERROR TESTS
// =============================================================================

describe('ApiClientError', () => {
  describe('Constructor', () => {
    it('creates error with code, message, and status', () => {
      const error = new ApiClientError('TEST_ERROR', 'Test message', 400);

      expect(error.code).toBe('TEST_ERROR');
      expect(error.message).toBe('Test message');
      expect(error.status).toBe(400);
      expect(error.name).toBe('ApiClientError');
    });

    it('stores breaking changes when provided', () => {
      const breakingChanges: BreakingChangeInfo[] = [
        {
          change_type: 'field_removed',
          field: 'test',
          description: 'Test field removed',
        },
      ];

      const error = new ApiClientError(
        'BREAKING_CHANGES_DETECTED',
        'Breaking changes',
        409,
        breakingChanges
      );

      expect(error.breakingChanges).toEqual(breakingChanges);
    });

    it('handles undefined breaking changes', () => {
      const error = new ApiClientError('OTHER_ERROR', 'Other error', 500);

      expect(error.breakingChanges).toBeUndefined();
    });
  });

  describe('isBreakingChangeError', () => {
    it('returns true for breaking change error', () => {
      const error = new ApiClientError(
        'BREAKING_CHANGES_DETECTED',
        'Breaking changes',
        409
      );

      expect(error.isBreakingChangeError()).toBe(true);
    });

    it('returns false for other error codes', () => {
      const error = new ApiClientError('OTHER_ERROR', 'Other error', 409);

      expect(error.isBreakingChangeError()).toBe(false);
    });

    it('returns false for other status codes', () => {
      const error = new ApiClientError(
        'BREAKING_CHANGES_DETECTED',
        'Breaking changes',
        400
      );

      expect(error.isBreakingChangeError()).toBe(false);
    });
  });
});

// =============================================================================
// UPDATE CONTRACT TESTS
// =============================================================================

describe('api.updateContract', () => {
  beforeEach(() => {
    global.fetch = jest.fn();
  });

  afterEach(() => {
    global.fetch = originalFetch;
  });

  it('successfully updates contract without breaking changes', async () => {
    (global.fetch as jest.Mock).mockReturnValue(
      mockResponse(200, { ...mockContract, name: 'Updated Contract' })
    );

    const result = await api.updateContract('test-contract', mockUpdate);

    expect(result.name).toBe('Updated Contract');
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/contracts/test-contract'),
      expect.objectContaining({
        method: 'PUT',
      })
    );
  });

  it('throws ApiClientError with breaking changes on 409', async () => {
    (global.fetch as jest.Mock).mockReturnValue(
      mockResponse(409, breakingChangesResponse)
    );

    try {
      await api.updateContract('test-contract', mockUpdate);
      fail('Expected error to be thrown');
    } catch (error) {
      expect(error).toBeInstanceOf(ApiClientError);
      const apiError = error as ApiClientError;
      expect(apiError.status).toBe(409);
      expect(apiError.code).toBe('BREAKING_CHANGES_DETECTED');
      expect(apiError.isBreakingChangeError()).toBe(true);
      expect(apiError.breakingChanges).toHaveLength(2);
      expect(apiError.breakingChanges?.[0].change_type).toBe('field_removed');
    }
  });

  it('passes allow_breaking query param when specified', async () => {
    (global.fetch as jest.Mock).mockReturnValue(mockResponse(200, mockContract));

    await api.updateContract('test-contract', mockUpdate, { allowBreaking: true });

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('?allow_breaking=true'),
      expect.any(Object)
    );
  });

  it('does not pass allow_breaking when not specified', async () => {
    (global.fetch as jest.Mock).mockReturnValue(mockResponse(200, mockContract));

    await api.updateContract('test-contract', mockUpdate);

    expect(global.fetch).toHaveBeenCalledWith(
      expect.not.stringContaining('allow_breaking'),
      expect.any(Object)
    );
  });

  it('handles network errors', async () => {
    (global.fetch as jest.Mock).mockRejectedValue(new Error('Network error'));

    await expect(api.updateContract('test-contract', mockUpdate)).rejects.toThrow(
      'Network error'
    );
  });
});

// =============================================================================
// CHECK BREAKING CHANGES TESTS
// =============================================================================

describe('api.checkBreakingChanges', () => {
  beforeEach(() => {
    global.fetch = jest.fn();
  });

  afterEach(() => {
    global.fetch = originalFetch;
  });

  it('returns empty array when no breaking changes', async () => {
    (global.fetch as jest.Mock).mockReturnValue(mockResponse(200, mockContract));

    const result = await api.checkBreakingChanges('test-contract', mockUpdate);

    expect(result).toEqual([]);
  });

  it('returns breaking changes when detected', async () => {
    (global.fetch as jest.Mock).mockReturnValue(
      mockResponse(409, breakingChangesResponse)
    );

    const result = await api.checkBreakingChanges('test-contract', mockUpdate);

    expect(result).toHaveLength(2);
    expect(result[0].change_type).toBe('field_removed');
    expect(result[1].change_type).toBe('type_changed_incompatible');
  });

  it('uses dry_run query parameter', async () => {
    (global.fetch as jest.Mock).mockReturnValue(mockResponse(200, mockContract));

    await api.checkBreakingChanges('test-contract', mockUpdate);

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('?dry_run=true'),
      expect.any(Object)
    );
  });

  it('rethrows non-409 errors', async () => {
    const errorResponse = {
      code: 'VALIDATION_ERROR',
      message: 'Invalid contract data',
    };
    (global.fetch as jest.Mock).mockReturnValue(mockResponse(400, errorResponse));

    await expect(
      api.checkBreakingChanges('test-contract', mockUpdate)
    ).rejects.toMatchObject({
      code: 'VALIDATION_ERROR',
      status: 400,
    });
  });
});

// =============================================================================
// DIFF VERSIONS TESTS
// =============================================================================

describe('api.diffVersions', () => {
  beforeEach(() => {
    global.fetch = jest.fn();
  });

  afterEach(() => {
    global.fetch = originalFetch;
  });

  const mockDiff = {
    from_version: '1.0.0',
    to_version: '2.0.0',
    has_breaking_changes: true,
    added_fields: ['new_field'],
    removed_fields: ['old_field'],
    type_changes: [],
    constraint_changes: [],
  };

  it('returns contract diff', async () => {
    (global.fetch as jest.Mock).mockReturnValue(mockResponse(200, mockDiff));

    const result = await api.diffVersions('test-contract', '1.0.0', '2.0.0');

    expect(result.from_version).toBe('1.0.0');
    expect(result.to_version).toBe('2.0.0');
    expect(result.has_breaking_changes).toBe(true);
  });

  it('includes version parameters in query string', async () => {
    (global.fetch as jest.Mock).mockReturnValue(mockResponse(200, mockDiff));

    await api.diffVersions('test-contract', '1.0.0', '2.0.0');

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('from=1.0.0'),
      expect.any(Object)
    );
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('to=2.0.0'),
      expect.any(Object)
    );
  });

  it('encodes special characters in version strings', async () => {
    (global.fetch as jest.Mock).mockReturnValue(mockResponse(200, mockDiff));

    await api.diffVersions('test-contract', '1.0.0-beta', '2.0.0+build');

    // URL encoding should handle special characters
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('1.0.0-beta'),
      expect.any(Object)
    );
  });
});

// =============================================================================
// GET VERSIONS TESTS
// =============================================================================

describe('api.getVersions', () => {
  beforeEach(() => {
    global.fetch = jest.fn();
  });

  afterEach(() => {
    global.fetch = originalFetch;
  });

  const mockVersionList = {
    items: [
      { version: '2.0.0', is_breaking: true },
      { version: '1.0.0', is_breaking: false },
    ],
    total: 2,
  };

  it('returns version list', async () => {
    (global.fetch as jest.Mock).mockReturnValue(mockResponse(200, mockVersionList));

    const result = await api.getVersions('test-contract');

    expect(result.items).toHaveLength(2);
    expect(result.items[0].version).toBe('2.0.0');
    expect(result.items[0].is_breaking).toBe(true);
  });

  it('handles pagination parameters', async () => {
    (global.fetch as jest.Mock).mockReturnValue(mockResponse(200, mockVersionList));

    await api.getVersions('test-contract', { limit: 10, offset: 20 });

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('limit=10'),
      expect.any(Object)
    );
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('offset=20'),
      expect.any(Object)
    );
  });
});
