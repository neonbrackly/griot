Your First Contract
===================

This tutorial walks you through building a complete data contract for a real-world
e-commerce scenario.

The Scenario
------------

You're building an e-commerce platform and need to define a contract for customer orders.
The contract must:

1. Define the order schema
2. Validate incoming order data
3. Track PII for GDPR compliance
4. Support data residency requirements

Step 1: Define the Basic Contract
---------------------------------

Start with the core fields:

.. code-block:: python

   from griot_core import GriotModel, Field

   class Order(GriotModel):
       """E-commerce order contract."""

       order_id: str = Field(
           description="Unique order identifier",
           primary_key=True,
           pattern=r"^ORD-\d{10}$",
           examples=["ORD-0000000001", "ORD-1234567890"]
       )

       customer_id: str = Field(
           description="Customer who placed the order",
           pattern=r"^CUST-\d{6}$"
       )

       order_date: str = Field(
           description="Date and time the order was placed",
           format="datetime"
       )

       status: str = Field(
           description="Current order status",
           enum=["pending", "confirmed", "shipped", "delivered", "cancelled"]
       )

       total_amount: float = Field(
           description="Total order amount in USD",
           ge=0.0,
           unit="USD"
       )

       item_count: int = Field(
           description="Number of items in the order",
           ge=1,
           le=100
       )

Step 2: Add PII Fields
----------------------

Add customer PII with proper classification:

.. code-block:: python

   from griot_core import (
       GriotModel, Field,
       PIICategory, SensitivityLevel, MaskingStrategy, LegalBasis
   )

   class Order(GriotModel):
       """E-commerce order contract with PII tracking."""

       # ... previous fields ...

       customer_email: str = Field(
           description="Customer email for order confirmation",
           format="email",
           pii_category=PIICategory.EMAIL,
           sensitivity=SensitivityLevel.CONFIDENTIAL,
           masking_strategy=MaskingStrategy.PARTIAL_MASK,
           legal_basis=LegalBasis.CONTRACT,
           retention_days=365
       )

       shipping_address: str = Field(
           description="Delivery address",
           pii_category=PIICategory.ADDRESS,
           sensitivity=SensitivityLevel.CONFIDENTIAL,
           masking_strategy=MaskingStrategy.REDACT,
           legal_basis=LegalBasis.CONTRACT
       )

       phone_number: str = Field(
           description="Contact phone number",
           pattern=r"^\+?[1-9]\d{1,14}$",
           pii_category=PIICategory.PHONE,
           sensitivity=SensitivityLevel.CONFIDENTIAL,
           masking_strategy=MaskingStrategy.PARTIAL_MASK,
           legal_basis=LegalBasis.CONSENT,
           nullable=True
       )

Step 3: Configure Data Residency
--------------------------------

Add geographic compliance rules:

.. code-block:: python

   from griot_core import (
       GriotModel, Field, DataRegion, ResidencyConfig, ResidencyRule
   )

   class Order(GriotModel):
       """E-commerce order contract with residency rules."""

       class Meta:
           residency = ResidencyConfig(
               default_rule=ResidencyRule(
                   allowed_regions=[DataRegion.US, DataRegion.EU],
                   prohibited_regions=[DataRegion.CN, DataRegion.RU]
               ),
               field_rules={
                   "customer_email": ResidencyRule(
                       allowed_regions=[DataRegion.EU],  # EU customers stay in EU
                       required_encryption=True
                   ),
                   "shipping_address": ResidencyRule(
                       allowed_regions=[DataRegion.US, DataRegion.EU]
                   )
               }
           )

       # ... fields ...

Step 4: Add Data Lineage
------------------------

Track where data comes from and where it goes:

.. code-block:: python

   from griot_core import (
       GriotModel, Field,
       LineageConfig, Source, Transformation, Consumer
   )

   class Order(GriotModel):
       """E-commerce order contract with lineage tracking."""

       class Meta:
           lineage = LineageConfig(
               sources=[
                   Source(
                       name="checkout_service",
                       type="api",
                       description="Order checkout microservice"
                   ),
                   Source(
                       name="payment_gateway",
                       type="api",
                       description="Payment processing response"
                   )
               ],
               transformations=[
                   Transformation(
                       name="enrich_customer",
                       description="Add customer profile data",
                       input_fields=["customer_id"],
                       output_fields=["customer_email", "shipping_address"]
                   ),
                   Transformation(
                       name="calculate_total",
                       description="Sum item prices with tax and shipping",
                       input_fields=["item_count"],
                       output_fields=["total_amount"]
                   )
               ],
               consumers=[
                   Consumer(
                       name="analytics_warehouse",
                       type="database",
                       description="BigQuery analytics"
                   ),
                   Consumer(
                       name="fulfillment_service",
                       type="api",
                       description="Order fulfillment system"
                   )
               ]
           )

       # ... fields ...

