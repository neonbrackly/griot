"""
Tests for ODCS (Open Data Contract Standard) schema support (T-393).

Tests the full ODCS schema parsing, export, and compatibility features.
"""
from __future__ import annotations

import pytest

from griot_core.contract import (
    load_contract_from_dict,
    load_contract_from_string,
    model_to_dict,
    model_to_yaml,
)
from griot_core.models import Field, GriotModel
from griot_core.types import ContractStatus


# =============================================================================
# ODCS CONTRACT METADATA TESTS
# =============================================================================


class TestODCSContractMetadata:
    """Tests for ODCS contract-level metadata parsing."""

    def test_load_contract_with_api_version(self) -> None:
        """Test loading contract with api_version."""
        yaml_content = """
api_version: v1.0.0
kind: DataContract
id: test-contract
name: TestContract
version: "1.0.0"
status: active
fields:
  id:
    type: string
    description: ID
    primary_key: true
"""
        model = load_contract_from_string(yaml_content)

        assert model._griot_api_version == "v1.0.0"
        assert model._griot_kind == "DataContract"
        assert model._griot_id == "test-contract"
        assert model._griot_version == "1.0.0"
        assert model._griot_status == ContractStatus.ACTIVE

    def test_load_contract_with_draft_status(self) -> None:
        """Test loading contract with draft status."""
        yaml_content = """
api_version: v1.0.0
kind: DataContract
name: DraftContract
version: "0.1.0"
status: draft
fields:
  id:
    type: string
    description: ID
"""
        model = load_contract_from_string(yaml_content)
        assert model._griot_status == ContractStatus.DRAFT

    def test_load_contract_with_deprecated_status(self) -> None:
        """Test loading contract with deprecated status."""
        yaml_content = """
api_version: v1.0.0
kind: DataContract
name: DeprecatedContract
version: "1.0.0"
status: deprecated
fields:
  id:
    type: string
    description: ID
"""
        model = load_contract_from_string(yaml_content)
        assert model._griot_status == ContractStatus.DEPRECATED

    def test_load_contract_with_retired_status(self) -> None:
        """Test loading contract with retired status."""
        yaml_content = """
api_version: v1.0.0
kind: DataContract
name: RetiredContract
version: "1.0.0"
status: retired
fields:
  id:
    type: string
    description: ID
"""
        model = load_contract_from_string(yaml_content)
        assert model._griot_status == ContractStatus.RETIRED

    def test_load_contract_defaults_to_draft(self) -> None:
        """Test that status defaults to draft when not specified."""
        yaml_content = """
name: NoStatusContract
fields:
  id:
    type: string
    description: ID
"""
        model = load_contract_from_string(yaml_content)
        assert model._griot_status == ContractStatus.DRAFT

    def test_export_contract_includes_odcs_metadata(self) -> None:
        """Test that exported contract includes ODCS metadata."""
        yaml_content = """
api_version: v1.0.0
kind: DataContract
id: export-test
name: ExportTest
version: "2.0.0"
status: active
fields:
  id:
    type: string
    description: ID
"""
        model = load_contract_from_string(yaml_content)
        data = model_to_dict(model)

        assert data["api_version"] == "v1.0.0"
        assert data["kind"] == "DataContract"
        assert data["id"] == "export-test"
        assert data["version"] == "2.0.0"
        assert data["status"] == "active"


# =============================================================================
# ODCS FIELD FORMAT TESTS (LIST VS DICT)
# =============================================================================


