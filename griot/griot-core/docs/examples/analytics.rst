Analytics Examples
==================

Data contracts for analytics and data warehouse applications.

Event Tracking Contract
-----------------------

.. code-block:: python

   from griot_core import (
       GriotModel, Field, AggregationType,
       PIICategory, SensitivityLevel, MaskingStrategy, LegalBasis,
       LineageConfig, Source, Transformation, Consumer
   )

   class UserEvent(GriotModel):
       """
       User behavior event contract.

       Clickstream and product analytics events.
       """

       class Meta:
           description = "User behavior tracking events"
           version = "3.0.0"
           owner = "analytics-team@company.com"
           tags = ["event", "clickstream", "analytics"]

           lineage = LineageConfig(
               sources=[
                   Source(name="web_sdk", type="stream",
                          description="JavaScript SDK events"),
                   Source(name="mobile_sdk", type="stream",
                          description="iOS/Android SDK events"),
                   Source(name="server_events", type="api",
                          description="Server-side events")
               ],
               transformations=[
                   Transformation(
                       name="sessionize",
                       description="Group events into sessions",
                       input_fields=["user_id", "timestamp"],
                       output_fields=["session_id"]
                   ),
                   Transformation(
                       name="enrich_user",
                       description="Add user profile attributes",
                       input_fields=["user_id"],
                       output_fields=["user_segment", "user_cohort"]
                   )
               ],
               consumers=[
                   Consumer(name="bigquery", type="warehouse"),
                   Consumer(name="amplitude", type="application"),
                   Consumer(name="ml_pipeline", type="ml")
               ]
           )

       event_id: str = Field(
           description="Unique event identifier",
           primary_key=True,
           format="uuid"
       )

       event_name: str = Field(
           description="Event type name",
           max_length=100,
           examples=["page_view", "button_click", "purchase", "signup"]
       )

       event_timestamp: str = Field(
           description="Event timestamp (ISO 8601)",
           format="datetime"
       )

       user_id: str = Field(
           description="Authenticated user ID",
           pattern=r"^[A-Za-z0-9_-]{8,36}$",
           pii_category=PIICategory.OTHER,
           sensitivity=SensitivityLevel.CONFIDENTIAL,
           masking_strategy=MaskingStrategy.HASH,
           legal_basis=LegalBasis.CONSENT,
           nullable=True
       )

       anonymous_id: str = Field(
           description="Anonymous/device ID",
           pii_category=PIICategory.DEVICE_ID,
           sensitivity=SensitivityLevel.CONFIDENTIAL,
           masking_strategy=MaskingStrategy.HASH,
           legal_basis=LegalBasis.LEGITIMATE_INTEREST
       )

       session_id: str = Field(
           description="Session identifier",
           format="uuid"
       )

       platform: str = Field(
           description="Platform/device type",
           enum=["web", "ios", "android", "server"]
       )

       page_url: str = Field(
           description="Page URL",
           format="uri",
           nullable=True
       )

       page_title: str = Field(
           description="Page title",
           max_length=500,
           nullable=True
       )

       referrer: str = Field(
           description="Referrer URL",
           format="uri",
           nullable=True
       )

       utm_source: str = Field(
           description="UTM source parameter",
           max_length=100,
           nullable=True
       )

       utm_medium: str = Field(
           description="UTM medium parameter",
           max_length=100,
           nullable=True
       )

       utm_campaign: str = Field(
           description="UTM campaign parameter",
           max_length=255,
           nullable=True
       )

       ip_address: str = Field(
           description="Client IP address",
           format="ipv4",
           pii_category=PIICategory.IP_ADDRESS,
           sensitivity=SensitivityLevel.CONFIDENTIAL,
           masking_strategy=MaskingStrategy.HASH,
           legal_basis=LegalBasis.LEGITIMATE_INTEREST
       )

       user_agent: str = Field(
           description="Browser user agent",
           max_length=1000
       )

       country: str = Field(
           description="Geo country code",
           pattern=r"^[A-Z]{2}$",
           nullable=True
       )

       city: str = Field(
           description="Geo city name",
           max_length=255,
           pii_category=PIICategory.LOCATION,
           sensitivity=SensitivityLevel.INTERNAL,
           masking_strategy=MaskingStrategy.GENERALIZE,
           legal_basis=LegalBasis.LEGITIMATE_INTEREST,
           nullable=True
       )

       properties: dict = Field(
           description="Event-specific properties (JSON)",
           nullable=True
       )

