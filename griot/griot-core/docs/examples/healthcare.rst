Healthcare Examples
===================

HIPAA-compliant data contracts for healthcare applications.

Patient Record Contract
-----------------------

.. code-block:: python

   from griot_core import (
       GriotModel, Field,
       PIICategory, SensitivityLevel, MaskingStrategy, LegalBasis,
       DataRegion, ResidencyConfig, ResidencyRule,
       LineageConfig, Source, Consumer
   )

   class PatientRecord(GriotModel):
       """
       HIPAA-compliant patient record contract.

       Protected Health Information (PHI) with strict access controls.
       """

       class Meta:
           description = "Patient demographic and clinical data"
           version = "1.0.0"
           owner = "health-it@hospital.org"
           tags = ["patient", "phi", "hipaa"]

           residency = ResidencyConfig(
               default_rule=ResidencyRule(
                   allowed_regions=[DataRegion.US],
                   required_encryption=True
               )
           )

           lineage = LineageConfig(
               sources=[
                   Source(name="ehr_system", type="database",
                          description="Epic EHR system"),
                   Source(name="admission_desk", type="manual")
               ],
               consumers=[
                   Consumer(name="clinical_dashboard", type="dashboard"),
                   Consumer(name="billing_system", type="application"),
                   Consumer(name="research_warehouse", type="warehouse",
                            description="De-identified data only")
               ]
           )

       patient_id: str = Field(
           description="Medical Record Number (MRN)",
           primary_key=True,
           pattern=r"^MRN-\d{10}$",
           examples=["MRN-0000000001"],
           sensitivity=SensitivityLevel.RESTRICTED
       )

       ssn: str = Field(
           description="Social Security Number",
           pattern=r"^\d{3}-\d{2}-\d{4}$",
           pii_category=PIICategory.SSN,
           sensitivity=SensitivityLevel.RESTRICTED,
           masking_strategy=MaskingStrategy.REDACT,
           legal_basis=LegalBasis.LEGAL_OBLIGATION,
           retention_days=2555  # 7 years per HIPAA
       )

       first_name: str = Field(
           description="Patient first name",
           max_length=100,
           pii_category=PIICategory.NAME,
           sensitivity=SensitivityLevel.RESTRICTED,
           masking_strategy=MaskingStrategy.REDACT,
           legal_basis=LegalBasis.CONTRACT
       )

       last_name: str = Field(
           description="Patient last name",
           max_length=100,
           pii_category=PIICategory.NAME,
           sensitivity=SensitivityLevel.RESTRICTED,
           masking_strategy=MaskingStrategy.REDACT,
           legal_basis=LegalBasis.CONTRACT
       )

       date_of_birth: str = Field(
           description="Date of birth",
           format="date",
           pii_category=PIICategory.DATE_OF_BIRTH,
           sensitivity=SensitivityLevel.RESTRICTED,
           masking_strategy=MaskingStrategy.GENERALIZE,
           legal_basis=LegalBasis.CONTRACT
       )

       gender: str = Field(
           description="Patient gender",
           enum=["male", "female", "other", "unknown"]
       )

       email: str = Field(
           description="Contact email",
           format="email",
           pii_category=PIICategory.EMAIL,
           sensitivity=SensitivityLevel.CONFIDENTIAL,
           masking_strategy=MaskingStrategy.PARTIAL_MASK,
           legal_basis=LegalBasis.CONSENT,
           nullable=True
       )

       phone: str = Field(
           description="Contact phone",
           format="phone",
           pii_category=PIICategory.PHONE,
           sensitivity=SensitivityLevel.CONFIDENTIAL,
           masking_strategy=MaskingStrategy.PARTIAL_MASK,
           legal_basis=LegalBasis.CONTRACT
       )

       address: str = Field(
           description="Home address",
           pii_category=PIICategory.ADDRESS,
           sensitivity=SensitivityLevel.CONFIDENTIAL,
           masking_strategy=MaskingStrategy.REDACT,
           legal_basis=LegalBasis.CONTRACT
       )

       insurance_id: str = Field(
           description="Insurance member ID",
           pattern=r"^[A-Z]{3}\d{9}$",
           pii_category=PIICategory.FINANCIAL,
           sensitivity=SensitivityLevel.CONFIDENTIAL,
           masking_strategy=MaskingStrategy.PARTIAL_MASK,
           legal_basis=LegalBasis.CONTRACT
       )

       primary_diagnosis: str = Field(
           description="Primary ICD-10 diagnosis code",
           pattern=r"^[A-Z]\d{2}(\.\d{1,4})?$",
           pii_category=PIICategory.HEALTH,
           sensitivity=SensitivityLevel.RESTRICTED,
           masking_strategy=MaskingStrategy.ENCRYPT,
           legal_basis=LegalBasis.CONTRACT,
           examples=["J18.9", "E11.9", "I10"]
       )

       admission_date: str = Field(
           description="Hospital admission date",
           format="datetime"
       )

       discharge_date: str = Field(
           description="Hospital discharge date",
           format="datetime",
           nullable=True
       )

       attending_physician: str = Field(
           description="Attending physician NPI",
           pattern=r"^\d{10}$"
       )

