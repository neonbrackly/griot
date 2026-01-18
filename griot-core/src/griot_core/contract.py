"""
Griot Core Contract

Data contract definition and manipulation based on the Open Data Contract Standard (ODCS).
A GriotContract contains contract-level metadata and one or more schema definitions.
"""
from __future__ import annotations

from dataclasses import dataclass, field as dataclass_field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Iterator

import yaml

from griot_core.exceptions import ContractNotFoundError, ContractParseError
from griot_core.types import ContractStatus, Severity

if TYPE_CHECKING:
    from griot_core.schema import Schema

__all__ = [
    # Contract class
    "Contract",
    # Contract-level dataclasses
    "ContractDescription",
    "ContractTeam",
    "TeamMember",
    "ContractSupport",
    "ContractRole",
    "SLAProperty",
    "Server",
    # Loading functions
    "load_contract",
    "load_contract_from_string",
    "load_contract_from_dict",
    # Export functions
    "contract_to_yaml",
    "contract_to_dict",
    # Linting
    "lint_contract",
    "LintIssue",
    # Contract structure validation
    "validate_contract_structure",
    "ContractStructureResult",
    "ContractStructureIssue",
    # Key normalization
    "normalize_keys",
    "to_snake_case",
    "to_camel_case",
    # Constants
    "CONTRACT_FIELD_TYPES",
    "ODCS_MANDATORY_FIELDS",
]


# =============================================================================
# ODCS Key Normalization
# =============================================================================

_ODCS_KEY_MAP = {
    "apiVersion": "api_version",
    "dataProduct": "data_product",
    "authoritativeDefinitions": "authoritative_definitions",
    "slaProperties": "sla_properties",
    "contractCreatedTs": "contract_created_ts",
    "logicalType": "logical_type",
    "physicalType": "physical_type",
    "physicalName": "physical_name",
    "businessName": "business_name",
    "customProperties": "custom_properties",
    "partitionKeyPosition": "partition_key_position",
    "criticalDataElement": "critical_data_element",
}

_ODCS_KEY_MAP_REVERSE = {v: k for k, v in _ODCS_KEY_MAP.items()}


def to_snake_case(s: str) -> str:
    """Convert camelCase to snake_case."""
    if s in _ODCS_KEY_MAP:
        return _ODCS_KEY_MAP[s]
    result = []
    for i, c in enumerate(s):
        if c.isupper() and i > 0:
            result.append("_")
        result.append(c.lower())
    return "".join(result)


def to_camel_case(s: str) -> str:
    """Convert snake_case to camelCase."""
    if s in _ODCS_KEY_MAP_REVERSE:
        return _ODCS_KEY_MAP_REVERSE[s]
    parts = s.split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


def normalize_keys(data: dict[str, Any], to_format: str = "snake") -> dict[str, Any]:
    """Normalize keys between camelCase and snake_case recursively."""
    converter = to_snake_case if to_format == "snake" else to_camel_case
    result: dict[str, Any] = {}

    for key, value in data.items():
        new_key = converter(key)
        if isinstance(value, dict):
            result[new_key] = normalize_keys(value, to_format)
        elif isinstance(value, list):
            result[new_key] = [
                normalize_keys(item, to_format) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            result[new_key] = value

    return result


# =============================================================================
# ODCS Contract Schema Constants
# =============================================================================

CONTRACT_FIELD_TYPES: dict[str, type] = {
    "api_version": str,
    "kind": str,
    "id": str,
    "version": str,
    "status": str,
    "schema": list,
    "custom_properties": dict,
    "name": str,
    "data_product": str,
    "authoritative_definitions": list,
    "description": dict,
    "tags": list,
    "support": list,
    "team": dict,
    "roles": list,
    "sla_properties": list,
    "servers": list,
    "contract_created_ts": str,
}

ODCS_MANDATORY_FIELDS = frozenset({
    "api_version",
    "kind",
    "id",
    "version",
    "status",
    "schema",
    "custom_properties",
})


# =============================================================================
# Contract-Level Dataclasses
# =============================================================================


@dataclass
class ContractDescription:
    """Contract description metadata (ODCS description structure)."""

    purpose: str = ""
    usage: str = ""
    limitations: str = ""
    logical_type: str = "string"

    def to_dict(self) -> dict[str, Any]:
        """Convert to ODCS dictionary format."""
        result: dict[str, Any] = {}
        if self.purpose:
            result["purpose"] = self.purpose
        if self.usage:
            result["usage"] = self.usage
        if self.limitations:
            result["limitations"] = self.limitations
        if self.logical_type:
            result["logicalType"] = self.logical_type
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any] | str) -> ContractDescription:
        """Create from dictionary or string."""
        if isinstance(data, str):
            return cls(purpose=data)
        return cls(
            purpose=data.get("purpose", ""),
            usage=data.get("usage", ""),
            limitations=data.get("limitations", ""),
            logical_type=data.get("logical_type", "string"),
        )


