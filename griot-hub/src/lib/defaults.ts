/**
 * Smart Defaults for Audit-Ready Contracts
 *
 * T-382: Smart defaults for audit-ready approach
 * T-383: Privacy-aligning defaults for enums/booleans
 *
 * These defaults are designed to:
 * 1. Create contracts that are compliance-ready out of the box
 * 2. Default to the most privacy-preserving options
 * 3. Set sensible SLA and governance targets
 * 4. Minimize configuration for common use cases
 */

import type {
  Compliance,
  SLA,
  Access,
  Governance,
  Legal,
  SchemaProperty,
  PrivacyInfo,
  SensitivityLevel,
  MaskingStrategy,
  LegalBasis,
  ReviewCadence,
  AccessLevel,
} from './types';

// =============================================================================
// Privacy Defaults (T-383)
// =============================================================================

/**
 * Default privacy configuration for new fields.
 * Defaults to privacy-preserving options:
 * - contains_pii: false (explicit opt-in required)
 * - sensitivity_level: "internal" (safe default)
 * - masking: "none" (no automatic masking unless PII)
 */
export const DEFAULT_PRIVACY: PrivacyInfo = {
  contains_pii: false,
  sensitivity_level: 'internal',
  masking: 'none',
};

/**
 * Privacy presets for common PII categories
 */
export const PII_PRIVACY_PRESETS: Record<string, Partial<PrivacyInfo>> = {
  email: {
    contains_pii: true,
    pii_category: 'email',
    sensitivity_level: 'confidential',
    masking: 'hash_sha256',
    retention_days: 365,
  },
  phone: {
    contains_pii: true,
    pii_category: 'phone',
    sensitivity_level: 'confidential',
    masking: 'redact',
    retention_days: 365,
  },
  national_id: {
    contains_pii: true,
    pii_category: 'national_id',
    sensitivity_level: 'restricted',
    masking: 'tokenize',
    retention_days: 730, // 2 years
  },
  name: {
    contains_pii: true,
    pii_category: 'name',
    sensitivity_level: 'confidential',
    masking: 'generalize',
  },
  address: {
    contains_pii: true,
    pii_category: 'address',
    sensitivity_level: 'confidential',
    masking: 'generalize',
  },
  dob: {
    contains_pii: true,
    pii_category: 'dob',
    sensitivity_level: 'confidential',
    masking: 'generalize',
  },
  financial: {
    contains_pii: true,
    pii_category: 'financial',
    sensitivity_level: 'restricted',
    masking: 'encrypt',
    retention_days: 2555, // 7 years for financial records
  },
  health: {
    contains_pii: true,
    pii_category: 'health',
    sensitivity_level: 'restricted',
    masking: 'encrypt',
    legal_basis: 'consent',
  },
  biometric: {
    contains_pii: true,
    pii_category: 'biometric',
    sensitivity_level: 'restricted',
    masking: 'encrypt',
    legal_basis: 'consent',
  },
  location: {
    contains_pii: true,
    pii_category: 'location',
    sensitivity_level: 'confidential',
    masking: 'generalize',
  },
};

// =============================================================================
// Compliance Defaults (T-382)
// =============================================================================

/**
 * Default compliance configuration for new contracts.
 * Audit-ready approach:
 * - data_classification: "internal" (safe default)
 * - audit_requirements.logging: true (always log)
 * - audit_requirements.log_retention: "P365D" (1 year)
 */
export const DEFAULT_COMPLIANCE: Compliance = {
  data_classification: 'internal',
  regulatory_scope: [],
  audit_requirements: {
    logging: true,
    log_retention: 'P365D', // 1 year
  },
  certification_requirements: [],
  export_restrictions: {
    allow_download: false,
    allow_external_transfer: false,
    allowed_destinations: [],
  },
};

/**
 * Compliance presets for common regulatory frameworks
 */
