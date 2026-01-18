griot\_core.dataframe\_validation
=================================

.. automodule:: griot_core.dataframe_validation

   
   .. rubric:: Functions

   .. autosummary::
   
      check_backend
      get_available_backends
      get_global_registry
      get_validator
      register_validator
      validate_data_batch
      validate_data_mapping
      validate_dataframe
      validate_list_of_dicts
      validate_schema_data
   
   .. rubric:: Classes

   .. autosummary::
   
      DaskValidator
      DataFrameType
      DataFrameValidationResult
      DataFrameValidator
      DataFrameValidatorRegistry
      FieldValidationResult
      MultiSchemaValidationResult
      PandasValidator
      PanderaSchemaGenerator
      PolarsValidator
      PySparkValidator
      ValidationMode
   
   .. rubric:: Exceptions

   .. autosummary::
   
      PanderaNotInstalledError
      ValidatorNotFoundError
   