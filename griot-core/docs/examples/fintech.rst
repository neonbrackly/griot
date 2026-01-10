FinTech Examples
================

Data contracts for financial technology applications.

Transaction Contract
--------------------

.. code-block:: python

   from griot_core import (
       GriotModel, Field, AggregationType,
       PIICategory, SensitivityLevel, MaskingStrategy, LegalBasis,
       DataRegion, ResidencyConfig, ResidencyRule,
       LineageConfig, Source, Transformation, Consumer
   )

   class Transaction(GriotModel):
       """
       Financial transaction contract.

       PCI-DSS compliant with full audit trail.
       """

       class Meta:
           description = "Payment transaction records"
           version = "2.0.0"
           owner = "payments-team@fintech.com"
           tags = ["payment", "transaction", "pci"]

           residency = ResidencyConfig(
               default_rule=ResidencyRule(
                   allowed_regions=[DataRegion.US, DataRegion.EU],
                   required_encryption=True
               )
           )

           lineage = LineageConfig(
               sources=[
                   Source(name="payment_gateway", type="api"),
                   Source(name="card_network", type="api")
               ],
               transformations=[
                   Transformation(
                       name="tokenize_card",
                       description="Tokenize card number",
                       input_fields=["card_number"],
                       output_fields=["card_token"]
                   ),
                   Transformation(
                       name="fraud_scoring",
                       description="Calculate fraud risk score",
                       input_fields=["amount", "merchant", "location"],
                       output_fields=["fraud_score"]
                   )
               ],
               consumers=[
                   Consumer(name="fraud_detection", type="ml"),
                   Consumer(name="settlement", type="application"),
                   Consumer(name="reporting", type="warehouse")
               ]
           )

       transaction_id: str = Field(
           description="Unique transaction identifier",
           primary_key=True,
           pattern=r"^TXN-[A-Z0-9]{16}$",
           examples=["TXN-ABC123XYZ456DEF7"]
       )

       account_id: str = Field(
           description="Customer account ID",
           pattern=r"^ACC-\d{12}$",
           pii_category=PIICategory.FINANCIAL,
           sensitivity=SensitivityLevel.CONFIDENTIAL
       )

       card_token: str = Field(
           description="Tokenized card number",
           pattern=r"^tok_[a-z0-9]{24}$",
           pii_category=PIICategory.CREDIT_CARD,
           sensitivity=SensitivityLevel.RESTRICTED,
           masking_strategy=MaskingStrategy.TOKENIZE,
           legal_basis=LegalBasis.CONTRACT
       )

       card_last_four: str = Field(
           description="Last 4 digits of card",
           pattern=r"^\d{4}$",
           sensitivity=SensitivityLevel.INTERNAL
       )

       amount: float = Field(
           description="Transaction amount",
           ge=0.01,
           le=1000000.00,
           unit="USD",
           aggregation=AggregationType.SUM
       )

       currency: str = Field(
           description="Currency code (ISO 4217)",
           pattern=r"^[A-Z]{3}$",
           examples=["USD", "EUR", "GBP"]
       )

       transaction_type: str = Field(
           description="Type of transaction",
           enum=["purchase", "refund", "chargeback", "transfer", "withdrawal"]
       )

       status: str = Field(
           description="Transaction status",
           enum=[
               "pending",
               "authorized",
               "captured",
               "settled",
               "declined",
               "refunded",
               "disputed"
           ]
       )

       merchant_id: str = Field(
           description="Merchant identifier",
           pattern=r"^MER-[A-Z0-9]{10}$"
       )

       merchant_name: str = Field(
           description="Merchant display name",
           max_length=255
       )

       merchant_category: str = Field(
           description="Merchant Category Code (MCC)",
           pattern=r"^\d{4}$",
           examples=["5411", "5812", "7011"]
       )

       timestamp: str = Field(
           description="Transaction timestamp",
           format="datetime"
       )

       authorization_code: str = Field(
           description="Authorization code from issuer",
           pattern=r"^[A-Z0-9]{6}$",
           nullable=True
       )

       fraud_score: float = Field(
           description="Fraud risk score (0-100)",
           ge=0.0,
           le=100.0,
           sensitivity=SensitivityLevel.INTERNAL
       )

       ip_address: str = Field(
           description="Customer IP address",
           format="ipv4",
           pii_category=PIICategory.IP_ADDRESS,
           sensitivity=SensitivityLevel.CONFIDENTIAL,
           masking_strategy=MaskingStrategy.HASH,
           legal_basis=LegalBasis.LEGITIMATE_INTEREST,
           nullable=True
       )

       device_id: str = Field(
           description="Device fingerprint",
           pii_category=PIICategory.DEVICE_ID,
           sensitivity=SensitivityLevel.CONFIDENTIAL,
           masking_strategy=MaskingStrategy.HASH,
           legal_basis=LegalBasis.LEGITIMATE_INTEREST,
           nullable=True
       )

Account Contract
----------------

