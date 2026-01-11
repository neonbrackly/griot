"""
Griot Core Contract Loading and Manipulation

Functions for loading, saving, diffing, and linting contracts.
"""
from __future__ import annotations

from dataclasses import dataclass, field as dataclass_field
from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml

from enum import Enum

from griot_core.exceptions import ContractNotFoundError, ContractParseError
from griot_core.types import ContractStatus, DataType, FieldFormat, Severity

if TYPE_CHECKING:
    from griot_core.models import GriotModel

__all__ = [
    "load_contract",
    "load_contract_from_string",
    "load_contract_from_dict",
    "model_to_yaml",
    "model_to_dict",
    "diff_contracts",
    "lint_contract",
    "detect_breaking_changes",
    "ContractDiff",
    "TypeChange",
    "ConstraintChange",
    "MetadataChange",
    "LintIssue",
    "BreakingChange",
    "BreakingChangeType",
]


# =============================================================================
# Breaking Change Types (T-300)
# =============================================================================


class BreakingChangeType(str, Enum):
    """
    Types of breaking changes in contract evolution (T-300).

    Based on Open Data Contract Standard breaking change rules.
    """

    FIELD_REMOVED = "field_removed"
    FIELD_RENAMED = "field_renamed"
    TYPE_CHANGED_INCOMPATIBLE = "type_changed_incompatible"
    REQUIRED_FIELD_ADDED = "required_field_added"
    ENUM_VALUES_REMOVED = "enum_values_removed"
    CONSTRAINT_TIGHTENED = "constraint_tightened"
    NULLABLE_TO_REQUIRED = "nullable_to_required"
    PATTERN_CHANGED = "pattern_changed"
    PRIMARY_KEY_CHANGED = "primary_key_changed"


@dataclass
class BreakingChange:
    """
    A single breaking change detected between contract versions.

    Attributes:
        change_type: The type of breaking change.
        field: The field affected (None for contract-level changes).
        description: Human-readable description of the change.
        from_value: The original value.
        to_value: The new value.
        migration_hint: Suggested migration approach.
    """

    change_type: BreakingChangeType
    field: str | None
    description: str
    from_value: Any = None
    to_value: Any = None
    migration_hint: str | None = None

    def __str__(self) -> str:
        field_info = f" on field '{self.field}'" if self.field else ""
        return f"[{self.change_type.value}]{field_info}: {self.description}"


@dataclass
class TypeChange:
    """Field type change record."""

    field: str
    from_type: str
    to_type: str
    is_breaking: bool


@dataclass
class ConstraintChange:
    """Constraint change record."""

    field: str
    constraint: str
    from_value: Any
    to_value: Any
    is_breaking: bool


@dataclass
class MetadataChange:
    """Metadata change record (non-breaking)."""

    field: str
    attribute: str
    from_value: Any
    to_value: Any


@dataclass
class ContractDiff:
    """Differences between two contract versions (T-302)."""

    has_breaking_changes: bool = False
    added_fields: list[str] = dataclass_field(default_factory=list)
    removed_fields: list[str] = dataclass_field(default_factory=list)
    type_changes: list[TypeChange] = dataclass_field(default_factory=list)
    constraint_changes: list[ConstraintChange] = dataclass_field(default_factory=list)
    metadata_changes: list[MetadataChange] = dataclass_field(default_factory=list)
    # T-302: Enhanced breaking change tracking
    breaking_changes: list[BreakingChange] = dataclass_field(default_factory=list)

    def summary(self) -> str:
        """Return a human-readable summary."""
        lines = []
        if self.has_breaking_changes:
            lines.append("BREAKING CHANGES DETECTED")
        else:
            lines.append("No breaking changes")

        if self.added_fields:
            lines.append(f"Added fields: {', '.join(self.added_fields)}")
        if self.removed_fields:
            lines.append(f"Removed fields (BREAKING): {', '.join(self.removed_fields)}")
        if self.type_changes:
            lines.append(f"Type changes: {len(self.type_changes)}")
        if self.constraint_changes:
            lines.append(f"Constraint changes: {len(self.constraint_changes)}")

        return "\n".join(lines) if lines else "No differences"

    def to_markdown(self) -> str:
        """Return a markdown-formatted diff report."""
        lines = ["# Contract Diff Report", ""]

        if self.has_breaking_changes:
            lines.append("**WARNING: Breaking changes detected!**")
            lines.append("")

        if self.added_fields:
            lines.append("## Added Fields")
            for f in self.added_fields:
                lines.append(f"- `{f}`")
            lines.append("")

        if self.removed_fields:
            lines.append("## Removed Fields (BREAKING)")
            for f in self.removed_fields:
                lines.append(f"- `{f}`")
            lines.append("")

        if self.type_changes:
            lines.append("## Type Changes")
            for tc in self.type_changes:
                breaking = " **(BREAKING)**" if tc.is_breaking else ""
                lines.append(f"- `{tc.field}`: {tc.from_type} -> {tc.to_type}{breaking}")
            lines.append("")

        if self.constraint_changes:
            lines.append("## Constraint Changes")
            for cc in self.constraint_changes:
                breaking = " **(BREAKING)**" if cc.is_breaking else ""
                lines.append(
                    f"- `{cc.field}.{cc.constraint}`: {cc.from_value} -> {cc.to_value}{breaking}"
                )
            lines.append("")

        return "\n".join(lines)


@dataclass
class LintIssue:
    """Contract quality issue."""

    code: str
    field: str | None
    message: str
    severity: Severity
    suggestion: str | None = None

    def __str__(self) -> str:
        loc = f" ({self.field})" if self.field else ""
        return f"[{self.code}]{loc}: {self.message}"


