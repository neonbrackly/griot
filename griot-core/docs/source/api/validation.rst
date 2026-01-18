Validation API
==============

The validation module provides DataFrame validation using Pandera.

Core Functions
--------------

validate_dataframe
^^^^^^^^^^^^^^^^^^

.. function:: griot_core.validate_dataframe(df, schema, *, coerce: bool = False) -> DataFrameValidationResult

   Validate a DataFrame against a schema.

   :param df: DataFrame to validate (pandas, polars, spark, or dask)
   :param schema: Schema class or instance
   :param coerce: Whether to coerce types before validation (default: False)
   :returns: :class:`DataFrameValidationResult` with validation results

   **Example**

   .. code-block:: python

      import pandas as pd
      from griot_core import Schema, Field, validate_dataframe

      class ProductSchema(Schema):
          product_id: str = Field("Product ID", primary_key=True)
          name: str = Field("Product name")
          price: float = Field("Price")

      df = pd.DataFrame({
          'product_id': ['P001', 'P002'],
          'name': ['Widget', 'Gadget'],
          'price': [9.99, 19.99]
      })

      result = validate_dataframe(df, ProductSchema)

      if result.is_valid:
          print("Data is valid!")
      else:
          for error in result.errors:
              print(f"Error: {error.message}")

validate_list_of_dicts
^^^^^^^^^^^^^^^^^^^^^^

.. function:: griot_core.validate_list_of_dicts(data: list[dict], schema) -> DataFrameValidationResult

   Validate a list of dictionaries against a schema.

   Converts the list to a DataFrame internally before validation.

   :param data: List of dictionaries to validate
   :param schema: Schema class or instance
   :returns: :class:`DataFrameValidationResult`

   .. code-block:: python

      data = [
          {'product_id': 'P001', 'name': 'Widget', 'price': 9.99},
          {'product_id': 'P002', 'name': 'Gadget', 'price': 19.99},
      ]

      result = validate_list_of_dicts(data, ProductSchema)

validate_schema_data
^^^^^^^^^^^^^^^^^^^^

.. function:: griot_core.validate_schema_data(schema, df) -> DataFrameValidationResult

   Validate data against a schema instance.

   :param schema: Schema instance
   :param df: DataFrame to validate
   :returns: :class:`DataFrameValidationResult`

   .. code-block:: python

      schema = ProductSchema()
      result = validate_schema_data(schema, df)

validate_data_mapping
^^^^^^^^^^^^^^^^^^^^^

.. function:: griot_core.validate_data_mapping(schemas: dict[str, Schema], data: dict[str, DataFrame]) -> MultiSchemaValidationResult

   Validate multiple DataFrames against multiple schemas.

   :param schemas: Dictionary mapping schema names to Schema instances
   :param data: Dictionary mapping schema names to DataFrames
   :returns: :class:`MultiSchemaValidationResult`

   .. code-block:: python

      schemas = {
          'orders': OrderSchema(),
          'products': ProductSchema(),
      }

      data = {
          'orders': orders_df,
          'products': products_df,
      }

      result = validate_data_mapping(schemas, data)

      for schema_name, validation_result in result.results.items():
          print(f"{schema_name}: {'Valid' if validation_result.is_valid else 'Invalid'}")

validate_data_batch
^^^^^^^^^^^^^^^^^^^

.. function:: griot_core.validate_data_batch(schema, dataframes: list) -> list[DataFrameValidationResult]

   Validate multiple DataFrames against a single schema.

   :param schema: Schema class or instance
   :param dataframes: List of DataFrames
   :returns: List of :class:`DataFrameValidationResult`

   .. code-block:: python

      results = validate_data_batch(ProductSchema, [df1, df2, df3])

      for i, result in enumerate(results):
          print(f"DataFrame {i}: {'Valid' if result.is_valid else 'Invalid'}")

Result Classes
--------------

DataFrameValidationResult
^^^^^^^^^^^^^^^^^^^^^^^^^

