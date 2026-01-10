"""
Performance benchmark tests for griot-core.

Tests to verify NFR-SDK-004: 100K rows validation <5s.
"""
from __future__ import annotations

import time
from typing import Any, Generator

import pytest

from griot_core.models import Field, GriotModel
from griot_core.validation import validate_data


class BenchmarkCustomer(GriotModel):
    """Customer model for benchmark tests."""

    customer_id: str = Field(
        description="Unique customer identifier",
        primary_key=True,
        pattern=r"^CUST-\d{6}$",
    )
    email: str = Field(
        description="Customer email address",
        format="email",
        max_length=255,
    )
    age: int = Field(
        description="Customer age in years",
        ge=0,
        le=150,
    )
    status: str = Field(
        description="Account status",
        enum=["active", "inactive", "suspended"],
    )


def generate_benchmark_data(rows: int) -> list[dict[str, Any]]:
    """Generate benchmark data with specified number of rows."""
    return [
        {
            "customer_id": f"CUST-{i:06d}",
            "email": f"user{i}@example.com",
            "age": (i % 80) + 18,
            "status": ["active", "inactive", "suspended"][i % 3],
        }
        for i in range(rows)
    ]


@pytest.mark.benchmark
class TestValidationPerformance:
    """Performance benchmark tests for validation."""

    @pytest.mark.slow
    def test_100k_rows_under_5_seconds(self) -> None:
        """
        NFR-SDK-004: Validate 100K rows in under 5 seconds.

        This is the primary performance requirement for the validation engine.
        """
        data = generate_benchmark_data(100_000)

        start_time = time.perf_counter()
        result = validate_data(BenchmarkCustomer, data)
        elapsed = time.perf_counter() - start_time

        assert result.passed is True, "Benchmark data should be valid"
        assert result.row_count == 100_000
        assert elapsed < 5.0, f"Validation took {elapsed:.2f}s, should be <5s"

    def test_10k_rows_performance(self) -> None:
        """Test validation performance with 10K rows (quick sanity check)."""
        data = generate_benchmark_data(10_000)

        start_time = time.perf_counter()
        result = validate_data(BenchmarkCustomer, data)
        elapsed = time.perf_counter() - start_time

        assert result.passed is True
        assert result.row_count == 10_000
        # 10K should complete in under 0.5s (proportionally)
        assert elapsed < 0.5, f"10K validation took {elapsed:.2f}s, should be <0.5s"

    def test_1k_rows_fast(self) -> None:
        """Test validation performance with 1K rows."""
        data = generate_benchmark_data(1_000)

        start_time = time.perf_counter()
        result = validate_data(BenchmarkCustomer, data)
        elapsed = time.perf_counter() - start_time

        assert result.passed is True
        assert result.row_count == 1_000
        # 1K should be very fast
        assert elapsed < 0.1, f"1K validation took {elapsed:.2f}s, should be <0.1s"

    def test_validation_with_errors_performance(self) -> None:
        """Test performance when validating data with errors."""
        # Generate data with ~10% errors
        data = [
            {
                "customer_id": f"CUST-{i:06d}" if i % 10 != 0 else "invalid-id",
                "email": f"user{i}@example.com" if i % 10 != 1 else "bad-email",
                "age": ((i % 80) + 18) if i % 10 != 2 else -5,
                "status": ["active", "inactive", "suspended"][i % 3]
                if i % 10 != 3
                else "unknown",
            }
            for i in range(10_000)
        ]

        start_time = time.perf_counter()
        result = validate_data(BenchmarkCustomer, data)
        elapsed = time.perf_counter() - start_time

        assert result.passed is False
        assert result.error_count > 0
        # Even with errors, should be reasonably fast
        assert elapsed < 1.0, f"Validation with errors took {elapsed:.2f}s"


@pytest.mark.benchmark
class TestMemoryEfficiency:
    """Memory efficiency tests for validation."""

    def test_large_dataset_doesnt_explode_memory(self) -> None:
        """Test that validating large datasets is memory efficient."""
        import sys

        # Generate a moderate dataset
        data = generate_benchmark_data(50_000)

        # Get approximate size of result
        result = validate_data(BenchmarkCustomer, data)

        # Basic sanity check - result shouldn't be excessively large
        result_dict = result.to_dict()
        result_size = sys.getsizeof(str(result_dict))

        # Result should be reasonable (under 1MB for 50K rows of metadata)
        assert result_size < 1_000_000, f"Result size {result_size} bytes is too large"


@pytest.mark.benchmark
class TestScalability:
    """Scalability tests for validation."""

    def test_linear_scaling(self) -> None:
        """Test that validation time scales linearly with data size."""
        sizes = [1000, 2000, 4000]
        times: list[float] = []

        for size in sizes:
            data = generate_benchmark_data(size)
            start = time.perf_counter()
            validate_data(BenchmarkCustomer, data)
            times.append(time.perf_counter() - start)

        # Check that doubling data size roughly doubles time
        # (allowing for overhead, ratio should be between 1.5 and 2.5)
        ratio_1_to_2 = times[1] / times[0]
        ratio_2_to_3 = times[2] / times[1]

        # These are approximate checks - we want roughly linear, not O(n^2)
        assert ratio_1_to_2 < 3.0, f"Scaling ratio 1->2 is {ratio_1_to_2}, expected ~2"
        assert ratio_2_to_3 < 3.0, f"Scaling ratio 2->3 is {ratio_2_to_3}, expected ~2"
