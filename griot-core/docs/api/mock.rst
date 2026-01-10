Mock Data
=========

Mock data generation.

generate_mock_data
------------------

.. py:function:: griot_core.generate_mock_data(model, rows=10, seed=None, null_rate=0.1) -> list[dict]

   Generate mock data that satisfies a contract.

   :param model: Model class to generate data for
   :type model: type[GriotModel]
   :param rows: Number of rows to generate
   :type rows: int
   :param seed: Random seed for reproducibility
   :type seed: int | None
   :param null_rate: Rate of null values for nullable fields (0.0-1.0)
   :type null_rate: float
   :returns: List of generated dictionaries
   :rtype: list[dict]

   The generator respects all field constraints:

   - **Pattern**: Generates strings matching regex patterns
   - **Format**: Generates valid emails, UUIDs, dates, etc.
   - **Enum**: Randomly selects from allowed values
   - **Range**: Generates numbers within ge/gt/le/lt bounds
   - **Length**: Generates strings within min/max length
   - **Examples**: Uses provided examples when available

   **Example:**

   .. code-block:: python

      from griot_core import GriotModel, Field, generate_mock_data

      class Order(GriotModel):
          order_id: str = Field(
              description="Order ID",
              pattern=r"^ORD-\d{8}$"
          )
          total: float = Field(
              description="Order total",
              ge=0.0,
              le=10000.0
          )
          status: str = Field(
              description="Status",
              enum=["pending", "shipped", "delivered"]
          )

      # Generate 100 rows
      data = generate_mock_data(Order, rows=100)

      # With seed for reproducibility
      data1 = generate_mock_data(Order, rows=50, seed=42)
      data2 = generate_mock_data(Order, rows=50, seed=42)
      assert data1 == data2  # Same data

      # Control null rate
      data = generate_mock_data(Order, rows=100, null_rate=0.2)

Format Generators
-----------------

Built-in generators for common formats:

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Format
     - Generated Example
   * - ``email``
     - john.doe@example.com
   * - ``uuid``
     - 550e8400-e29b-41d4-a716-446655440000
   * - ``date``
     - 2026-01-10
   * - ``time``
     - 14:30:00
   * - ``datetime``
     - 2026-01-10T14:30:00Z
   * - ``uri``
     - https://example.com/path/to/resource
   * - ``ipv4``
     - 192.168.1.100
   * - ``ipv6``
     - 2001:0db8:85a3::8a2e:0370:7334
   * - ``hostname``
     - api.example.com
   * - ``phone``
     - +14155551234

Pattern Generation
------------------

The generator creates strings matching regex patterns:

.. code-block:: python

   class Product(GriotModel):
       sku: str = Field(
           description="SKU",
           pattern=r"^[A-Z]{3}-\d{4}$"
       )
       # Generates: "ABC-1234", "XYZ-9876", etc.

   class User(GriotModel):
       username: str = Field(
           description="Username",
           pattern=r"^[a-z][a-z0-9_]{2,19}$"
       )
       # Generates: "john_doe", "user123", etc.

Supported pattern features:

- Character classes: ``[A-Z]``, ``[a-z]``, ``[0-9]``, ``\d``, ``\w``
- Quantifiers: ``{n}``, ``{n,m}``, ``*``, ``+``, ``?``
- Anchors: ``^``, ``$``
- Groups: ``(abc)``
- Alternation: ``(a|b|c)``

Performance
-----------

Mock generation is optimized for large datasets:

.. code-block:: python

   import time

   start = time.time()
   data = generate_mock_data(Order, rows=100000)
   elapsed = time.time() - start

   print(f"Generated 100K rows in {elapsed:.2f}s")
   # Typically < 5 seconds

For very large datasets, generate in batches:

.. code-block:: python

   def generate_batched(model, total, batch_size=10000):
       """Generate in memory-efficient batches."""
       for i in range(0, total, batch_size):
           batch = generate_mock_data(
               model,
               rows=min(batch_size, total - i),
               seed=i
           )
           yield from batch

   # Stream to file
   import csv

   with open("large_dataset.csv", "w", newline="") as f:
       writer = None
       for i, row in enumerate(generate_batched(Order, 1000000)):
           if writer is None:
               writer = csv.DictWriter(f, fieldnames=row.keys())
               writer.writeheader()
           writer.writerow(row)