.. class:: griot_core.DataFrameValidationResult

   Result of DataFrame validation.

   **Properties**

   .. attribute:: is_valid
      :type: bool

      ``True`` if validation passed.

   .. attribute:: errors
      :type: list[FieldValidationResult]

      List of validation errors.

   .. attribute:: schema_name
      :type: str | None

      Name of the validated schema.

   .. attribute:: row_count
      :type: int | None

      Number of rows validated.

   **Methods**

   .. method:: summary() -> str

      Get a summary string.

   .. method:: to_dict() -> dict

      Convert to dictionary representation.

   **Example**

   .. code-block:: python

      result = validate_dataframe(df, schema)

      print(f"Valid: {result.is_valid}")
      print(f"Schema: {result.schema_name}")
      print(f"Rows: {result.row_count}")
      print(f"Error count: {len(result.errors)}")

      # Iterate over errors
      for error in result.errors:
          print(f"  {error.field}: {error.message}")

      # Get summary
      print(result.summary())

      # Convert to dict
      report = result.to_dict()

FieldValidationResult
^^^^^^^^^^^^^^^^^^^^^

.. class:: griot_core.FieldValidationResult

   Validation result for a single field.

   .. attribute:: field
      :type: str

      Field name.

   .. attribute:: is_valid
      :type: bool

      Whether the field passed validation.

   .. attribute:: message
      :type: str | None

      Error message if validation failed.

   .. attribute:: error_type
      :type: str | None

      Type of error.

   .. attribute:: details
      :type: dict | None

      Additional error details.

MultiSchemaValidationResult
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. class:: griot_core.MultiSchemaValidationResult

   Result of validating multiple schemas.

   .. attribute:: is_valid
      :type: bool

      ``True`` if all schemas passed validation.

   .. attribute:: results
      :type: dict[str, DataFrameValidationResult]

      Dictionary mapping schema names to validation results.

   .. method:: summary() -> str

      Get a summary string.

   .. method:: to_dict() -> dict

      Convert to dictionary representation.

Pandera Integration
-------------------

PanderaSchemaGenerator
^^^^^^^^^^^^^^^^^^^^^^

.. class:: griot_core.PanderaSchemaGenerator

   Generates Pandera schemas from Griot schemas.

   This class is used internally by validation functions but can be used
   directly for advanced use cases.

   **Methods**

   .. method:: generate(schema: Schema) -> pa.DataFrameSchema

      Generate a Pandera DataFrameSchema from a Griot Schema.

      :param schema: Griot Schema instance
      :returns: Pandera DataFrameSchema

   .. code-block:: python

      from griot_core import PanderaSchemaGenerator, Schema, Field

      class MySchema(Schema):
          id: str = Field("ID", primary_key=True)
          value: int = Field("Value")

      generator = PanderaSchemaGenerator()
      pandera_schema = generator.generate(MySchema())

      # Use pandera schema directly
      validated_df = pandera_schema.validate(df)

Backend Management
------------------

get_available_backends
^^^^^^^^^^^^^^^^^^^^^^

.. function:: griot_core.get_available_backends() -> dict[str, dict]

   Get information about available DataFrame backends.

   :returns: Dictionary with backend info

   .. code-block:: python

      backends = get_available_backends()

      for name, info in backends.items():
          status = "Available" if info['available'] else "Not installed"
          print(f"  {name}: {status}")

   Example output:

   .. code-block:: text

      pandas: Available
      polars: Not installed
      spark: Not installed
      dask: Not installed

check_backend
^^^^^^^^^^^^^

.. function:: griot_core.check_backend(backend: str) -> bool

   Check if a specific backend is available.

   :param backend: Backend name ("pandas", "polars", "spark", "dask")
   :returns: ``True`` if backend is available

   .. code-block:: python

      if check_backend("pandas"):
          # Use pandas features
          pass

Validator Registry
------------------

get_validator
^^^^^^^^^^^^^

.. function:: griot_core.get_validator(df_type: DataFrameType | str) -> DataFrameValidator

   Get a validator for a specific DataFrame type.

   :param df_type: DataFrame type (enum or string)
   :returns: :class:`DataFrameValidator` instance
   :raises ValidatorNotFoundError: If no validator for the type

   .. code-block:: python

      validator = get_validator("pandas")
      result = validator.validate(df, schema)

register_validator
^^^^^^^^^^^^^^^^^^