def load_contract(path: str | Path) -> type[GriotModel]:
    """
    Load a contract definition from a YAML file.

    Args:
        path: Path to the YAML contract file.

    Returns:
        A GriotModel subclass representing the contract.

    Raises:
        ContractNotFoundError: If the file doesn't exist.
        ContractParseError: If the YAML is invalid.
    """
    path = Path(path)
    if not path.exists():
        raise ContractNotFoundError(str(path))

    content = path.read_text(encoding="utf-8")
    return load_contract_from_string(content, source=str(path))


def load_contract_from_string(
    content: str,
    source: str | None = None,
) -> type[GriotModel]:
    """
    Load a contract from a YAML string.

    Args:
        content: YAML content as a string.
        source: Optional source identifier for error messages.

    Returns:
        A GriotModel subclass representing the contract.

    Raises:
        ContractParseError: If the YAML is invalid.
    """
    try:
        data = yaml.safe_load(content)
    except yaml.YAMLError as e:
        source_info = f" in {source}" if source else ""
        raise ContractParseError(f"Invalid YAML{source_info}: {e}") from e

    if data is None:
        raise ContractParseError(f"Empty contract{' in ' + source if source else ''}")

    if not isinstance(data, dict):
        raise ContractParseError(
            f"Contract must be a YAML mapping, got {type(data).__name__}"
        )

    return load_contract_from_dict(data)


def load_contract_from_dict(data: dict[str, Any]) -> type[GriotModel]:
    """
    Load a contract from a dictionary (T-310 enhanced).

    Supports two field formats:
    1. List format (from registry): fields: [{name: "field1", type: "string", ...}]
    2. Dict format (legacy): fields: {field1: {type: "string", ...}}

    Parses ODCS contract-level metadata:
    - api_version, kind, id, version, status

    Args:
        data: Dictionary containing contract definition.

    Returns:
        A GriotModel subclass representing the contract.
    """
    from griot_core.models import Field, GriotModel

    name = data.get("name", "DynamicContract")
    description = data.get("description", "")
    fields_data = data.get("fields", [])

    # T-310: Parse contract-level metadata
    api_version = data.get("api_version", "v1.0.0")
    kind = data.get("kind", "DataContract")
    contract_id = data.get("id")
    version = data.get("version", "1.0.0")
    status_str = data.get("status", "draft")

    # Parse status enum
    try:
        status = ContractStatus(status_str)
    except ValueError:
        status = ContractStatus.DRAFT

    # Build field definitions
    annotations: dict[str, type] = {}
    namespace: dict[str, Any] = {"__annotations__": annotations}

    if description:
        namespace["__doc__"] = description

    # Normalize fields to list of (name, definition) tuples
    field_items: list[tuple[str, dict[str, Any]]] = []

    if isinstance(fields_data, list):
        # List format: [{name: "field1", type: "string", ...}, ...]
        for field_def in fields_data:
            if isinstance(field_def, dict):
                field_name = field_def.get("name")
                if field_name:
                    field_items.append((field_name, field_def))
    elif isinstance(fields_data, dict):
        # Dict format: {field1: {type: "string", ...}, ...}
        for field_name, field_def in fields_data.items():
            if isinstance(field_def, dict):
                field_items.append((field_name, field_def))
            else:
                # Simple field with just a type string
                field_items.append((field_name, {"type": str(field_def)}))

    for field_name, field_def in field_items:
        # Parse field type
        type_str = field_def.get("type", "string")
        python_type = _type_str_to_python(type_str)
        annotations[field_name] = python_type

        # Build Field kwargs
        field_kwargs: dict[str, Any] = {
            "description": field_def.get("description", f"Field: {field_name}"),
        }

        # Extract constraints from nested object if present
        constraints = field_def.get("constraints", {}) or {}

        # Copy constraint parameters (check both top-level and nested constraints)
        for param in [
            "min_length",
            "max_length",
            "pattern",
            "ge",
            "le",
            "gt",
            "lt",
            "multiple_of",
            "enum",
        ]:
            # First check nested constraints, then top-level
            if param in constraints:
                field_kwargs[param] = constraints[param]
            elif param in field_def:
                field_kwargs[param] = field_def[param]

        # Copy field-level attributes (not in constraints)
        for param in ["unique", "primary_key", "nullable"]:
            if param in field_def:
                field_kwargs[param] = field_def[param]

        # Extract metadata from nested object if present
        metadata = field_def.get("metadata", {}) or {}

        # Handle unit (check both metadata and top-level)
        unit_value = metadata.get("unit") or field_def.get("unit")
        if unit_value:
            field_kwargs["unit"] = unit_value

        # Handle glossary_term (check both metadata and top-level)
        glossary_value = metadata.get("glossary_term") or field_def.get("glossary_term")
        if glossary_value:
            field_kwargs["glossary_term"] = glossary_value

        # Handle format (check both constraints and top-level)
        format_value = constraints.get("format") or field_def.get("format")
        if format_value:
            try:
                field_kwargs["format"] = FieldFormat(format_value)
            except ValueError:
                pass  # Skip invalid format values

        # Handle aggregation (check both metadata and top-level)
        aggregation_value = metadata.get("aggregation") or field_def.get("aggregation")
        if aggregation_value:
            from griot_core.types import AggregationType

            try:
                field_kwargs["aggregation"] = AggregationType(aggregation_value)
            except ValueError:
                pass  # Skip invalid aggregation values

        # Handle default value
        if "default" in field_def:
            field_kwargs["default"] = field_def["default"]

        namespace[field_name] = Field(**field_kwargs)

    # Create the dynamic class
    contract_cls = type(name, (GriotModel,), namespace)

    # T-310: Set contract-level metadata on the created class
    contract_cls._griot_api_version = api_version
    contract_cls._griot_kind = kind
    contract_cls._griot_id = contract_id
    contract_cls._griot_version = version
    contract_cls._griot_status = status

    # T-329: Parse and set all ODCS sections
    _parse_odcs_sections(contract_cls, data)

    return contract_cls


