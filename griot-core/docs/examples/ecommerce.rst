E-Commerce Examples
===================

Data contracts for e-commerce applications.

Customer Contract
-----------------

.. code-block:: python

   from griot_core import (
       GriotModel, Field,
       PIICategory, SensitivityLevel, MaskingStrategy, LegalBasis,
       DataRegion, ResidencyConfig, ResidencyRule,
       LineageConfig, Source, Consumer
   )

   class Customer(GriotModel):
       """
       Customer master data contract for e-commerce platform.

       GDPR and CCPA compliant with full PII tracking.
       """

       class Meta:
           description = "E-commerce customer master data"
           version = "2.0.0"
           owner = "customer-team@company.com"
           tags = ["customer", "master-data", "gdpr"]

           residency = ResidencyConfig(
               default_rule=ResidencyRule(
                   allowed_regions=[DataRegion.US, DataRegion.EU],
                   required_encryption=True
               ),
               field_rules={
                   "email": ResidencyRule(allowed_regions=[DataRegion.EU]),
                   "phone": ResidencyRule(allowed_regions=[DataRegion.EU])
               }
           )

           lineage = LineageConfig(
               sources=[
                   Source(name="registration_api", type="api"),
                   Source(name="crm_sync", type="database")
               ],
               consumers=[
                   Consumer(name="analytics", type="warehouse"),
                   Consumer(name="marketing", type="application")
               ]
           )

       customer_id: str = Field(
           description="Unique customer identifier",
           primary_key=True,
           pattern=r"^CUST-[A-Z0-9]{8}$",
           examples=["CUST-ABC12345", "CUST-XYZ98765"]
       )

       email: str = Field(
           description="Primary email address",
           format="email",
           max_length=255,
           pii_category=PIICategory.EMAIL,
           sensitivity=SensitivityLevel.CONFIDENTIAL,
           masking_strategy=MaskingStrategy.PARTIAL_MASK,
           legal_basis=LegalBasis.CONTRACT
       )

       first_name: str = Field(
           description="Customer first name",
           min_length=1,
           max_length=100,
           pii_category=PIICategory.NAME,
           sensitivity=SensitivityLevel.CONFIDENTIAL,
           masking_strategy=MaskingStrategy.REDACT,
           legal_basis=LegalBasis.CONTRACT
       )

       last_name: str = Field(
           description="Customer last name",
           min_length=1,
           max_length=100,
           pii_category=PIICategory.NAME,
           sensitivity=SensitivityLevel.CONFIDENTIAL,
           masking_strategy=MaskingStrategy.REDACT,
           legal_basis=LegalBasis.CONTRACT
       )

       phone: str = Field(
           description="Phone number (E.164 format)",
           format="phone",
           pii_category=PIICategory.PHONE,
           sensitivity=SensitivityLevel.CONFIDENTIAL,
           masking_strategy=MaskingStrategy.PARTIAL_MASK,
           legal_basis=LegalBasis.CONSENT,
           nullable=True
       )

       created_at: str = Field(
           description="Account creation timestamp",
           format="datetime"
       )

       marketing_consent: bool = Field(
           description="Marketing communications consent",
           default=False
       )

       tier: str = Field(
           description="Customer loyalty tier",
           enum=["bronze", "silver", "gold", "platinum"],
           default="bronze"
       )

Order Contract
--------------