class TestODCSFieldFormats:
    """Tests for ODCS field format variations."""

    def test_load_contract_list_format(self) -> None:
        """Test loading contract with list format fields (registry format)."""
        data = {
            "name": "ListFormatContract",
            "fields": [
                {
                    "name": "customer_id",
                    "type": "string",
                    "description": "Customer ID",
                    "primary_key": True,
                },
                {
                    "name": "email",
                    "type": "string",
                    "description": "Email",
                    "nullable": True,
                },
            ],
        }
        model = load_contract_from_dict(data)

        assert "customer_id" in model._griot_fields
        assert "email" in model._griot_fields
        assert model._griot_fields["customer_id"].primary_key is True
        assert model._griot_fields["email"].nullable is True

    def test_load_contract_dict_format(self) -> None:
        """Test loading contract with dict format fields (legacy format)."""
        data = {
            "name": "DictFormatContract",
            "fields": {
                "customer_id": {
                    "type": "string",
                    "description": "Customer ID",
                    "primary_key": True,
                },
                "email": {
                    "type": "string",
                    "description": "Email",
                    "nullable": True,
                },
            },
        }
        model = load_contract_from_dict(data)

        assert "customer_id" in model._griot_fields
        assert "email" in model._griot_fields

    def test_export_contract_uses_list_format(self) -> None:
        """Test that exported contract uses list format for fields."""

        class SimpleModel(GriotModel):
            id: str = Field(description="ID", primary_key=True)
            name: str = Field(description="Name")

        data = model_to_dict(SimpleModel)

        assert isinstance(data["fields"], list)
        assert len(data["fields"]) == 2
        assert any(f["name"] == "id" for f in data["fields"])
        assert any(f["name"] == "name" for f in data["fields"])

    def test_list_format_with_nested_constraints(self) -> None:
        """Test list format with nested constraints object."""
        data = {
            "name": "NestedConstraintsContract",
            "fields": [
                {
                    "name": "code",
                    "type": "string",
                    "description": "Code",
                    "constraints": {
                        "min_length": 3,
                        "max_length": 10,
                        "pattern": "^[A-Z]+$",
                    },
                },
            ],
        }
        model = load_contract_from_dict(data)

        field = model._griot_fields["code"]
        assert field.min_length == 3
        assert field.max_length == 10
        assert field.pattern == "^[A-Z]+$"

    def test_list_format_with_nested_metadata(self) -> None:
        """Test list format with nested metadata object."""
        data = {
            "name": "NestedMetadataContract",
            "fields": [
                {
                    "name": "amount",
                    "type": "float",
                    "description": "Amount",
                    "metadata": {
                        "unit": "USD",
                        "aggregation": "sum",
                        "glossary_term": "revenue",
                    },
                },
            ],
        }
        model = load_contract_from_dict(data)

        field = model._griot_fields["amount"]
        assert field.unit == "USD"
        assert field.glossary_term == "revenue"


# =============================================================================
# ODCS DESCRIPTION SECTION TESTS
# =============================================================================


class TestODCSDescriptionSection:
    """Tests for ODCS description section parsing."""

    def test_load_contract_with_description_object(self) -> None:
        """Test loading contract with structured description."""
        yaml_content = """
name: DescriptionContract
description:
  purpose: Store customer profile data
  usage: Analytics and marketing
  limitations: Not for PII-sensitive operations
fields:
  id:
    type: string
    description: ID
"""
        model = load_contract_from_string(yaml_content)

        desc = model._griot_description
        assert desc is not None
        assert desc.purpose == "Store customer profile data"
        assert desc.usage == "Analytics and marketing"
        assert desc.limitations == "Not for PII-sensitive operations"

    def test_load_contract_with_custom_properties(self) -> None:
        """Test loading contract with custom properties in description."""
        data = {
            "name": "CustomPropsContract",
            "description": {
                "purpose": "Test contract",
                "customProperties": [
                    {
                        "name": "team_owner",
                        "value": "Data Platform",
                        "description": "Owning team",
                    },
                    {
                        "name": "cost_center",
                        "value": "12345",
                    },
                ],
            },
            "fields": [
                {"name": "id", "type": "string", "description": "ID"},
            ],
        }
        model = load_contract_from_dict(data)

        desc = model._griot_description
        assert desc is not None
        assert len(desc.custom_properties) == 2
        assert desc.custom_properties[0].name == "team_owner"
        assert desc.custom_properties[0].value == "Data Platform"


# =============================================================================
# ODCS QUALITY SECTION TESTS
# =============================================================================


