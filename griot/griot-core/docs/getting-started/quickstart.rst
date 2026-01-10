Quickstart
==========

This quickstart shows you the core concepts of griot-core in 5 minutes.

Define a Contract
-----------------

A data contract defines the schema and constraints for your data:

.. code-block:: python

   from griot_core import GriotModel, Field

   class UserEvent(GriotModel):
       """User activity event contract."""

       event_id: str = Field(
           description="Unique event identifier",
           primary_key=True,
           pattern=r"^EVT-[A-Z0-9]{8}$"
       )
       user_id: str = Field(
           description="User who triggered the event",
           pattern=r"^USR-\d{6}$"
       )
       event_type: str = Field(
           description="Type of event",
           enum=["click", "view", "purchase", "signup"]
       )
       timestamp: str = Field(
           description="When the event occurred",
           format="datetime"
       )
       value: float = Field(
           description="Monetary value if applicable",
           ge=0.0,
           default=0.0
       )

Validate Data
-------------

Validate your data against the contract:

.. code-block:: python

   # Sample data
   data = [
       {
           "event_id": "EVT-ABC12345",
           "user_id": "USR-000001",
           "event_type": "purchase",
           "timestamp": "2026-01-10T14:30:00Z",
           "value": 99.99
       },
       {
           "event_id": "INVALID",  # Will fail pattern validation
           "user_id": "USR-000002",
           "event_type": "click",
           "timestamp": "2026-01-10T14:31:00Z",
           "value": 0.0
       }
   ]

   # Validate
   result = UserEvent.validate(data)

   print(f"Passed: {result.passed}")
   print(f"Total rows: {result.total_rows}")
   print(f"Failed rows: {result.failed_rows}")

   # Show errors
   for error in result.errors:
       print(f"Row {error.row_index}, Field '{error.field}': {error.message}")

Generate Mock Data
------------------

Create realistic test data that respects your constraints:

.. code-block:: python

   # Generate 100 rows of mock data
   mock_data = UserEvent.mock(rows=100)

   for row in mock_data[:3]:
       print(row)

   # Output:
   # {'event_id': 'EVT-X7K9M2PQ', 'user_id': 'USR-847291', ...}
   # {'event_id': 'EVT-L3N8R5TW', 'user_id': 'USR-193847', ...}
   # {'event_id': 'EVT-B2C6H9JK', 'user_id': 'USR-562018', ...}

Export for AI/LLM
-----------------

Export your contract in formats optimized for AI consumption:

.. code-block:: python

   # Export as LLM context
   manifest = UserEvent.to_manifest(format="llm_context")
   print(manifest)

   # Export as JSON-LD for semantic web
   json_ld = UserEvent.to_manifest(format="json_ld")

   # Export as Markdown documentation
   markdown = UserEvent.to_manifest(format="markdown")

Next Steps
----------

- :doc:`first-contract` - Build your first real contract
- :doc:`../user-guide/index` - Deep dive into all features
- :doc:`../examples/index` - Real-world contract examples
