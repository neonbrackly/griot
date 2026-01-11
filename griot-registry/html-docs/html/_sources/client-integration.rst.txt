Client Integration
==================

This guide shows how to integrate with griot-registry from various clients and languages.

.. contents:: Table of Contents
   :local:
   :depth: 2

Python Client
-------------

Installation
~~~~~~~~~~~~

.. code-block:: bash

   pip install griot-registry[client]

   # Or with httpx for async support
   pip install httpx

Basic Usage
~~~~~~~~~~~

.. code-block:: python

   from griot_registry.client import RegistryClient

   # Initialize client
   client = RegistryClient(
       base_url="http://localhost:8000/api/v1",
       api_key="your-api-key"
   )

   # List contracts
   contracts = client.list_contracts()
   for contract in contracts:
       print(f"{contract.name} v{contract.current_version}")

   # Get a specific contract
   contract = client.get_contract("user_profile")
   print(contract.fields)

   # Create a contract
   new_contract = client.create_contract(
       name="order_events",
       description="E-commerce order events",
       owner="data-team",
       fields=[
           {"name": "order_id", "type": "string", "required": True},
           {"name": "amount", "type": "number", "constraints": {"min": 0}},
       ]
   )

   # Record validation result
   client.record_validation(
       contract_name="user_profile",
       version="1.2.0",
       status="passed",
       total_rows=10000,
       valid_rows=9950
   )

Async Client
~~~~~~~~~~~~

.. code-block:: python

   import asyncio
   from griot_registry.client import AsyncRegistryClient

   async def main():
       async with AsyncRegistryClient(
           base_url="http://localhost:8000/api/v1",
           api_key="your-api-key"
       ) as client:
           contracts = await client.list_contracts()
           print(contracts)

   asyncio.run(main())

Using with httpx Directly
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import httpx

   # Synchronous
   with httpx.Client(
       base_url="http://localhost:8000/api/v1",
       headers={"X-API-Key": "your-api-key"}
   ) as client:
       response = client.get("/contracts")
       contracts = response.json()

   # Async
   async with httpx.AsyncClient(
       base_url="http://localhost:8000/api/v1",
       headers={"X-API-Key": "your-api-key"}
   ) as client:
       response = await client.get("/contracts")
       contracts = response.json()

Using with requests
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import requests

   session = requests.Session()
   session.headers.update({"X-API-Key": "your-api-key"})

   # List contracts
   response = session.get("http://localhost:8000/api/v1/contracts")
   contracts = response.json()

   # Create contract
   response = session.post(
       "http://localhost:8000/api/v1/contracts",
       json={
           "name": "my_contract",
           "description": "My data contract",
           "owner": "my-team",
           "fields": [
               {"name": "id", "type": "string", "required": True}
           ]
       }
   )

CLI Integration
---------------

The griot CLI provides built-in registry integration.

Configuration
~~~~~~~~~~~~~

.. code-block:: bash

   # Set registry URL
   export GRIOT_REGISTRY_URL=http://localhost:8000/api/v1
   export GRIOT_API_KEY=your-api-key

   # Or use config file (~/.griot/config.yaml)
   cat > ~/.griot/config.yaml << EOF
   registry:
     url: http://localhost:8000/api/v1
     api_key: your-api-key
   EOF

Push and Pull Contracts
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Push a contract to registry
   griot push contracts/user_profile.yaml

   # Push all contracts in directory
   griot push --dir ./contracts/

   # Pull a contract from registry
   griot pull user_profile --output ./contracts/

   # Pull all contracts
   griot pull --all --output ./contracts/

Validate Against Registry
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Validate data using contract from registry
   griot validate --registry user_profile data.csv

curl Examples
-------------

Common operations using curl.

Authentication
~~~~~~~~~~~~~~

.. code-block:: bash

   # Using X-API-Key header
   curl http://localhost:8000/api/v1/contracts \
     -H "X-API-Key: your-api-key"

   # Using Bearer token (OAuth2)
   curl http://localhost:8000/api/v1/contracts \
     -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIs..."