def _parse_odcs_sections(contract_cls: type, data: dict[str, Any]) -> None:
    """
    Parse and set all ODCS sections on a contract class (T-329).

    Args:
        contract_cls: The contract class to configure.
        data: Dictionary containing the contract definition.
    """
    from griot_core.types import (
        AccessApproval,
        AccessConfig,
        AccessGrant,
        AccessLevel,
        AccuracySLA,
        ApprovalRecord,
        AuditRequirements,
        AvailabilitySLA,
        ChangeManagement,
        CheckType,
        Compliance,
        CompletenessSLA,
        CrossBorder,
        CustomCheck,
        CustomProperty,
        Description,
        Distribution,
        DistributionChannel,
        DistributionType,
        FreshnessSLA,
        Governance,
        GovernanceConsumer,
        GovernanceProducer,
        LegalBasis,
        Legal,
        QualityRule,
        QualityRuleType,
        ResponseTimeSLA,
        ReviewCadence,
        ReviewConfig,
        Role,
        SensitivityLevel,
        Server,
        SLA,
        Steward,
        Team,
        Timestamps,
    )

    # Parse description section
    if "description" in data and isinstance(data["description"], dict):
        desc_data = data["description"]
        custom_props = []
        if "customProperties" in desc_data:
            for prop in desc_data["customProperties"]:
                custom_props.append(
                    CustomProperty(
                        name=prop.get("name", ""),
                        value=prop.get("value", ""),
                        description=prop.get("description"),
                    )
                )
        contract_cls._griot_description = Description(
            purpose=desc_data.get("purpose"),
            usage=desc_data.get("usage"),
            limitations=desc_data.get("limitations"),
            custom_properties=custom_props,
        )

    # Parse quality rules section
    if "quality" in data and isinstance(data["quality"], list):
        quality_rules = []
        for rule_data in data["quality"]:
            if "rule" in rule_data:
                try:
                    rule_type = QualityRuleType(rule_data["rule"])
                    quality_rules.append(
                        QualityRule(
                            rule=rule_type,
                            min_percent=rule_data.get("min_percent"),
                            critical_fields=rule_data.get("critical_fields"),
                            max_error_rate=rule_data.get("max_error_rate"),
                            validation_method=rule_data.get("validation_method"),
                            max_age=rule_data.get("max_age"),
                            timestamp_field=rule_data.get("timestamp_field"),
                            min_rows=rule_data.get("min_rows"),
                            max_rows=rule_data.get("max_rows"),
                            field=rule_data.get("field"),
                            expected_distribution=rule_data.get("expected_distribution"),
                        )
                    )
                except ValueError:
                    pass  # Skip invalid rule types
        contract_cls._griot_quality_rules = quality_rules

    # Parse custom checks section
    if "custom_checks" in data and isinstance(data["custom_checks"], list):
        custom_checks = []
        for check_data in data["custom_checks"]:
            try:
                check_type = CheckType(check_data.get("type", "sql"))
                custom_checks.append(
                    CustomCheck(
                        name=check_data.get("name", ""),
                        type=check_type,
                        definition=check_data.get("definition", ""),
                        severity=Severity(check_data["severity"]) if "severity" in check_data else None,
                    )
                )
            except ValueError:
                pass  # Skip invalid check types
        contract_cls._griot_custom_checks = custom_checks

    # Parse legal section
    if "legal" in data and isinstance(data["legal"], dict):
        legal_data = data["legal"]
        cross_border = None
        if "cross_border" in legal_data and isinstance(legal_data["cross_border"], dict):
            cb_data = legal_data["cross_border"]
            cross_border = CrossBorder(
                restrictions=cb_data.get("restrictions", []),
                transfer_mechanisms=cb_data.get("transfer_mechanisms", []),
                data_residency=cb_data.get("data_residency"),
            )
        contract_cls._griot_legal = Legal(
            jurisdiction=legal_data.get("jurisdiction", []),
            basis=LegalBasis(legal_data["basis"]) if "basis" in legal_data else None,
            consent_id=legal_data.get("consent_id"),
            regulations=legal_data.get("regulations", []),
            cross_border=cross_border,
        )

    # Parse compliance section
    if "compliance" in data and isinstance(data["compliance"], dict):
        comp_data = data["compliance"]
        audit_reqs = None
        if "audit_requirements" in comp_data and isinstance(comp_data["audit_requirements"], dict):
            ar_data = comp_data["audit_requirements"]
            audit_reqs = AuditRequirements(
                logging=ar_data.get("logging", False),
                log_retention=ar_data.get("log_retention"),
            )
        contract_cls._griot_compliance = Compliance(
            data_classification=SensitivityLevel(comp_data["data_classification"]) if "data_classification" in comp_data else None,
            regulatory_scope=comp_data.get("regulatory_scope", []),
            audit_requirements=audit_reqs,
            certification_requirements=comp_data.get("certification_requirements", []),
            export_restrictions=comp_data.get("export_restrictions"),
        )

    # Parse SLA section
    if "sla" in data and isinstance(data["sla"], dict):
        sla_data = data["sla"]
        availability = None
        if "availability" in sla_data:
            av_data = sla_data["availability"]
            availability = AvailabilitySLA(
                target_percent=av_data.get("target_percent", 99.0),
                measurement_window=av_data.get("measurement_window"),
            )
        freshness = None
        if "freshness" in sla_data:
            fr_data = sla_data["freshness"]
            freshness = FreshnessSLA(
                target=fr_data.get("target", "P1D"),
                measurement_field=fr_data.get("measurement_field"),
            )
        completeness = None
        if "completeness" in sla_data:
            co_data = sla_data["completeness"]
            completeness = CompletenessSLA(
                target_percent=co_data.get("target_percent", 99.0),
                critical_fields=co_data.get("critical_fields", []),
                critical_target_percent=co_data.get("critical_target_percent"),
            )
        accuracy = None
        if "accuracy" in sla_data:
            ac_data = sla_data["accuracy"]
            accuracy = AccuracySLA(
                error_rate_target=ac_data.get("error_rate_target", 0.001),
                validation_method=ac_data.get("validation_method"),
            )
        response_time = None
        if "response_time" in sla_data:
            rt_data = sla_data["response_time"]
            response_time = ResponseTimeSLA(
                p50_ms=rt_data.get("p50_ms"),
                p99_ms=rt_data.get("p99_ms"),
            )
        contract_cls._griot_sla = SLA(
            availability=availability,
            freshness=freshness,
            completeness=completeness,
            accuracy=accuracy,
            response_time=response_time,
        )

    # Parse access section
    if "access" in data and isinstance(data["access"], dict):
        access_data = data["access"]
        grants = []
        if "grants" in access_data:
            for grant_data in access_data["grants"]:
                grants.append(
                    AccessGrant(
                        principal=grant_data.get("principal", ""),
                        level=AccessLevel(grant_data.get("level", "read")),
                        fields=grant_data.get("fields"),
                        expiry=grant_data.get("expiry"),
                        conditions=grant_data.get("conditions"),
                    )
                )
        approval = None
        if "approval" in access_data:
            ap_data = access_data["approval"]
            approval = AccessApproval(
                required=ap_data.get("required", False),
                approvers=ap_data.get("approvers", []),
                workflow=ap_data.get("workflow"),
            )
        contract_cls._griot_access = AccessConfig(
            default_level=AccessLevel(access_data["default_level"]) if "default_level" in access_data else None,
            grants=grants,
            approval=approval,
            authentication=access_data.get("authentication"),
        )

    # Parse distribution section
    if "distribution" in data and isinstance(data["distribution"], dict):
        dist_data = data["distribution"]
        channels = []
        if "channels" in dist_data:
            for ch_data in dist_data["channels"]:
                channels.append(
                    DistributionChannel(
                        type=DistributionType(ch_data.get("type", "warehouse")),
                        identifier=ch_data.get("identifier", ""),
                        format=ch_data.get("format"),
                        partitioning=ch_data.get("partitioning"),
                    )
                )
        contract_cls._griot_distribution = Distribution(channels=channels)

    # Parse governance section
    if "governance" in data and isinstance(data["governance"], dict):
        gov_data = data["governance"]
        producer = None
        if "producer" in gov_data:
            pr_data = gov_data["producer"]
            producer = GovernanceProducer(
                team=pr_data.get("team", ""),
                contact=pr_data.get("contact"),
                responsibilities=pr_data.get("responsibilities", []),
            )
        consumers = []
        if "consumers" in gov_data:
            for con_data in gov_data["consumers"]:
                consumers.append(
                    GovernanceConsumer(
                        team=con_data.get("team", ""),
                        contact=con_data.get("contact"),
                        use_case=con_data.get("use_case"),
                        approved_date=con_data.get("approved_date"),
                        approved_by=con_data.get("approved_by"),
                    )
                )
        approval_chain = []
        if "approval_chain" in gov_data:
            for ap_data in gov_data["approval_chain"]:
                approval_chain.append(
                    ApprovalRecord(
                        role=ap_data.get("role", ""),
                        approver=ap_data.get("approver"),
                        approved_date=ap_data.get("approved_date"),
                        comments=ap_data.get("comments"),
                    )
                )
        review = None
        if "review" in gov_data:
            rv_data = gov_data["review"]
            review = ReviewConfig(
                cadence=ReviewCadence(rv_data["cadence"]) if "cadence" in rv_data else None,
                last_review=rv_data.get("last_review"),
                next_review=rv_data.get("next_review"),
                reviewers=rv_data.get("reviewers", []),
            )
        change_mgmt = None
        if "change_management" in gov_data:
            cm_data = gov_data["change_management"]
            change_mgmt = ChangeManagement(
                breaking_change_notice=cm_data.get("breaking_change_notice"),
                deprecation_notice=cm_data.get("deprecation_notice"),
                communication_channels=cm_data.get("communication_channels", []),
                migration_support=cm_data.get("migration_support", False),
            )
        contract_cls._griot_governance = Governance(
            producer=producer,
            consumers=consumers,
            approval_chain=approval_chain,
            review=review,
            change_management=change_mgmt,
            dispute_resolution=gov_data.get("dispute_resolution"),
            documentation=gov_data.get("documentation"),
        )

    # Parse team section
    if "team" in data and isinstance(data["team"], dict):
        team_data = data["team"]
        steward = None
        if "steward" in team_data:
            st_data = team_data["steward"]
            steward = Steward(
                name=st_data.get("name", ""),
                email=st_data.get("email"),
            )
        contract_cls._griot_team = Team(
            name=team_data.get("name", ""),
            department=team_data.get("department"),
            steward=steward,
        )

    # Parse servers section
    if "servers" in data and isinstance(data["servers"], list):
        servers = []
        for srv_data in data["servers"]:
            servers.append(
                Server(
                    server=srv_data.get("server", ""),
                    environment=srv_data.get("environment", ""),
                    type=srv_data.get("type", ""),
                    project=srv_data.get("project", ""),
                    dataset=srv_data.get("dataset", ""),
                )
            )
        contract_cls._griot_servers = servers

    # Parse roles section
    if "roles" in data and isinstance(data["roles"], list):
        roles = []
        for role_data in data["roles"]:
            roles.append(
                Role(
                    role=role_data.get("role", ""),
                    access=AccessLevel(role_data.get("access", "read")),
                )
            )
        contract_cls._griot_roles = roles

    # Parse timestamps section
    if "timestamps" in data and isinstance(data["timestamps"], dict):
        ts_data = data["timestamps"]
        contract_cls._griot_timestamps = Timestamps(
            created_at=ts_data.get("created_at"),
            updated_at=ts_data.get("updated_at"),
            effective_from=ts_data.get("effective_from"),
            effective_until=ts_data.get("effective_until"),
        )


