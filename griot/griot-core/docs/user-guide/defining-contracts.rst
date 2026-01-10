Defining Contracts with GriotModel
==================================

The :class:`~griot_core.GriotModel` class is the foundation of griot-core. All data contracts
inherit from this base class.

Basic Contract Definition
-------------------------

A minimal contract only requires field definitions:

.. code-block:: python

   from griot_core import GriotModel, Field

   class Product(GriotModel):
       product_id: str = Field(description="Unique product identifier")
       name: str = Field(description="Product name")
       price: float = Field(description="Product price")

Contract Metadata
-----------------

Add metadata using the ``Meta`` inner class:

.. code-block:: python

   class Product(GriotModel):
       """Product catalog contract."""

       class Meta:
           description = "Product catalog data contract"
           version = "2.1.0"
           owner = "catalog-team@company.com"
           tags = ["product", "catalog", "inventory"]

       product_id: str = Field(description="Unique product identifier")
       # ... fields ...

Available Meta Options
^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 20 20 60

   * - Option
     - Type
     - Description
   * - ``description``
     - str
     - Human-readable description of the contract
   * - ``version``
     - str
     - Semantic version (e.g., "1.0.0")
   * - ``owner``
     - str
     - Contact email for the contract owner
   * - ``tags``
     - list[str]
     - Tags for categorization and search
   * - ``residency``
     - ResidencyConfig
     - Data residency configuration
   * - ``lineage``
     - LineageConfig
     - Data lineage configuration

Primary Keys
------------

Mark fields as primary keys for unique identification:

.. code-block:: python

   class Transaction(GriotModel):
       # Single primary key
       transaction_id: str = Field(
           description="Unique transaction ID",
           primary_key=True
       )

       # ... other fields ...

   class OrderItem(GriotModel):
       # Composite primary key
       order_id: str = Field(
           description="Order ID",
           primary_key=True
       )
       line_number: int = Field(
           description="Line item number within order",
           primary_key=True
       )

       # ... other fields ...

Nullable Fields
---------------

By default, all fields are required. Mark fields as nullable:

.. code-block:: python

   class Customer(GriotModel):
       customer_id: str = Field(description="Customer ID", primary_key=True)

       # Required field
       email: str = Field(description="Primary email")

       # Optional field
       phone: str = Field(
           description="Phone number",
           nullable=True
       )

       # Optional with default
       status: str = Field(
           description="Account status",
           default="active"
       )

Field Inheritance
-----------------

Contracts can inherit from other contracts:

.. code-block:: python

   class BaseEntity(GriotModel):
       """Base entity with audit fields."""
       created_at: str = Field(description="Creation timestamp", format="datetime")
       updated_at: str = Field(description="Last update timestamp", format="datetime")
       created_by: str = Field(description="User who created the record")

   class Product(BaseEntity):
       """Product inherits audit fields."""
       product_id: str = Field(description="Product ID", primary_key=True)
       name: str = Field(description="Product name")
       # Inherits: created_at, updated_at, created_by

Contract Methods
----------------

GriotModel provides several class methods:

.. code-block:: python

   # Get all field definitions
   fields = Product.get_fields()

   # Get primary key field(s)
   pk_fields = Product.get_primary_keys()

   # Get PII fields
   pii_fields = Product.pii_inventory()

   # Validate data
   result = Product.validate(data)

   # Generate mock data
   mock_data = Product.mock(rows=100)

   # Export manifest
   manifest = Product.to_manifest(format="llm_context")

   # Diff against another contract
   diff = Product.diff(OldProduct)

   # Lint the contract
   issues = Product.lint()

Export to YAML
--------------

Convert contracts to YAML for storage:

.. code-block:: python

   from griot_core import load_contract

   # Export to YAML string
   yaml_str = Product.to_yaml()

   # Save to file
   Product.to_yaml_file("contracts/product.yaml")

   # Load from YAML file
   LoadedProduct = load_contract("contracts/product.yaml")

YAML format example:

.. code-block:: yaml

   name: Product
   description: Product catalog contract
   version: 2.1.0
   owner: catalog-team@company.com

   fields:
     - name: product_id
       type: string
       description: Unique product identifier
       primary_key: true
       pattern: "^PROD-\\d{6}$"

     - name: name
       type: string
       description: Product name
       max_length: 255

     - name: price
       type: float
       description: Product price
       ge: 0.0
       unit: USD

Best Practices
--------------

1. **Always add descriptions**: Every field should have a clear description
2. **Use semantic versioning**: Follow semver for contract versions
3. **Mark primary keys**: Always define primary keys for data identity
4. **Add examples**: Include example values for complex fields
5. **Document constraints**: Use descriptive constraint values
6. **Set owners**: Always specify a contact for the contract
