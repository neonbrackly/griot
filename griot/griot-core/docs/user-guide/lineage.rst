Data Lineage
============

griot-core supports documenting data lineage - tracking where data comes from,
how it's transformed, and where it goes.

Basic Lineage Configuration
---------------------------

Add lineage tracking to your contract:

.. code-block:: python

   from griot_core import (
       GriotModel, Field,
       LineageConfig, Source, Transformation, Consumer
   )

   class SalesData(GriotModel):
       """Sales data with lineage tracking."""

       class Meta:
           lineage = LineageConfig(
               sources=[
                   Source(name="pos_system", type="database")
               ],
               consumers=[
                   Consumer(name="analytics", type="warehouse")
               ]
           )

       sale_id: str = Field(description="Sale ID", primary_key=True)
       amount: float = Field(description="Sale amount")
       timestamp: str = Field(description="Sale timestamp", format="datetime")

Sources
-------

Document where data originates:

.. code-block:: python

   from griot_core import Source

   class OrderData(GriotModel):
       class Meta:
           lineage = LineageConfig(
               sources=[
                   # Database source
                   Source(
                       name="orders_db",
                       type="database",
                       description="PostgreSQL orders database",
                       connection="postgresql://orders-primary.internal"
                   ),
                   # API source
                   Source(
                       name="payment_api",
                       type="api",
                       description="Payment gateway webhook",
                       connection="https://api.payments.com/webhooks"
                   ),
                   # File source
                   Source(
                       name="inventory_feed",
                       type="file",
                       description="Daily inventory CSV from warehouse",
                       connection="s3://warehouse-exports/inventory/"
                   ),
                   # Stream source
                   Source(
                       name="clickstream",
                       type="stream",
                       description="Kafka clickstream events",
                       connection="kafka://clicks.events.internal"
                   )
               ]
           )

Source Types
^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Type
     - Description
   * - ``database``
     - Relational or NoSQL database
   * - ``api``
     - REST API, GraphQL, or webhook
   * - ``file``
     - File-based (CSV, JSON, Parquet, etc.)
   * - ``stream``
     - Streaming source (Kafka, Kinesis, Pub/Sub)
   * - ``manual``
     - Manual data entry
   * - ``external``
     - External third-party source

Transformations
---------------

Document how data is transformed:

.. code-block:: python

   from griot_core import Transformation

   class EnrichedOrder(GriotModel):
       class Meta:
           lineage = LineageConfig(
               sources=[
                   Source(name="orders_db", type="database"),
                   Source(name="customers_db", type="database"),
                   Source(name="products_db", type="database")
               ],
               transformations=[
                   # Join transformation
                   Transformation(
                       name="enrich_customer",
                       description="Join with customer profile data",
                       input_fields=["customer_id"],
                       output_fields=["customer_name", "customer_email", "customer_segment"]
                   ),
                   # Calculation
                   Transformation(
                       name="calculate_totals",
                       description="Calculate order totals with tax and shipping",
                       input_fields=["line_items", "tax_rate", "shipping_cost"],
                       output_fields=["subtotal", "tax_amount", "total"]
                   ),
                   # Aggregation
                   Transformation(
                       name="aggregate_metrics",
                       description="Calculate customer lifetime metrics",
                       input_fields=["order_history"],
                       output_fields=["lifetime_value", "order_count", "avg_order_value"]
                   ),
                   # Derivation
                   Transformation(
                       name="derive_status",
                       description="Derive fulfillment status from events",
                       input_fields=["fulfillment_events"],
                       output_fields=["current_status", "status_timestamp"]
                   )
               ]
           )

       order_id: str = Field(description="Order ID", primary_key=True)
       customer_id: str = Field(description="Customer ID")
       customer_name: str = Field(description="Customer name (enriched)")
       customer_email: str = Field(description="Customer email (enriched)")
       customer_segment: str = Field(description="Customer segment (enriched)")
       subtotal: float = Field(description="Subtotal (calculated)")
       tax_amount: float = Field(description="Tax (calculated)")
       total: float = Field(description="Total (calculated)")
       lifetime_value: float = Field(description="LTV (aggregated)")

Transformation Fields
^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Field
     - Description
   * - ``name``
     - Unique transformation identifier
   * - ``description``
     - Human-readable description
   * - ``input_fields``
     - List of source field names
   * - ``output_fields``
     - List of resulting field names
   * - ``logic``
     - Optional SQL or code snippet

Consumers
---------

Document where data goes:

.. code-block:: python

   from griot_core import Consumer

   class AnalyticsData(GriotModel):
       class Meta:
           lineage = LineageConfig(
               sources=[Source(name="events", type="stream")],
               consumers=[
                   # Data warehouse
                   Consumer(
                       name="bigquery_analytics",
                       type="warehouse",
                       description="BigQuery analytics tables",
                       connection="bigquery://project.analytics.events"
                   ),
                   # Dashboard
                   Consumer(
                       name="executive_dashboard",
                       type="dashboard",
                       description="Looker executive dashboard",
                       connection="https://looker.company.com/dashboards/exec"
                   ),
                   # API
                   Consumer(
                       name="reporting_api",
                       type="api",
                       description="Internal reporting API",
                       connection="https://api.internal/reporting"
                   ),
                   # ML pipeline
                   Consumer(
                       name="ml_pipeline",
                       type="ml",
                       description="Recommendation model training",
                       connection="sagemaker://recommendations-training"
                   ),
                   # Archive
                   Consumer(
                       name="cold_storage",
                       type="archive",
                       description="S3 Glacier archive",
                       connection="s3://archive-bucket/analytics/"
                   )
               ]
           )

