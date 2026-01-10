"""
Griot Enforce - Airflow Integration

Operators and sensors for validating data in Airflow DAGs.

Example:
    from griot_enforce.airflow import GriotValidateOperator, GriotFreshnessSensor

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
from griot_enforce.airflow.operators import GriotValidateOperator
from griot_enforce.airflow.sensors import GriotFreshnessSensor

__all__ = [
    "GriotValidateOperator",
    "GriotFreshnessSensor",
]