@dataclass
class TeamMember:
    """Team member definition (ODCS team.members structure)."""

    username: str
    role: str = ""
    custom_properties: list[dict[str, Any]] = dataclass_field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to ODCS dictionary format."""
        result: dict[str, Any] = {"username": self.username}
        if self.role:
            result["role"] = self.role
        if self.custom_properties:
            result["customProperties"] = self.custom_properties
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TeamMember:
        """Create from dictionary."""
        return cls(
            username=data.get("username", ""),
            role=data.get("role", ""),
            custom_properties=data.get("custom_properties", []),
        )


@dataclass
class ContractTeam:
    """Contract team definition (ODCS team structure)."""

    id: str = ""
    name: str = ""
    description: str = ""
    members: list[TeamMember] = dataclass_field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to ODCS dictionary format."""
        result: dict[str, Any] = {}
        if self.id:
            result["id"] = self.id
        if self.name:
            result["name"] = self.name
        if self.description:
            result["description"] = self.description
        if self.members:
            result["members"] = [m.to_dict() for m in self.members]
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ContractTeam:
        """Create from dictionary."""
        members = [TeamMember.from_dict(m) for m in data.get("members", [])]
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            description=data.get("description", ""),
            members=members,
        )


@dataclass
class ContractSupport:
    """Contract support channel definition (ODCS support structure)."""

    id: str = ""
    channel: str = ""
    tool: str = ""
    scope: str = ""
    description: str = ""
    url: str = ""
    custom_properties: list[dict[str, Any]] = dataclass_field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to ODCS dictionary format."""
        result: dict[str, Any] = {}
        if self.id:
            result["id"] = self.id
        if self.channel:
            result["channel"] = self.channel
        if self.tool:
            result["tool"] = self.tool
        if self.scope:
            result["scope"] = self.scope
        if self.description:
            result["description"] = self.description
        if self.url:
            result["url"] = self.url
        if self.custom_properties:
            result["customProperties"] = self.custom_properties
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ContractSupport:
        """Create from dictionary."""
        return cls(
            id=data.get("id", ""),
            channel=data.get("channel", ""),
            tool=data.get("tool", ""),
            scope=data.get("scope", ""),
            description=data.get("description", ""),
            url=data.get("url", ""),
            custom_properties=data.get("custom_properties", []),
        )


@dataclass
class ContractRole:
    """Contract role/access definition (ODCS roles structure)."""

    role: str
    access: str = ""
    first_level_approvers: str = ""
    second_level_approvers: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to ODCS dictionary format."""
        result: dict[str, Any] = {"role": self.role}
        if self.access:
            result["access"] = self.access
        if self.first_level_approvers:
            result["firstLevelApprovers"] = self.first_level_approvers
        if self.second_level_approvers:
            result["secondLevelApprovers"] = self.second_level_approvers
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ContractRole:
        """Create from dictionary."""
        return cls(
            role=data.get("role", ""),
            access=data.get("access", ""),
            first_level_approvers=data.get("first_level_approvers", ""),
            second_level_approvers=data.get("second_level_approvers", ""),
        )


