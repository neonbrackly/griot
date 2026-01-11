"""
Performance benchmark tests for schema operations (T-394).

Tests performance of contract loading, serialization, diffing,
and breaking change detection.
"""
from __future__ import annotations

import time
from typing import Any

import pytest

from griot_core.contract import (
    detect_breaking_changes,
    diff_contracts,
    load_contract_from_dict,
    load_contract_from_string,
    model_to_dict,
    model_to_yaml,
)
from griot_core.models import Field, GriotModel


# =============================================================================
# BENCHMARK MODELS
# =============================================================================


class LargeContract(GriotModel):
    """Large contract with many fields for performance testing."""

    id: str = Field(description="ID", primary_key=True)
    field_001: str = Field(description="Field 001", max_length=100)
    field_002: str = Field(description="Field 002", max_length=100)
    field_003: str = Field(description="Field 003", max_length=100)
    field_004: str = Field(description="Field 004", max_length=100)
    field_005: int = Field(description="Field 005", ge=0, le=1000)
    field_006: int = Field(description="Field 006", ge=0, le=1000)
    field_007: int = Field(description="Field 007", ge=0, le=1000)
    field_008: float = Field(description="Field 008", ge=0.0, le=100.0)
    field_009: float = Field(description="Field 009", ge=0.0, le=100.0)
    field_010: float = Field(description="Field 010", ge=0.0, le=100.0)
    field_011: bool = Field(description="Field 011")
    field_012: bool = Field(description="Field 012")
    field_013: str = Field(description="Field 013", enum=["a", "b", "c", "d"])
    field_014: str = Field(description="Field 014", enum=["x", "y", "z"])
    field_015: str = Field(description="Field 015", pattern=r"^[A-Z]{3}$")
    field_016: str = Field(description="Field 016", format="email")
    field_017: str = Field(description="Field 017", nullable=True)
    field_018: str = Field(description="Field 018", nullable=True)
    field_019: str = Field(description="Field 019", unique=True)
    field_020: str = Field(description="Field 020", unique=True)


def generate_contract_yaml(num_fields: int) -> str:
    """Generate a YAML contract with specified number of fields."""
    fields_yaml = ""
    for i in range(num_fields):
        field_type = ["string", "integer", "float", "boolean"][i % 4]
        fields_yaml += f"""  field_{i:04d}:
    type: {field_type}
    description: Field {i}
"""
        if field_type == "string":
            fields_yaml += f"    max_length: {100 + i}\n"
        elif field_type in ("integer", "float"):
            fields_yaml += f"    ge: {i}\n"

    return f"""api_version: v1.0.0
kind: DataContract
id: benchmark-contract
name: BenchmarkContract
version: "1.0.0"
status: active
fields:
  id:
    type: string
    description: Primary key
    primary_key: true
{fields_yaml}"""


def generate_contract_dict(num_fields: int) -> dict[str, Any]:
    """Generate a dictionary contract with specified number of fields."""
    fields = [
        {
            "name": "id",
            "type": "string",
            "description": "Primary key",
            "primary_key": True,
        }
    ]

    for i in range(num_fields):
        field_type = ["string", "integer", "float", "boolean"][i % 4]
        field: dict[str, Any] = {
            "name": f"field_{i:04d}",
            "type": field_type,
            "description": f"Field {i}",
        }
        if field_type == "string":
            field["constraints"] = {"max_length": 100 + i}
        elif field_type in ("integer", "float"):
            field["constraints"] = {"ge": i}
        fields.append(field)

    return {
        "api_version": "v1.0.0",
        "kind": "DataContract",
        "id": "benchmark-contract",
        "name": "BenchmarkContract",
        "version": "1.0.0",
        "status": "active",
        "fields": fields,
    }


# =============================================================================
# CONTRACT LOADING BENCHMARKS
# =============================================================================


