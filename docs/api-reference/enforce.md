# griot-enforce API Reference

Runtime validation for data orchestrators.

## Installation

```bash
# Core only
pip install griot-validate

# With Airflow
pip install griot-validate[airflow]

# With Dagster
pip install griot-validate[dagster]

# With Prefect
pip install griot-validate[prefect]

# All orchestrators
pip install griot-validate[all]
```

## RuntimeValidator

The core validator class for runtime data validation.

```{eval-rst}
.. autoclass:: griot_enforce.RuntimeValidator
   :members:
   :undoc-members:
   :show-inheritance:
```

### Usage

```python
from griot_validate import RuntimeValidator

# Create validator
validator = RuntimeValidator(
    registry_url="https://registry.example.com",
    api_key="your-api-key",
    cache_ttl=300,  # 5 minutes
)

# Validate data
result = validator.validate(
    contract_name="customer",
    data=dataframe,
)

# Validate with local contract
result = validator.validate_local(
    contract_path="contracts/customer.yaml",
    data=dataframe,
)
```

## Airflow Integration

### GriotValidateOperator

```{eval-rst}
.. autoclass:: griot_enforce.airflow.GriotValidateOperator
   :members:
   :undoc-members:
```

**Usage:**

```python
from griot_validate.airflow import GriotValidateOperator

validate_task = GriotValidateOperator(
    task_id="validate_customer_data",
    contract_name="customer",
    data_path="/data/customers.parquet",
    registry_url="https://registry.example.com",
    fail_on_error=True,
)
```

### GriotFreshnessSensor

```{eval-rst}
.. autoclass:: griot_enforce.airflow.GriotFreshnessSensor
   :members:
   :undoc-members:
```

### GriotResidencyOperator

```{eval-rst}
.. autoclass:: griot_enforce.airflow.GriotResidencyOperator
   :members:
   :undoc-members:
```

## Dagster Integration

### GriotResource

```{eval-rst}
.. autoclass:: griot_enforce.dagster.GriotResource
   :members:
   :undoc-members:
```

**Usage:**

```python
from dagster import Definitions, asset
from griot_validate.dagster import GriotResource


@asset
def customer_data(griot: GriotResource):
    data = load_data()
    result = griot.validate("customer", data)
    result.raise_on_failure()
    return data


defs = Definitions(
    assets=[customer_data],
    resources={
        "griot": GriotResource(
            registry_url="https://registry.example.com",
        ),
    },
)
```

### @griot_asset Decorator

```{eval-rst}
.. autodecorator:: griot_enforce.dagster.griot_asset
```

**Usage:**

```python
from griot_validate.dagster import griot_asset


@griot_asset(contract="customer")
def customer_data():
    return load_customer_data()
```

## Prefect Integration

### validate_task

```{eval-rst}
.. autodecorator:: griot_enforce.prefect.validate_task
```

**Usage:**

```python
from prefect import flow
from griot_validate.prefect import validate_task


@validate_task(contract="customer")
def process_customers(data):
    return transform(data)


@flow
def customer_pipeline():
    data = load_data()
    result = process_customers(data)
    save(result)
```

### check_residency_task

```{eval-rst}
.. autodecorator:: griot_enforce.prefect.check_residency_task
```

### verify_masking_task

```{eval-rst}
.. autodecorator:: griot_enforce.prefect.verify_masking_task
```

## Exceptions

```{eval-rst}
.. autoexception:: griot_enforce.ResidencyViolationError
.. autoexception:: griot_enforce.MaskingViolationError
```