.. code-block:: python

   class Order(GriotModel):
       """
       Order transaction contract.

       Captures order lifecycle with full audit trail.
       """

       class Meta:
           description = "E-commerce order transactions"
           version = "3.1.0"
           owner = "orders-team@company.com"
           tags = ["order", "transaction", "revenue"]

           lineage = LineageConfig(
               sources=[
                   Source(name="checkout_api", type="api"),
                   Source(name="payment_gateway", type="api")
               ],
               transformations=[
                   Transformation(
                       name="calculate_totals",
                       description="Calculate order totals with tax",
                       input_fields=["line_items", "tax_rate"],
                       output_fields=["subtotal", "tax_amount", "total"]
                   )
               ],
               consumers=[
                   Consumer(name="fulfillment", type="api"),
                   Consumer(name="analytics", type="warehouse"),
                   Consumer(name="finance", type="application")
               ]
           )

       order_id: str = Field(
           description="Unique order identifier",
           primary_key=True,
           pattern=r"^ORD-\d{10}$",
           examples=["ORD-0000000001", "ORD-1234567890"]
       )

       customer_id: str = Field(
           description="Customer who placed the order",
           pattern=r"^CUST-[A-Z0-9]{8}$"
       )

       order_date: str = Field(
           description="Order placement timestamp",
           format="datetime"
       )

       status: str = Field(
           description="Current order status",
           enum=[
               "pending",
               "payment_processing",
               "confirmed",
               "preparing",
               "shipped",
               "delivered",
               "cancelled",
               "refunded"
           ]
       )

       subtotal: float = Field(
           description="Order subtotal before tax",
           ge=0.0,
           unit="USD",
           aggregation=AggregationType.SUM
       )

       tax_amount: float = Field(
           description="Tax amount",
           ge=0.0,
           unit="USD",
           aggregation=AggregationType.SUM
       )

       shipping_cost: float = Field(
           description="Shipping cost",
           ge=0.0,
           unit="USD",
           aggregation=AggregationType.SUM
       )

       total: float = Field(
           description="Order total",
           ge=0.0,
           unit="USD",
           aggregation=AggregationType.SUM
       )

       item_count: int = Field(
           description="Number of line items",
           ge=1,
           le=100,
           aggregation=AggregationType.SUM
       )

       shipping_address: str = Field(
           description="Shipping address",
           pii_category=PIICategory.ADDRESS,
           sensitivity=SensitivityLevel.CONFIDENTIAL,
           masking_strategy=MaskingStrategy.REDACT,
           legal_basis=LegalBasis.CONTRACT
       )

       payment_method: str = Field(
           description="Payment method used",
           enum=["credit_card", "debit_card", "paypal", "apple_pay", "google_pay"]
       )

Product Contract
----------------

.. code-block:: python

   class Product(GriotModel):
       """
       Product catalog contract.

       Includes inventory and pricing information.
       """

       class Meta:
           description = "Product catalog master data"
           version = "2.0.0"
           owner = "catalog-team@company.com"
           tags = ["product", "catalog", "inventory"]

       sku: str = Field(
           description="Stock Keeping Unit",
           primary_key=True,
           pattern=r"^[A-Z]{3}-[A-Z0-9]{6}$",
           examples=["ELC-ABC123", "CLO-XYZ789"]
       )

       name: str = Field(
           description="Product display name",
           min_length=3,
           max_length=255,
           examples=["Wireless Bluetooth Headphones", "Cotton T-Shirt"]
       )

       description: str = Field(
           description="Product description",
           max_length=5000
       )

       category: str = Field(
           description="Primary product category",
           enum=[
               "electronics",
               "clothing",
               "home_garden",
               "sports",
               "books",
               "toys",
               "health_beauty",
               "food_beverage"
           ]
       )

       price: float = Field(
           description="Current selling price",
           ge=0.01,
           le=99999.99,
           unit="USD"
       )

       cost: float = Field(
           description="Product cost (internal)",
           ge=0.0,
           unit="USD",
           sensitivity=SensitivityLevel.INTERNAL
       )

       stock_quantity: int = Field(
           description="Current stock quantity",
           ge=0,
           aggregation=AggregationType.SUM
       )

       weight_kg: float = Field(
           description="Product weight",
           ge=0.0,
           unit="kg",
           nullable=True
       )

       is_active: bool = Field(
           description="Product is available for sale",
           default=True
       )

       created_at: str = Field(
           description="Product creation timestamp",
           format="datetime"
       )

       updated_at: str = Field(
           description="Last update timestamp",
           format="datetime"
       )

Usage Example
-------------

.. code-block:: python

   # Validate customer data
   customer_data = [
       {
           "customer_id": "CUST-ABC12345",
           "email": "john.doe@example.com",
           "first_name": "John",
           "last_name": "Doe",
           "phone": "+14155551234",
           "created_at": "2026-01-10T10:00:00Z",
           "marketing_consent": True,
           "tier": "gold"
       }
   ]

   result = Customer.validate(customer_data)
   print(f"Valid: {result.passed}")

   # Generate compliance report
   from griot_core import generate_audit_report

   audit = generate_audit_report(Customer)
   print(f"GDPR Ready: {audit.gdpr_ready}")
   print(f"CCPA Ready: {audit.ccpa_ready}")
   print(f"Compliance Score: {audit.compliance_score}%")

   # Generate mock order data
   mock_orders = Order.mock(rows=1000, seed=42)
   print(f"Generated {len(mock_orders)} orders")
   print(f"Total revenue: ${sum(o['total'] for o in mock_orders):,.2f}")