@dataclass
class SLAProperty:
    """SLA property definition (ODCS slaProperties structure)."""

    id: str = ""
    property: str = ""
    value: str | int | float = ""
    value_ext: str | int | float = ""
    unit: str = ""
    element: str = ""
    driver: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to ODCS dictionary format."""
        result: dict[str, Any] = {}
        if self.id:
            result["id"] = self.id
        if self.property:
            result["property"] = self.property
        if self.value:
            result["value"] = self.value
        if self.value_ext:
            result["valueExt"] = self.value_ext
        if self.unit:
            result["unit"] = self.unit
        if self.element:
            result["element"] = self.element
        if self.driver:
            result["driver"] = self.driver
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SLAProperty:
        """Create from dictionary."""
        return cls(
            id=data.get("id", ""),
            property=data.get("property", ""),
            value=data.get("value", ""),
            value_ext=data.get("value_ext", ""),
            unit=data.get("unit", ""),
            element=data.get("element", ""),
            driver=data.get("driver", ""),
        )


@dataclass
class Server:
    """Server/data source definition (ODCS servers structure)."""

    server: str
    type: str = ""
    description: str = ""
    environment: str = ""
    project: str = ""
    dataset: str = ""
    roles: list[str] = dataclass_field(default_factory=list)
    custom_properties: list[dict[str, Any]] = dataclass_field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to ODCS dictionary format."""
        result: dict[str, Any] = {"server": self.server}
        if self.type:
            result["type"] = self.type
        if self.description:
            result["description"] = self.description
        if self.environment:
            result["environment"] = self.environment
        if self.project:
            result["project"] = self.project
        if self.dataset:
            result["dataset"] = self.dataset
        if self.roles:
            result["roles"] = self.roles
        if self.custom_properties:
            result["customProperties"] = self.custom_properties
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Server:
        """Create from dictionary."""
        return cls(
            server=data.get("server", ""),
            type=data.get("type", ""),
            description=data.get("description", ""),
            environment=data.get("environment", ""),
            project=data.get("project", ""),
            dataset=data.get("dataset", ""),
            roles=data.get("roles", []),
            custom_properties=data.get("custom_properties", []),
        )


# =============================================================================
# Contract Class
# =============================================================================