@pytest.mark.benchmark
class TestContractLoadingPerformance:
    """Performance benchmarks for contract loading."""

    def test_load_small_contract_from_yaml(self) -> None:
        """Test loading a small contract (10 fields) from YAML."""
        yaml_content = generate_contract_yaml(10)

        start = time.perf_counter()
        for _ in range(100):
            load_contract_from_string(yaml_content)
        elapsed = time.perf_counter() - start

        avg_time = elapsed / 100
        assert avg_time < 0.01, f"Avg load time {avg_time:.4f}s, should be <0.01s"

    def test_load_medium_contract_from_yaml(self) -> None:
        """Test loading a medium contract (50 fields) from YAML."""
        yaml_content = generate_contract_yaml(50)

        start = time.perf_counter()
        for _ in range(50):
            load_contract_from_string(yaml_content)
        elapsed = time.perf_counter() - start

        avg_time = elapsed / 50
        assert avg_time < 0.05, f"Avg load time {avg_time:.4f}s, should be <0.05s"

    def test_load_large_contract_from_yaml(self) -> None:
        """Test loading a large contract (100 fields) from YAML."""
        yaml_content = generate_contract_yaml(100)

        start = time.perf_counter()
        for _ in range(20):
            load_contract_from_string(yaml_content)
        elapsed = time.perf_counter() - start

        avg_time = elapsed / 20
        assert avg_time < 0.1, f"Avg load time {avg_time:.4f}s, should be <0.1s"

    def test_load_contract_from_dict_performance(self) -> None:
        """Test loading a contract from dictionary (should be faster than YAML)."""
        data = generate_contract_dict(50)

        start = time.perf_counter()
        for _ in range(100):
            load_contract_from_dict(data)
        elapsed = time.perf_counter() - start

        avg_time = elapsed / 100
        # Dict loading should be faster than YAML since no parsing
        assert avg_time < 0.02, f"Avg load time {avg_time:.4f}s, should be <0.02s"


# =============================================================================
# CONTRACT SERIALIZATION BENCHMARKS
# =============================================================================


@pytest.mark.benchmark
class TestContractSerializationPerformance:
    """Performance benchmarks for contract serialization."""

    def test_export_to_dict_performance(self) -> None:
        """Test exporting contract to dictionary."""
        start = time.perf_counter()
        for _ in range(100):
            model_to_dict(LargeContract)
        elapsed = time.perf_counter() - start

        avg_time = elapsed / 100
        assert avg_time < 0.01, f"Avg export time {avg_time:.4f}s, should be <0.01s"

    def test_export_to_yaml_performance(self) -> None:
        """Test exporting contract to YAML."""
        start = time.perf_counter()
        for _ in range(100):
            model_to_yaml(LargeContract)
        elapsed = time.perf_counter() - start

        avg_time = elapsed / 100
        assert avg_time < 0.01, f"Avg export time {avg_time:.4f}s, should be <0.01s"

    def test_roundtrip_performance(self) -> None:
        """Test YAML roundtrip (load -> export -> load)."""
        yaml_content = generate_contract_yaml(50)

        start = time.perf_counter()
        for _ in range(20):
            model = load_contract_from_string(yaml_content)
            yaml_out = model_to_yaml(model)
            load_contract_from_string(yaml_out)
        elapsed = time.perf_counter() - start

        avg_time = elapsed / 20
        assert avg_time < 0.15, f"Avg roundtrip time {avg_time:.4f}s, should be <0.15s"


# =============================================================================
# BREAKING CHANGE DETECTION BENCHMARKS
# =============================================================================