Contract Operations
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # List all contracts
   curl http://localhost:8000/api/v1/contracts \
     -H "X-API-Key: your-key"

   # Get specific contract
   curl http://localhost:8000/api/v1/contracts/user_profile \
     -H "X-API-Key: your-key"

   # Create contract
   curl -X POST http://localhost:8000/api/v1/contracts \
     -H "X-API-Key: your-key" \
     -H "Content-Type: application/json" \
     -d @contract.json

   # Update contract
   curl -X PUT http://localhost:8000/api/v1/contracts/user_profile \
     -H "X-API-Key: your-key" \
     -H "Content-Type: application/json" \
     -d @updated_contract.json

   # Deprecate contract
   curl -X DELETE http://localhost:8000/api/v1/contracts/old_contract \
     -H "X-API-Key: your-key"

Version Operations
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # List versions
   curl http://localhost:8000/api/v1/contracts/user_profile/versions \
     -H "X-API-Key: your-key"

   # Get specific version
   curl http://localhost:8000/api/v1/contracts/user_profile/versions/1.0.0 \
     -H "X-API-Key: your-key"

   # Diff versions
   curl "http://localhost:8000/api/v1/contracts/user_profile/diff?from=1.0.0&to=2.0.0" \
     -H "X-API-Key: your-key"

Validation History
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Record validation
   curl -X POST http://localhost:8000/api/v1/contracts/user_profile/validate \
     -H "X-API-Key: your-key" \
     -H "Content-Type: application/json" \
     -d '{
       "version": "1.2.0",
       "status": "passed",
       "total_rows": 10000,
       "valid_rows": 9950,
       "error_count": 50
     }'

   # Get validation history
   curl "http://localhost:8000/api/v1/contracts/user_profile/validations?limit=10" \
     -H "X-API-Key: your-key"

JavaScript/TypeScript
---------------------

Using Fetch API
~~~~~~~~~~~~~~~

.. code-block:: javascript

   const API_URL = 'http://localhost:8000/api/v1';
   const API_KEY = 'your-api-key';

   async function listContracts() {
     const response = await fetch(`${API_URL}/contracts`, {
       headers: {
         'X-API-Key': API_KEY,
         'Accept': 'application/json'
       }
     });
     return response.json();
   }

   async function createContract(contract) {
     const response = await fetch(`${API_URL}/contracts`, {
       method: 'POST',
       headers: {
         'X-API-Key': API_KEY,
         'Content-Type': 'application/json'
       },
       body: JSON.stringify(contract)
     });
     return response.json();
   }

TypeScript Client
~~~~~~~~~~~~~~~~~

.. code-block:: typescript

   interface Contract {
     name: string;
     description: string;
     owner: string;
     current_version: string;
     status: 'active' | 'deprecated';
     fields: Field[];
   }

   interface Field {
     name: string;
     type: string;
     required?: boolean;
     constraints?: Record<string, unknown>;
   }

   class RegistryClient {
     constructor(
       private baseUrl: string,
       private apiKey: string
     ) {}

     private async request<T>(
       path: string,
       options: RequestInit = {}
     ): Promise<T> {
       const response = await fetch(`${this.baseUrl}${path}`, {
         ...options,
         headers: {
           'X-API-Key': this.apiKey,
           'Content-Type': 'application/json',
           ...options.headers
         }
       });
       if (!response.ok) {
         throw new Error(`API error: ${response.status}`);
       }
       return response.json();
     }

     async listContracts(): Promise<Contract[]> {
       const data = await this.request<{contracts: Contract[]}>('/contracts');
       return data.contracts;
     }

     async getContract(name: string): Promise<Contract> {
       return this.request<Contract>(`/contracts/${name}`);
     }

     async createContract(contract: Omit<Contract, 'current_version' | 'status'>): Promise<Contract> {
       return this.request<Contract>('/contracts', {
         method: 'POST',
         body: JSON.stringify(contract)
       });
     }
   }

   // Usage
   const client = new RegistryClient('http://localhost:8000/api/v1', 'your-key');
   const contracts = await client.listContracts();

Airflow Integration
-------------------

