Getting Started
===============

This guide walks you through installing and running griot-registry for local development.

Installation
------------

Install griot-registry using pip:

.. code-block:: bash

   pip install griot-registry

For development, clone the repository and install in editable mode:

.. code-block:: bash

   git clone https://github.com/your-org/griot.git
   cd griot/griot-registry
   pip install -e ".[dev]"

Quick Start
-----------

1. **Start the server**:

   .. code-block:: bash

      # Using the CLI
      griot-registry

      # Or using uvicorn directly
      uvicorn griot_registry.server:create_app --factory --reload

   The server starts on ``http://localhost:8000`` by default.

2. **Access the API documentation**:

   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc
   - OpenAPI spec: http://localhost:8000/openapi.json

3. **Check server health**:

   .. code-block:: bash

      curl http://localhost:8000/api/v1/health

   Response:

   .. code-block:: json

      {
        "status": "healthy",
        "storage": "healthy",
        "version": "0.1.0"
      }

Configuration
-------------

Configure the server using environment variables or a ``.env`` file:

.. code-block:: bash

   # Server settings
   GRIOT_HOST=0.0.0.0
   GRIOT_PORT=8000
   GRIOT_DEBUG=false
   GRIOT_LOG_LEVEL=INFO

   # API settings
   GRIOT_API_V1_PREFIX=/api/v1

   # Storage backend (filesystem, git, postgres)
   GRIOT_STORAGE_BACKEND=filesystem
   GRIOT_STORAGE_PATH=/var/lib/griot/contracts

   # CORS settings
   GRIOT_CORS_ORIGINS=["http://localhost:3000"]

   # Authentication
   GRIOT_AUTH_ENABLED=true
   GRIOT_API_KEYS=["your-api-key-here"]

Creating Your First Contract
----------------------------

1. **Create a contract via API**:

   .. code-block:: bash

      curl -X POST http://localhost:8000/api/v1/contracts \
        -H "Content-Type: application/json" \
        -H "X-API-Key: your-api-key" \
        -d '{
          "name": "user_profile",
          "description": "User profile data contract",
          "owner": "data-team",
          "fields": [
            {
              "name": "user_id",
              "type": "string",
              "required": true,
              "description": "Unique user identifier"
            },
            {
              "name": "email",
              "type": "string",
              "required": true,
              "format": "email"
            },
            {
              "name": "age",
              "type": "integer",
              "constraints": {
                "min": 0,
                "max": 150
              }
            }
          ]
        }'

2. **Retrieve the contract**:

   .. code-block:: bash

      curl http://localhost:8000/api/v1/contracts/user_profile \
        -H "X-API-Key: your-api-key"

3. **List all contracts**:

   .. code-block:: bash

      curl http://localhost:8000/api/v1/contracts \
        -H "X-API-Key: your-api-key"

Next Steps
----------

- :doc:`deployment` - Deploy to production
- :doc:`storage` - Configure storage backends
- :doc:`authentication` - Set up authentication
- :doc:`api-reference` - Full API documentation
