"""
Griot Enforce - Runtime Validator

Core RuntimeValidator class that wraps griot-core SDK for runtime validation
with registry integration, caching, and result reporting.
"""
from __future__ import annotations

import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pandas as pd

__all__ = ["RuntimeValidator", "RuntimeValidationError"]


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

    contract: Any
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
    """

    def __init__(
        self,
        registry_url: str | None = None,
        api_key: str | None = None,
        cache_ttl: int = 300,
        report_results: bool = True,
    ) -> None:
        self.registry_url = registry_url or os.environ.get("GRIOT_REGISTRY_URL")
        self.api_key = api_key or os.environ.get("GRIOT_API_KEY")
        self.cache_ttl = cache_ttl
        self.report_results = report_results
        self._cache: dict[str, CacheEntry] = {}
        self._client: Any = None

    @property
    def _http_client(self) -> Any:
        """Get or create HTTP client."""
        if self._client is None:
            import httpx

            headers = {}
            if self.api_key:
                headers["X-API-Key"] = self.api_key
            self._client = httpx.Client(
                base_url=self.registry_url or "",
                headers=headers,
                timeout=30.0,
            )
        return self._client

    def validate(
        self,
        contract_id: str,
        data: pd.DataFrame | list[dict[str, Any]],
        version: str | None = None,
        fail_on_error: bool = True,
    ) -> Any:
        """Validate data against a contract from registry."""
        contract = self.get_contract(contract_id, version)
        result = contract.validate(data)

        if self.report_results and self.registry_url:
            self._report_to_registry(contract_id, result, version)

        if fail_on_error and not result.passed:
            raise RuntimeValidationError(
                f"Validation failed for '{contract_id}' with {result.error_count} errors",
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
    ) -> Any:
        """Validate data against a local contract file."""
        from griot_core import load_contract

        contract = load_contract(contract_path)
        result = contract.validate(data)

        if fail_on_error and not result.passed:
            raise RuntimeValidationError(
                f"Validation failed for '{contract_path}' with {result.error_count} errors",
                contract_id=str(contract_path),
                error_count=result.error_count,
                error_rate=result.error_rate,
            )
        return result

    def get_contract(self, contract_id: str, version: str | None = None) -> Any:
        """Fetch contract from registry (with caching)."""
        if not self.registry_url:
            raise ValueError("registry_url is required to fetch contracts")

        cache_key = f"{contract_id}:{version or 'latest'}"
        if cache_key in self._cache:
            entry = self._cache[cache_key]
            if time.time() - entry.fetched_at < self.cache_ttl:
                return entry.contract

        from griot_core import GriotModel

        endpoint = f"/api/v1/contracts/{contract_id}"
        if version:
            endpoint += f"/versions/{version}"

        response = self._http_client.get(endpoint)
        response.raise_for_status()
        contract_data = response.json()
        contract = GriotModel.from_dict(contract_data.get("contract", contract_data))

        self._cache[cache_key] = CacheEntry(
            contract=contract, fetched_at=time.time(), version=version
        )
        return contract

    def clear_cache(self) -> None:
        """Clear the contract cache."""
        self._cache.clear()

    def _report_to_registry(
        self, contract_id: str, result: Any, version: str | None = None
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
                "errors": [e.to_dict() for e in result.errors[:100]],
            }
            self._http_client.post(endpoint, json=payload)
        except Exception:
            pass

    def check_residency(
        self, contract_id: str, region: str, version: str | None = None
    ) -> dict[str, Any]:
        """Check if data can be stored in a given region."""
        contract = self.get_contract(contract_id, version)
        return contract.check_residency(region)

    def verify_masking(
        self,
        contract_id: str,
        data: pd.DataFrame | list[dict[str, Any]],
        version: str | None = None,
    ) -> dict[str, Any]:
        """Verify that PII fields are properly masked."""
        contract = self.get_contract(contract_id, version)
        pii_fields = contract.pii_inventory()

        violations = []
        for field_info in pii_fields:
            if field_info.masking_strategy is None:
                continue
            field_name = field_info.name
            strategy = field_info.masking_strategy

            if not self._check_masking_applied(data, field_name, strategy):
                violations.append({
                    "field": field_name,
                    "expected_strategy": getattr(strategy, "value", str(strategy)),
                    "message": f"Field '{field_name}' not properly masked",
                })

        return {
            "compliant": len(violations) == 0,
            "pii_fields_checked": [f.name for f in pii_fields],
            "violations": violations,
        }

    def _check_masking_applied(self, data: Any, field_name: str, strategy: Any) -> bool:
        """Check if masking strategy appears to be applied."""
        if hasattr(data, "to_dict"):
            rows = data.to_dict("records")
        elif isinstance(data, dict):
            rows = [data]
        else:
            rows = list(data)

        if not rows:
            return True

        for row in rows[:10]:
            value = row.get(field_name)
            if value is None:
                continue
            str_value = str(value)
            if strategy.value == "redact" and "[REDACTED]" not in str_value:
                return False
            if strategy.value == "partial" and "*" not in str_value:
                return False
            if strategy.value == "hash":
                if len(str_value) < 32:
                    return False
        return True

    def __enter__(self) -> RuntimeValidator:
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    def close(self) -> None:
        """Close HTTP client."""
        if self._client is not None:
            self._client.close()
            self._client = None
