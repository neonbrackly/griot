/**
 * Registry API Client
 *
 * Provides typed methods for all Registry API endpoints.
 * All data in griot-hub comes through this client - never import griot-core directly.
 *
 * T-388: Updated for ODCS schema support
 * T-305, T-384: Added breaking change detection support
 */

import type {
  Contract,
  ContractCreate,
  ContractUpdate,
  ContractList,
  ContractListParams,
  ContractDiff,
  VersionList,
  ValidationReport,
  ValidationRecord,
  ValidationList,
  ValidationListParams,
  SearchResults,
  SearchParams,
  HealthResponse,
  ApiError,
  AuditReport,
  AnalyticsReport,
  AIReadinessReport,
  ReadinessReport,
  ReportParams,
  ResidencyStatus,
  Region,
  BreakingChangesResponse,
  BreakingChangeInfo,
} from './types';

// =============================================================================
// CONFIGURATION
// =============================================================================

// NEXT_PUBLIC_REGISTRY_API_URL must be set at build time via .env.local or build args
// Default to localhost:8000 for local development without Docker
const API_BASE_URL = process.env.NEXT_PUBLIC_REGISTRY_API_URL || 'http://localhost:8000/api/v1';

// =============================================================================
// FETCH WRAPPER
// =============================================================================

class ApiClient {
  private baseUrl: string;
  private apiKey?: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  setApiKey(key: string) {
    this.apiKey = key;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.apiKey) {
      (headers as Record<string, string>)['X-API-Key'] = this.apiKey;
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({
        code: 'UNKNOWN_ERROR',
        message: `Request failed with status ${response.status}`,
      }));

      // Check for breaking changes response (T-305, T-384)
      if (response.status === 409 && errorData.code === 'BREAKING_CHANGES_DETECTED') {
        const breakingChangesResponse = errorData as BreakingChangesResponse;
        throw new ApiClientError(
          errorData.code,
          errorData.message,
          response.status,
          breakingChangesResponse.breaking_changes
        );
      }