def model_to_yaml(model: type[GriotModel]) -> str:
    """
    Export a GriotModel to YAML format.

    Uses the list format for fields to match the registry schema:
    fields:
    - name: field1
      type: string
      ...

    Args:
        model: The GriotModel class to export.

    Returns:
        YAML string representation.
    """
    data = model_to_dict(model)
    return yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True)


def model_to_dict(model: type[GriotModel]) -> dict[str, Any]:
    """
    Export a GriotModel to a dictionary (T-310 enhanced).

    Uses the ODCS format with contract-level metadata.
    Includes api_version, kind, id, version, status.

    Args:
        model: The GriotModel class to export.

    Returns:
        Dictionary representation of the contract in ODCS format.
    """
    # T-310: Contract-level metadata
    data: dict[str, Any] = {
        "api_version": model._griot_api_version,
        "kind": model._griot_kind,
        "name": model.__name__,
        "version": model._griot_version,
        "status": model._griot_status.value,
    }

    # Add optional ID if set
    if model._griot_id:
        data["id"] = model._griot_id

    if model.__doc__:
        data["description"] = model.__doc__.strip()

    fields_list: list[dict[str, Any]] = []

    for field_name, field_info in model._griot_fields.items():
        field_dict: dict[str, Any] = {
            "name": field_name,
            "type": field_info.type.value,
            "description": field_info.description,
            "nullable": field_info.nullable,
            "primary_key": field_info.primary_key,
            "unique": field_info.unique,
        }

        # Build constraints object
        constraints: dict[str, Any] = {}
        for constraint in [
            "min_length",
            "max_length",
            "pattern",
            "ge",
            "le",
            "gt",
            "lt",
            "multiple_of",
        ]:
            value = getattr(field_info, constraint)
            if value is not None:
                constraints[constraint] = value

        if field_info.format:
            constraints["format"] = field_info.format.value

        if field_info.enum:
            constraints["enum"] = field_info.enum

        field_dict["constraints"] = constraints

        # Build metadata object
        metadata: dict[str, Any] = {}
        if field_info.unit:
            metadata["unit"] = field_info.unit
        if field_info.aggregation:
            metadata["aggregation"] = field_info.aggregation.value
        if field_info.glossary_term:
            metadata["glossary_term"] = field_info.glossary_term

        field_dict["metadata"] = metadata if metadata else None

        # Additional top-level fields
        if field_info.has_default:
            field_dict["default"] = field_info.default

        fields_list.append(field_dict)

    data["fields"] = fields_list

    # T-328: Add all ODCS sections
    odcs_sections = model.get_odcs_sections()
    data.update(odcs_sections)

    # Add lineage if configured (Phase 2 compatibility)
    if model._griot_lineage_config:
        data["lineage"] = model._griot_lineage_config.to_dict()

    # Add residency if configured (Phase 2 compatibility)
    if model._griot_residency_config:
        data["residency"] = model._griot_residency_config.to_dict()

    return data


