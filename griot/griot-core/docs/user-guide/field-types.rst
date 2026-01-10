Field Types and Constraints
===========================

The :func:`~griot_core.Field` function defines field metadata and constraints.

Basic Types
-----------

griot-core supports these Python types:

.. list-table::
   :header-rows: 1
   :widths: 20 30 50

   * - Python Type
     - Description
     - Example
   * - ``str``
     - Text/string data
     - ``name: str = Field(...)``
   * - ``int``
     - Integer numbers
     - ``count: int = Field(...)``
   * - ``float``
     - Decimal numbers
     - ``price: float = Field(...)``
   * - ``bool``
     - Boolean values
     - ``active: bool = Field(...)``
   * - ``list``
     - Array/list of values
     - ``tags: list = Field(...)``
   * - ``dict``
     - Object/dictionary
     - ``metadata: dict = Field(...)``

String Constraints
------------------

.. code-block:: python

   from griot_core import GriotModel, Field, FieldFormat

   class User(GriotModel):
       # Length constraints
       username: str = Field(
           description="Username",
           min_length=3,
           max_length=50
       )

       # Pattern (regex)
       user_id: str = Field(
           description="User ID",
           pattern=r"^USR-\d{6}$"
       )

       # Format validation
       email: str = Field(
           description="Email address",
           format="email"
       )

       # Enumeration
       status: str = Field(
           description="Account status",
           enum=["active", "inactive", "suspended"]
       )

Available String Formats
^^^^^^^^^^^^^^^^^^^^^^^^

Use the ``format`` parameter for common patterns:

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * - Format
     - Description
     - Example Match
   * - ``email``
     - Email address
     - user@example.com
   * - ``uri``
     - URI/URL
     - https://example.com/path
   * - ``uuid``
     - UUID v4
     - 550e8400-e29b-41d4-a716-446655440000
   * - ``date``
     - ISO 8601 date
     - 2026-01-10
   * - ``time``
     - ISO 8601 time
     - 14:30:00
   * - ``datetime``
     - ISO 8601 datetime
     - 2026-01-10T14:30:00Z
   * - ``ipv4``
     - IPv4 address
     - 192.168.1.1
   * - ``ipv6``
     - IPv6 address
     - 2001:0db8:85a3::8a2e:0370:7334
   * - ``hostname``
     - DNS hostname
     - api.example.com
   * - ``phone``
     - Phone number (E.164)
     - +14155551234

Numeric Constraints
-------------------

.. code-block:: python

   class Product(GriotModel):
       # Greater than or equal
       price: float = Field(
           description="Product price",
           ge=0.0  # >= 0.0
       )

       # Greater than (exclusive)
       discount: float = Field(
           description="Discount percentage",
           gt=0.0,  # > 0.0
           le=100.0  # <= 100.0
       )

       # Range
       quantity: int = Field(
           description="Stock quantity",
           ge=0,
           le=10000
       )

       # Multiple of
       weight_grams: int = Field(
           description="Weight in grams",
           multiple_of=5  # Must be divisible by 5
       )

Numeric Constraint Summary
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 15 25 60

   * - Parameter
     - Meaning
     - Example
   * - ``gt``
     - Greater than
     - ``gt=0`` means value > 0
   * - ``ge``
     - Greater or equal
     - ``ge=0`` means value >= 0
   * - ``lt``
     - Less than
     - ``lt=100`` means value < 100
   * - ``le``
     - Less or equal
     - ``le=100`` means value <= 100
   * - ``multiple_of``
     - Divisible by
     - ``multiple_of=5`` means value % 5 == 0

Array Constraints
-----------------

.. code-block:: python

   class Order(GriotModel):
       # Array length constraints
       tags: list = Field(
           description="Product tags",
           min_items=1,
           max_items=10
       )

       # Unique items only
       categories: list = Field(
           description="Category IDs",
           unique_items=True
       )

       # Item type specification
       line_items: list = Field(
           description="Order line items",
           items_type="object"
       )

Default Values
--------------

.. code-block:: python

   class Configuration(GriotModel):
       # Static default
       enabled: bool = Field(
           description="Feature enabled",
           default=True
       )

       # Default for nullable
       notes: str = Field(
           description="Optional notes",
           nullable=True,
           default=None
       )

       # Numeric default
       retry_count: int = Field(
           description="Number of retries",
           default=3,
           ge=0,
           le=10
       )

Examples
--------

Add example values for documentation:

.. code-block:: python

   class Customer(GriotModel):
       customer_id: str = Field(
           description="Customer ID",
           pattern=r"^CUST-\d{6}$",
           examples=["CUST-000001", "CUST-123456"]
       )

       email: str = Field(
           description="Customer email",
           format="email",
           examples=["john@example.com", "jane@company.org"]
       )

Units
-----

Specify units for numeric fields:

.. code-block:: python

   class Measurement(GriotModel):
       temperature: float = Field(
           description="Temperature reading",
           unit="celsius"
       )

       weight: float = Field(
           description="Package weight",
           unit="kg"
       )

       duration: int = Field(
           description="Processing time",
           unit="milliseconds"
       )

       amount: float = Field(
           description="Transaction amount",
           unit="USD"
       )

Aggregation Hints
-----------------

Specify how fields should be aggregated in analytics:

.. code-block:: python

   from griot_core import AggregationType

   class Sales(GriotModel):
       revenue: float = Field(
           description="Sale revenue",
           aggregation=AggregationType.SUM
       )

       quantity: int = Field(
           description="Items sold",
           aggregation=AggregationType.SUM
       )

       price: float = Field(
           description="Unit price",
           aggregation=AggregationType.AVERAGE
       )

       sale_date: str = Field(
           description="Sale date",
           format="date",
           aggregation=AggregationType.COUNT_DISTINCT
       )

Available Aggregation Types
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Type
     - Description
   * - ``SUM``
     - Sum of values
   * - ``AVERAGE``
     - Mean of values
   * - ``COUNT``
     - Count of records
   * - ``COUNT_DISTINCT``
     - Count of unique values
   * - ``MIN``
     - Minimum value
   * - ``MAX``
     - Maximum value
   * - ``FIRST``
     - First value
   * - ``LAST``
     - Last value

Complete Field Example
----------------------

Here's a field using multiple constraints:

.. code-block:: python

   class Order(GriotModel):
       order_id: str = Field(
           description="Unique order identifier",
           primary_key=True,
           pattern=r"^ORD-[A-Z0-9]{8}$",
           examples=["ORD-ABC12345", "ORD-XYZ98765"],
           min_length=12,
           max_length=12
       )

       total: float = Field(
           description="Order total amount",
           ge=0.0,
           le=1000000.0,
           unit="USD",
           aggregation=AggregationType.SUM,
           examples=[99.99, 1499.00]
       )

       items: list = Field(
           description="Line items in the order",
           min_items=1,
           max_items=100,
           unique_items=False
       )

       status: str = Field(
           description="Order status",
           enum=["pending", "processing", "shipped", "delivered"],
           default="pending"
       )

       created_at: str = Field(
           description="Order creation timestamp",
           format="datetime",
           examples=["2026-01-10T14:30:00Z"]
       )
