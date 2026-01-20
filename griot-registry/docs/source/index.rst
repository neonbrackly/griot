Griot Registry Documentation
=============================

**Griot Registry** is a central registry service for managing data contracts in the Griot ecosystem.
It provides storage, versioning, validation history, and search capabilities for ODCS-compliant
data contracts.

.. note::

   This documentation covers version |version| of Griot Registry.

Key Features
------------

- **Contract Management**: Full CRUD operations with semantic versioning
- **MongoDB Storage**: Scalable document storage with full-text search
- **Schema Catalog**: Cross-contract schema discovery and querying
- **Validation History**: Track validation results over time
- **Pipeline Integration**: Run tracking for data pipeline executions
- **Collaboration**: Comments, issues, and approval workflows
- **Authentication**: JWT token authentication with role-based access
- **Python Client**: Async and sync clients for easy integration

Quick Start
-----------

Install the package:

.. code-block:: bash

   pip install griot-registry

Start MongoDB and the server:

.. code-block:: bash

   # Start MongoDB (using Docker)
   docker run -d --name mongodb -p 27017:27017 mongo:7

   # Set required environment variables
   export MONGODB_URI="mongodb://localhost:27017"
   export MONGODB_DATABASE="griot_registry"
   export JWT_SECRET_KEY="your-secret-key"

   # Run the server
   griot-registry

Use the Python client:

.. code-block:: python

   import httpx
   from griot_registry import SyncRegistryClient
   from griot_core import load_contract_from_dict

   # Get an authentication token (POST request)
   response = httpx.post(
       "http://localhost:8000/api/v1/auth/token",
       params={"user_id": "myuser", "roles": "editor"}
   )
   token = response.json()["access_token"]

   # Connect to the registry
   with SyncRegistryClient("http://localhost:8000", token=token) as client:
       # Create a contract
       contract_data = {
           "apiVersion": "v1.0.0",
           "kind": "DataContract",
           "id": "my-first-contract",
           "name": "my_first_contract",
           "version": "1.0.0",
           "status": "draft",
           "schema": [
               {
                   "name": "MySchema",
                   "id": "my-schema",
                   "logicalType": "object",
                   "properties": [
                       {"name": "id", "logicalType": "string", "required": True}
                   ]
               }
           ]
       }
       contract = load_contract_from_dict(contract_data)
       created = client.create(contract)
       print(f"Created: {created.id} v{created.version}")

       # List all contracts
       contracts, total = client.list_contracts()
       print(f"Total contracts: {total}")

Documentation Contents
----------------------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   getting_started
   configuration
   authentication

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/endpoints
   api/contracts
   api/schemas
   api/validations
   api/runs
   api/issues
   api/comments
   api/approvals
   api/search

.. toctree::
   :maxdepth: 2
   :caption: Python Client

   client/index
   client/examples

.. toctree::
   :maxdepth: 2
   :caption: Developer Guide

   architecture
   storage
   services
   extending

.. toctree::
   :maxdepth: 1
   :caption: Reference

   changelog
   api_reference

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
