"""Pydantic schemas for API request/response models."""

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# =============================================================================
# Common
# =============================================================================
class ErrorResponse(BaseModel):
    """Standard error response."""

    code: str
    message: str
    details: dict[str, Any] | None = None


class PaginatedResponse(BaseModel):
    """Base for paginated responses."""

    total: int
    limit: int
    offset: int


# =============================================================================
# Field Schemas
# =============================================================================
class FieldConstraints(BaseModel):
    """Constraints applied to a field."""

    model_config = ConfigDict(extra="allow")

    min_length: int | None = None
    max_length: int | None = None
    pattern: str | None = None
    format: Literal[
        "email", "uri", "uuid", "date", "datetime", "ipv4", "ipv6", "hostname"
    ] | None = None
    ge: float | None = None
    le: float | None = None
    gt: float | None = None
    lt: float | None = None
    multiple_of: float | None = None
    enum: list[Any] | None = None


class FieldMetadata(BaseModel):
    """Additional metadata for a field."""

    model_config = ConfigDict(extra="allow")

    unit: str | None = None
    aggregation: Literal["sum", "avg", "count", "min", "max", "none"] | None = None
    glossary_term: str | None = None


class FieldDefinition(BaseModel):
    """Schema for a single field in a contract."""

    name: str
    type: Literal["string", "integer", "float", "boolean", "date", "datetime", "array", "object"]
    description: str
    nullable: bool = False
    primary_key: bool = False
    unique: bool = False
    constraints: FieldConstraints | None = None
    metadata: FieldMetadata | None = None


# =============================================================================
# Contract Schemas
# =============================================================================
class ContractBase(BaseModel):
    """Base contract fields."""

    id: str = Field(..., examples=["customer-profile"])
    name: str = Field(..., examples=["Customer Profile"])
    description: str | None = None
    owner: str | None = None


class ContractCreate(ContractBase):
    """Schema for creating a new contract."""

    fields: list[FieldDefinition]


class ContractUpdate(BaseModel):
    """Schema for updating a contract (creates new version)."""

    name: str | None = None
    description: str | None = None
    fields: list[FieldDefinition] | None = None
    change_type: Literal["patch", "minor", "major"] = "minor"
    change_notes: str | None = None


class Contract(ContractBase):
    """Full contract response schema."""

    version: str = Field(..., examples=["1.2.0"])
    status: Literal["draft", "active", "deprecated"]
    fields: list[FieldDefinition]
    created_at: datetime
    updated_at: datetime


class ContractList(PaginatedResponse):
    """Paginated list of contracts."""

    items: list[Contract]


# =============================================================================
# Version Schemas
# =============================================================================
class VersionSummary(BaseModel):
    """Summary of a contract version."""

    version: str
    created_at: datetime
    created_by: str | None = None
    change_type: Literal["patch", "minor", "major"] | None = None
    change_notes: str | None = None
    is_breaking: bool = False


class VersionList(BaseModel):
    """List of version summaries."""

    items: list[VersionSummary]
    total: int


class TypeChange(BaseModel):
    """Represents a field type change between versions."""

    field: str
    from_type: str
    to_type: str
    is_breaking: bool


class ConstraintChange(BaseModel):
    """Represents a constraint change between versions."""

    field: str
    constraint: str
    from_value: Any
    to_value: Any
    is_breaking: bool


class ContractDiff(BaseModel):
    """Diff between two contract versions."""

    from_version: str
    to_version: str
    has_breaking_changes: bool
    added_fields: list[str]
    removed_fields: list[str]
    type_changes: list[TypeChange]
    constraint_changes: list[ConstraintChange]


# =============================================================================
# Validation Schemas
# =============================================================================
class ValidationError(BaseModel):
    """A single validation error."""

    field: str
    row: int | None = None
    value: Any = None
    constraint: str
    message: str


class ValidationReport(BaseModel):
    """Report of a validation run (from griot-enforce)."""

    contract_id: str
    contract_version: str | None = None
    passed: bool
    row_count: int
    error_count: int = 0
    error_rate: float = 0.0
    duration_ms: float | None = None
    environment: Literal["development", "staging", "production"] | None = None
    pipeline_id: str | None = None
    run_id: str | None = None
    sample_errors: list[ValidationError] = Field(default_factory=list, max_length=100)


class ValidationRecord(BaseModel):
    """Stored validation record."""

    id: UUID
    contract_id: str
    contract_version: str | None = None
    passed: bool
    row_count: int
    error_count: int
    recorded_at: datetime


class ValidationList(PaginatedResponse):
    """Paginated list of validation records."""

    items: list[ValidationRecord]


# =============================================================================
# Search Schemas
# =============================================================================
class SearchHit(BaseModel):
    """A single search result."""

    contract_id: str
    contract_name: str
    field_name: str | None = None
    match_type: Literal["name", "description", "field"]
    snippet: str | None = None


class SearchResults(BaseModel):
    """Search results response."""

    query: str
    items: list[SearchHit]
    total: int
