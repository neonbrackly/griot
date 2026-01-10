Examples
========

This page provides real-world examples of using griot-enforce in data pipelines.

E-Commerce Data Pipeline
------------------------

A complete e-commerce data pipeline with validation at each stage:

.. code-block:: python

   from griot_enforce import RuntimeValidator, ResidencyViolationError
   import pandas as pd

   class ECommerceDataPipeline:
       def __init__(self, registry_url: str):
           self.validator = RuntimeValidator(
               registry_url=registry_url,
               cache_ttl=600,
           )

       def process_orders(self, orders_df: pd.DataFrame) -> pd.DataFrame:
           """Process and validate order data."""
           # Validate raw orders
           self.validator.validate(
               "raw-order-events",
               orders_df,
               fail_on_error=True,
           )

           # Transform
           processed = self._transform_orders(orders_df)

           # Validate processed orders
           self.validator.validate(
               "processed-orders",
               processed,
               fail_on_error=True,
           )

           return processed

       def process_customers(
           self,
           customers_df: pd.DataFrame,
           environment: str,
       ) -> pd.DataFrame:
           """Process customer data with PII handling."""
           # Validate with masking verification for non-prod
           self.validator.validate(
               "customer-profile",
               customers_df,
               verify_masking=(environment != "production"),
               environment=environment,
               fail_on_error=True,
           )

           return customers_df

       def write_to_region(
           self,
           data: pd.DataFrame,
           contract_id: str,
           destination: str,
       ):
           """Write data to regional storage with residency check."""
           # Check residency before writing
           self.validator.check_residency(
               contract_id,
               destination=destination,
               fail_on_violation=True,
           )

           # Safe to write
           data.to_parquet(destination)

       def _transform_orders(self, df: pd.DataFrame) -> pd.DataFrame:
           # Transform logic here
           return df

   # Usage
   pipeline = ECommerceDataPipeline("https://registry.example.com")

   orders = pd.read_parquet("s3://raw/orders.parquet")
   processed_orders = pipeline.process_orders(orders)

   pipeline.write_to_region(
       processed_orders,
       "processed-orders",
       "s3://processed-eu-west-1/orders/",
   )

Multi-Region Data Compliance
----------------------------

Handling data across multiple regions with compliance checks:

.. code-block:: python

   from griot_enforce import RuntimeValidator, ResidencyViolationError
   from dataclasses import dataclass
   from typing import Dict, List

   @dataclass
   class RegionalConfig:
       name: str
       storage_uri: str
       allowed_contracts: List[str]

   class MultiRegionDataManager:
       def __init__(self, registry_url: str, regions: List[RegionalConfig]):
           self.validator = RuntimeValidator(registry_url=registry_url)
           self.regions = {r.name: r for r in regions}

       def route_data(
           self,
           data,
           contract_id: str,
           preferred_region: str = None,
       ) -> str:
           """Route data to compliant region."""
           # Get compliant regions for this contract
           compliant_regions = []

           for region_name, config in self.regions.items():
               if contract_id not in config.allowed_contracts:
                   continue

               try:
                   self.validator.check_residency(
                       contract_id,
                       destination=config.storage_uri,
                       fail_on_violation=True,
                   )
                   compliant_regions.append(region_name)
               except ResidencyViolationError:
                   continue

           if not compliant_regions:
               raise ValueError(f"No compliant region found for {contract_id}")

           # Use preferred region if compliant, otherwise first compliant
           if preferred_region in compliant_regions:
               target_region = preferred_region
           else:
               target_region = compliant_regions[0]

           return target_region

       def write_to_compliant_region(
           self,
           data,
           contract_id: str,
           preferred_region: str = None,
       ):
           """Write data to a compliant region."""
           target_region = self.route_data(data, contract_id, preferred_region)
           config = self.regions[target_region]

           # Validate data
           self.validator.validate(contract_id, data, fail_on_error=True)

           # Write to storage
           write_to_storage(data, config.storage_uri)
           return target_region

   # Configuration
   regions = [
       RegionalConfig(
           name="eu-west-1",
           storage_uri="s3://data-eu-west-1/",
           allowed_contracts=["customer-profile-eu", "order-events-eu"],
       ),
       RegionalConfig(
           name="us-east-1",
           storage_uri="s3://data-us-east-1/",
           allowed_contracts=["customer-profile-us", "order-events-us"],
       ),
   ]

   manager = MultiRegionDataManager("https://registry.example.com", regions)

   # Route and write data
   target = manager.write_to_compliant_region(
       customer_data,
       "customer-profile-eu",
       preferred_region="eu-west-1",
   )

Staging Environment with Masking
--------------------------------

Pipeline for staging environments with PII masking verification:

.. code-block:: python

   from griot_enforce import RuntimeValidator, MaskingViolationError
   import pandas as pd
   import hashlib

   class StagingDataPreparer:
       def __init__(self, registry_url: str):
           self.validator = RuntimeValidator(registry_url=registry_url)

       def mask_pii_fields(self, df: pd.DataFrame, contract_id: str) -> pd.DataFrame:
           """Apply masking to PII fields based on contract definition."""
           # Get contract to find PII fields
           contract = self.validator.get_contract(contract_id)
           pii_inventory = contract.pii_inventory()

           masked_df = df.copy()

           for pii_field in pii_inventory:
               field_name = pii_field.name
               strategy = pii_field.masking_strategy

               if field_name not in masked_df.columns:
                   continue

               if strategy.value == "redact":
                   masked_df[field_name] = "[REDACTED]"
               elif strategy.value == "partial":
                   masked_df[field_name] = masked_df[field_name].apply(
                       lambda x: self._partial_mask(str(x))
                   )
               elif strategy.value == "hash":
                   masked_df[field_name] = masked_df[field_name].apply(
                       lambda x: hashlib.sha256(str(x).encode()).hexdigest()
                   )

           return masked_df

       def prepare_for_staging(
           self,
           data: pd.DataFrame,
           contract_id: str,
       ) -> pd.DataFrame:
           """Prepare data for staging environment."""
           # Apply masking
           masked_data = self.mask_pii_fields(data, contract_id)

           # Verify masking was applied correctly
           try:
               self.validator.verify_masking(
                   contract_id,
                   masked_data,
                   environment="staging",
                   fail_on_violation=True,
               )
           except MaskingViolationError as e:
               print(f"Masking verification failed: {e.violations}")
               raise

           # Validate the masked data
           self.validator.validate(
               contract_id,
               masked_data,
               fail_on_error=True,
           )

           return masked_data

       def _partial_mask(self, value: str) -> str:
           """Apply partial masking (show last 4 chars)."""
           if len(value) <= 4:
               return "****"
           return "*" * (len(value) - 4) + value[-4:]

   # Usage
   preparer = StagingDataPreparer("https://registry.example.com")

   production_data = pd.read_parquet("s3://prod/customers.parquet")
   staging_data = preparer.prepare_for_staging(
       production_data,
       "customer-profile",
   )
   staging_data.to_parquet("s3://staging/customers.parquet")

Batch Validation Service
------------------------

A service for batch validation of multiple datasets:

.. code-block:: python

   from griot_enforce import RuntimeValidator, RuntimeValidationError
   from dataclasses import dataclass
   from typing import Dict, List, Any
   from concurrent.futures import ThreadPoolExecutor, as_completed
   import pandas as pd

   @dataclass
   class ValidationJob:
       dataset_id: str
       contract_id: str
       data: pd.DataFrame
       version: str = None

   @dataclass
   class ValidationResult:
       dataset_id: str
       contract_id: str
       passed: bool
       row_count: int
       error_count: int
       error_rate: float
       errors: List[Dict[str, Any]] = None

   class BatchValidationService:
       def __init__(self, registry_url: str, max_workers: int = 4):
           self.validator = RuntimeValidator(
               registry_url=registry_url,
               cache_ttl=3600,  # Long cache for batch jobs
           )
           self.max_workers = max_workers

       def validate_batch(
           self,
           jobs: List[ValidationJob],
       ) -> Dict[str, ValidationResult]:
           """Validate multiple datasets concurrently."""
           results = {}

           with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
               future_to_job = {
                   executor.submit(self._validate_job, job): job
                   for job in jobs
               }

               for future in as_completed(future_to_job):
                   job = future_to_job[future]
                   try:
                       result = future.result()
                       results[job.dataset_id] = result
                   except Exception as e:
                       results[job.dataset_id] = ValidationResult(
                           dataset_id=job.dataset_id,
                           contract_id=job.contract_id,
                           passed=False,
                           row_count=0,
                           error_count=0,
                           error_rate=0.0,
                           errors=[{"error": str(e)}],
                       )

           return results

       def _validate_job(self, job: ValidationJob) -> ValidationResult:
           """Validate a single job."""
           result = self.validator.validate(
               job.contract_id,
               job.data,
               version=job.version,
               fail_on_error=False,
           )

           return ValidationResult(
               dataset_id=job.dataset_id,
               contract_id=job.contract_id,
               passed=result.passed,
               row_count=result.row_count,
               error_count=result.error_count,
               error_rate=result.error_rate,
               errors=[e.to_dict() for e in result.errors[:10]],
           )

       def generate_report(
           self,
           results: Dict[str, ValidationResult],
       ) -> Dict[str, Any]:
           """Generate validation report."""
           total = len(results)
           passed = sum(1 for r in results.values() if r.passed)
           failed = total - passed

           total_rows = sum(r.row_count for r in results.values())
           total_errors = sum(r.error_count for r in results.values())

           return {
               "summary": {
                   "total_datasets": total,
                   "passed": passed,
                   "failed": failed,
                   "pass_rate": passed / total if total > 0 else 0,
                   "total_rows_validated": total_rows,
                   "total_errors": total_errors,
               },
               "details": {
                   dataset_id: {
                       "contract_id": r.contract_id,
                       "passed": r.passed,
                       "row_count": r.row_count,
                       "error_count": r.error_count,
                       "error_rate": r.error_rate,
                   }
                   for dataset_id, r in results.items()
               },
           }

   # Usage
   service = BatchValidationService("https://registry.example.com")

   jobs = [
       ValidationJob("customers_2024_01", "customer-profile", df1),
       ValidationJob("customers_2024_02", "customer-profile", df2),
       ValidationJob("orders_2024_01", "order-events", df3),
       ValidationJob("orders_2024_02", "order-events", df4),
   ]

   results = service.validate_batch(jobs)
   report = service.generate_report(results)
   print(f"Validation report: {report['summary']}")