Metrics Contract
----------------

.. code-block:: python

   class DailyMetric(GriotModel):
       """
       Daily aggregated metrics contract.

       Pre-computed metrics for dashboards and reporting.
       """

       class Meta:
           description = "Daily aggregated business metrics"
           version = "2.0.0"
           owner = "bi-team@company.com"
           tags = ["metrics", "kpi", "dashboard"]

           lineage = LineageConfig(
               sources=[
                   Source(name="events_table", type="database"),
                   Source(name="transactions_table", type="database"),
                   Source(name="users_table", type="database")
               ],
               transformations=[
                   Transformation(
                       name="daily_aggregation",
                       description="Aggregate events to daily metrics",
                       input_fields=["event_timestamp", "user_id", "event_name"],
                       output_fields=["active_users", "events_count", "sessions_count"]
                   )
               ],
               consumers=[
                   Consumer(name="executive_dashboard", type="dashboard"),
                   Consumer(name="weekly_report", type="export")
               ]
           )

       metric_date: str = Field(
           description="Metric date",
           format="date",
           primary_key=True
       )

       segment: str = Field(
           description="User segment",
           primary_key=True,
           enum=["all", "new", "returning", "premium"]
       )

       platform: str = Field(
           description="Platform",
           primary_key=True,
           enum=["all", "web", "ios", "android"]
       )

       daily_active_users: int = Field(
           description="Daily Active Users (DAU)",
           ge=0,
           aggregation=AggregationType.SUM
       )

       new_users: int = Field(
           description="New user signups",
           ge=0,
           aggregation=AggregationType.SUM
       )

       sessions: int = Field(
           description="Total sessions",
           ge=0,
           aggregation=AggregationType.SUM
       )

       page_views: int = Field(
           description="Total page views",
           ge=0,
           aggregation=AggregationType.SUM
       )

       events: int = Field(
           description="Total events tracked",
           ge=0,
           aggregation=AggregationType.SUM
       )

       revenue: float = Field(
           description="Total revenue",
           ge=0.0,
           unit="USD",
           aggregation=AggregationType.SUM
       )

       transactions: int = Field(
           description="Total transactions",
           ge=0,
           aggregation=AggregationType.SUM
       )

       avg_session_duration: float = Field(
           description="Average session duration",
           ge=0.0,
           unit="seconds",
           aggregation=AggregationType.AVERAGE
       )

       bounce_rate: float = Field(
           description="Bounce rate (0-1)",
           ge=0.0,
           le=1.0,
           aggregation=AggregationType.AVERAGE
       )

       conversion_rate: float = Field(
           description="Conversion rate (0-1)",
           ge=0.0,
           le=1.0,
           aggregation=AggregationType.AVERAGE
       )

Funnel Analysis Contract
------------------------

.. code-block:: python

   class FunnelStep(GriotModel):
       """
       Funnel analysis step contract.

       Tracks user progression through conversion funnels.
       """

       class Meta:
           description = "Funnel step metrics"
           version = "1.0.0"
           owner = "growth-team@company.com"
           tags = ["funnel", "conversion", "growth"]

       funnel_id: str = Field(
           description="Funnel identifier",
           primary_key=True,
           pattern=r"^FNL-[A-Z0-9]{6}$",
           examples=["FNL-SIGNUP", "FNL-PURCH1"]
       )

       step_number: int = Field(
           description="Step position in funnel",
           primary_key=True,
           ge=1,
           le=20
       )

       date: str = Field(
           description="Analysis date",
           primary_key=True,
           format="date"
       )

       step_name: str = Field(
           description="Step name",
           max_length=100,
           examples=["Landing Page", "Signup Form", "Email Verified"]
       )

       entered: int = Field(
           description="Users who entered this step",
           ge=0,
           aggregation=AggregationType.SUM
       )

       completed: int = Field(
           description="Users who completed this step",
           ge=0,
           aggregation=AggregationType.SUM
       )

       dropped: int = Field(
           description="Users who dropped at this step",
           ge=0,
           aggregation=AggregationType.SUM
       )

       conversion_rate: float = Field(
           description="Step conversion rate",
           ge=0.0,
           le=1.0
       )

       cumulative_conversion: float = Field(
           description="Cumulative funnel conversion",
           ge=0.0,
           le=1.0
       )

       avg_time_to_complete: float = Field(
           description="Average time to complete step",
           ge=0.0,
           unit="seconds",
           nullable=True
       )