def diff_contracts(
    base: type[GriotModel],
    other: type[GriotModel],
) -> ContractDiff:
    """
    Compare two contract versions (T-302 enhanced).

    Args:
        base: The original contract version.
        other: The new contract version.

    Returns:
        ContractDiff describing the differences, including detailed breaking changes.
    """
    diff = ContractDiff()

    # T-302: Populate breaking_changes using detect_breaking_changes
    diff.breaking_changes = detect_breaking_changes(base, other)

    base_fields = set(base._griot_fields.keys())
    other_fields = set(other._griot_fields.keys())

    # Find added and removed fields
    diff.added_fields = list(other_fields - base_fields)
    diff.removed_fields = list(base_fields - other_fields)

    # Removed fields are breaking changes
    if diff.removed_fields:
        diff.has_breaking_changes = True

    # Check common fields for changes
    common_fields = base_fields & other_fields
    for field_name in common_fields:
        base_info = base._griot_fields[field_name]
        other_info = other._griot_fields[field_name]

        # Check type changes
        if base_info.type != other_info.type:
            is_breaking = not _is_type_widening(base_info.type, other_info.type)
            diff.type_changes.append(
                TypeChange(
                    field=field_name,
                    from_type=base_info.type.value,
                    to_type=other_info.type.value,
                    is_breaking=is_breaking,
                )
            )
            if is_breaking:
                diff.has_breaking_changes = True

        # Check constraint changes
        for constraint in [
            "min_length",
            "max_length",
            "ge",
            "le",
            "gt",
            "lt",
            "pattern",
            "enum",
        ]:
            base_val = getattr(base_info, constraint)
            other_val = getattr(other_info, constraint)
            if base_val != other_val:
                is_breaking = _is_constraint_breaking(constraint, base_val, other_val)
                diff.constraint_changes.append(
                    ConstraintChange(
                        field=field_name,
                        constraint=constraint,
                        from_value=base_val,
                        to_value=other_val,
                        is_breaking=is_breaking,
                    )
                )
                if is_breaking:
                    diff.has_breaking_changes = True

        # Check nullable changes (making non-nullable is breaking)
        if base_info.nullable and not other_info.nullable:
            diff.constraint_changes.append(
                ConstraintChange(
                    field=field_name,
                    constraint="nullable",
                    from_value=True,
                    to_value=False,
                    is_breaking=True,
                )
            )
            diff.has_breaking_changes = True

        # Check metadata changes (non-breaking)
        for attr in ["description", "unit", "aggregation", "glossary_term"]:
            base_val = getattr(base_info, attr)
            other_val = getattr(other_info, attr)
            if base_val != other_val:
                diff.metadata_changes.append(
                    MetadataChange(
                        field=field_name,
                        attribute=attr,
                        from_value=base_val,
                        to_value=other_val,
                    )
                )

    return diff