class TestODCSQualitySection:
    """Tests for ODCS quality rules section parsing."""

    def test_load_contract_with_quality_rules(self) -> None:
        """Test loading contract with quality rules."""
        yaml_content = """
name: QualityContract
quality:
  - rule: completeness
    min_percent: 99.9
    critical_fields: [id, email]
  - rule: freshness
    max_age: PT24H
    timestamp_field: updated_at
fields:
  id:
    type: string
    description: ID
  email:
    type: string
    description: Email
  updated_at:
    type: datetime
    description: Last update
"""
        model = load_contract_from_string(yaml_content)

        quality_rules = model._griot_quality_rules
        assert quality_rules is not None
        assert len(quality_rules) == 2

        completeness = quality_rules[0]
        assert completeness.min_percent == 99.9
        assert completeness.critical_fields == ["id", "email"]

        freshness = quality_rules[1]
        assert freshness.max_age == "PT24H"
        assert freshness.timestamp_field == "updated_at"


# =============================================================================
# ODCS LEGAL SECTION TESTS
# =============================================================================


class TestODCSLegalSection:
    """Tests for ODCS legal section parsing."""

    def test_load_contract_with_legal_section(self) -> None:
        """Test loading contract with legal configuration."""
        yaml_content = """
name: LegalContract
legal:
  jurisdiction: [US, EU]
  basis: consent
  consent_id: CONSENT-001
  regulations: [GDPR, CCPA]
fields:
  id:
    type: string
    description: ID
"""
        model = load_contract_from_string(yaml_content)

        legal = model._griot_legal
        assert legal is not None
        assert legal.jurisdiction == ["US", "EU"]
        assert legal.consent_id == "CONSENT-001"
        assert legal.regulations == ["GDPR", "CCPA"]

    def test_load_contract_with_cross_border(self) -> None:
        """Test loading contract with cross-border restrictions."""
        data = {
            "name": "CrossBorderContract",
            "legal": {
                "jurisdiction": ["EU"],
                "cross_border": {
                    "restrictions": ["CN", "RU"],
                    "transfer_mechanisms": ["SCCs", "BCRs"],
                    "data_residency": "EU",
                },
            },
            "fields": [
                {"name": "id", "type": "string", "description": "ID"},
            ],
        }
        model = load_contract_from_dict(data)

        legal = model._griot_legal
        assert legal is not None
        assert legal.cross_border is not None
        assert legal.cross_border.restrictions == ["CN", "RU"]
        assert legal.cross_border.data_residency == "EU"


# =============================================================================
# ODCS COMPLIANCE SECTION TESTS
# =============================================================================


class TestODCSComplianceSection:
    """Tests for ODCS compliance section parsing."""

    def test_load_contract_with_compliance_section(self) -> None:
        """Test loading contract with compliance configuration."""
        yaml_content = """
name: ComplianceContract
compliance:
  data_classification: confidential
  regulatory_scope: [GDPR, HIPAA]
  certification_requirements: [SOC2, ISO27001]
fields:
  id:
    type: string
    description: ID
"""
        model = load_contract_from_string(yaml_content)

        compliance = model._griot_compliance
        assert compliance is not None
        assert compliance.regulatory_scope == ["GDPR", "HIPAA"]
        assert compliance.certification_requirements == ["SOC2", "ISO27001"]

    def test_load_contract_with_audit_requirements(self) -> None:
        """Test loading contract with audit requirements."""
        data = {
            "name": "AuditContract",
            "compliance": {
                "audit_requirements": {
                    "logging": True,
                    "log_retention": "P365D",
                },
            },
            "fields": [
                {"name": "id", "type": "string", "description": "ID"},
            ],
        }
        model = load_contract_from_dict(data)

        compliance = model._griot_compliance
        assert compliance is not None
        assert compliance.audit_requirements is not None
        assert compliance.audit_requirements.logging is True
        assert compliance.audit_requirements.log_retention == "P365D"


# =============================================================================
# ODCS SLA SECTION TESTS
# =============================================================================