AI/ML Feature Contract
----------------------

.. code-block:: python

   class UserFeature(GriotModel):
       """
       ML feature store contract.

       Pre-computed features for machine learning models.
       """

       class Meta:
           description = "User features for ML models"
           version = "1.0.0"
           owner = "ml-platform@company.com"
           tags = ["features", "ml", "prediction"]

           lineage = LineageConfig(
               sources=[
                   Source(name="events", type="database"),
                   Source(name="transactions", type="database"),
                   Source(name="user_profiles", type="database")
               ],
               transformations=[
                   Transformation(
                       name="feature_engineering",
                       description="Compute ML features from raw data",
                       input_fields=["events", "transactions"],
                       output_fields=["*_features"]
                   )
               ],
               consumers=[
                   Consumer(name="churn_model", type="ml"),
                   Consumer(name="recommendation_model", type="ml"),
                   Consumer(name="fraud_model", type="ml")
               ]
           )

       user_id: str = Field(
           description="User identifier",
           primary_key=True,
           pii_category=PIICategory.OTHER,
           sensitivity=SensitivityLevel.CONFIDENTIAL,
           masking_strategy=MaskingStrategy.HASH
       )

       feature_date: str = Field(
           description="Feature computation date",
           primary_key=True,
           format="date"
       )

       # Engagement features
       days_since_signup: int = Field(
           description="Days since user signup",
           ge=0
       )

       days_since_last_activity: int = Field(
           description="Days since last activity",
           ge=0
       )

       total_sessions_7d: int = Field(
           description="Sessions in last 7 days",
           ge=0
       )

       total_sessions_30d: int = Field(
           description="Sessions in last 30 days",
           ge=0
       )

       avg_session_duration_7d: float = Field(
           description="Avg session duration (7d)",
           ge=0.0,
           unit="seconds"
       )

       # Transaction features
       total_transactions_30d: int = Field(
           description="Transactions in last 30 days",
           ge=0
       )

       total_revenue_30d: float = Field(
           description="Revenue in last 30 days",
           ge=0.0,
           unit="USD"
       )

       avg_order_value: float = Field(
           description="Average order value",
           ge=0.0,
           unit="USD"
       )

       # Behavioral features
       preferred_platform: str = Field(
           description="Most used platform",
           enum=["web", "ios", "android", "unknown"]
       )

       preferred_time_of_day: str = Field(
           description="Most active time",
           enum=["morning", "afternoon", "evening", "night"]
       )

       # Model scores
       churn_probability: float = Field(
           description="Churn prediction score",
           ge=0.0,
           le=1.0
       )

       lifetime_value_predicted: float = Field(
           description="Predicted LTV",
           ge=0.0,
           unit="USD"
       )

Usage Example
-------------

.. code-block:: python

   from griot_core import generate_ai_readiness_report

   # Check if events are AI-ready
   ai_report = generate_ai_readiness_report(UserEvent)

   print("AI Readiness Assessment")
   print("=" * 40)
   print(f"Overall Score: {ai_report.overall_score:.1f}%")
   print(f"Grade: {ai_report.overall_grade}")
   print()
   print("Component Scores:")
   print(f"  Semantic: {ai_report.semantic_score:.1f}%")
   print(f"  Descriptions: {ai_report.description_score:.1f}%")
   print(f"  Examples: {ai_report.example_score:.1f}%")
   print()

   # Generate mock analytics data
   events = UserEvent.mock(rows=10000, seed=42)
   metrics = DailyMetric.mock(rows=365, seed=42)

   print(f"Generated {len(events)} events")
   print(f"Generated {len(metrics)} daily metric rows")