def lint_contract(model: type[GriotModel]) -> list[LintIssue]:
    """
    Check a contract for quality issues.

    Args:
        model: The GriotModel class to lint.

    Returns:
        List of LintIssue objects describing any problems.
    """
    issues: list[LintIssue] = []

    # G001: No primary key defined
    if model._griot_primary_key is None:
        issues.append(
            LintIssue(
                code="G001",
                field=None,
                message="No primary key defined",
                severity=Severity.WARNING,
                suggestion="Add primary_key=True to a unique identifier field",
            )
        )

    for field_name, field_info in model._griot_fields.items():
        # G002: Missing description
        if (
            not field_info.description
            or field_info.description == f"Field: {field_name}"
        ):
            issues.append(
                LintIssue(
                    code="G002",
                    field=field_name,
                    message="Field has no meaningful description",
                    severity=Severity.WARNING,
                    suggestion="Add a description explaining the field's purpose",
                )
            )

        # G003: String field without constraints
        if field_info.type == DataType.STRING:
            if (
                field_info.max_length is None
                and field_info.pattern is None
                and field_info.format is None
                and field_info.enum is None
            ):
                issues.append(
                    LintIssue(
                        code="G003",
                        field=field_name,
                        message="String field has no length or format constraints",
                        severity=Severity.INFO,
                        suggestion="Consider adding max_length, pattern, format, or enum",
                    )
                )

        # G004: Numeric field without range
        if field_info.type in (DataType.INTEGER, DataType.FLOAT):
            if all(
                getattr(field_info, c) is None for c in ["ge", "le", "gt", "lt"]
            ):
                issues.append(
                    LintIssue(
                        code="G004",
                        field=field_name,
                        message="Numeric field has no range constraints",
                        severity=Severity.INFO,
                        suggestion="Consider adding ge/le/gt/lt constraints",
                    )
                )

        # G005: Field name style
        if not _is_valid_field_name(field_name):
            issues.append(
                LintIssue(
                    code="G005",
                    field=field_name,
                    message="Field name should be snake_case",
                    severity=Severity.WARNING,
                    suggestion="Rename to snake_case format",
                )
            )

    return issues


def _is_valid_field_name(name: str) -> bool:
    """Check if a field name follows snake_case convention."""
    import re

    return bool(re.match(r"^[a-z][a-z0-9_]*$", name))


def _is_type_widening(from_type: DataType, to_type: DataType) -> bool:
    """Check if type change is a widening (non-breaking) conversion."""
    # int -> float is widening
    if from_type == DataType.INTEGER and to_type == DataType.FLOAT:
        return True
    # Any specific type -> any is widening
    if to_type == DataType.ANY:
        return True
    return False


def _is_constraint_breaking(
    constraint: str,
    old_value: Any,
    new_value: Any,
) -> bool:
    """Determine if a constraint change is breaking."""
    if old_value is None:
        # Adding a new constraint is breaking
        return new_value is not None

    if new_value is None:
        # Removing a constraint is not breaking
        return False

    # For range constraints, check if the new range is narrower
    if constraint in ("ge", "gt"):
        # Increasing lower bound is breaking
        return new_value > old_value
    if constraint in ("le", "lt"):
        # Decreasing upper bound is breaking
        return new_value < old_value
    if constraint in ("min_length",):
        # Increasing minimum is breaking
        return new_value > old_value
    if constraint in ("max_length",):
        # Decreasing maximum is breaking
        return new_value < old_value
    if constraint == "pattern":
        # Any pattern change could be breaking
        return True
    if constraint == "enum":
        # Removing values is breaking
        old_set = set(old_value) if old_value else set()
        new_set = set(new_value) if new_value else set()
        return bool(old_set - new_set)

    return True


def _type_str_to_python(type_str: str) -> type:
    """Convert a type string to Python type."""
    type_map = {
        "string": str,
        "str": str,
        "integer": int,
        "int": int,
        "float": float,
        "number": float,
        "boolean": bool,
        "bool": bool,
        "array": list,
        "list": list,
        "object": dict,
        "dict": dict,
        "date": str,
        "datetime": str,
        "any": object,
    }
    return type_map.get(type_str.lower(), str)


# =============================================================================
# Breaking Change Detection (T-300, T-301, T-302)
# =============================================================================


