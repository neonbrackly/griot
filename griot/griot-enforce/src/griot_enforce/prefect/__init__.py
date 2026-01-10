"""
Griot Enforce - Prefect Integration

Tasks for validating data in Prefect flows.

Example:
    from prefect import flow
    from griot_enforce.prefect import validate_task

    @flow
    def etl_flow():
        df = extract_customers()
        validate_task("customer-profile", df)
        load_customers(df)

    # Or use pre-decorated tasks:
    from griot_enforce.prefect import griot_validate

    @flow
    def etl_flow():
        df = extract_customers()
        griot_validate("customer-profile", df)
        load_customers(df)
"""
from griot_enforce.prefect.tasks import (
    check_residency_task,
    griot_check_residency,
    griot_validate,
    griot_validate_local,
    validate_local_task,
    validate_task,
)

__all__ = [
    "validate_task",
    "validate_local_task",
    "check_residency_task",
    "griot_validate",
    "griot_validate_local",
    "griot_check_residency",
]