      throw new ApiClientError(errorData.code, errorData.message, response.status);
    }

    // Handle 204 No Content
    if (response.status === 204) {
      return undefined as T;
    }

    return response.json();
  }

  private buildQueryString(params: Record<string, unknown>): string {
    const searchParams = new URLSearchParams();
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined && value !== null) {
        searchParams.append(key, String(value));
      }
    }
    const query = searchParams.toString();
    return query ? `?${query}` : '';
  }

  // ===========================================================================
  // HEALTH
  // ===========================================================================

  async health(): Promise<HealthResponse> {
    return this.request<HealthResponse>('/health');
  }

  // ===========================================================================
  // CONTRACTS
  // ===========================================================================

  async getContracts(params: ContractListParams = {}): Promise<ContractList> {
    const query = this.buildQueryString(params);
    return this.request<ContractList>(`/contracts${query}`);
  }

  async getContract(id: string, version?: string): Promise<Contract> {
    const query = version ? `?version=${encodeURIComponent(version)}` : '';
    return this.request<Contract>(`/contracts/${encodeURIComponent(id)}${query}`);
  }

  async createContract(data: ContractCreate): Promise<Contract> {
    return this.request<Contract>('/contracts', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateContract(
    id: string,
    data: ContractUpdate,
    options?: { allowBreaking?: boolean }
  ): Promise<Contract> {
    const query = options?.allowBreaking ? '?allow_breaking=true' : '';
    return this.request<Contract>(`/contracts/${encodeURIComponent(id)}${query}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  /**
   * Check for breaking changes before updating a contract (dry run)
   * T-305, T-384: Breaking change detection
   */
  async checkBreakingChanges(
    id: string,
    data: ContractUpdate
  ): Promise<BreakingChangeInfo[]> {
    try {
      // Attempt update without allow_breaking - will fail if breaking changes exist
      await this.request<Contract>(`/contracts/${encodeURIComponent(id)}?dry_run=true`, {
        method: 'PUT',
        body: JSON.stringify(data),
      });
      return []; // No breaking changes
    } catch (err) {
      if (err instanceof ApiClientError && err.status === 409) {
        // Parse breaking changes from response
        const response = err as ApiClientError & { breakingChanges?: BreakingChangeInfo[] };
        return response.breakingChanges || [];
      }
      throw err;
    }
  }

  async deprecateContract(id: string): Promise<void> {
    return this.request<void>(`/contracts/${encodeURIComponent(id)}`, {
      method: 'DELETE',
    });
  }

  // ===========================================================================
  // VERSIONS
  // ===========================================================================

  async getVersions(
    contractId: string,
    params: { limit?: number; offset?: number } = {}
  ): Promise<VersionList> {
    const query = this.buildQueryString(params);
    return this.request<VersionList>(
      `/contracts/${encodeURIComponent(contractId)}/versions${query}`
    );
  }

  async getVersion(contractId: string, version: string): Promise<Contract> {
    return this.request<Contract>(
      `/contracts/${encodeURIComponent(contractId)}/versions/${encodeURIComponent(version)}`
    );
  }

  async diffVersions(
    contractId: string,
    fromVersion: string,
    toVersion: string
  ): Promise<ContractDiff> {
    const query = `?from=${encodeURIComponent(fromVersion)}&to=${encodeURIComponent(toVersion)}`;
    return this.request<ContractDiff>(
      `/contracts/${encodeURIComponent(contractId)}/diff${query}`
    );
  }

  // ===========================================================================
  // VALIDATIONS
  // ===========================================================================

  async reportValidation(data: ValidationReport): Promise<ValidationRecord> {
    return this.request<ValidationRecord>('/validations', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getValidations(params: ValidationListParams = {}): Promise<ValidationList> {
    const query = this.buildQueryString(params);
    return this.request<ValidationList>(`/validations${query}`);
  }

  async getContractValidations(
    contractId: string,
    params: { limit?: number; offset?: number } = {}
  ): Promise<ValidationList> {
    const query = this.buildQueryString(params);
    return this.request<ValidationList>(
      `/contracts/${encodeURIComponent(contractId)}/validations${query}`
    );
  }

  // ===========================================================================
  // SEARCH
  // ===========================================================================

  async search(params: SearchParams): Promise<SearchResults> {
    const query = this.buildQueryString(params);
    return this.request<SearchResults>(`/search${query}`);
  }

  // ===========================================================================
  // REPORTS (T-102)
  // ===========================================================================

  async getAuditReport(params: ReportParams = {}): Promise<AuditReport> {
    const query = this.buildQueryString(params);
    return this.request<AuditReport>(`/reports/audit${query}`);
  }

  async getAnalyticsReport(params: ReportParams = {}): Promise<AnalyticsReport> {
    const query = this.buildQueryString(params);
    return this.request<AnalyticsReport>(`/reports/analytics${query}`);
  }

  async getAIReadinessReport(params: ReportParams = {}): Promise<AIReadinessReport> {
    const query = this.buildQueryString(params);
    return this.request<AIReadinessReport>(`/reports/ai-readiness${query}`);
  }

  async getReadinessReport(params: ReportParams = {}): Promise<ReadinessReport> {
    const query = this.buildQueryString(params);
    return this.request<ReadinessReport>(`/reports/readiness${query}`);
  }

  // ===========================================================================
  // RESIDENCY
  // ===========================================================================

  async checkResidency(
    contractId: string,
    region: Region
  ): Promise<ResidencyStatus[]> {
    return this.request<ResidencyStatus[]>(
      `/contracts/${encodeURIComponent(contractId)}/residency?region=${encodeURIComponent(region)}`
    );
  }

  async getResidencyMap(): Promise<Record<Region, string[]>> {
    return this.request<Record<Region, string[]>>('/residency/map');
  }
}

// =============================================================================
// ERROR CLASS
// =============================================================================

export class ApiClientError extends Error {
  public breakingChanges?: BreakingChangeInfo[];

  constructor(
    public code: string,
    message: string,
    public status: number,
    breakingChanges?: BreakingChangeInfo[]
  ) {
    super(message);
    this.name = 'ApiClientError';
    this.breakingChanges = breakingChanges;
  }

  /**
   * Check if this error is due to breaking changes being detected
   */
  isBreakingChangeError(): boolean {
    return this.code === 'BREAKING_CHANGES_DETECTED' && this.status === 409;
  }
}

// =============================================================================
// SINGLETON INSTANCE
// =============================================================================

export const api = new ApiClient();

export default api;