Clinical Event Contract
-----------------------

.. code-block:: python

   class ClinicalEvent(GriotModel):
       """
       Clinical event/encounter contract.

       Records patient interactions with healthcare system.
       """

       class Meta:
           description = "Clinical events and encounters"
           version = "1.0.0"
           owner = "clinical-informatics@hospital.org"
           tags = ["clinical", "encounter", "phi"]

           residency = ResidencyConfig(
               default_rule=ResidencyRule(
                   allowed_regions=[DataRegion.US],
                   required_encryption=True
               )
           )

       event_id: str = Field(
           description="Unique event identifier",
           primary_key=True,
           pattern=r"^EVT-\d{12}$"
       )

       patient_id: str = Field(
           description="Patient MRN",
           pattern=r"^MRN-\d{10}$",
           sensitivity=SensitivityLevel.RESTRICTED
       )

       event_type: str = Field(
           description="Type of clinical event",
           enum=[
               "admission",
               "discharge",
               "transfer",
               "procedure",
               "lab_order",
               "lab_result",
               "medication_order",
               "medication_admin",
               "vital_signs",
               "progress_note",
               "consult"
           ]
       )

       event_datetime: str = Field(
           description="Event timestamp",
           format="datetime"
       )

       department: str = Field(
           description="Department code",
           pattern=r"^[A-Z]{2,4}\d{3}$"
       )

       provider_npi: str = Field(
           description="Provider NPI",
           pattern=r"^\d{10}$"
       )

       diagnosis_codes: list = Field(
           description="Associated ICD-10 codes",
           pii_category=PIICategory.HEALTH,
           sensitivity=SensitivityLevel.RESTRICTED,
           min_items=0,
           max_items=25
       )

       procedure_codes: list = Field(
           description="CPT/HCPCS procedure codes",
           min_items=0,
           max_items=50
       )

       notes: str = Field(
           description="Clinical notes (encrypted)",
           pii_category=PIICategory.HEALTH,
           sensitivity=SensitivityLevel.RESTRICTED,
           masking_strategy=MaskingStrategy.ENCRYPT,
           legal_basis=LegalBasis.CONTRACT,
           nullable=True
       )

Lab Result Contract
-------------------

.. code-block:: python

   class LabResult(GriotModel):
       """
       Laboratory test result contract.
       """

       class Meta:
           description = "Laboratory test results"
           version = "1.0.0"
           owner = "lab-informatics@hospital.org"
           tags = ["lab", "results", "phi"]

       result_id: str = Field(
           description="Unique result identifier",
           primary_key=True,
           pattern=r"^LAB-\d{14}$"
       )

       patient_id: str = Field(
           description="Patient MRN",
           pattern=r"^MRN-\d{10}$",
           sensitivity=SensitivityLevel.RESTRICTED
       )

       order_id: str = Field(
           description="Lab order ID",
           pattern=r"^ORD-\d{12}$"
       )

       test_code: str = Field(
           description="LOINC test code",
           pattern=r"^\d{4,7}-\d$",
           examples=["2345-7", "718-7", "4548-4"]
       )

       test_name: str = Field(
           description="Test display name",
           max_length=255,
           examples=["Glucose", "Hemoglobin", "HbA1c"]
       )

       result_value: str = Field(
           description="Result value",
           pii_category=PIICategory.HEALTH,
           sensitivity=SensitivityLevel.RESTRICTED
       )

       result_unit: str = Field(
           description="Result unit of measure",
           examples=["mg/dL", "g/dL", "%"]
       )

       reference_range: str = Field(
           description="Normal reference range",
           examples=["70-100", "12.0-16.0", "4.0-5.6"]
       )

       abnormal_flag: str = Field(
           description="Abnormal result flag",
           enum=["N", "L", "H", "LL", "HH", "A"],
           nullable=True
       )

       collection_datetime: str = Field(
           description="Specimen collection time",
           format="datetime"
       )

       result_datetime: str = Field(
           description="Result available time",
           format="datetime"
       )

       status: str = Field(
           description="Result status",
           enum=["preliminary", "final", "corrected", "cancelled"]
       )

HIPAA Compliance Check
----------------------

.. code-block:: python

   from griot_core import generate_audit_report

   # Check HIPAA compliance
   audit = generate_audit_report(PatientRecord)

   print("HIPAA Compliance Assessment")
   print("=" * 40)
   print(f"Compliance Score: {audit.compliance_score:.1f}%")
   print(f"HIPAA Ready: {'Yes' if audit.hipaa_ready else 'No'}")
   print()
   print("PHI Fields:")
   for field in audit.pii_fields:
       print(f"  - {field['name']}: {field['category']} ({field['sensitivity']})")
   print()
   print("Recommendations:")
   for rec in audit.recommendations:
       print(f"  - {rec}")
