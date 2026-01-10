# API Reference

Complete API documentation for all Griot packages.

```{toctree}
:maxdepth: 2

core
cli
enforce
registry
```

## Package Overview

### griot-core

The foundation library with all business logic.

**Key Classes:**
- {py:class}`griot_core.GriotModel` - Base class for data contracts
- {py:class}`griot_core.Field` - Field definition with constraints
- {py:class}`griot_core.ValidationResult` - Validation results
- {py:class}`griot_core.FieldValidationError` - Validation errors

**Key Functions:**
- {py:func}`griot_core.validate_data` - Validate data against a contract
- {py:func}`griot_core.load_contract_from_yaml` - Load contract from YAML
- {py:func}`griot_core.generate_mock_data` - Generate mock data

### griot-cli

Command-line interface for contract operations.

**Commands:**
- `griot validate` - Validate data against contracts
- `griot lint` - Check contract quality
- `griot diff` - Compare contract versions
- `griot mock` - Generate mock data
- `griot manifest` - Export contract manifests
- `griot report` - Generate reports
- `griot push/pull` - Registry operations

### griot-enforce

Runtime validation for data orchestrators.

**Key Classes:**
- {py:class}`griot_enforce.RuntimeValidator` - Core validator
- {py:class}`griot_enforce.airflow.GriotValidateOperator` - Airflow operator
- {py:class}`griot_enforce.dagster.GriotResource` - Dagster resource

### griot-registry

FastAPI server for contract management.

**Endpoints:**
- `POST /contracts` - Create contract
- `GET /contracts/{name}` - Get contract
- `GET /contracts/{name}/versions` - List versions
- `POST /contracts/{name}/validate` - Validate data