Consumer Types
^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Type
     - Description
   * - ``warehouse``
     - Data warehouse (BigQuery, Snowflake, Redshift)
   * - ``dashboard``
     - BI/visualization tool (Looker, Tableau, PowerBI)
   * - ``api``
     - API endpoint serving the data
   * - ``application``
     - Application consuming the data
   * - ``ml``
     - Machine learning pipeline
   * - ``export``
     - Data export destination
   * - ``archive``
     - Long-term storage/archive

Complete Lineage Example
------------------------

Here's a comprehensive lineage configuration:

.. code-block:: python

   from griot_core import (
       GriotModel, Field,
       LineageConfig, Source, Transformation, Consumer
   )

   class CustomerAnalytics(GriotModel):
       """Customer analytics with full lineage tracking."""

       class Meta:
           description = "Aggregated customer analytics data"
           version = "2.0.0"
           owner = "analytics-team@company.com"

           lineage = LineageConfig(
               sources=[
                   Source(
                       name="customers_db",
                       type="database",
                       description="Customer master data from CRM",
                       connection="postgresql://crm.internal/customers"
                   ),
                   Source(
                       name="orders_db",
                       type="database",
                       description="Orders transactional database",
                       connection="postgresql://orders.internal/orders"
                   ),
                   Source(
                       name="events_stream",
                       type="stream",
                       description="Real-time customer events from Kafka",
                       connection="kafka://events.internal/customer-events"
                   ),
                   Source(
                       name="support_api",
                       type="api",
                       description="Support ticket data from Zendesk",
                       connection="https://company.zendesk.com/api/v2"
                   )
               ],

               transformations=[
                   Transformation(
                       name="deduplicate_customers",
                       description="Deduplicate and merge customer records",
                       input_fields=["customer_id", "email"],
                       output_fields=["canonical_customer_id"]
                   ),
                   Transformation(
                       name="calculate_ltv",
                       description="Calculate customer lifetime value",
                       input_fields=["order_history", "returns"],
                       output_fields=["lifetime_value", "net_revenue"]
                   ),
                   Transformation(
                       name="compute_engagement",
                       description="Compute engagement score from events",
                       input_fields=["page_views", "clicks", "sessions"],
                       output_fields=["engagement_score", "activity_level"]
                   ),
                   Transformation(
                       name="derive_health_score",
                       description="Derive customer health from multiple signals",
                       input_fields=["lifetime_value", "engagement_score", "support_tickets"],
                       output_fields=["health_score", "churn_risk"]
                   )
               ],

               consumers=[
                   Consumer(
                       name="analytics_warehouse",
                       type="warehouse",
                       description="Snowflake analytics warehouse",
                       connection="snowflake://company.analytics/customer_360"
                   ),
                   Consumer(
                       name="customer_dashboard",
                       type="dashboard",
                       description="Customer 360 dashboard in Tableau",
                       connection="https://tableau.company.com/views/customer360"
                   ),
                   Consumer(
                       name="marketing_platform",
                       type="application",
                       description="Braze marketing automation",
                       connection="https://dashboard.braze.com"
                   ),
                   Consumer(
                       name="churn_model",
                       type="ml",
                       description="Customer churn prediction model",
                       connection="sagemaker://churn-prediction"
                   ),
                   Consumer(
                       name="data_science_api",
                       type="api",
                       description="Internal DS API for ad-hoc analysis",
                       connection="https://api.internal/datascience"
                   )
               ]
           )

       # Fields with lineage context
       canonical_customer_id: str = Field(
           description="Deduplicated customer ID",
           primary_key=True
       )
       email: str = Field(description="Primary email")
       lifetime_value: float = Field(
           description="Customer LTV (calculated)",
           unit="USD"
       )
       net_revenue: float = Field(
           description="Net revenue after returns",
           unit="USD"
       )
       engagement_score: float = Field(
           description="Engagement score 0-100",
           ge=0, le=100
       )
       health_score: float = Field(
           description="Customer health score 0-100",
           ge=0, le=100
       )
       churn_risk: str = Field(
           description="Churn risk category",
           enum=["low", "medium", "high"]
       )

Querying Lineage
----------------

Access lineage information programmatically:

.. code-block:: python

   # Get lineage config
   lineage = CustomerAnalytics.get_lineage()

   # List sources
   for source in lineage.sources:
       print(f"Source: {source.name} ({source.type})")
       print(f"  Connection: {source.connection}")

   # List transformations
   for transform in lineage.transformations:
       print(f"Transform: {transform.name}")
       print(f"  Inputs: {transform.input_fields}")
       print(f"  Outputs: {transform.output_fields}")

   # List consumers
   for consumer in lineage.consumers:
       print(f"Consumer: {consumer.name} ({consumer.type})")

   # Find which transformation produces a field
   def find_field_origin(field_name, lineage):
       for t in lineage.transformations:
           if field_name in t.output_fields:
               return t
       return None

   origin = find_field_origin("lifetime_value", lineage)
   print(f"lifetime_value comes from: {origin.name}")

Lineage in Reports
------------------

Lineage information is included in audit reports:

.. code-block:: python

   from griot_core import generate_audit_report

   audit = generate_audit_report(CustomerAnalytics)

   print(f"Source count: {audit.lineage_source_count}")
   print(f"Transformation count: {audit.lineage_transformation_count}")
   print(f"Consumer count: {audit.lineage_consumer_count}")
   print(f"Lineage documented: {audit.lineage_documented}")
