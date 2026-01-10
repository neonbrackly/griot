Reports
=======

Report generation classes and functions.

AnalyticsReport
---------------

.. py:class:: griot_core.AnalyticsReport

   Contract analytics report.

   **Attributes:**

   .. py:attribute:: contract_name
      :type: str

      Name of the contract.

   .. py:attribute:: generated_at
      :type: str

      ISO timestamp of generation.

   .. py:attribute:: total_fields
      :type: int

      Total number of fields.

   .. py:attribute:: required_field_count
      :type: int

      Number of required fields.

   .. py:attribute:: nullable_field_count
      :type: int

      Number of nullable fields.

   .. py:attribute:: pii_field_count
      :type: int

      Number of PII fields.

   .. py:attribute:: primary_key_count
      :type: int

      Number of primary key fields.

   .. py:attribute:: field_types
      :type: dict[str, int]

      Count of each field type.

   .. py:attribute:: constraint_coverage
      :type: float

      Percentage of fields with constraints.

   .. py:attribute:: description_coverage
      :type: float

      Percentage of fields with descriptions.

   **Methods:**

   .. py:method:: to_dict() -> dict
   .. py:method:: to_json() -> str
   .. py:method:: to_markdown() -> str

generate_analytics_report
-------------------------

.. py:function:: griot_core.generate_analytics_report(model) -> AnalyticsReport

   Generate an analytics report for a model.

   :param model: Model class to analyze
   :type model: type[GriotModel]
   :returns: Analytics report
   :rtype: AnalyticsReport

AIReadinessReport
-----------------

.. py:class:: griot_core.AIReadinessReport

   AI/LLM readiness assessment report.

   **Attributes:**

   .. py:attribute:: contract_name
      :type: str

      Name of the contract.

   .. py:attribute:: generated_at
      :type: str

      ISO timestamp of generation.

   .. py:attribute:: overall_score
      :type: float

      Overall readiness score (0-100).

   .. py:attribute:: overall_grade
      :type: str

      Letter grade (A-F).

   .. py:attribute:: semantic_score
      :type: float

      Semantic coverage score.

   .. py:attribute:: description_score
      :type: float

      Description quality score.

   .. py:attribute:: example_score
      :type: float

      Example coverage score.

   .. py:attribute:: type_score
      :type: float

      Type clarity score.

   .. py:attribute:: recommendations
      :type: list[str]

      Improvement recommendations.

   **Methods:**

   .. py:method:: to_dict() -> dict
   .. py:method:: to_json() -> str
   .. py:method:: to_markdown() -> str

generate_ai_readiness_report
----------------------------

.. py:function:: griot_core.generate_ai_readiness_report(model) -> AIReadinessReport

   Generate an AI readiness report for a model.

   :param model: Model class to analyze
   :type model: type[GriotModel]
   :returns: AI readiness report
   :rtype: AIReadinessReport

AuditReport
-----------

.. py:class:: griot_core.AuditReport

   Compliance and privacy audit report.

   **Attributes:**

   .. py:attribute:: contract_name
      :type: str

      Name of the contract.

   .. py:attribute:: generated_at
      :type: str

      ISO timestamp of generation.

   .. py:attribute:: compliance_score
      :type: float

      Overall compliance score (0-100).

   .. py:attribute:: compliance_grade
      :type: str

      Letter grade (A-F).

   .. py:attribute:: compliance_status
      :type: str

      Status: compliant, partial, non_compliant.

   .. py:attribute:: pii_field_count
      :type: int

      Number of PII fields.

   .. py:attribute:: pii_fields
      :type: list[dict]

      Details of each PII field.

   .. py:attribute:: pii_categories
      :type: dict[str, int]

      Count by PII category.

   .. py:attribute:: sensitivity_breakdown
      :type: dict[str, int]

      Count by sensitivity level.

   .. py:attribute:: masking_coverage
      :type: float

      Percentage of PII with masking.

   .. py:attribute:: legal_basis_coverage
      :type: float

      Percentage of PII with legal basis.

   .. py:attribute:: retention_coverage
      :type: float

      Percentage with retention periods.

   .. py:attribute:: gdpr_ready
      :type: bool

      GDPR compliance readiness.

   .. py:attribute:: ccpa_ready
      :type: bool

      CCPA compliance readiness.

   .. py:attribute:: hipaa_ready
      :type: bool

      HIPAA compliance readiness.

   .. py:attribute:: recommendations
      :type: list[str]

      Improvement recommendations.

   **Methods:**

   .. py:method:: to_dict() -> dict
   .. py:method:: to_json() -> str
   .. py:method:: to_markdown() -> str

generate_audit_report
---------------------

.. py:function:: griot_core.generate_audit_report(model) -> AuditReport

   Generate a compliance audit report for a model.

   :param model: Model class to analyze
   :type model: type[GriotModel]
   :returns: Audit report
   :rtype: AuditReport

ReadinessReport
---------------

.. py:class:: griot_core.ReadinessReport

   Combined readiness assessment report.

   **Attributes:**

   .. py:attribute:: contract_name
      :type: str

      Name of the contract.

   .. py:attribute:: generated_at
      :type: str

      ISO timestamp of generation.

   .. py:attribute:: overall_score
      :type: float

      Overall readiness score (0-100).

   .. py:attribute:: overall_grade
      :type: str

      Letter grade (A-F).

   .. py:attribute:: readiness_status
      :type: str

      Status: ready, partial, not_ready.

   .. py:attribute:: data_quality_score
      :type: float

      Data quality score from analytics.

   .. py:attribute:: ai_readiness_score
      :type: float

      AI readiness score.

   .. py:attribute:: compliance_score
      :type: float

      Compliance score from audit.

   .. py:attribute:: analytics_report
      :type: AnalyticsReport

      Embedded analytics report.

   .. py:attribute:: ai_report
      :type: AIReadinessReport

      Embedded AI readiness report.

   .. py:attribute:: audit_report
      :type: AuditReport

      Embedded audit report.

   .. py:attribute:: recommendations
      :type: list[str]

      Consolidated recommendations.

   **Methods:**

   .. py:method:: to_dict() -> dict
   .. py:method:: to_json() -> str
   .. py:method:: to_markdown() -> str

generate_readiness_report
-------------------------

.. py:function:: griot_core.generate_readiness_report(model) -> ReadinessReport

   Generate a combined readiness report for a model.

   :param model: Model class to analyze
   :type model: type[GriotModel]
   :returns: Combined readiness report
   :rtype: ReadinessReport

   **Example:**

   .. code-block:: python

      from griot_core import generate_readiness_report

      report = generate_readiness_report(Customer)

      print(f"Overall: {report.overall_grade} ({report.overall_score:.0f}%)")
      print(f"Data Quality: {report.data_quality_score:.0f}%")
      print(f"AI Readiness: {report.ai_readiness_score:.0f}%")
      print(f"Compliance: {report.compliance_score:.0f}%")

      for rec in report.recommendations:
          print(f"  - {rec}")