class TestODCSSLASection:
    """Tests for ODCS SLA section parsing."""

    def test_load_contract_with_sla_section(self) -> None:
        """Test loading contract with SLA configuration."""
        yaml_content = """
name: SLAContract
sla:
  availability:
    target_percent: 99.9
    measurement_window: P30D
  freshness:
    target: PT4H
    measurement_field: updated_at
  completeness:
    target_percent: 99.5
    critical_fields: [id, email]
  accuracy:
    error_rate_target: 0.001
    validation_method: cross-reference
  response_time:
    p50_ms: 100
    p99_ms: 500
fields:
  id:
    type: string
    description: ID
"""
        model = load_contract_from_string(yaml_content)

        sla = model._griot_sla
        assert sla is not None

        assert sla.availability.target_percent == 99.9
        assert sla.availability.measurement_window == "P30D"

        assert sla.freshness.target == "PT4H"
        assert sla.freshness.measurement_field == "updated_at"

        assert sla.completeness.target_percent == 99.5
        assert sla.completeness.critical_fields == ["id", "email"]

        assert sla.accuracy.error_rate_target == 0.001

        assert sla.response_time.p50_ms == 100
        assert sla.response_time.p99_ms == 500


# =============================================================================
# ODCS ACCESS SECTION TESTS
# =============================================================================


class TestODCSAccessSection:
    """Tests for ODCS access section parsing."""

    def test_load_contract_with_access_section(self) -> None:
        """Test loading contract with access configuration."""
        yaml_content = """
name: AccessContract
access:
  default_level: read
  authentication: oauth2
  grants:
    - principal: team://analytics
      level: read
    - principal: service://etl-pipeline
      level: write
      expiry: "2025-12-31"
fields:
  id:
    type: string
    description: ID
"""
        model = load_contract_from_string(yaml_content)

        access = model._griot_access
        assert access is not None
        assert access.authentication == "oauth2"
        assert len(access.grants) == 2

        analytics_grant = access.grants[0]
        assert analytics_grant.principal == "team://analytics"

        etl_grant = access.grants[1]
        assert etl_grant.principal == "service://etl-pipeline"
        assert etl_grant.expiry == "2025-12-31"

    def test_load_contract_with_access_approval(self) -> None:
        """Test loading contract with access approval workflow."""
        data = {
            "name": "ApprovalContract",
            "access": {
                "default_level": "read",
                "approval": {
                    "required": True,
                    "approvers": ["data-owner@example.com", "security@example.com"],
                    "workflow": "standard-review",
                },
            },
            "fields": [
                {"name": "id", "type": "string", "description": "ID"},
            ],
        }
        model = load_contract_from_dict(data)

        access = model._griot_access
        assert access is not None
        assert access.approval is not None
        assert access.approval.required is True
        assert len(access.approval.approvers) == 2


# =============================================================================
# ODCS GOVERNANCE SECTION TESTS
# =============================================================================


class TestODCSGovernanceSection:
    """Tests for ODCS governance section parsing."""

    def test_load_contract_with_governance_section(self) -> None:
        """Test loading contract with governance configuration."""
        yaml_content = """
name: GovernanceContract
governance:
  producer:
    team: Data Platform
    contact: data-platform@example.com
    responsibilities: [data quality, schema updates]
  review:
    cadence: quarterly
    last_review: "2024-01-15"
    next_review: "2024-04-15"
    reviewers: [data-owner@example.com]
  change_management:
    breaking_change_notice: P30D
    deprecation_notice: P90D
    migration_support: true
fields:
  id:
    type: string
    description: ID
"""
        model = load_contract_from_string(yaml_content)

        governance = model._griot_governance
        assert governance is not None

        assert governance.producer.team == "Data Platform"
        assert governance.producer.contact == "data-platform@example.com"

        assert governance.review.last_review == "2024-01-15"
        assert governance.review.next_review == "2024-04-15"

        assert governance.change_management.breaking_change_notice == "P30D"
        assert governance.change_management.migration_support is True

    def test_load_contract_with_consumers(self) -> None:
        """Test loading contract with consumer information."""
        data = {
            "name": "ConsumersContract",
            "governance": {
                "producer": {
                    "team": "Data Team",
                },
                "consumers": [
                    {
                        "team": "Analytics",
                        "use_case": "Dashboard reporting",
                        "approved_date": "2024-01-01",
                    },
                    {
                        "team": "ML Platform",
                        "use_case": "Model training",
                    },
                ],
            },
            "fields": [
                {"name": "id", "type": "string", "description": "ID"},
            ],
        }
        model = load_contract_from_dict(data)

        governance = model._griot_governance
        assert len(governance.consumers) == 2
        assert governance.consumers[0].team == "Analytics"
        assert governance.consumers[0].use_case == "Dashboard reporting"


