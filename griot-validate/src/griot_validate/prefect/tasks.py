"""
Griot Enforce - Prefect Tasks

Prefect tasks for validating data against Griot contracts.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pandas as pd

__all__ = [
    "validate_task",
    "validate_local_task",
    "check_residency_task",
    "verify_masking_task",
    "griot_validate",
    "griot_validate_local",
    "griot_check_residency",
    "griot_verify_masking",
]


def validate_task(
    contract_id: str,
    data: pd.DataFrame | list[dict[str, Any]],
    registry_url: str | None = None,
    version: str | None = None,
    fail_on_error: bool = True,
    api_key: str | None = None,
    verify_masking: bool = False,
    environment: str | None = None,
) -> Any:
    """
    Prefect task for validating data against a registry contract.

    Args:
        contract_id: Contract ID in the registry.
        data: DataFrame or list of dicts to validate.
        registry_url: Registry URL (or from env).
        version: Specific contract version.
        fail_on_error: Raise exception on failure (default: True).
        api_key: API key for registry (or from env).
        verify_masking: Verify PII masking (default: False).
        environment: Environment name for masking checks.

    Returns:
        ValidationResult from griot-core.

    Example:
        from prefect import flow
        from griot_validate.prefect import validate_task

        @flow
        def etl_flow():
            df = extract_customers()
            validate_task("customer-profile", df, verify_masking=True, environment="staging")
            load_customers(df)
    """
    from griot_validate.validator import RuntimeValidator

    validator = RuntimeValidator(
        registry_url=registry_url,
        api_key=api_key,
        report_results=True,
    )

    return validator.validate(
        contract_id,
        data,
        version=version,
        fail_on_error=fail_on_error,
        verify_masking=verify_masking,
        environment=environment,
    )


def validate_local_task(
    contract_path: str,
    data: pd.DataFrame | list[dict[str, Any]],
    fail_on_error: bool = True,
) -> Any:
    """
    Prefect task for validating data against a local contract file.

    Args:
        contract_path: Path to YAML contract file.
        data: DataFrame or list of dicts to validate.
        fail_on_error: Raise exception on failure (default: True).

    Returns:
        ValidationResult from griot-core.
    """
    from griot_validate.validator import RuntimeValidator

    validator = RuntimeValidator()

    return validator.validate_local(
        contract_path,
        data,
        fail_on_error=fail_on_error,
    )


def check_residency_task(
    contract_id: str,
    region: str | None = None,
    destination: str | None = None,
    registry_url: str | None = None,
    version: str | None = None,
    api_key: str | None = None,
    fail_on_violation: bool = False,
) -> dict[str, Any]:
    """
    Prefect task for checking data residency compliance.

    FR-ENF-008: Block writes to non-compliant regions.

    Args:
        contract_id: Contract ID in the registry.
        region: Target region for data storage (explicit).
        destination: Cloud URI to auto-detect region from (e.g., s3://bucket-eu-west-1/).
        registry_url: Registry URL (or from env).
        version: Specific contract version.
        api_key: API key for registry (or from env).
        fail_on_violation: Raise exception on violation (default: False).

    Returns:
        Dictionary with compliance status and violations.

    Example:
        from prefect import flow
        from griot_validate.prefect import check_residency_task

        @flow
        def etl_flow():
            check_residency_task(
                "customer-profile",
                destination="s3://my-bucket-eu-west-1/data/",
                fail_on_violation=True
            )
            # Proceed with write if no exception raised
    """
    from griot_validate.validator import RuntimeValidator

    validator = RuntimeValidator(
        registry_url=registry_url,
        api_key=api_key,
    )

    return validator.check_residency(
        contract_id,
        region=region,
        destination=destination,
        version=version,
        fail_on_violation=fail_on_violation,
    )


def verify_masking_task(
    contract_id: str,
    data: pd.DataFrame | list[dict[str, Any]],
    registry_url: str | None = None,
    version: str | None = None,
    api_key: str | None = None,
    environment: str | None = None,
    fail_on_violation: bool = False,
) -> dict[str, Any]:
    """
    Prefect task for verifying PII masking compliance.

    FR-ENF-009: Verify PII is masked in non-prod environments.

    Args:
        contract_id: Contract ID in the registry.
        data: Data to check for masking compliance.
        registry_url: Registry URL (or from env).
        version: Specific contract version.
        api_key: API key for registry (or from env).
        environment: Environment name (e.g., "staging", "dev").
        fail_on_violation: Raise exception on violation (default: False).

    Returns:
        Dictionary with masking verification results.

    Example:
        from prefect import flow
        from griot_validate.prefect import verify_masking_task

        @flow
        def etl_flow():
            df = extract_customers()
            verify_masking_task(
                "customer-profile",
                df,
                environment="staging",
                fail_on_violation=True
            )
            load_customers(df)
    """
    from griot_validate.validator import RuntimeValidator

    validator = RuntimeValidator(
        registry_url=registry_url,
        api_key=api_key,
    )

    return validator.verify_masking(
        contract_id,
        data,
        version=version,
        environment=environment,
        fail_on_violation=fail_on_violation,
    )


# Create decorated versions for easy import
def _create_prefect_tasks() -> tuple[Any, Any, Any, Any]:
    """Create Prefect-decorated versions of tasks."""
    try:
        from prefect import task

        return (
            task(validate_task, name="griot_validate"),
            task(validate_local_task, name="griot_validate_local"),
            task(check_residency_task, name="griot_check_residency"),
            task(verify_masking_task, name="griot_verify_masking"),
        )
    except ImportError:
        return validate_task, validate_local_task, check_residency_task, verify_masking_task


try:
    griot_validate, griot_validate_local, griot_check_residency, griot_verify_masking = (
        _create_prefect_tasks()
    )
except Exception:
    griot_validate = validate_task
    griot_validate_local = validate_local_task
    griot_check_residency = check_residency_task
    griot_verify_masking = verify_masking_task