Step 5: Validate Your Data
--------------------------

Now use your complete contract:

.. code-block:: python

   # Sample order data
   orders = [
       {
           "order_id": "ORD-0000000001",
           "customer_id": "CUST-123456",
           "order_date": "2026-01-10T10:30:00Z",
           "status": "confirmed",
           "total_amount": 149.99,
           "item_count": 3,
           "customer_email": "john.doe@example.com",
           "shipping_address": "123 Main St, New York, NY 10001",
           "phone_number": "+14155551234"
       }
   ]

   # Validate
   result = Order.validate(orders)

   if result.passed:
       print("All orders valid!")
   else:
       for error in result.errors:
           print(f"Error: {error.field} - {error.message}")

Step 6: Generate Reports
------------------------

Generate compliance and readiness reports:

.. code-block:: python

   from griot_core import (
       generate_analytics_report,
       generate_audit_report,
       generate_ai_readiness_report,
       generate_readiness_report
   )

   # Analytics report
   analytics = generate_analytics_report(Order)
   print(f"Fields: {analytics.total_fields}")
   print(f"PII fields: {analytics.pii_field_count}")

   # Compliance audit
   audit = generate_audit_report(Order)
   print(f"Compliance score: {audit.compliance_score}%")
   print(f"GDPR ready: {audit.gdpr_ready}")
   print(f"CCPA ready: {audit.ccpa_ready}")

   # AI readiness
   ai_report = generate_ai_readiness_report(Order)
   print(f"AI readiness: {ai_report.overall_score}%")

   # Combined readiness
   readiness = generate_readiness_report(Order)
   print(f"Overall grade: {readiness.overall_grade}")

Complete Contract
-----------------

Here's the complete contract with all features:

.. code-block:: python

   from griot_core import (
       GriotModel, Field,
       PIICategory, SensitivityLevel, MaskingStrategy, LegalBasis,
       DataRegion, ResidencyConfig, ResidencyRule,
       LineageConfig, Source, Transformation, Consumer
   )

   class Order(GriotModel):
       """
       E-commerce order contract.

       Defines the schema for customer orders with full PII tracking,
       data residency compliance, and lineage documentation.
       """

       class Meta:
           description = "E-commerce order data contract"
           owner = "orders-team@company.com"
           version = "1.0.0"

           residency = ResidencyConfig(
               default_rule=ResidencyRule(
                   allowed_regions=[DataRegion.US, DataRegion.EU]
               )
           )

           lineage = LineageConfig(
               sources=[
                   Source(name="checkout_service", type="api")
               ],
               consumers=[
                   Consumer(name="analytics_warehouse", type="database")
               ]
           )

       order_id: str = Field(
           description="Unique order identifier",
           primary_key=True,
           pattern=r"^ORD-\d{10}$"
       )

       customer_id: str = Field(
           description="Customer who placed the order",
           pattern=r"^CUST-\d{6}$"
       )

       customer_email: str = Field(
           description="Customer email for order confirmation",
           format="email",
           pii_category=PIICategory.EMAIL,
           sensitivity=SensitivityLevel.CONFIDENTIAL,
           masking_strategy=MaskingStrategy.PARTIAL_MASK,
           legal_basis=LegalBasis.CONTRACT
       )

       order_date: str = Field(
           description="Date and time the order was placed",
           format="datetime"
       )

       status: str = Field(
           description="Current order status",
           enum=["pending", "confirmed", "shipped", "delivered", "cancelled"]
       )

       total_amount: float = Field(
           description="Total order amount in USD",
           ge=0.0,
           unit="USD"
       )

       item_count: int = Field(
           description="Number of items in the order",
           ge=1,
           le=100
       )

   # Use the contract
   result = Order.validate(data)
   mock_data = Order.mock(rows=100)
   manifest = Order.to_manifest(format="llm_context")

Next Steps
----------

Now that you've built your first contract:

- Explore :doc:`../user-guide/index` for advanced features
- See :doc:`../examples/index` for more real-world examples
- Learn about :doc:`../api/index` for the complete API reference