Real-time Validation API
------------------------

A FastAPI service for real-time validation:

.. code-block:: python

   from fastapi import FastAPI, HTTPException
   from pydantic import BaseModel
   from griot_enforce import RuntimeValidator, RuntimeValidationError
   from typing import List, Dict, Any

   app = FastAPI(title="Data Validation API")

   validator = RuntimeValidator(
       registry_url="https://registry.example.com",
       cache_ttl=300,
   )

   class ValidationRequest(BaseModel):
       contract_id: str
       data: List[Dict[str, Any]]
       version: str = None
       verify_masking: bool = False
       environment: str = None

   class ValidationResponse(BaseModel):
       passed: bool
       row_count: int
       error_count: int
       error_rate: float
       errors: List[Dict[str, Any]]
       masking_compliant: bool = None

   @app.post("/validate", response_model=ValidationResponse)
   async def validate_data(request: ValidationRequest):
       try:
           result = validator.validate(
               request.contract_id,
               request.data,
               version=request.version,
               verify_masking=request.verify_masking,
               environment=request.environment,
               fail_on_error=False,
           )

           response = ValidationResponse(
               passed=result.passed,
               row_count=result.row_count,
               error_count=result.error_count,
               error_rate=result.error_rate,
               errors=[e.to_dict() for e in result.errors[:100]],
           )

           if request.verify_masking and hasattr(result, "masking_result"):
               response.masking_compliant = result.masking_result.get("compliant")

           return response

       except Exception as e:
           raise HTTPException(status_code=500, detail=str(e))

   @app.post("/check-residency")
   async def check_residency(
       contract_id: str,
       destination: str = None,
       region: str = None,
   ):
       try:
           result = validator.check_residency(
               contract_id,
               region=region,
               destination=destination,
               fail_on_violation=False,
           )
           return result
       except ValueError as e:
           raise HTTPException(status_code=400, detail=str(e))

   # Run with: uvicorn main:app --host 0.0.0.0 --port 8000

Monitoring Integration
----------------------

Integration with monitoring and alerting systems:

.. code-block:: python

   from griot_enforce import RuntimeValidator, RuntimeValidationError
   from dataclasses import dataclass
   from datetime import datetime
   import json

   @dataclass
   class ValidationMetric:
       timestamp: datetime
       contract_id: str
       dataset_id: str
       passed: bool
       row_count: int
       error_count: int
       error_rate: float
       duration_ms: float

   class MonitoredValidator:
       def __init__(
           self,
           registry_url: str,
           metrics_client=None,
           alert_client=None,
       ):
           self.validator = RuntimeValidator(registry_url=registry_url)
           self.metrics_client = metrics_client
           self.alert_client = alert_client

       def validate_with_monitoring(
           self,
           contract_id: str,
           data,
           dataset_id: str,
           alert_threshold: float = 0.05,
       ):
           """Validate and report metrics."""
           start_time = datetime.now()

           result = self.validator.validate(
               contract_id,
               data,
               fail_on_error=False,
           )

           duration_ms = (datetime.now() - start_time).total_seconds() * 1000

           # Create metric
           metric = ValidationMetric(
               timestamp=datetime.now(),
               contract_id=contract_id,
               dataset_id=dataset_id,
               passed=result.passed,
               row_count=result.row_count,
               error_count=result.error_count,
               error_rate=result.error_rate,
               duration_ms=duration_ms,
           )

           # Report metrics
           if self.metrics_client:
               self._report_metrics(metric)

           # Check alert threshold
           if result.error_rate > alert_threshold and self.alert_client:
               self._send_alert(metric)

           return result

       def _report_metrics(self, metric: ValidationMetric):
           """Report to metrics system (e.g., DataDog, Prometheus)."""
           self.metrics_client.gauge(
               "griot.validation.error_rate",
               metric.error_rate,
               tags=[
                   f"contract:{metric.contract_id}",
                   f"dataset:{metric.dataset_id}",
               ],
           )
           self.metrics_client.gauge(
               "griot.validation.duration_ms",
               metric.duration_ms,
               tags=[
                   f"contract:{metric.contract_id}",
               ],
           )

       def _send_alert(self, metric: ValidationMetric):
           """Send alert for high error rates."""
           self.alert_client.send(
               title=f"High Validation Error Rate: {metric.contract_id}",
               message=f"""
               Dataset: {metric.dataset_id}
               Contract: {metric.contract_id}
               Error Rate: {metric.error_rate:.2%}
               Error Count: {metric.error_count}
               Row Count: {metric.row_count}
               Time: {metric.timestamp}
               """,
               severity="warning" if metric.error_rate < 0.1 else "critical",
           )