def detect_breaking_changes(
    base: type[GriotModel],
    other: type[GriotModel],
) -> list[BreakingChange]:
    """
    Detect all breaking changes between two contract versions (T-301).

    Breaking changes are changes that could cause existing data consumers
    to fail or produce incorrect results. Based on ODCS breaking change rules.

    Breaking Change Rules (T-300):
    - Field removal = BREAKING
    - Field type change (incompatible) = BREAKING
    - Field rename = BREAKING (detected as remove + add with same type)
    - Adding required (non-nullable) field without default = BREAKING
    - Removing enum values = BREAKING
    - Tightening constraints (reducing max_length, stricter pattern) = BREAKING
    - Making nullable field non-nullable = BREAKING
    - Changing primary key = BREAKING

    Args:
        base: The original (current) contract version.
        other: The new (proposed) contract version.

    Returns:
        List of BreakingChange objects describing each breaking change.

    Example:
        changes = detect_breaking_changes(ContractV1, ContractV2)
        if changes:
            print("Cannot upgrade: breaking changes detected")
            for change in changes:
                print(f"  - {change}")
    """
    breaking_changes: list[BreakingChange] = []

    base_fields = set(base._griot_fields.keys())
    other_fields = set(other._griot_fields.keys())

    removed_fields = base_fields - other_fields
    added_fields = other_fields - base_fields
    common_fields = base_fields & other_fields

    # Rule 1: Field removal is BREAKING
    for field_name in removed_fields:
        field_info = base._griot_fields[field_name]
        breaking_changes.append(
            BreakingChange(
                change_type=BreakingChangeType.FIELD_REMOVED,
                field=field_name,
                description=f"Field '{field_name}' was removed",
                from_value=field_info.type.value,
                to_value=None,
                migration_hint="Add the field back or migrate consumers to not depend on this field",
            )
        )

    # Rule 2: Adding required field without default is BREAKING
    for field_name in added_fields:
        field_info = other._griot_fields[field_name]
        if not field_info.nullable and not field_info.has_default:
            breaking_changes.append(
                BreakingChange(
                    change_type=BreakingChangeType.REQUIRED_FIELD_ADDED,
                    field=field_name,
                    description=f"Required field '{field_name}' added without default value",
                    from_value=None,
                    to_value=field_info.type.value,
                    migration_hint="Make the field nullable or provide a default value",
                )
            )

    # Check field rename heuristic (removed + added with same type)
    _detect_potential_renames(base, other, removed_fields, added_fields, breaking_changes)

    # Check common fields for breaking changes
    for field_name in common_fields:
        base_info = base._griot_fields[field_name]
        other_info = other._griot_fields[field_name]

        # Rule 3: Incompatible type change is BREAKING
        if base_info.type != other_info.type:
            if not _is_type_widening(base_info.type, other_info.type):
                breaking_changes.append(
                    BreakingChange(
                        change_type=BreakingChangeType.TYPE_CHANGED_INCOMPATIBLE,
                        field=field_name,
                        description=f"Type changed from '{base_info.type.value}' to '{other_info.type.value}'",
                        from_value=base_info.type.value,
                        to_value=other_info.type.value,
                        migration_hint="Use a compatible type or create a new field",
                    )
                )

        # Rule 4: Making nullable field non-nullable is BREAKING
        if base_info.nullable and not other_info.nullable:
            breaking_changes.append(
                BreakingChange(
                    change_type=BreakingChangeType.NULLABLE_TO_REQUIRED,
                    field=field_name,
                    description=f"Field '{field_name}' changed from nullable to required",
                    from_value=True,
                    to_value=False,
                    migration_hint="Keep the field nullable or ensure all existing data has values",
                )
            )

        # Rule 5: Removing enum values is BREAKING
        if base_info.enum is not None and other_info.enum is not None:
            removed_values = set(base_info.enum) - set(other_info.enum)
            if removed_values:
                breaking_changes.append(
                    BreakingChange(
                        change_type=BreakingChangeType.ENUM_VALUES_REMOVED,
                        field=field_name,
                        description=f"Enum values removed: {sorted(removed_values)}",
                        from_value=base_info.enum,
                        to_value=other_info.enum,
                        migration_hint="Add the removed values back or migrate existing data",
                    )
                )
        elif base_info.enum is not None and other_info.enum is None:
            # Removing enum entirely is not breaking (widening)
            pass
        elif base_info.enum is None and other_info.enum is not None:
            # Adding enum constraint is breaking (narrowing)
            breaking_changes.append(
                BreakingChange(
                    change_type=BreakingChangeType.CONSTRAINT_TIGHTENED,
                    field=field_name,
                    description=f"Enum constraint added: {other_info.enum}",
                    from_value=None,
                    to_value=other_info.enum,
                    migration_hint="Remove the enum constraint or ensure all existing values are valid",
                )
            )

        # Rule 6: Tightening constraints is BREAKING
        _detect_constraint_tightening(field_name, base_info, other_info, breaking_changes)

        # Rule 7: Pattern change is potentially BREAKING
        if base_info.pattern != other_info.pattern:
            if base_info.pattern is None and other_info.pattern is not None:
                # Adding pattern is breaking (more restrictive)
                breaking_changes.append(
                    BreakingChange(
                        change_type=BreakingChangeType.PATTERN_CHANGED,
                        field=field_name,
                        description=f"Pattern constraint added: {other_info.pattern}",
                        from_value=None,
                        to_value=other_info.pattern,
                        migration_hint="Remove the pattern or ensure all existing values match",
                    )
                )
            elif base_info.pattern is not None and other_info.pattern is not None:
                # Pattern changed - assume breaking unless we can prove otherwise
                breaking_changes.append(
                    BreakingChange(
                        change_type=BreakingChangeType.PATTERN_CHANGED,
                        field=field_name,
                        description=f"Pattern changed from '{base_info.pattern}' to '{other_info.pattern}'",
                        from_value=base_info.pattern,
                        to_value=other_info.pattern,
                        migration_hint="Verify all existing values match the new pattern",
                    )
                )

    # Rule 8: Primary key changes are BREAKING
    if base._griot_primary_key != other._griot_primary_key:
        breaking_changes.append(
            BreakingChange(
                change_type=BreakingChangeType.PRIMARY_KEY_CHANGED,
                field=None,
                description=f"Primary key changed from '{base._griot_primary_key}' to '{other._griot_primary_key}'",
                from_value=base._griot_primary_key,
                to_value=other._griot_primary_key,
                migration_hint="Keep the same primary key or coordinate with all consumers",
            )
        )

    return breaking_changes


def _detect_potential_renames(
    base: type[GriotModel],
    other: type[GriotModel],
    removed_fields: set[str],
    added_fields: set[str],
    breaking_changes: list[BreakingChange],
) -> None:
    """Detect potential field renames (heuristic: same type, description similarity)."""
    for removed in removed_fields:
        removed_info = base._griot_fields[removed]
        for added in added_fields:
            added_info = other._griot_fields[added]
            # Same type suggests possible rename
            if removed_info.type == added_info.type:
                # Check description similarity or other hints
                if _descriptions_similar(removed_info.description, added_info.description):
                    breaking_changes.append(
                        BreakingChange(
                            change_type=BreakingChangeType.FIELD_RENAMED,
                            field=removed,
                            description=f"Field possibly renamed from '{removed}' to '{added}'",
                            from_value=removed,
                            to_value=added,
                            migration_hint=f"If this is a rename, update consumers to use '{added}'",
                        )
                    )


def _descriptions_similar(desc1: str, desc2: str) -> bool:
    """Check if two descriptions are similar (simple heuristic)."""
    if not desc1 or not desc2:
        return False
    # Simple word overlap check
    words1 = set(desc1.lower().split())
    words2 = set(desc2.lower().split())
    if not words1 or not words2:
        return False
    overlap = len(words1 & words2) / min(len(words1), len(words2))
    return overlap > 0.5