class Contract:
    """
    Top-level data contract entity following ODCS.

    A Contract contains contract-level metadata and one or more Schema objects.
    This separation allows a single contract to govern multiple related schemas.

    Attributes:
        api_version: ODCS version (e.g., "v1.0.0")
        kind: Contract type (e.g., "DataContract")
        id: Unique contract identifier
        name: Human-readable contract name
        version: Contract version
        status: Lifecycle status (draft, active, deprecated, retired)
        schemas: List of Schema objects

    Example:
        from griot_core import Contract, Schema, Field

        class Employees(Schema):
            id: str = Field(description="Employee ID", primary_key=True)
            name: str = Field(description="Employee name")

        contract = Contract(
            id="emp-001",
            name="Employee Contract",
            version="1.0.0",
            schemas=[Employees()],
        )
    """

    def __init__(
        self,
        *,
        api_version: str = "v1.0.0",
        kind: str = "DataContract",
        id: str | None = None,
        name: str = "",
        version: str = "1.0.0",
        status: ContractStatus | str = ContractStatus.DRAFT,
        data_product: str = "",
        description: ContractDescription | dict[str, Any] | str | None = None,
        tags: list[str] | None = None,
        team: ContractTeam | dict[str, Any] | None = None,
        roles: list[ContractRole | dict[str, Any]] | None = None,
        servers: list[Server | dict[str, Any]] | None = None,
        sla_properties: list[SLAProperty | dict[str, Any]] | None = None,
        support: list[ContractSupport | dict[str, Any]] | None = None,
        authoritative_definitions: list[dict[str, Any]] | None = None,
        custom_properties: dict[str, Any] | None = None,
        schemas: list[Schema] | None = None,
    ) -> None:
        self.api_version = api_version
        self.kind = kind
        self.id = id
        self.name = name
        self.version = version

        if isinstance(status, str):
            try:
                self.status = ContractStatus(status)
            except ValueError:
                self.status = ContractStatus.DRAFT
        else:
            self.status = status

        self.data_product = data_product

        if description is None:
            self.description = ContractDescription()
        elif isinstance(description, ContractDescription):
            self.description = description
        else:
            self.description = ContractDescription.from_dict(description)

        self.tags = tags or []

        if team is None:
            self.team: ContractTeam | None = None
        elif isinstance(team, ContractTeam):
            self.team = team
        else:
            self.team = ContractTeam.from_dict(team)

        self.roles: list[ContractRole] = []
        if roles:
            for role in roles:
                if isinstance(role, ContractRole):
                    self.roles.append(role)
                else:
                    self.roles.append(ContractRole.from_dict(role))

        self.servers: list[Server] = []
        if servers:
            for server in servers:
                if isinstance(server, Server):
                    self.servers.append(server)
                else:
                    self.servers.append(Server.from_dict(server))

        self.sla_properties: list[SLAProperty] = []
        if sla_properties:
            for sla in sla_properties:
                if isinstance(sla, SLAProperty):
                    self.sla_properties.append(sla)
                else:
                    self.sla_properties.append(SLAProperty.from_dict(sla))

        self.support: list[ContractSupport] = []
        if support:
            for sup in support:
                if isinstance(sup, ContractSupport):
                    self.support.append(sup)
                else:
                    self.support.append(ContractSupport.from_dict(sup))

        self.authoritative_definitions = authoritative_definitions or []
        self.custom_properties = custom_properties or {}
        self._schemas: list[Schema] = schemas or []

    # -------------------------------------------------------------------------
    # Schema Management
    # -------------------------------------------------------------------------

    @property
    def schemas(self) -> list[Schema]:
        """Get all schemas in this contract."""
        return self._schemas

    def add_schema(self, schema: Schema) -> None:
        """Add a schema to this contract."""
        self._schemas.append(schema)

    def remove_schema(self, schema: Schema) -> bool:
        """Remove a schema from this contract."""
        try:
            self._schemas.remove(schema)
            return True
        except ValueError:
            return False

    def get_schema(self, index: int) -> Schema | None:
        """Get schema by index."""
        if 0 <= index < len(self._schemas):
            return self._schemas[index]
        return None

    def get_schema_by_id(self, schema_id: str) -> Schema | None:
        """Get schema by its ID."""
        for schema in self._schemas:
            if schema.id == schema_id:
                return schema
        return None

    def get_schema_by_name(self, name: str) -> Schema | None:
        """Get schema by its name."""
        for schema in self._schemas:
            if schema.name == name:
                return schema
        return None

    def list_schemas(self) -> list[Schema]:
        """List all schemas in this contract."""
        return list(self._schemas)

    def list_schema_names(self) -> list[str]:
        """List names of all schemas in this contract."""
        return [s.name for s in self._schemas]

    def __iter__(self) -> Iterator[Schema]:
        """Iterate over schemas."""
        return iter(self._schemas)

    def __len__(self) -> int:
        """Return number of schemas."""
        return len(self._schemas)

    # -------------------------------------------------------------------------
    # Serialization
    # -------------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Convert to ODCS dictionary format (camelCase keys)."""
        result: dict[str, Any] = {
            "apiVersion": self.api_version,
            "kind": self.kind,
            "version": self.version,
            "status": self.status.value,
        }

        if self.id:
            result["id"] = self.id
        if self.name:
            result["name"] = self.name
        if self.data_product:
            result["dataProduct"] = self.data_product
        if self.authoritative_definitions:
            result["authoritativeDefinitions"] = self.authoritative_definitions

        desc_dict = self.description.to_dict()
        if desc_dict:
            result["description"] = desc_dict

        if self.tags:
            result["tags"] = self.tags
        if self._schemas:
            result["schema"] = [s.to_dict() for s in self._schemas]
        if self.support:
            result["support"] = [s.to_dict() for s in self.support]
        if self.team:
            result["team"] = self.team.to_dict()
        if self.roles:
            result["roles"] = [r.to_dict() for r in self.roles]
        if self.sla_properties:
            result["slaProperties"] = [s.to_dict() for s in self.sla_properties]
        if self.servers:
            result["servers"] = [s.to_dict() for s in self.servers]
        if self.custom_properties:
            result["customProperties"] = self.custom_properties

        return result

    def to_yaml(self) -> str:
        """Export contract to YAML string."""
        return yaml.dump(
            self.to_dict(),
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
        )

    # -------------------------------------------------------------------------
    # Class Methods for Loading
    # -------------------------------------------------------------------------

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Contract:
        """Create Contract from dictionary."""
        from griot_core.schema import Schema

        data = normalize_keys(data, to_format="snake")

        schemas: list[Schema] = []
        for s in data.get("schema", []):
            schemas.append(Schema.from_dict(s))

        return cls(
            api_version=data.get("api_version", "v1.0.0"),
            kind=data.get("kind", "DataContract"),
            id=data.get("id"),
            name=data.get("name", ""),
            version=data.get("version", "1.0.0"),
            status=data.get("status", "draft"),
            data_product=data.get("data_product", ""),
            description=data.get("description"),
            tags=data.get("tags", []),
            team=data.get("team"),
            roles=data.get("roles", []),
            servers=data.get("servers", []),
            sla_properties=data.get("sla_properties", []),
            support=data.get("support", []),
            authoritative_definitions=data.get("authoritative_definitions", []),
            custom_properties=data.get("custom_properties", {}),
            schemas=schemas,
        )

    @classmethod
    def from_yaml(cls, path: str) -> Contract:
        """Load Contract from YAML file."""
        file_path = Path(path)
        if not file_path.exists():
            raise ContractNotFoundError(str(path))

        try:
            content = file_path.read_text(encoding="utf-8")
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            raise ContractParseError(f"Invalid YAML: {e}") from e

        if not isinstance(data, dict):
            raise ContractParseError("Contract must be a YAML mapping")

        return cls.from_dict(data)

    @classmethod
    def from_yaml_string(cls, content: str) -> Contract:
        """Load Contract from YAML string."""
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            raise ContractParseError(f"Invalid YAML: {e}") from e

        if not isinstance(data, dict):
            raise ContractParseError("Contract must be a YAML mapping")

        return cls.from_dict(data)

    def __repr__(self) -> str:
        return f"<Contract id={self.id!r} name={self.name!r} version={self.version!r} schemas={len(self._schemas)}>"

    def __str__(self) -> str:
        return f"Contract({self.name or self.id or 'unnamed'}, {len(self._schemas)} schemas)"