Using griot-enforce operators with registry:

.. code-block:: python

   from airflow import DAG
   from airflow.operators.python import PythonOperator
   from griot_enforce.airflow import GriotValidateOperator
   from datetime import datetime

   with DAG(
       'data_validation',
       start_date=datetime(2024, 1, 1),
       schedule_interval='@daily'
   ) as dag:

       validate_users = GriotValidateOperator(
           task_id='validate_users',
           contract_name='user_profile',  # Fetched from registry
           registry_url='http://griot-registry:8000/api/v1',
           api_key='{{ var.value.griot_api_key }}',
           data_path='/data/users/{{ ds }}.parquet'
       )

Dagster Integration
-------------------

.. code-block:: python

   from dagster import asset, Definitions
   from griot_enforce.dagster import GriotResource, griot_asset

   @griot_asset(
       contract_name="user_profile",
       registry_url="http://griot-registry:8000/api/v1"
   )
   def users_validated(context, raw_users):
       # Validation happens automatically
       return raw_users

   defs = Definitions(
       assets=[users_validated],
       resources={
           "griot": GriotResource(
               registry_url="http://griot-registry:8000/api/v1",
               api_key=EnvVar("GRIOT_API_KEY")
           )
       }
   )

Prefect Integration
-------------------

.. code-block:: python

   from prefect import flow, task
   from griot_enforce.prefect import validate_task

   @task
   def load_data():
       import pandas as pd
       return pd.read_parquet("data/users.parquet")

   @flow
   def validation_flow():
       data = load_data()
       result = validate_task(
           data=data,
           contract_name="user_profile",
           registry_url="http://griot-registry:8000/api/v1",
           api_key="your-key"
       )
       if not result.is_valid:
           raise ValueError(f"Validation failed: {result.error_count} errors")

   validation_flow()

Error Handling
--------------

Python Error Handling
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from griot_registry.client import RegistryClient
   from griot_registry.exceptions import (
       ContractNotFoundError,
       AuthenticationError,
       ValidationError
   )

   client = RegistryClient(base_url="...", api_key="...")

   try:
       contract = client.get_contract("unknown")
   except ContractNotFoundError:
       print("Contract not found")
   except AuthenticationError:
       print("Invalid API key")
   except ValidationError as e:
       print(f"Validation failed: {e.details}")

Retry Logic
~~~~~~~~~~~

.. code-block:: python

   import httpx
   from tenacity import retry, stop_after_attempt, wait_exponential

   @retry(
       stop=stop_after_attempt(3),
       wait=wait_exponential(multiplier=1, min=1, max=10)
   )
   def fetch_contract(client: httpx.Client, name: str):
       response = client.get(f"/contracts/{name}")
       response.raise_for_status()
       return response.json()

Webhook Integration
-------------------

Configure webhooks to receive notifications on contract changes:

.. code-block:: bash

   export GRIOT_WEBHOOKS='[
     {
       "url": "https://your-service.com/webhook",
       "events": ["contract.created", "contract.updated", "approval.completed"],
       "secret": "webhook-secret"
     }
   ]'

Webhook Payload
~~~~~~~~~~~~~~~

.. code-block:: json

   {
     "event": "contract.updated",
     "timestamp": "2024-01-10T14:30:00Z",
     "data": {
       "contract": "user_profile",
       "version": "2.0.0",
       "updated_by": "alice@example.com"
     }
   }

Verifying Webhook Signature
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import hmac
   import hashlib

   def verify_webhook(payload: bytes, signature: str, secret: str) -> bool:
       expected = hmac.new(
           secret.encode(),
           payload,
           hashlib.sha256
       ).hexdigest()
       return hmac.compare_digest(f"sha256={expected}", signature)

   # In your webhook handler
   @app.post("/webhook")
   async def handle_webhook(request: Request):
       payload = await request.body()
       signature = request.headers.get("X-Griot-Signature")

       if not verify_webhook(payload, signature, "your-secret"):
           raise HTTPException(401, "Invalid signature")

       data = json.loads(payload)
       # Process webhook...