.. code-block:: python

   class Account(GriotModel):
       """
       Customer account contract.

       Financial account with KYC information.
       """

       class Meta:
           description = "Customer financial accounts"
           version = "1.0.0"
           owner = "accounts-team@fintech.com"
           tags = ["account", "kyc", "aml"]

           residency = ResidencyConfig(
               default_rule=ResidencyRule(
                   allowed_regions=[DataRegion.US],
                   required_encryption=True
               )
           )

       account_id: str = Field(
           description="Unique account identifier",
           primary_key=True,
           pattern=r"^ACC-\d{12}$"
       )

       customer_id: str = Field(
           description="Customer identifier",
           pattern=r"^CUS-[A-Z0-9]{10}$"
       )

       account_type: str = Field(
           description="Type of account",
           enum=["checking", "savings", "investment", "credit"]
       )

       account_number: str = Field(
           description="Account number (masked)",
           pii_category=PIICategory.BANK_ACCOUNT,
           sensitivity=SensitivityLevel.RESTRICTED,
           masking_strategy=MaskingStrategy.PARTIAL_MASK,
           legal_basis=LegalBasis.CONTRACT
       )

       routing_number: str = Field(
           description="Bank routing number",
           pattern=r"^\d{9}$",
           pii_category=PIICategory.BANK_ACCOUNT,
           sensitivity=SensitivityLevel.RESTRICTED,
           masking_strategy=MaskingStrategy.PARTIAL_MASK,
           legal_basis=LegalBasis.CONTRACT
       )

       balance: float = Field(
           description="Current account balance",
           unit="USD",
           sensitivity=SensitivityLevel.CONFIDENTIAL,
           aggregation=AggregationType.SUM
       )

       available_balance: float = Field(
           description="Available balance",
           unit="USD",
           sensitivity=SensitivityLevel.CONFIDENTIAL
       )

       status: str = Field(
           description="Account status",
           enum=["active", "frozen", "closed", "pending_verification"]
       )

       kyc_status: str = Field(
           description="KYC verification status",
           enum=["pending", "verified", "failed", "expired"]
       )

       kyc_verified_at: str = Field(
           description="KYC verification timestamp",
           format="datetime",
           nullable=True
       )

       risk_rating: str = Field(
           description="AML risk rating",
           enum=["low", "medium", "high"],
           sensitivity=SensitivityLevel.INTERNAL
       )

       opened_at: str = Field(
           description="Account opening date",
           format="datetime"
       )

       last_activity_at: str = Field(
           description="Last transaction timestamp",
           format="datetime"
       )

Wire Transfer Contract
----------------------

.. code-block:: python

   class WireTransfer(GriotModel):
       """
       Wire transfer contract.

       International and domestic wire transfers with compliance tracking.
       """

       class Meta:
           description = "Wire transfer records"
           version = "1.0.0"
           owner = "treasury-team@fintech.com"
           tags = ["wire", "transfer", "aml", "ofac"]

       transfer_id: str = Field(
           description="Wire transfer reference",
           primary_key=True,
           pattern=r"^WIRE-\d{14}$"
       )

       from_account: str = Field(
           description="Source account ID",
           pattern=r"^ACC-\d{12}$"
       )

       to_account_number: str = Field(
           description="Destination account number",
           pii_category=PIICategory.BANK_ACCOUNT,
           sensitivity=SensitivityLevel.RESTRICTED,
           masking_strategy=MaskingStrategy.PARTIAL_MASK,
           legal_basis=LegalBasis.CONTRACT
       )

       to_routing_number: str = Field(
           description="Destination routing/SWIFT",
           max_length=34
       )

       beneficiary_name: str = Field(
           description="Beneficiary name",
           pii_category=PIICategory.NAME,
           sensitivity=SensitivityLevel.CONFIDENTIAL,
           masking_strategy=MaskingStrategy.REDACT,
           legal_basis=LegalBasis.CONTRACT
       )

       beneficiary_address: str = Field(
           description="Beneficiary address",
           pii_category=PIICategory.ADDRESS,
           sensitivity=SensitivityLevel.CONFIDENTIAL,
           masking_strategy=MaskingStrategy.REDACT,
           legal_basis=LegalBasis.CONTRACT
       )

       amount: float = Field(
           description="Transfer amount",
           ge=0.01,
           unit="USD",
           aggregation=AggregationType.SUM
       )

       currency: str = Field(
           description="Currency code",
           pattern=r"^[A-Z]{3}$"
       )

       purpose: str = Field(
           description="Transfer purpose/memo",
           max_length=500
       )

       transfer_type: str = Field(
           description="Wire type",
           enum=["domestic", "international", "internal"]
       )

       status: str = Field(
           description="Transfer status",
           enum=[
               "pending_review",
               "approved",
               "processing",
               "completed",
               "rejected",
               "returned"
           ]
       )

       ofac_screened: bool = Field(
           description="OFAC screening completed",
           default=False
       )

       ofac_cleared: bool = Field(
           description="OFAC screening passed",
           nullable=True
       )

       initiated_at: str = Field(
           description="Transfer initiation time",
           format="datetime"
       )

       completed_at: str = Field(
           description="Transfer completion time",
           format="datetime",
           nullable=True
       )

Compliance Example
------------------

.. code-block:: python

   from griot_core import generate_audit_report, generate_readiness_report

   # PCI-DSS compliance check
   audit = generate_audit_report(Transaction)

   print("PCI-DSS Compliance Check")
   print("=" * 40)
   print(f"Compliance Score: {audit.compliance_score:.1f}%")
   print()
   print("Card Data Fields:")
   for field in audit.pii_fields:
       if field['category'] == 'CREDIT_CARD':
           print(f"  - {field['name']}: Masked={field.get('masking', 'None')}")
   print()

   # Full readiness assessment
   readiness = generate_readiness_report(Account)
   print(f"Overall Readiness: {readiness.overall_grade}")
   print(f"Data Quality: {readiness.data_quality_score:.0f}%")
   print(f"Compliance: {readiness.compliance_score:.0f}%")