# =============================================================================
# Loading Functions
# =============================================================================


def load_contract(path: str | Path) -> Contract:
    """Load a contract from a YAML file."""
    return Contract.from_yaml(str(path))


def load_contract_from_string(content: str) -> Contract:
    """Load a contract from a YAML string."""
    return Contract.from_yaml_string(content)


def load_contract_from_dict(data: dict[str, Any]) -> Contract:
    """Load a contract from a dictionary."""
    return Contract.from_dict(data)


# =============================================================================
# Export Functions
# =============================================================================


def contract_to_yaml(contract: Contract, camel_case: bool = True) -> str:
    """Export a Contract to YAML format."""
    data = contract_to_dict(contract, camel_case=camel_case)
    return yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True)


def contract_to_dict(contract: Contract, camel_case: bool = True) -> dict[str, Any]:
    """Export a Contract to dictionary format."""
    data = contract.to_dict()
    if not camel_case:
        data = normalize_keys(data, to_format="snake")
    return data


# =============================================================================
# Linting
# =============================================================================


@dataclass
class LintIssue:
    """Contract quality issue."""
    code: str
    field: str | None
    message: str
    severity: Severity
    suggestion: str | None = None


def lint_contract(contract: Contract) -> list[LintIssue]:
    """Check a Contract for quality issues and ODCS compliance."""
    issues: list[LintIssue] = []

    if not contract.id:
        issues.append(LintIssue(
            code="ODCS-001",
            field=None,
            message="Contract is missing required 'id' field",
            severity=Severity.ERROR,
            suggestion="Add a unique identifier",
        ))

    if contract.status not in ContractStatus:
        issues.append(LintIssue(
            code="ODCS-002",
            field=None,
            message="Contract has invalid status",
            severity=Severity.ERROR,
            suggestion="Use: draft, active, deprecated, or retired",
        ))

    if not contract.schemas:
        issues.append(LintIssue(
            code="ODCS-003",
            field=None,
            message="Contract has no schemas",
            severity=Severity.ERROR,
            suggestion="Add at least one schema to the contract",
        ))

    for schema in contract.schemas:
        if not schema.name:
            issues.append(LintIssue(
                code="ODCS-010",
                field=None,
                message="Schema is missing a name",
                severity=Severity.ERROR,
                suggestion="Add a name to the schema",
            ))

        fields = schema.fields
        if not fields:
            issues.append(LintIssue(
                code="ODCS-011",
                field=None,
                message=f"Schema '{schema.name}' has no properties",
                severity=Severity.ERROR,
                suggestion="Add at least one property to the schema",
            ))

        has_primary_key = False
        for field_name, field_info in fields.items():
            if field_info.primary_key:
                has_primary_key = True

            if not field_info.description:
                issues.append(LintIssue(
                    code="G001",
                    field=f"{schema.name}.{field_name}",
                    message="Field has no description",
                    severity=Severity.WARNING,
                    suggestion="Add a description",
                ))

        if not has_primary_key:
            issues.append(LintIssue(
                code="ODCS-004",
                field=None,
                message=f"Schema '{schema.name}' has no primary key defined",
                severity=Severity.WARNING,
                suggestion="Add primary_key=True to a field",
            ))

    return issues


