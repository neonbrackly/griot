# griot-core API Reference

Complete API reference for the griot-core package.

## Models Module

```{eval-rst}
.. module:: griot_core.models
   :synopsis: Data contract models
```

### GriotModel

```{eval-rst}
.. autoclass:: griot_core.GriotModel
   :members:
   :undoc-members:
   :show-inheritance:
```

### Field

```{eval-rst}
.. autoclass:: griot_core.Field
   :members:
   :undoc-members:
```

### FieldInfo

```{eval-rst}
.. autoclass:: griot_core.models.FieldInfo
   :members:
   :undoc-members:
```

## Validation Module

```{eval-rst}
.. module:: griot_core.validation
   :synopsis: Data validation engine
```

### ValidationResult

```{eval-rst}
.. autoclass:: griot_core.ValidationResult
   :members:
   :undoc-members:
```

### FieldValidationError

```{eval-rst}
.. autoclass:: griot_core.FieldValidationError
   :members:
   :undoc-members:
```

### FieldStats

```{eval-rst}
.. autoclass:: griot_core.validation.FieldStats
   :members:
   :undoc-members:
```

### Functions

```{eval-rst}
.. autofunction:: griot_core.validate_data
.. autofunction:: griot_core.validation.validate_single_row
.. autofunction:: griot_core.validation.validate_value
```

## Contract Module

```{eval-rst}
.. module:: griot_core.contract
   :synopsis: Contract loading and operations
```

### ContractDiff

```{eval-rst}
.. autoclass:: griot_core.contract.ContractDiff
   :members:
   :undoc-members:
```

### Functions

```{eval-rst}
.. autofunction:: griot_core.load_contract_from_yaml
.. autofunction:: griot_core.load_contract_from_string
.. autofunction:: griot_core.load_contract_from_dict
.. autofunction:: griot_core.contract.diff_contracts
.. autofunction:: griot_core.contract.lint_contract
.. autofunction:: griot_core.contract.model_to_yaml
```

## Types Module

```{eval-rst}
.. module:: griot_core.types
   :synopsis: Type definitions and enums
```

### Enums

```{eval-rst}
.. autoclass:: griot_core.types.DataType
   :members:
   :undoc-members:

.. autoclass:: griot_core.types.ConstraintType
   :members:
   :undoc-members:

.. autoclass:: griot_core.types.FieldFormat
   :members:
   :undoc-members:

.. autoclass:: griot_core.types.Severity
   :members:
   :undoc-members:

.. autoclass:: griot_core.types.AggregationType
   :members:
   :undoc-members:

.. autoclass:: griot_core.types.PIICategory
   :members:
   :undoc-members:

.. autoclass:: griot_core.types.SensitivityLevel
   :members:
   :undoc-members:

.. autoclass:: griot_core.types.MaskingStrategy
   :members:
   :undoc-members:

.. autoclass:: griot_core.types.LegalBasis
   :members:
   :undoc-members:

.. autoclass:: griot_core.types.DataRegion
   :members:
   :undoc-members:
```

## Mock Module

```{eval-rst}
.. module:: griot_core.mock
   :synopsis: Mock data generation
```

```{eval-rst}
.. autofunction:: griot_core.generate_mock_data
```

## Manifest Module

```{eval-rst}
.. module:: griot_core.manifest
   :synopsis: Contract manifest export
```

```{eval-rst}
.. autofunction:: griot_core.export_manifest
```

## Reports Module

```{eval-rst}
.. module:: griot_core.reports
   :synopsis: Report generation
```

### AnalyticsReport

```{eval-rst}
.. autoclass:: griot_core.reports.AnalyticsReport
   :members:
   :undoc-members:
```

### AIReadinessReport

```{eval-rst}
.. autoclass:: griot_core.reports.AIReadinessReport
   :members:
   :undoc-members:
```

### Functions

```{eval-rst}
.. autofunction:: griot_core.reports.generate_analytics_report
.. autofunction:: griot_core.reports.generate_ai_readiness_report
```

## Exceptions Module

```{eval-rst}
.. module:: griot_core.exceptions
   :synopsis: Exception hierarchy
```

```{eval-rst}
.. autoexception:: griot_core.GriotError
.. autoexception:: griot_core.ValidationError
.. autoexception:: griot_core.ContractError
.. autoexception:: griot_core.SchemaError
```