export const COMPLIANCE_PRESETS: Record<string, Partial<Compliance>> = {
  gdpr: {
    data_classification: 'confidential',
    regulatory_scope: ['GDPR'],
    audit_requirements: {
      logging: true,
      log_retention: 'P1825D', // 5 years
    },
    export_restrictions: {
      allow_download: false,
      allow_external_transfer: false,
      allowed_destinations: ['EU', 'EEA', 'UK'],
    },
  },
  ccpa: {
    data_classification: 'confidential',
    regulatory_scope: ['CCPA'],
    audit_requirements: {
      logging: true,
      log_retention: 'P730D', // 2 years
    },
  },
  hipaa: {
    data_classification: 'restricted',
    regulatory_scope: ['HIPAA'],
    audit_requirements: {
      logging: true,
      log_retention: 'P2190D', // 6 years
    },
    certification_requirements: ['HIPAA BAA'],
    export_restrictions: {
      allow_download: false,
      allow_external_transfer: false,
      allowed_destinations: [],
    },
  },
  'pci-dss': {
    data_classification: 'restricted',
    regulatory_scope: ['PCI-DSS'],
    audit_requirements: {
      logging: true,
      log_retention: 'P365D', // 1 year
    },
    certification_requirements: ['PCI DSS Level 1'],
  },
  sox: {
    data_classification: 'confidential',
    regulatory_scope: ['SOX'],
    audit_requirements: {
      logging: true,
      log_retention: 'P2555D', // 7 years
    },
  },
};

// =============================================================================
// SLA Defaults (T-382)
// =============================================================================

/**
 * Default SLA configuration for new contracts.
 * Sensible targets for most data products:
 * - availability: 99.0%
 * - freshness: P1D (daily)
 * - completeness: 99.5%
 * - accuracy: 99.9%
 */
export const DEFAULT_SLA: SLA = {
  availability: {
    target_percent: 99.0,
    measurement_window: 'P30D', // 30-day rolling window
  },
  freshness: {
    target: 'P1D', // Daily updates
  },
  completeness: {
    target_percent: 99.5,
  },
  accuracy: {
    error_rate_target: 0.001, // 0.1% max error rate (99.9% accuracy)
  },
};

/**
 * SLA presets for different data tiers
 */
export const SLA_PRESETS: Record<string, SLA> = {
  critical: {
    availability: {
      target_percent: 99.99,
      measurement_window: 'P30D',
    },
    freshness: {
      target: 'PT1H', // Hourly
    },
    completeness: {
      target_percent: 99.99,
    },
    accuracy: {
      error_rate_target: 0.0001, // 99.99%
    },
    response_time: {
      p50_ms: 100,
      p99_ms: 500,
    },
  },
  standard: DEFAULT_SLA,
  basic: {
    availability: {
      target_percent: 95.0,
      measurement_window: 'P30D',
    },
    freshness: {
      target: 'P7D', // Weekly
    },
    completeness: {
      target_percent: 95.0,
    },
    accuracy: {
      error_rate_target: 0.01, // 99%
    },
  },
  realtime: {
    availability: {
      target_percent: 99.9,
      measurement_window: 'P1D',
    },
    freshness: {
      target: 'PT5M', // 5 minutes
    },
    completeness: {
      target_percent: 99.9,
    },
    accuracy: {
      error_rate_target: 0.001,
    },
    response_time: {
      p50_ms: 50,
      p99_ms: 200,
    },
  },
};

// =============================================================================
// Access Defaults (T-382)
// =============================================================================

/**
 * Default access configuration for new contracts.
 * Conservative approach:
 * - default_level: "read" (least privilege)
 * - approval.required: true (require approval for access)
 */
export const DEFAULT_ACCESS: Access = {
  default_level: 'read',
  grants: [],
  approval: {
    required: true,
    approvers: [],
    workflow: 'default',
  },
  authentication: {
    methods: ['oauth2'],
  },
};