# =============================================================================
# ODCS TEAM SECTION TESTS
# =============================================================================


class TestODCSTeamSection:
    """Tests for ODCS team section parsing."""

    def test_load_contract_with_team_section(self) -> None:
        """Test loading contract with team information."""
        yaml_content = """
name: TeamContract
team:
  name: Customer Data Team
  department: Engineering
  steward:
    name: Jane Doe
    email: jane.doe@example.com
fields:
  id:
    type: string
    description: ID
"""
        model = load_contract_from_string(yaml_content)

        team = model._griot_team
        assert team is not None
        assert team.name == "Customer Data Team"
        assert team.department == "Engineering"
        assert team.steward.name == "Jane Doe"
        assert team.steward.email == "jane.doe@example.com"


# =============================================================================
# ODCS SERVERS SECTION TESTS
# =============================================================================


class TestODCSServersSection:
    """Tests for ODCS servers section parsing."""

    def test_load_contract_with_servers_section(self) -> None:
        """Test loading contract with server definitions."""
        yaml_content = """
name: ServersContract
servers:
  - server: prod-dwh-001
    environment: production
    type: bigquery
    project: my-gcp-project
    dataset: customer_data
  - server: dev-dwh-001
    environment: development
    type: bigquery
    project: my-gcp-project-dev
    dataset: customer_data_dev
fields:
  id:
    type: string
    description: ID
"""
        model = load_contract_from_string(yaml_content)

        servers = model._griot_servers
        assert servers is not None
        assert len(servers) == 2

        prod_server = servers[0]
        assert prod_server.server == "prod-dwh-001"
        assert prod_server.environment == "production"
        assert prod_server.type == "bigquery"
        assert prod_server.project == "my-gcp-project"


# =============================================================================
# ODCS ROLES SECTION TESTS
# =============================================================================


class TestODCSRolesSection:
    """Tests for ODCS roles section parsing."""

    def test_load_contract_with_roles_section(self) -> None:
        """Test loading contract with role definitions."""
        yaml_content = """
name: RolesContract
roles:
  - role: data_analyst
    access: read
  - role: data_engineer
    access: write
  - role: data_admin
    access: admin
fields:
  id:
    type: string
    description: ID
"""
        model = load_contract_from_string(yaml_content)

        roles = model._griot_roles
        assert roles is not None
        assert len(roles) == 3

        analyst = roles[0]
        assert analyst.role == "data_analyst"


# =============================================================================
# ODCS TIMESTAMPS SECTION TESTS
# =============================================================================


class TestODCSTimestampsSection:
    """Tests for ODCS timestamps section parsing."""

    def test_load_contract_with_timestamps_section(self) -> None:
        """Test loading contract with timestamp metadata."""
        yaml_content = """
name: TimestampsContract
timestamps:
  created_at: "2024-01-01T00:00:00Z"
  updated_at: "2024-06-15T12:30:00Z"
  effective_from: "2024-02-01T00:00:00Z"
  effective_until: "2025-01-31T23:59:59Z"
fields:
  id:
    type: string
    description: ID
"""
        model = load_contract_from_string(yaml_content)

        timestamps = model._griot_timestamps
        assert timestamps is not None
        assert timestamps.created_at == "2024-01-01T00:00:00Z"
        assert timestamps.updated_at == "2024-06-15T12:30:00Z"
        assert timestamps.effective_from == "2024-02-01T00:00:00Z"
        assert timestamps.effective_until == "2025-01-31T23:59:59Z"


# =============================================================================
# ODCS DISTRIBUTION SECTION TESTS
# =============================================================================