# =============================================================================
# Contract Structure Validation
# =============================================================================


@dataclass
class ContractStructureIssue:
    """Issue found during contract structure validation."""

    code: str
    path: str
    message: str
    severity: Severity
    suggestion: str | None = None


@dataclass
class ContractStructureResult:
    """Result of contract structure validation."""

    is_valid: bool
    contract_id: str | None
    issues: list[ContractStructureIssue]
    error_count: int = 0
    warning_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "is_valid": self.is_valid,
            "contract_id": self.contract_id,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "issues": [
                {
                    "code": i.code,
                    "path": i.path,
                    "message": i.message,
                    "severity": i.severity.value,
                    "suggestion": i.suggestion,
                }
                for i in self.issues
            ],
        }

    def summary(self) -> str:
        """Return human-readable summary."""
        status = "VALID" if self.is_valid else "INVALID"
        return f"Contract structure {status}: {self.error_count} errors, {self.warning_count} warnings"


def validate_contract_structure(contract: Contract) -> ContractStructureResult:
    """Validate the structure of a Contract."""
    issues: list[ContractStructureIssue] = []

    if not contract.id:
        issues.append(ContractStructureIssue(
            code="CS-001",
            path="$.id",
            message="Contract is missing required 'id' field",
            severity=Severity.ERROR,
            suggestion="Add a unique identifier to the contract",
        ))

    if not contract.version:
        issues.append(ContractStructureIssue(
            code="CS-002",
            path="$.version",
            message="Contract is missing required 'version' field",
            severity=Severity.ERROR,
            suggestion="Add a semantic version (e.g., '1.0.0')",
        ))

    if contract.status not in ContractStatus:
        issues.append(ContractStructureIssue(
            code="CS-003",
            path="$.status",
            message=f"Invalid contract status: {contract.status}",
            severity=Severity.ERROR,
            suggestion="Use: draft, active, deprecated, or retired",
        ))

    if not contract.name:
        issues.append(ContractStructureIssue(
            code="CS-004",
            path="$.name",
            message="Contract is missing a name",
            severity=Severity.WARNING,
            suggestion="Add a human-readable name",
        ))

    if not contract.schemas:
        issues.append(ContractStructureIssue(
            code="CS-010",
            path="$.schema",
            message="Contract has no schemas defined",
            severity=Severity.ERROR,
            suggestion="Add at least one schema to the contract",
        ))
    else:
        for idx, schema in enumerate(contract.schemas):
            schema_path = f"$.schema[{idx}]"

            if not schema.name:
                issues.append(ContractStructureIssue(
                    code="CS-011",
                    path=f"{schema_path}.name",
                    message=f"Schema at index {idx} is missing a name",
                    severity=Severity.ERROR,
                    suggestion="Add a name to the schema",
                ))

            fields = schema.fields
            if not fields:
                issues.append(ContractStructureIssue(
                    code="CS-012",
                    path=f"{schema_path}.properties",
                    message=f"Schema '{schema.name}' has no properties defined",
                    severity=Severity.ERROR,
                    suggestion="Add at least one property to the schema",
                ))
            else:
                has_primary_key = False
                for field_name, field_info in fields.items():
                    field_path = f"{schema_path}.properties.{field_name}"

                    if field_info.primary_key:
                        has_primary_key = True

                    if not field_info.description:
                        issues.append(ContractStructureIssue(
                            code="CS-020",
                            path=f"{field_path}.description",
                            message=f"Field '{field_name}' has no description",
                            severity=Severity.WARNING,
                            suggestion="Add a description explaining the field's purpose",
                        ))

                if not has_primary_key:
                    issues.append(ContractStructureIssue(
                        code="CS-013",
                        path=f"{schema_path}.properties",
                        message=f"Schema '{schema.name}' has no primary key defined",
                        severity=Severity.WARNING,
                        suggestion="Add primary_key=true to one of the fields",
                    ))

    error_count = sum(1 for i in issues if i.severity == Severity.ERROR)
    warning_count = sum(1 for i in issues if i.severity == Severity.WARNING)

    return ContractStructureResult(
        is_valid=error_count == 0,
        contract_id=contract.id,
        issues=issues,
        error_count=error_count,
        warning_count=warning_count,
    )
