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
    "griot_validate",
    "griot_validate_local",
    "griot_check_residency",
]


def validate_task(
    contract_id: str,
    data: pd.DataFrame | list[dict[str, Any]],
    registry_url: str | None = None,
    version: str | None = None,
    fail_on_error: bool = True,
    api_key: str | None = None,
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

    Returns:
        ValidationResult from griot-core.

    Example:
        from prefect import flow
        from griot_enforce.prefect import validate_task

        @flow
        def etl_flow():
            df = extract_customers()
            validate_task("customer-profile", df)
            load_customers(df)
    """
    from griot_enforce.validator import RuntimeValidator

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
    from griot_enforce.validator import RuntimeValidator

    validator = RuntimeValidator()

    return validator.validate_local(
        contract_path,
        data,
        fail_on_error=fail_on_error,
    )


def check_residency_task(
    contract_id: str,
    region: str,
    registry_url: str | None = None,
    version: str | None = None,
    api_key: str | None = None,
) -> dict[str, Any]:
    """
    Prefect task for checking data residency compliance.

    Args:
        contract_id: Contract ID in the registry.
        region: Target region for data storage.
        registry_url: Registry URL (or from env).
        version: Specific contract version.
        api_key: API key for registry (or from env).

    Returns:
        Dictionary with compliance status and violations.
    """
    from griot_enforce.validator import RuntimeValidator

    validator = RuntimeValidator(
        registry_url=registry_url,
        api_key=api_key,
    )

    return validator.check_residency(contract_id, region, version)


# Create decorated versions for easy import
def _create_prefect_tasks() -> tuple[Any, Any, Any]:
    """Create Prefect-decorated versions of tasks."""
    try:
        from prefect import task

        return (
            task(validate_task, name="griot_validate"),
            task(validate_local_task, name="griot_validate_local"),
            task(check_residency_task, name="griot_check_residency"),
        )
    except ImportError:
        return validate_task, validate_local_task, check_residency_task


try:
    griot_validate, griot_validate_local, griot_check_residency = _create_prefect_tasks()
except Exception:
    griot_validate = validate_task
    griot_validate_local = validate_local_task
    griot_check_residency = check_residency_task
