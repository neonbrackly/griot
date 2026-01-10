griot-core Documentation
=========================

**griot-core** is the foundation library for defining, validating, and managing data contracts
with full AI/LLM readiness support. It uses Python stdlib only (zero external dependencies).

.. code-block:: python

   from griot_core import GriotModel, Field

   class Customer(GriotModel):
       customer_id: str = Field(
           description="Unique customer identifier",
           primary_key=True,
           pattern=r"^CUST-\d{6}$"
       )
       email: str = Field(
           description="Customer email address",
           format="email"
       )

   # Validate data
   result = Customer.validate(data)

   # Generate mock data
   mock_data = Customer.mock(rows=100)

   # Export for AI/LLM
   manifest = Customer.to_manifest(format="llm_context")

Key Features
------------

- **Zero Dependencies**: Pure Python stdlib implementation
- **Type-Safe Contracts**: Define schemas with full type hints
- **Rich Validation**: Pattern matching, ranges, enums, custom rules
- **PII Support**: Built-in PII classification and sensitivity levels
- **Data Residency**: Geographic compliance configuration
- **Data Lineage**: Track sources, transformations, and consumers
- **AI/LLM Ready**: Export contracts for AI consumption
- **Report Generation**: Analytics, AI readiness, and compliance reports

.. toctree::
   :maxdepth: 2
   :caption: Contents

   getting-started/index
   user-guide/index
   api/index
   examples/index
   types/index
   changelog

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