// =============================================================================
// Governance Defaults (T-382)
// =============================================================================

/**
 * Default governance configuration for new contracts.
 * Enterprise-ready approach:
 * - review.cadence: "quarterly"
 * - change_management.breaking_change_notice: "P30D" (30 days)
 * - change_management.deprecation_notice: "P90D" (90 days)
 * - change_management.migration_support: true
 */
export const DEFAULT_GOVERNANCE: Governance = {
  review: {
    cadence: 'quarterly',
    reviewers: [],
  },
  change_management: {
    breaking_change_notice: 'P30D', // 30 days notice
    deprecation_notice: 'P90D', // 90 days notice
    communication_channels: ['email', 'slack'],
    migration_support: true,
  },
  dispute_resolution: {
    process: 'escalation',
    escalation_path: [],
  },
  documentation: {},
};

// =============================================================================
// Legal Defaults (T-382)
// =============================================================================

/**
 * Default legal configuration for new contracts.
 */
export const DEFAULT_LEGAL: Legal = {
  jurisdiction: [],
  basis: 'legitimate_interest', // Most common basis for internal data
  regulations: [],
  cross_border: {
    restrictions: [],
    transfer_mechanisms: [],
  },
};

// =============================================================================
// Schema Property Defaults (T-382, T-383)
// =============================================================================

/**
 * Default schema property values.
 * Privacy-first approach:
 * - nullable: true (allow nulls by default)
 * - primary_key: false
 * - contains_pii: false (explicit opt-in)
 */
export const DEFAULT_SCHEMA_PROPERTY: Partial<SchemaProperty> = {
  logicalType: 'string',
  nullable: true,
  primary_key: false,
  privacy: DEFAULT_PRIVACY,
};

// =============================================================================
// Helper Functions
// =============================================================================

/**
 * Apply audit-ready defaults to a contract
 */
export function applyAuditReadyDefaults(overrides?: {
  compliance?: Partial<Compliance>;
  sla?: Partial<SLA>;
  access?: Partial<Access>;
  governance?: Partial<Governance>;
  legal?: Partial<Legal>;
}): {
  compliance: Compliance;
  sla: SLA;
  access: Access;
  governance: Governance;
  legal: Legal;
} {
  return {
    compliance: { ...DEFAULT_COMPLIANCE, ...overrides?.compliance },
    sla: { ...DEFAULT_SLA, ...overrides?.sla },
    access: { ...DEFAULT_ACCESS, ...overrides?.access },
    governance: { ...DEFAULT_GOVERNANCE, ...overrides?.governance },
    legal: { ...DEFAULT_LEGAL, ...overrides?.legal },
  };
}

/**
 * Apply privacy defaults based on field name patterns
 */
