"""
Griot Enforce - Dagster Resources

Dagster resources for Griot validation.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pandas as pd

__all__ = [
    "GriotResource",
]


class GriotResource:
    """
    Dagster resource for Griot validation.

    Provides validator instance to assets/ops with automatic
    registry integration and result reporting.

    Example:
        from dagster import Definitions, asset
        from griot_validate.dagster import GriotResource

        @asset
        def customers(griot: GriotResource):
            df = extract_customers()
            griot.validate("customer-profile", df)
            return df

        defs = Definitions(
            assets=[customers],
            resources={"griot": GriotResource(registry_url="...")}
        )
    """

    def __new__(cls, **kwargs: Any) -> Any:
        """Create resource instance using Dagster's ConfigurableResource."""
        try:
            from dagster import ConfigurableResource
        except ImportError:
            raise ImportError(
                "dagster is required for Dagster resources. "
                "Install with: pip install griot-validate[dagster]"
            )

        class _GriotResource(ConfigurableResource):
            """Dagster ConfigurableResource for Griot validation."""

            registry_url: str | None = None
            api_key: str | None = None
            cache_ttl: int = 300
            report_results: bool = True

            def validate(
                self,
                contract_id: str,
                data: pd.DataFrame | list[dict[str, Any]],
                version: str | None = None,
                fail_on_error: bool = True,
                verify_masking: bool = False,
                environment: str | None = None,
            ) -> Any:
                """
                Validate data against a contract from registry.

                Args:
                    contract_id: Contract ID in registry.
                    data: DataFrame or list of dicts to validate.
                    version: Specific contract version.
                    fail_on_error: Raise on validation failure (default: True).
                    verify_masking: Verify PII masking (default: False).
                    environment: Environment name for masking checks.
                """
                from griot_validate.validator import RuntimeValidator

                validator = RuntimeValidator(
                    registry_url=self.registry_url,
                    api_key=self.api_key,
                    cache_ttl=self.cache_ttl,
                    report_results=self.report_results,
                )
                return validator.validate(
                    contract_id,
                    data,
                    version=version,
                    fail_on_error=fail_on_error,
                    verify_masking=verify_masking,
                    environment=environment,
                )

            def validate_local(
                self,
                contract_path: str,
                data: pd.DataFrame | list[dict[str, Any]],
                fail_on_error: bool = True,
            ) -> Any:
                """Validate data against a local contract file."""
                from griot_validate.validator import RuntimeValidator

                validator = RuntimeValidator()
                return validator.validate_local(
                    contract_path,
                    data,
                    fail_on_error=fail_on_error,
                )

            def get_contract(
                self,
                contract_id: str,
                version: str | None = None,
            ) -> Any:
                """Fetch contract from registry."""
                from griot_validate.validator import RuntimeValidator

                validator = RuntimeValidator(
                    registry_url=self.registry_url,
                    api_key=self.api_key,
                    cache_ttl=self.cache_ttl,
                )
                return validator.get_contract(contract_id, version)

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

                FR-ENF-008: Block writes to non-compliant regions.

                Args:
                    contract_id: Contract ID in registry.
                    region: Explicit region to check.
                    destination: Cloud URI to auto-detect region from.
                    version: Specific contract version.
                    fail_on_violation: Raise on violation (default: False).
                """
                from griot_validate.validator import RuntimeValidator

                validator = RuntimeValidator(
                    registry_url=self.registry_url,
                    api_key=self.api_key,
                )
                return validator.check_residency(
                    contract_id,
                    region=region,
                    destination=destination,
                    version=version,
                    fail_on_violation=fail_on_violation,
                )

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
                    contract_id: Contract ID in registry.
                    data: Data to check for masking compliance.
                    version: Specific contract version.
                    environment: Environment name for conditional enforcement.
                    fail_on_violation: Raise on violation (default: False).
                """
                from griot_validate.validator import RuntimeValidator

                validator = RuntimeValidator(
                    registry_url=self.registry_url,
                    api_key=self.api_key,
                )
                return validator.verify_masking(
                    contract_id,
                    data,
                    version=version,
                    environment=environment,
                    fail_on_violation=fail_on_violation,
                )

        return _GriotResource(**kwargs)
