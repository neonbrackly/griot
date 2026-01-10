"""
Griot Enforce - Runtime Validation for Data Orchestrators

Runtime validation library for data orchestrators (Airflow, Dagster, Prefect).
Wraps griot-core SDK with runtime features including registry integration,
caching, and result reporting.

Core Usage:
    from griot_enforce import RuntimeValidator

    validator = RuntimeValidator(registry_url="https://registry.example.com")
    result = validator.validate("customer-profile", dataframe)

    # Or with local contracts:
    result = validator.validate_local("./contracts/customer.yaml", dataframe)

Airflow:
    from griot_enforce.airflow import GriotValidateOperator, GriotFreshnessSensor

    validate = GriotValidateOperator(
        task_id="validate",
        contract_id="customer-profile",
        data_path="{{ ti.xcom_pull('extract') }}",
    )

Dagster:
    from griot_enforce.dagster import GriotResource, griot_asset

    @asset
    def customers(griot: GriotResource):
        df = extract_customers()
        griot.validate("customer-profile", df)
        return df

Prefect:
    from griot_enforce.prefect import validate_task

    @flow
    def etl_flow():
        df = extract_customers()
        validate_task("customer-profile", df)
        load_customers(df)
"""
from __future__ import annotations

__version__ = "0.1.0"

# Core validator and exceptions
from griot_enforce.validator import (
    MaskingViolationError,
    ResidencyViolationError,
    RuntimeValidationError,
    RuntimeValidator,
)

__all__ = [
    "__version__",
    "RuntimeValidator",
    "RuntimeValidationError",
    "ResidencyViolationError",
    "MaskingViolationError",
]


def __getattr__(name: str) -> object:
    """Lazy import orchestrator integrations."""
    if name == "airflow":
        from griot_enforce import airflow
        return airflow
    if name == "dagster":
        from griot_enforce import dagster
        return dagster
    if name == "prefect":
        from griot_enforce import prefect
        return prefect
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