@pytest.mark.benchmark
class TestBreakingChangeDetectionPerformance:
    """Performance benchmarks for breaking change detection."""

    def test_detect_breaking_changes_identical_contracts(self) -> None:
        """Test breaking change detection on identical contracts."""
        start = time.perf_counter()
        for _ in range(100):
            detect_breaking_changes(LargeContract, LargeContract)
        elapsed = time.perf_counter() - start

        avg_time = elapsed / 100
        assert avg_time < 0.005, f"Avg detection time {avg_time:.4f}s, should be <0.005s"

    def test_detect_breaking_changes_modified_contracts(self) -> None:
        """Test breaking change detection on modified contracts."""

        class ModifiedContract(GriotModel):
            """Modified version with changes."""

            id: str = Field(description="ID", primary_key=True)
            field_001: str = Field(description="Field 001 modified", max_length=50)  # reduced
            field_002: int = Field(description="Type changed")  # type change
            # field_003 removed
            field_004: str = Field(description="Field 004", max_length=100)
            field_005: int = Field(description="Field 005", ge=10, le=1000)  # ge increased
            field_006: int = Field(description="Field 006", ge=0, le=1000)
            field_007: int = Field(description="Field 007", ge=0, le=1000)
            field_008: float = Field(description="Field 008", ge=0.0, le=100.0)
            field_009: float = Field(description="Field 009", ge=0.0, le=100.0)
            field_010: float = Field(description="Field 010", ge=0.0, le=100.0)
            field_011: bool = Field(description="Field 011")
            field_012: bool = Field(description="Field 012")
            field_013: str = Field(description="Field 013", enum=["a", "b", "c"])  # d removed
            field_014: str = Field(description="Field 014", enum=["x", "y", "z"])
            field_015: str = Field(description="Field 015", pattern=r"^[A-Z]{4}$")  # pattern changed
            field_016: str = Field(description="Field 016", format="email")
            field_017: str = Field(description="Field 017", nullable=False)  # now required
            field_018: str = Field(description="Field 018", nullable=True)
            field_019: str = Field(description="Field 019", unique=True)
            field_020: str = Field(description="Field 020", unique=True)
            new_required: str = Field(description="New required field")  # new required

        start = time.perf_counter()
        for _ in range(50):
            changes = detect_breaking_changes(LargeContract, ModifiedContract)
        elapsed = time.perf_counter() - start

        avg_time = elapsed / 50
        assert avg_time < 0.01, f"Avg detection time {avg_time:.4f}s, should be <0.01s"

        # Verify we detected changes
        assert len(changes) > 0

    def test_detect_breaking_changes_large_contract(self) -> None:
        """Test breaking change detection on very large contracts."""
        data_v1 = generate_contract_dict(200)
        data_v2 = generate_contract_dict(200)

        # Modify v2 slightly
        data_v2["fields"][50]["constraints"]["max_length"] = 50  # reduced

        v1 = load_contract_from_dict(data_v1)
        v2 = load_contract_from_dict(data_v2)

        start = time.perf_counter()
        for _ in range(20):
            detect_breaking_changes(v1, v2)
        elapsed = time.perf_counter() - start

        avg_time = elapsed / 20
        assert avg_time < 0.05, f"Avg detection time {avg_time:.4f}s, should be <0.05s"


# =============================================================================
# CONTRACT DIFF BENCHMARKS
# =============================================================================


@pytest.mark.benchmark
class TestContractDiffPerformance:
    """Performance benchmarks for contract diffing."""

    def test_diff_identical_contracts(self) -> None:
        """Test diffing identical contracts."""
        start = time.perf_counter()
        for _ in range(100):
            diff_contracts(LargeContract, LargeContract)
        elapsed = time.perf_counter() - start

        avg_time = elapsed / 100
        assert avg_time < 0.005, f"Avg diff time {avg_time:.4f}s, should be <0.005s"

    def test_diff_with_many_changes(self) -> None:
        """Test diffing contracts with many changes."""

        class HeavilyModified(GriotModel):
            """Heavily modified contract."""

            id: str = Field(description="ID", primary_key=True)
            new_field_1: str = Field(description="New 1")
            new_field_2: str = Field(description="New 2")
            new_field_3: str = Field(description="New 3")
            field_001: int = Field(description="Changed type")
            field_005: int = Field(description="Field 005", ge=100, le=500)

        start = time.perf_counter()
        for _ in range(50):
            diff = diff_contracts(LargeContract, HeavilyModified)
        elapsed = time.perf_counter() - start

        avg_time = elapsed / 50
        assert avg_time < 0.01, f"Avg diff time {avg_time:.4f}s, should be <0.01s"

        # Verify diff detected changes
        assert diff.has_breaking_changes is True