class TestODCSDistributionSection:
    """Tests for ODCS distribution section parsing."""

    def test_load_contract_with_distribution_section(self) -> None:
        """Test loading contract with distribution channels."""
        data = {
            "name": "DistributionContract",
            "distribution": {
                "channels": [
                    {
                        "type": "warehouse",
                        "identifier": "project.dataset.table",
                        "format": "parquet",
                    },
                    {
                        "type": "api",
                        "identifier": "https://api.example.com/data",
                        "format": "json",
                    },
                ],
            },
            "fields": [
                {"name": "id", "type": "string", "description": "ID"},
            ],
        }
        model = load_contract_from_dict(data)

        distribution = model._griot_distribution
        assert distribution is not None
        assert len(distribution.channels) == 2

        warehouse_channel = distribution.channels[0]
        assert warehouse_channel.identifier == "project.dataset.table"
        assert warehouse_channel.format == "parquet"


# =============================================================================
# ODCS FULL CONTRACT ROUNDTRIP TEST
# =============================================================================


class TestODCSRoundtrip:
    """Tests for ODCS contract roundtrip (load -> export -> load)."""

    def test_full_odcs_contract_roundtrip(self) -> None:
        """Test that a full ODCS contract survives roundtrip."""
        yaml_content = """
api_version: v1.0.0
kind: DataContract
id: roundtrip-test
name: RoundtripTest
version: "1.0.0"
status: active
quality:
  - rule: completeness
    min_percent: 99.0
legal:
  jurisdiction: [US]
  basis: consent
compliance:
  data_classification: internal
sla:
  availability:
    target_percent: 99.9
governance:
  producer:
    team: Test Team
team:
  name: Quality Team
  department: Engineering
fields:
  - name: id
    type: string
    description: Primary identifier
    primary_key: true
  - name: value
    type: integer
    description: Numeric value
    constraints:
      ge: 0
      le: 100
"""
        # Load the contract
        model = load_contract_from_string(yaml_content)

        # Export to dict
        data = model_to_dict(model)

        # Verify key sections are preserved
        assert data["api_version"] == "v1.0.0"
        assert data["kind"] == "DataContract"
        assert data["id"] == "roundtrip-test"
        assert data["status"] == "active"

        # Fields should be in list format
        assert isinstance(data["fields"], list)
        assert len(data["fields"]) == 2

        # Reload from dict
        reloaded = load_contract_from_dict(data)

        # Verify metadata preserved
        assert reloaded._griot_api_version == "v1.0.0"
        assert reloaded._griot_id == "roundtrip-test"
        assert reloaded._griot_status == ContractStatus.ACTIVE

        # Verify fields preserved
        assert "id" in reloaded._griot_fields
        assert "value" in reloaded._griot_fields
        assert reloaded._griot_fields["id"].primary_key is True


# =============================================================================
# ODCS EXPORT TESTS
# =============================================================================


class TestODCSExport:
    """Tests for ODCS export functionality."""

    def test_export_includes_odcs_sections(self) -> None:
        """Test that export includes ODCS sections from model."""
        yaml_content = """
api_version: v1.0.0
kind: DataContract
id: export-sections-test
name: ExportSectionsTest
version: "1.0.0"
status: active
sla:
  availability:
    target_percent: 99.5
governance:
  producer:
    team: Export Team
fields:
  id:
    type: string
    description: ID
"""
        model = load_contract_from_string(yaml_content)
        data = model_to_dict(model)

        # Should include ODCS sections
        assert "sla" in data
        assert "governance" in data

    def test_export_to_yaml_preserves_structure(self) -> None:
        """Test that YAML export preserves ODCS structure."""

        class ExportModel(GriotModel):
            """Export test model."""

            id: str = Field(description="ID", primary_key=True)
            score: float = Field(description="Score", ge=0.0, le=100.0, unit="points")

        yaml_str = model_to_yaml(ExportModel)

        # Should be valid YAML
        import yaml
        data = yaml.safe_load(yaml_str)

        assert data["name"] == "ExportModel"
        assert "fields" in data
        assert isinstance(data["fields"], list)