export function inferPrivacyFromFieldName(fieldName: string): Partial<PrivacyInfo> {
  const lowerName = fieldName.toLowerCase();

  // Email patterns
  if (lowerName.includes('email')) {
    return PII_PRIVACY_PRESETS.email;
  }

  // Phone patterns
  if (lowerName.includes('phone') || lowerName.includes('mobile') || lowerName.includes('tel')) {
    return PII_PRIVACY_PRESETS.phone;
  }

  // National ID patterns
  if (
    lowerName.includes('ssn') ||
    lowerName.includes('social_security') ||
    lowerName.includes('national_id') ||
    lowerName.includes('passport')
  ) {
    return PII_PRIVACY_PRESETS.national_id;
  }

  // Name patterns
  if (
    lowerName.includes('first_name') ||
    lowerName.includes('last_name') ||
    lowerName.includes('full_name') ||
    lowerName === 'name'
  ) {
    return PII_PRIVACY_PRESETS.name;
  }

  // Address patterns
  if (
    lowerName.includes('address') ||
    lowerName.includes('street') ||
    lowerName.includes('city') ||
    lowerName.includes('zipcode') ||
    lowerName.includes('postal')
  ) {
    return PII_PRIVACY_PRESETS.address;
  }

  // Date of birth patterns
  if (
    lowerName.includes('dob') ||
    lowerName.includes('birth_date') ||
    lowerName.includes('birthday') ||
    lowerName.includes('date_of_birth')
  ) {
    return PII_PRIVACY_PRESETS.dob;
  }

  // Financial patterns
  if (
    lowerName.includes('credit_card') ||
    lowerName.includes('bank_account') ||
    lowerName.includes('account_number') ||
    lowerName.includes('routing_number')
  ) {
    return PII_PRIVACY_PRESETS.financial;
  }

  // Health patterns
  if (
    lowerName.includes('diagnosis') ||
    lowerName.includes('medical') ||
    lowerName.includes('health') ||
    lowerName.includes('prescription')
  ) {
    return PII_PRIVACY_PRESETS.health;
  }

  // Location patterns
  if (
    lowerName.includes('lat') ||
    lowerName.includes('lng') ||
    lowerName.includes('longitude') ||
    lowerName.includes('latitude') ||
    lowerName.includes('geolocation')
  ) {
    return PII_PRIVACY_PRESETS.location;
  }

  // IP address
  if (lowerName.includes('ip_address') || lowerName === 'ip') {
    return {
      contains_pii: true,
      pii_category: 'other',
      sensitivity_level: 'internal',
      masking: 'hash_sha256',
    };
  }

  // Default: no PII detected
  return DEFAULT_PRIVACY;
}

/**
 * Get compliance preset by framework name
 */
export function getCompliancePreset(framework: string): Compliance {
  const preset = COMPLIANCE_PRESETS[framework.toLowerCase()];
  if (preset) {
    return { ...DEFAULT_COMPLIANCE, ...preset };
  }
  return DEFAULT_COMPLIANCE;
}

/**
 * Get SLA preset by tier name
 */
export function getSLAPreset(tier: string): SLA {
  const preset = SLA_PRESETS[tier.toLowerCase()];
  return preset || DEFAULT_SLA;
}

/**
 * Merge multiple compliance requirements
 */
export function mergeComplianceRequirements(frameworks: string[]): Compliance {
  const merged = { ...DEFAULT_COMPLIANCE };

  for (const framework of frameworks) {
    const preset = COMPLIANCE_PRESETS[framework.toLowerCase()];
    if (preset) {
      // Use the most restrictive classification
      if (preset.data_classification) {
        const levels: SensitivityLevel[] = ['public', 'internal', 'confidential', 'restricted'];
        const currentLevel = levels.indexOf(merged.data_classification);
        const presetLevel = levels.indexOf(preset.data_classification);
        if (presetLevel > currentLevel) {
          merged.data_classification = preset.data_classification;
        }
      }

      // Merge regulatory scope
      if (preset.regulatory_scope) {
        merged.regulatory_scope = [
          ...new Set([...(merged.regulatory_scope || []), ...preset.regulatory_scope]),
        ];
      }

      // Use longest retention
      if (preset.audit_requirements?.log_retention) {
        const currentDays = parseDuration(merged.audit_requirements?.log_retention || 'P0D');
        const presetDays = parseDuration(preset.audit_requirements.log_retention);
        if (presetDays > currentDays) {
          merged.audit_requirements = {
            ...merged.audit_requirements,
            logging: true,
            log_retention: preset.audit_requirements.log_retention,
          };
        }
      }

      // Merge certification requirements
      if (preset.certification_requirements) {
        merged.certification_requirements = [
          ...new Set([...(merged.certification_requirements || []), ...preset.certification_requirements]),
        ];
      }
    }
  }

  return merged;
}

/**
 * Parse ISO 8601 duration to days (approximate)
 */
function parseDuration(duration: string): number {
  const match = duration.match(/P(\d+)D/);
  return match ? parseInt(match[1], 10) : 0;
}
