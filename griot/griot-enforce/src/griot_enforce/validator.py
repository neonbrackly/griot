"""
Griot Enforce - Runtime Validator

Core RuntimeValidator class that wraps griot-core SDK for runtime validation
with registry integration, caching, and result reporting.
"""
from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pandas as pd

__all__ = [
    "RuntimeValidator",
    "RuntimeValidationError",
]


class RuntimeValidationError(Exception):
    """Raised when runtime validation fails."""

    def __init__(
        self,
        message: str,
        contract_id: str | None = None,
        error_count: int = 0,
        error_rate: float = 0.0,
    ) -> None:
        super().__init__(message)
        self.contract_id = contract_id
        self.error_count = error_count
        self.error_rate = error_rate


@dataclass
class CacheEntry:
    """Cached contract entry with TTL."""

    contract: Any  # GriotModel type
    fetched_at: float
    version: str | None = None


class RuntimeValidator:
    """
    Core validator for runtime data validation.

    Wraps griot-core SDK validation with runtime features:
    - Registry integration for contract fetching
    - Validation result reporting
    - Caching for performance

    Example:
        validator = RuntimeValidator(registry_url="https://registry.example.com")
        result = validator.validate("customer-profile", dataframe)

        # Or with local contracts:
        result = validator.validate_local("./contracts/customer.yaml", dataframe)
    """

    def __init__(
        self,
        registry_url: str | None = None,
        api_key: str | None = None,
        cache_ttl: int = 300,
        report_results: bool = True,
    ) -> None:
        """
        Initialize RuntimeValidator.

        Args:
            registry_url: Registry URL (or GRIOT_REGISTRY_URL env var).
            api_key: API key (or GRIOT_API_KEY env var).
            cache_ttl: Contract cache TTL in seconds (default: 300).
            report_results: Whether to report results to registry (default: True).
        """
        self.registry_url = registry_url or os.environ.get("GRIOT_REGISTRY_URL")
        self.api_key = api_key or os.environ.get("GRIOT_API_KEY")
        self.cache_ttl = cache_ttl
        self.report_results = report_results

        # Contract cache: contract_id -> CacheEntry
        self._cache: dict[str, CacheEntry] = {}

        # Lazy-load httpx client
        self._client: Any = None

    @property
    def _http_client(self) -> Any:
        """Get or create HTTP client."""
        if self._client is None:
            try:
                import httpx

                headers = {}
                if self.api_key:
                    headers["X-API-Key"] = self.api_key

                self._client = httpx.Client(
                    base_url=self.registry_url or "",
                    headers=headers,
                    timeout=30.0,
                )
            except ImportError:
                raise ImportError(
                    "httpx is required for registry integration. "
                    "Install with: pip install griot-enforce"
                )
        return self._client

    def validate(
        self,
        contract_id: str,
        data: pd.DataFrame | list[dict[str, Any]],
        version: str | None = None,
        fail_on_error: bool = True,
    ) -> Any:  # Returns ValidationResult
        """
        Validate data against a contract from registry.

        Args:
            contract_id: Contract ID in the registry.
            data: DataFrame or list of dicts to validate.
            version: Specific contract version (default: latest).
            fail_on_error: Raise exception on validation failure (default: True).

        Returns:
            ValidationResult from griot-core.

        Raises:
            RuntimeValidationError: If validation fails and fail_on_error=True.
            ValueError: If registry_url is not configured.

        Example:
            validator = RuntimeValidator(registry_url="https://registry.example.com")
            result = validator.validate("customer-profile", df)
            if result.passed:
                print("Validation successful!")
        """
        # Get contract from registry (cached)
        contract = self.get_contract(contract_id, version)

        # Validate using griot-core (contract.validate does the work)
        result = contract.validate(data)

        # Report results to registry if configured
        if self.report_results and self.registry_url:
            self._report_to_registry(contract_id, result, version)

        # Raise on failure if configured
        if fail_on_error and not result.passed:
            raise RuntimeValidationError(
                f"Validation failed for contract '{contract_id}' with {result.error_count} errors",
                contract_id=contract_id,
                error_count=result.error_count,
                error_rate=result.error_rate,
            )

        return result

    def validate_local(
        self,
        contract_path: str | Path,
        data: pd.DataFrame | list[dict[str, Any]],
        fail_on_error: bool = True,
    ) -> Any:  # Returns ValidationResult
        """
        Validate data against a local contract file.

        Args:
            contract_path: Path to YAML contract file.
            data: DataFrame or list of dicts to validate.
            fail_on_error: Raise exception on validation failure (default: True).

        Returns:
            ValidationResult from griot-core.

        Raises:
            RuntimeValidationError: If validation fails and fail_on_error=True.
            FileNotFoundError: If contract file doesn't exist.

        Example:
            validator = RuntimeValidator()
            result = validator.validate_local("./contracts/customer.yaml", df)
        """
        from griot_core import load_contract

        # Load contract from file (griot-core does the work)
        contract = load_contract(contract_path)

        # Validate using griot-core
        result = contract.validate(data)

        # Raise on failure if configured
        if fail_on_error and not result.passed:
            raise RuntimeValidationError(
                f"Validation failed for contract '{contract_path}' with {result.error_count} errors",
                contract_id=str(contract_path),
                error_count=result.error_count,
                error_rate=result.error_rate,
            )

        return result

    def get_contract(
        self,
        contract_id: str,
        version: str | None = None,
    ) -> Any:  # Returns GriotModel type
        """
        Fetch contract from registry (with caching).

        Args:
            contract_id: Contract ID in the registry.
            version: Specific contract version (default: latest).

        Returns:
            GriotModel subclass representing the contract.

        Raises:
            ValueError: If registry_url is not configured.
            RuntimeError: If contract fetch fails.
        """
        if not self.registry_url:
            raise ValueError(
                "registry_url is required to fetch contracts. "
                "Set it in constructor or GRIOT_REGISTRY_URL env var."
            )

        # Check cache
        cache_key = f"{contract_id}:{version or 'latest'}"
        if cache_key in self._cache:
            entry = self._cache[cache_key]
            if time.time() - entry.fetched_at < self.cache_ttl:
                return entry.contract

        # Fetch from registry
        from griot_core import GriotModel

        endpoint = f"/api/v1/contracts/{contract_id}"
        if version:
            endpoint += f"/versions/{version}"

        response = self._http_client.get(endpoint)
        response.raise_for_status()

        contract_data = response.json()

        # Load contract using griot-core
        contract = GriotModel.from_dict(contract_data.get("contract", contract_data))

        # Cache it
        self._cache[cache_key] = CacheEntry(
            contract=contract,
            fetched_at=time.time(),
            version=version,
        )

        return contract

    def clear_cache(self) -> None:
        """Clear the contract cache."""
        self._cache.clear()

    def _report_to_registry(
        self,
        contract_id: str,
        result: Any,
        version: str | None = None,
    ) -> None:
        """Report validation result to registry."""
        try:
            endpoint = f"/api/v1/contracts/{contract_id}/validations"
            payload = {
                "contract_id": contract_id,
                "version": version,
                "passed": result.passed,
                "row_count": result.row_count,
                "error_count": result.error_count,
                "error_rate": result.error_rate,
                "duration_ms": result.duration_ms,
                "errors": [e.to_dict() for e in result.errors[:100]],  # Limit errors
            }

            self._http_client.post(endpoint, json=payload)
        except Exception:
            # Don't fail validation if reporting fails
            pass

    def check_residency(
        self,
        contract_id: str,
        region: str,
        version: str | None = None,
    ) -> dict[str, Any]:
        """
        Check if data can be stored in a given region.

        Args:
            contract_id: Contract ID in the registry.
            region: Target region for data storage.
            version: Specific contract version.

        Returns:
            Dictionary with compliance status and violations.
        """
        contract = self.get_contract(contract_id, version)

        # Use griot-core's check_residency method
        return contract.check_residency(region)

    def verify_masking(
        self,
        contract_id: str,
        data: pd.DataFrame | list[dict[str, Any]],
        version: str | None = None,
    ) -> dict[str, Any]:
        """
        Verify that PII fields are properly masked.

        Args:
            contract_id: Contract ID in the registry.
            data: Data to check for masking compliance.
            version: Specific contract version.

        Returns:
            Dictionary with masking verification results.
        """
        contract = self.get_contract(contract_id, version)

        # Get PII fields from contract
        pii_fields = contract.pii_inventory()

        # Check each PII field for proper masking
        violations = []
        for field_info in pii_fields:
            if field_info.masking_strategy is None:
                continue

            field_name = field_info.name
            strategy = field_info.masking_strategy

            # Check if data appears to be masked
            # This is a basic check - implementations can be more sophisticated
            if not self._check_masking_applied(data, field_name, strategy):
                violations.append({
                    "field": field_name,
                    "expected_strategy": strategy.value if hasattr(strategy, "value") else str(strategy),
                    "message": f"Field '{field_name}' does not appear to be properly masked",
                })

        return {
            "compliant": len(violations) == 0,
            "pii_fields_checked": [f.name for f in pii_fields],
            "violations": violations,
        }

    def _check_masking_applied(
        self,
        data: Any,
        field_name: str,
        strategy: Any,
    ) -> bool:
        """
        Check if a masking strategy appears to be applied to a field.

        This is a basic heuristic check. Implementations may override
        for more sophisticated validation.
        """
        # Convert to list of dicts if DataFrame
        if hasattr(data, "to_dict"):
            rows = data.to_dict("records")
        elif isinstance(data, dict):
            rows = [data]
        else:
            rows = list(data)

        if not rows:
            return True  # Empty data is compliant

        # Check first few rows for masking patterns
        for row in rows[:10]:
            value = row.get(field_name)
            if value is None:
                continue

            # Check for common masking patterns
            str_value = str(value)

            # Redacted values
            if strategy.value == "redact" and "[REDACTED]" not in str_value:
                return False

            # Masked values (e.g., ****1234)
            if strategy.value == "partial" and "*" not in str_value:
                return False

            # Hashed values (long hex strings)
            if strategy.value == "hash":
                if len(str_value) < 32 or not all(c in "0123456789abcdef" for c in str_value.lower()):
                    return False

        return True

    def __enter__(self) -> RuntimeValidator:
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit - cleanup resources."""
        if self._client is not None:
            self._client.close()
            self._client = None

    def close(self) -> None:
        """Close HTTP client and release resources."""
        if self._client is not None:
            self._client.close()
            self._client = None
