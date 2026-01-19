"""
Griot Enforce - Airflow Integration

Operators and sensors for validating data in Airflow DAGs.

Example:
    from griot_validate.airflow import GriotValidateOperator, GriotFreshnessSensor

    validate_customers = GriotValidateOperator(
        task_id="validate_customers",
        contract_id="customer-profile",
        data_path="{{ ti.xcom_pull('extract') }}",
    )

    wait_for_data = GriotFreshnessSensor(
        task_id="wait_for_data",
        contract_id="customer-profile",
        max_age_minutes=60,
    )
"""
from griot_validate.airflow.operators import GriotResidencyOperator, GriotValidateOperator
from griot_validate.airflow.sensors import GriotFreshnessSensor

__all__ = [
    "GriotValidateOperator",
    "GriotResidencyOperator",
    "GriotFreshnessSensor",
]
