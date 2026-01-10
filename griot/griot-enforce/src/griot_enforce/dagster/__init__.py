"""
Griot Enforce - Dagster Integration

Resources and decorators for validating data in Dagster pipelines.

Example:
    from dagster import Definitions, asset
    from griot_enforce.dagster import GriotResource, griot_asset

    @asset
    def customers(griot: GriotResource):
        df = extract_customers()
        griot.validate("customer-profile", df)
        return df

    # Or with decorator:
    @asset
    @griot_asset(contract_id="customer-profile")
    def customers():
        return extract_customers()

    defs = Definitions(
        assets=[customers],
        resources={"griot": GriotResource(registry_url="...")}
    )
"""
from griot_enforce.dagster.decorators import griot_asset, griot_op
from griot_enforce.dagster.resources import GriotResource

__all__ = [
    "GriotResource",
    "griot_asset",
    "griot_op",
]
