Mock Data Generation
====================

griot-core can generate realistic mock data that respects your contract constraints.

Basic Mock Generation
---------------------

Generate mock data using the ``mock()`` class method:

.. code-block:: python

   from griot_core import GriotModel, Field

   class User(GriotModel):
       user_id: str = Field(
           description="User ID",
           primary_key=True,
           pattern=r"^USR-\d{6}$"
       )
       email: str = Field(
           description="Email",
           format="email"
       )
       age: int = Field(
           description="Age",
           ge=18,
           le=100
       )
       status: str = Field(
           description="Status",
           enum=["active", "inactive", "pending"]
       )

   # Generate 10 rows
   mock_data = User.mock(rows=10)

   for row in mock_data:
       print(row)
   # {'user_id': 'USR-847291', 'email': 'user_847@example.com', 'age': 42, 'status': 'active'}
   # {'user_id': 'USR-193847', 'email': 'user_193@example.com', 'age': 35, 'status': 'pending'}
   # ...

Constraint-Aware Generation
---------------------------

Mock data respects all field constraints:

.. code-block:: python

   class Product(GriotModel):
       # Pattern constraint
       sku: str = Field(
           description="SKU",
           pattern=r"^[A-Z]{3}-\d{4}$"
       )
       # Generated: "ABC-1234", "XYZ-5678"

       # Length constraints
       name: str = Field(
           description="Product name",
           min_length=5,
           max_length=50
       )
       # Generated: Names between 5-50 chars

       # Numeric range
       price: float = Field(
           description="Price",
           ge=0.01,
           le=9999.99
       )
       # Generated: Values in range 0.01-9999.99

       # Enum constraint
       category: str = Field(
           description="Category",
           enum=["electronics", "clothing", "home", "food"]
       )
       # Generated: One of the enum values

       # Multiple of
       weight_grams: int = Field(
           description="Weight",
           ge=100,
           le=10000,
           multiple_of=50
       )
       # Generated: 100, 150, 200, ..., 10000

Format-Aware Generation
-----------------------

Built-in format generators:

.. code-block:: python

   class ContactInfo(GriotModel):
       # Email format
       email: str = Field(format="email")
       # Generated: "john.doe@example.com"

       # UUID format
       record_id: str = Field(format="uuid")
       # Generated: "550e8400-e29b-41d4-a716-446655440000"

       # Date format
       birth_date: str = Field(format="date")
       # Generated: "1990-05-15"

       # Datetime format
       created_at: str = Field(format="datetime")
       # Generated: "2026-01-10T14:30:00Z"

       # Time format
       scheduled_time: str = Field(format="time")
       # Generated: "14:30:00"

       # URI format
       website: str = Field(format="uri")
       # Generated: "https://example.com/path"

       # IPv4 format
       ip_address: str = Field(format="ipv4")
       # Generated: "192.168.1.100"

       # Phone format
       phone: str = Field(format="phone")
       # Generated: "+14155551234"

Using Examples
--------------

If examples are provided, mock data will use them:

.. code-block:: python

   class Customer(GriotModel):
       customer_id: str = Field(
           description="Customer ID",
           examples=["CUST-000001", "CUST-123456", "CUST-999999"]
       )
       # Generated: Randomly picks from examples

       country: str = Field(
           description="Country",
           examples=["US", "UK", "CA", "AU", "DE", "FR", "JP"]
       )
       # Generated: Randomly picks from provided countries

Default Values
--------------

Fields with defaults may use them in mock data:

.. code-block:: python

   class Configuration(GriotModel):
       enabled: bool = Field(
           description="Enabled",
           default=True
       )
       # May generate: True (the default)

       retry_count: int = Field(
           description="Retries",
           default=3
       )
       # May generate: 3 (the default)

Nullable Fields
---------------

Nullable fields may generate null values:

.. code-block:: python

   class OptionalData(GriotModel):
       required_field: str = Field(description="Required")
       # Always has a value

       optional_field: str = Field(
           description="Optional",
           nullable=True
       )
       # May generate: null or a value

   mock_data = OptionalData.mock(rows=10)
   # Some rows will have optional_field=None

Control Null Rate
^^^^^^^^^^^^^^^^^

.. code-block:: python

   # Higher null rate for nullable fields
   mock_data = OptionalData.mock(rows=100, null_rate=0.3)
   # ~30% of nullable fields will be null

Seed for Reproducibility
------------------------

Use a seed for reproducible mock data:

.. code-block:: python

   # Same seed = same data
   data1 = User.mock(rows=10, seed=42)
   data2 = User.mock(rows=10, seed=42)

   assert data1 == data2  # True

   # Different seed = different data
   data3 = User.mock(rows=10, seed=123)
   assert data1 != data3  # True

Large Dataset Generation
------------------------

Generate large datasets efficiently:

.. code-block:: python

   # Generate 100,000 rows
   large_dataset = Product.mock(rows=100000)

   print(f"Generated {len(large_dataset)} rows")

   # Streaming generation for very large datasets
   def generate_batched(model, total_rows, batch_size=10000):
       """Generate large dataset in batches."""
       for i in range(0, total_rows, batch_size):
           batch = model.mock(
               rows=min(batch_size, total_rows - i),
               seed=i  # Different seed per batch
           )
           yield from batch

   # Use generator
   for row in generate_batched(Product, 1000000, batch_size=10000):
       process_row(row)

Export Formats
--------------

Export mock data to different formats:

.. code-block:: python

   # As list of dicts (default)
   data = Product.mock(rows=100)

   # Convert to JSON
   import json
   json_data = json.dumps(data, indent=2)

   # Convert to CSV
   import csv
   with open("mock_data.csv", "w", newline="") as f:
       writer = csv.DictWriter(f, fieldnames=data[0].keys())
       writer.writeheader()
       writer.writerows(data)

   # Convert to pandas DataFrame
   import pandas as pd
   df = pd.DataFrame(data)
   df.to_parquet("mock_data.parquet")

Using generate_mock_data Function
---------------------------------

Alternatively, use the standalone function:

.. code-block:: python

   from griot_core import generate_mock_data

   # Generate from model class
   data = generate_mock_data(Product, rows=100)

   # With options
   data = generate_mock_data(
       Product,
       rows=1000,
       seed=42,
       null_rate=0.1
   )

Testing with Mock Data
----------------------

Use mock data for testing:

.. code-block:: python

   import pytest
   from griot_core import GriotModel, Field

   class Order(GriotModel):
       order_id: str = Field(description="Order ID", primary_key=True)
       total: float = Field(description="Total", ge=0)
       status: str = Field(description="Status", enum=["pending", "complete"])

   @pytest.fixture
   def sample_orders():
       """Generate sample orders for testing."""
       return Order.mock(rows=100, seed=42)

   def test_order_processing(sample_orders):
       """Test order processing with mock data."""
       for order in sample_orders:
           result = process_order(order)
           assert result.success

   def test_validation_with_mock_data():
       """Validate mock data passes validation."""
       data = Order.mock(rows=1000)
       result = Order.validate(data)
       assert result.passed  # Mock data always valid

Best Practices
--------------

1. **Use seeds in tests**: Ensure reproducible test data
2. **Match production scale**: Generate data at realistic volumes
3. **Test edge cases**: Generate data near constraint boundaries
4. **Validate mock data**: Mock data should always pass validation
5. **Use examples**: Provide realistic examples for better mock data
