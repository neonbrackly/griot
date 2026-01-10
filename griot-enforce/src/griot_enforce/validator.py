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
    "ResidencyViolationError",
    "MaskingViolationError",
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


class ResidencyViolationError(Exception):
    """Raised when data residency requirements are violated."""

    def __init__(
        self,
        message: str,
        contract_id: str | None = None,
        violations: list[dict[str, Any]] | None = None,
        detected_region: str | None = None,
        allowed_regions: list[str] | None = None,
    ) -> None:
        super().__init__(message)
        self.contract_id = contract_id
        self.violations = violations or []
        self.detected_region = detected_region
        self.allowed_regions = allowed_regions or []


class MaskingViolationError(Exception):
    """Raised when PII masking requirements are violated."""

    def __init__(
        self,
        message: str,
        contract_id: str | None = None,
        violations: list[dict[str, Any]] | None = None,
    ) -> None:
        super().__init__(message)
        self.contract_id = contract_id
        self.violations = violations or []


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
        verify_masking: bool = False,
        environment: str | None = None,
    ) -> Any:  # Returns ValidationResult
        """
        Validate data against a contract from registry.

        Args:
            contract_id: Contract ID in the registry.
            data: DataFrame or list of dicts to validate.
            version: Specific contract version (default: latest).
            fail_on_error: Raise exception on validation failure (default: True).
            verify_masking: Verify PII fields are properly masked (default: False).
            environment: Environment name (e.g., "staging", "dev") for masking checks.

        Returns:
            ValidationResult from griot-core (with masking_result if verify_masking=True).

        Raises:
            RuntimeValidationError: If validation fails and fail_on_error=True.
            MaskingViolationError: If masking verification fails and fail_on_error=True.
            ValueError: If registry_url is not configured.

        Example:
            validator = RuntimeValidator(registry_url="https://registry.example.com")
            result = validator.validate("customer-profile", df, verify_masking=True)
            if result.passed:
                print("Validation successful!")
        """
        # Get contract from registry (cached)
        contract = self.get_contract(contract_id, version)

        # Validate using griot-core (contract.validate does the work)
        result = contract.validate(data)

        # Verify masking if requested (FR-ENF-009)
        masking_result = None
        if verify_masking:
            masking_result = self._verify_masking_internal(contract, data, environment)
            # Attach masking result to validation result
            if hasattr(result, "__dict__"):
                result.masking_result = masking_result

        # Report results to registry if configured
        if self.report_results and self.registry_url:
            self._report_to_registry(contract_id, result, version, masking_result)

        # Raise on masking failure if configured
        if verify_masking and fail_on_error and masking_result and not masking_result["compliant"]:
            raise MaskingViolationError(
                f"Masking verification failed for contract '{contract_id}' with "
                f"{len(masking_result['violations'])} violations",
                contract_id=contract_id,
                violations=masking_result["violations"],
            )

        # Raise on validation failure if configured
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
        masking_result: dict[str, Any] | None = None,
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

            # Include masking verification results if available
            if masking_result is not None:
                payload["masking_verified"] = True
                payload["masking_compliant"] = masking_result["compliant"]
                payload["masking_violations"] = masking_result.get("violations", [])[:20]

            self._http_client.post(endpoint, json=payload)
        except Exception:
            # Don't fail validation if reporting fails
            pass

    def check_residency(
        self,
        contract_id: str,
        region: str | None = None,
        destination: str | None = None,
        version: str | None = None,
        fail_on_violation: bool = False,
    ) -> dict[str, Any]:
        """
        Check if data can be stored in a given region.

        FR-ENF-008: Block writes to non-compliant regions. Auto-detect region from cloud URIs.

        Args:
            contract_id: Contract ID in the registry.
            region: Target region for data storage (explicit).
            destination: Cloud URI to auto-detect region from (e.g., s3://bucket-eu-west-1/).
            version: Specific contract version.
            fail_on_violation: Raise ResidencyViolationError if not compliant (default: False).

        Returns:
            Dictionary with compliance status, detected region, and violations.

        Raises:
            ResidencyViolationError: If not compliant and fail_on_violation=True.
            ValueError: If neither region nor destination is provided.

        Example:
            # Explicit region
            result = validator.check_residency("customer-profile", region="eu-west-1")

            # Auto-detect from S3 URI
            result = validator.check_residency(
                contract_id="customer-profile",
                destination="s3://my-bucket-eu-west-1/data/",
                fail_on_violation=True
            )
        """
        # Determine region
        detected_region = None
        if destination:
            detected_region = self._detect_region_from_uri(destination)
            if not detected_region and not region:
                raise ValueError(
                    f"Could not auto-detect region from destination '{destination}'. "
                    "Please provide an explicit 'region' parameter."
                )
        target_region = region or detected_region

        if not target_region:
            raise ValueError("Either 'region' or 'destination' must be provided.")

        contract = self.get_contract(contract_id, version)

        # Use griot-core's check_residency method
        core_result = contract.check_residency(target_region)

        # Enhance result with auto-detection info
        result = {
            **core_result,
            "detected_region": detected_region,
            "destination": destination,
            "target_region": target_region,
        }

        # Raise on violation if configured
        if fail_on_violation and not result.get("compliant", True):
            allowed = result.get("allowed_regions", [])
            raise ResidencyViolationError(
                f"Data residency violation: region '{target_region}' is not allowed. "
                f"Allowed regions: {allowed}",
                contract_id=contract_id,
                violations=result.get("violations", []),
                detected_region=detected_region,
                allowed_regions=allowed,
            )

        return result

    def _detect_region_from_uri(self, uri: str) -> str | None:
        """
        Auto-detect cloud region from a storage URI.

        Supports:
        - AWS S3: s3://bucket-name/ or s3://bucket.s3.region.amazonaws.com/
        - GCP GCS: gs://bucket-name/ (requires bucket metadata, returns None)
        - Azure Blob: https://account.blob.core.windows.net/container
        """
        import re

        uri_lower = uri.lower()

        # AWS S3 patterns
        if uri_lower.startswith("s3://"):
            # Pattern 1: Region in bucket name (common convention)
            # e.g., s3://my-bucket-eu-west-1/path
            region_match = re.search(
                r"-(us-east-[12]|us-west-[12]|eu-west-[123]|eu-central-1|"
                r"eu-north-1|eu-south-[12]|ap-south-[12]|ap-northeast-[123]|"
                r"ap-southeast-[1234]|sa-east-1|ca-central-1|me-south-1|"
                r"me-central-1|af-south-1|ap-east-1)[/-]?",
                uri,
                re.IGNORECASE,
            )
            if region_match:
                return region_match.group(1).lower()

            # Pattern 2: S3 endpoint with region
            # e.g., s3://bucket.s3.eu-west-1.amazonaws.com/
            endpoint_match = re.search(
                r"\.s3[.-]([a-z]{2}-[a-z]+-\d)\.amazonaws\.com",
                uri,
                re.IGNORECASE,
            )
            if endpoint_match:
                return endpoint_match.group(1).lower()

        # Azure Blob patterns
        # e.g., https://account.blob.core.windows.net/container
        # Azure regions in account naming or from subdomain
        if "blob.core.windows.net" in uri_lower:
            # Check for region in URL path patterns
            region_match = re.search(
                r"(westeurope|northeurope|westus|westus2|eastus|eastus2|"
                r"centralus|northcentralus|southcentralus|westcentralus|"
                r"canadacentral|canadaeast|brazilsouth|uksouth|ukwest|"
                r"francecentral|francesouth|germanywestcentral|norwayeast|"
                r"switzerlandnorth|uaenorth|southafricanorth|australiaeast|"
                r"australiasoutheast|japaneast|japanwest|koreacentral|"
                r"southeastasia|eastasia|centralindia|southindia|westindia)",
                uri,
                re.IGNORECASE,
            )
            if region_match:
                return region_match.group(1).lower()

        # GCP GCS - cannot auto-detect without API call
        # Would require calling GCS API to get bucket location
        if uri_lower.startswith("gs://"):
            # Try to find region hints in bucket name
            region_match = re.search(
                r"-(us-central1|us-east[14]|us-west[1234]|europe-west[1-6]|"
                r"europe-north1|europe-central2|asia-east[12]|asia-northeast[123]|"
                r"asia-south[12]|asia-southeast[12]|australia-southeast[12]|"
                r"southamerica-east1|northamerica-northeast[12])[/-]?",
                uri,
                re.IGNORECASE,
            )
            if region_match:
                return region_match.group(1).lower()

        return None

    def verify_masking(
        self,
        contract_id: str,
        data: pd.DataFrame | list[dict[str, Any]],
        version: str | None = None,
        environment: str | None = None,
        fail_on_violation: bool = False,
    ) -> dict[str, Any]:
        """
        Verify that PII fields are properly masked.

        FR-ENF-009: Verify PII is masked in non-prod environments.

        Args:
            contract_id: Contract ID in the registry.
            data: Data to check for masking compliance.
            version: Specific contract version.
            environment: Environment name (e.g., "staging", "dev"). If "prod" or "production",
                         masking verification is skipped (returns compliant).
            fail_on_violation: Raise MaskingViolationError if not compliant (default: False).

        Returns:
            Dictionary with masking verification results.

        Raises:
            MaskingViolationError: If not compliant and fail_on_violation=True.

        Example:
            result = validator.verify_masking(
                "customer-profile",
                dataframe,
                environment="staging",
                fail_on_violation=True
            )
        """
        contract = self.get_contract(contract_id, version)
        result = self._verify_masking_internal(contract, data, environment)

        # Raise on violation if configured
        if fail_on_violation and not result["compliant"]:
            raise MaskingViolationError(
                f"Masking verification failed with {len(result['violations'])} violations",
                contract_id=contract_id,
                violations=result["violations"],
            )

        return result

    def _verify_masking_internal(
        self,
        contract: Any,
        data: pd.DataFrame | list[dict[str, Any]],
        environment: str | None = None,
    ) -> dict[str, Any]:
        """
        Internal masking verification using an already-loaded contract.

        Args:
            contract: Already-loaded GriotModel contract.
            data: Data to check for masking compliance.
            environment: Environment name for conditional enforcement.

        Returns:
            Dictionary with masking verification results.
        """
        # Skip verification in production (masking not required for authorized access)
        if environment and environment.lower() in ("prod", "production"):
            return {
                "compliant": True,
                "skipped": True,
                "reason": "Masking verification skipped in production environment",
                "pii_fields_checked": [],
                "violations": [],
            }

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
            if not self._check_masking_applied(data, field_name, strategy):
                violations.append({
                    "field": field_name,
                    "expected_strategy": strategy.value if hasattr(strategy, "value") else str(strategy),
                    "message": f"Field '{field_name}' does not appear to be properly masked",
                    "pii_category": field_info.pii_category.value if hasattr(field_info.pii_category, "value") else str(field_info.pii_category) if field_info.pii_category else None,
                })

        return {
            "compliant": len(violations) == 0,
            "environment": environment,
            "pii_fields_checked": [f.name for f in pii_fields if f.masking_strategy],
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