def _detect_constraint_tightening(
    field_name: str,
    base_info: Any,
    other_info: Any,
    breaking_changes: list[BreakingChange],
) -> None:
    """Detect constraint tightening changes."""
    # max_length decreased
    if base_info.max_length is not None and other_info.max_length is not None:
        if other_info.max_length < base_info.max_length:
            breaking_changes.append(
                BreakingChange(
                    change_type=BreakingChangeType.CONSTRAINT_TIGHTENED,
                    field=field_name,
                    description=f"max_length reduced from {base_info.max_length} to {other_info.max_length}",
                    from_value=base_info.max_length,
                    to_value=other_info.max_length,
                    migration_hint="Increase max_length or truncate existing data",
                )
            )
    elif base_info.max_length is None and other_info.max_length is not None:
        breaking_changes.append(
            BreakingChange(
                change_type=BreakingChangeType.CONSTRAINT_TIGHTENED,
                field=field_name,
                description=f"max_length constraint added: {other_info.max_length}",
                from_value=None,
                to_value=other_info.max_length,
                migration_hint="Remove max_length or ensure all existing values fit",
            )
        )

    # min_length increased
    if base_info.min_length is not None and other_info.min_length is not None:
        if other_info.min_length > base_info.min_length:
            breaking_changes.append(
                BreakingChange(
                    change_type=BreakingChangeType.CONSTRAINT_TIGHTENED,
                    field=field_name,
                    description=f"min_length increased from {base_info.min_length} to {other_info.min_length}",
                    from_value=base_info.min_length,
                    to_value=other_info.min_length,
                    migration_hint="Decrease min_length or pad existing data",
                )
            )
    elif base_info.min_length is None and other_info.min_length is not None:
        breaking_changes.append(
            BreakingChange(
                change_type=BreakingChangeType.CONSTRAINT_TIGHTENED,
                field=field_name,
                description=f"min_length constraint added: {other_info.min_length}",
                from_value=None,
                to_value=other_info.min_length,
                migration_hint="Remove min_length or ensure all existing values meet minimum",
            )
        )

    # ge (greater than or equal) increased
    if base_info.ge is not None and other_info.ge is not None:
        if other_info.ge > base_info.ge:
            breaking_changes.append(
                BreakingChange(
                    change_type=BreakingChangeType.CONSTRAINT_TIGHTENED,
                    field=field_name,
                    description=f"Minimum value (ge) increased from {base_info.ge} to {other_info.ge}",
                    from_value=base_info.ge,
                    to_value=other_info.ge,
                    migration_hint="Decrease ge or update existing data below threshold",
                )
            )
    elif base_info.ge is None and other_info.ge is not None:
        breaking_changes.append(
            BreakingChange(
                change_type=BreakingChangeType.CONSTRAINT_TIGHTENED,
                field=field_name,
                description=f"ge constraint added: {other_info.ge}",
                from_value=None,
                to_value=other_info.ge,
                migration_hint="Remove ge or ensure all existing values meet minimum",
            )
        )

    # le (less than or equal) decreased
    if base_info.le is not None and other_info.le is not None:
        if other_info.le < base_info.le:
            breaking_changes.append(
                BreakingChange(
                    change_type=BreakingChangeType.CONSTRAINT_TIGHTENED,
                    field=field_name,
                    description=f"Maximum value (le) decreased from {base_info.le} to {other_info.le}",
                    from_value=base_info.le,
                    to_value=other_info.le,
                    migration_hint="Increase le or update existing data above threshold",
                )
            )
    elif base_info.le is None and other_info.le is not None:
        breaking_changes.append(
            BreakingChange(
                change_type=BreakingChangeType.CONSTRAINT_TIGHTENED,
                field=field_name,
                description=f"le constraint added: {other_info.le}",
                from_value=None,
                to_value=other_info.le,
                migration_hint="Remove le or ensure all existing values meet maximum",
            )
        )

    # gt (greater than) increased
    if base_info.gt is not None and other_info.gt is not None:
        if other_info.gt > base_info.gt:
            breaking_changes.append(
                BreakingChange(
                    change_type=BreakingChangeType.CONSTRAINT_TIGHTENED,
                    field=field_name,
                    description=f"Minimum value (gt) increased from {base_info.gt} to {other_info.gt}",
                    from_value=base_info.gt,
                    to_value=other_info.gt,
                    migration_hint="Decrease gt or update existing data below threshold",
                )
            )
    elif base_info.gt is None and other_info.gt is not None:
        breaking_changes.append(
            BreakingChange(
                change_type=BreakingChangeType.CONSTRAINT_TIGHTENED,
                field=field_name,
                description=f"gt constraint added: {other_info.gt}",
                from_value=None,
                to_value=other_info.gt,
                migration_hint="Remove gt or ensure all existing values meet minimum",
            )
        )

    # lt (less than) decreased
    if base_info.lt is not None and other_info.lt is not None:
        if other_info.lt < base_info.lt:
            breaking_changes.append(
                BreakingChange(
                    change_type=BreakingChangeType.CONSTRAINT_TIGHTENED,
                    field=field_name,
                    description=f"Maximum value (lt) decreased from {base_info.lt} to {other_info.lt}",
                    from_value=base_info.lt,
                    to_value=other_info.lt,
                    migration_hint="Increase lt or update existing data above threshold",
                )
            )
    elif base_info.lt is None and other_info.lt is not None:
        breaking_changes.append(
            BreakingChange(
                change_type=BreakingChangeType.CONSTRAINT_TIGHTENED,
                field=field_name,
                description=f"lt constraint added: {other_info.lt}",
                from_value=None,
                to_value=other_info.lt,
                migration_hint="Remove lt or ensure all existing values meet maximum",
            )
        )