.. function:: griot_core.register_validator(df_type: DataFrameType | str, validator: DataFrameValidator) -> None

   Register a custom validator for a DataFrame type.

   :param df_type: DataFrame type
   :param validator: Validator instance

   .. code-block:: python

      class CustomValidator(DataFrameValidator):
          def validate(self, df, schema):
              # Custom validation logic
              pass

      register_validator("custom", CustomValidator())

DataFrameValidator
^^^^^^^^^^^^^^^^^^

.. class:: griot_core.DataFrameValidator

   Base class for DataFrame validators.

   Subclass this to create custom validators.

   .. method:: validate(df, schema) -> DataFrameValidationResult
      :abstractmethod:

      Validate a DataFrame against a schema.

      :param df: DataFrame to validate
      :param schema: Schema to validate against
      :returns: Validation result

DataFrameValidatorRegistry
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. class:: griot_core.DataFrameValidatorRegistry

   Registry for DataFrame validators.

   .. method:: register(df_type: DataFrameType | str, validator: DataFrameValidator) -> None

      Register a validator.

   .. method:: get(df_type: DataFrameType | str) -> DataFrameValidator

      Get a validator.

   .. method:: detect_type(df) -> DataFrameType

      Detect the DataFrame type.

Validation Modes
----------------

ValidationMode
^^^^^^^^^^^^^^

.. class:: griot_core.ValidationMode

   Validation strictness modes.

   .. attribute:: STRICT

      Fail on any validation error.

   .. attribute:: LENIENT

      Continue validation after errors.

   .. attribute:: COERCE

      Attempt to coerce types before validation.

Exceptions
----------

ValidatorNotFoundError
^^^^^^^^^^^^^^^^^^^^^^

.. exception:: griot_core.ValidatorNotFoundError

   Raised when no validator is found for a DataFrame type.

   .. code-block:: python

      try:
          validator = get_validator("unknown")
      except ValidatorNotFoundError as e:
          print(f"No validator for: {e}")

PanderaNotInstalledError
^^^^^^^^^^^^^^^^^^^^^^^^

.. exception:: griot_core.PanderaNotInstalledError

   Raised when Pandera is not installed.

   .. code-block:: python

      try:
          result = validate_dataframe(df, schema)
      except PanderaNotInstalledError:
          print("Install pandera: pip install griot-core[pandas]")

Usage Examples
--------------

Basic Validation
^^^^^^^^^^^^^^^^

.. code-block:: python

   import pandas as pd
   from griot_core import Schema, Field, validate_dataframe

   class OrderSchema(Schema):
       order_id: str = Field("Order ID", primary_key=True)
       customer_id: str = Field("Customer ID")
       total: float = Field("Order total")

   df = pd.DataFrame({
       'order_id': ['O001', 'O002', 'O003'],
       'customer_id': ['C001', 'C002', 'C003'],
       'total': [100.00, 250.50, 75.25]
   })

   result = validate_dataframe(df, OrderSchema)
   print(f"Valid: {result.is_valid}")

Validation with Quality Rules
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from griot_core import Schema, Field, QualityRule, validate_dataframe

   class StrictOrderSchema(Schema):
       _quality = [
           QualityRule.row_count(must_be_greater_than=0),
       ]

       order_id: str = Field(
           "Order ID",
           primary_key=True,
           quality=[
               QualityRule.null_values(must_be=0),
               QualityRule.duplicate_values(must_be=0),
           ]
       )

       total: float = Field(
           "Order total",
           quality=[
               QualityRule.null_values(must_be=0),
               QualityRule.invalid_values(must_be=0, min_value=0),
           ]
       )

   result = validate_dataframe(df, StrictOrderSchema)

   for error in result.errors:
       print(f"Error in {error.field}: {error.message}")

Multi-Backend Support
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # pandas
   import pandas as pd
   pandas_df = pd.DataFrame(...)
   result = validate_dataframe(pandas_df, schema)

   # polars
   import polars as pl
   polars_df = pl.DataFrame(...)
   result = validate_dataframe(polars_df, schema)

   # Detect backend
   backends = get_available_backends()
   print(f"Available: {[k for k, v in backends.items() if v['available']]}")