# =============================================================================
# BATCH OPERATIONS BENCHMARKS
# =============================================================================


@pytest.mark.benchmark
class TestBatchOperationsPerformance:
    """Performance benchmarks for batch schema operations."""

    def test_batch_load_multiple_contracts(self) -> None:
        """Test loading multiple contracts in sequence."""
        yamls = [generate_contract_yaml(20 + i * 5) for i in range(10)]

        start = time.perf_counter()
        contracts = [load_contract_from_string(y) for y in yamls]
        elapsed = time.perf_counter() - start

        assert len(contracts) == 10
        assert elapsed < 0.5, f"Batch load took {elapsed:.2f}s, should be <0.5s"

    def test_batch_diff_multiple_pairs(self) -> None:
        """Test diffing multiple contract pairs."""
        yamls = [generate_contract_yaml(30) for _ in range(10)]
        contracts = [load_contract_from_string(y) for y in yamls]

        start = time.perf_counter()
        diffs = []
        for i in range(len(contracts) - 1):
            diffs.append(diff_contracts(contracts[i], contracts[i + 1]))
        elapsed = time.perf_counter() - start

        assert len(diffs) == 9
        assert elapsed < 0.1, f"Batch diff took {elapsed:.2f}s, should be <0.1s"


# =============================================================================
# SCALING TESTS
# =============================================================================


@pytest.mark.benchmark
class TestSchemaScaling:
    """Tests for schema operation scaling characteristics."""

    def test_linear_scaling_field_count(self) -> None:
        """Test that operations scale linearly with field count."""
        field_counts = [20, 40, 80]
        load_times: list[float] = []

        for count in field_counts:
            yaml_content = generate_contract_yaml(count)
            start = time.perf_counter()
            for _ in range(10):
                load_contract_from_string(yaml_content)
            load_times.append((time.perf_counter() - start) / 10)

        # Check roughly linear scaling (doubling fields ~ doubles time)
        ratio_1 = load_times[1] / load_times[0]
        ratio_2 = load_times[2] / load_times[1]

        # Allow for some overhead; ratios should be between 1.5 and 3.0
        assert ratio_1 < 3.0, f"Scaling 20->40: {ratio_1:.2f}x, should be ~2x"
        assert ratio_2 < 3.0, f"Scaling 40->80: {ratio_2:.2f}x, should be ~2x"

    def test_breaking_change_detection_scales_well(self) -> None:
        """Test that breaking change detection scales reasonably."""
        field_counts = [25, 50, 100]
        detection_times: list[float] = []

        for count in field_counts:
            data_v1 = generate_contract_dict(count)
            data_v2 = generate_contract_dict(count)
            # Make a breaking change in v2
            if count > 0 and len(data_v2["fields"]) > 1:
                data_v2["fields"][1]["constraints"] = {"max_length": 10}

            v1 = load_contract_from_dict(data_v1)
            v2 = load_contract_from_dict(data_v2)

            start = time.perf_counter()
            for _ in range(20):
                detect_breaking_changes(v1, v2)
            detection_times.append((time.perf_counter() - start) / 20)

        # Check scaling
        ratio_1 = detection_times[1] / detection_times[0]
        ratio_2 = detection_times[2] / detection_times[1]

        # Detection should scale linearly or better
        assert ratio_1 < 4.0, f"Scaling 25->50: {ratio_1:.2f}x, should be ~2x"
        assert ratio_2 < 4.0, f"Scaling 50->100: {ratio_2:.2f}x, should be ~2x"
