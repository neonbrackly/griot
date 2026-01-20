Configuration
=============

Griot Registry is configured using environment variables. This page documents
all available configuration options.

Environment Variables
---------------------

Server Settings
^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 30 15 55

   * - Variable
     - Default
     - Description
   * - ``HOST``
     - ``0.0.0.0``
     - Host address to bind the server to
   * - ``PORT``
     - ``8000``
     - Port number for the server
   * - ``DEBUG``
     - ``false``
     - Enable debug mode with auto-reload
   * - ``LOG_LEVEL``
     - ``INFO``
     - Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
   * - ``API_V1_PREFIX``
     - ``/api/v1``
     - Prefix for all API v1 endpoints
   * - ``CORS_ORIGINS``
     - ``["*"]``
     - Allowed CORS origins (JSON array or comma-separated)

MongoDB Settings
^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 30 15 55

   * - Variable
     - Default
     - Description
   * - ``MONGODB_URI``
     - ``mongodb://localhost:27017``
     - MongoDB connection URI
   * - ``MONGODB_DATABASE``
     - ``griot_registry``
     - Database name to use

JWT Authentication Settings
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 30 15 55

   * - Variable
     - Default
     - Description
   * - ``JWT_SECRET_KEY``
     - *required*
     - Secret key for signing JWT tokens (use a strong random key)
   * - ``JWT_ALGORITHM``
     - ``HS256``
     - Algorithm for JWT signing (HS256, HS384, HS512, RS256, etc.)
   * - ``JWT_ACCESS_TOKEN_EXPIRE_MINUTES``
     - ``30``
     - Access token expiration time in minutes
   * - ``JWT_REFRESH_TOKEN_EXPIRE_DAYS``
     - ``7``
     - Refresh token expiration time in days

API Key Settings
^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 30 15 55

   * - Variable
     - Default
     - Description
   * - ``API_KEYS``
     - ``[]``
     - List of valid API keys (JSON array)
   * - ``API_KEY_HEADER``
     - ``X-API-Key``
     - Header name for API key authentication

Validation Settings
^^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 30 15 55

   * - Variable
     - Default
     - Description
   * - ``VALIDATE_ON_CREATE``
     - ``true``
     - Validate contracts on creation
   * - ``VALIDATE_ON_UPDATE``
     - ``true``
     - Validate contracts on update
   * - ``BLOCK_ON_LINT_ERRORS``
     - ``false``
     - Block operations when lint errors are found
   * - ``BLOCK_ON_LINT_WARNINGS``
     - ``false``
     - Block operations when lint warnings are found

Configuration File
------------------

You can also use a ``.env`` file in your working directory:

.. code-block:: bash
   :caption: .env

   # Server
   HOST=0.0.0.0
   PORT=8000
   DEBUG=false
   LOG_LEVEL=INFO

   # MongoDB
   MONGODB_URI=mongodb://localhost:27017
   MONGODB_DATABASE=griot_registry

   # JWT Authentication
   JWT_SECRET_KEY=your-super-secret-key-change-in-production
   JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
   JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

   # API Keys (JSON array)
   API_KEYS=["key1", "key2"]

   # Validation
   VALIDATE_ON_CREATE=true
   VALIDATE_ON_UPDATE=true
   BLOCK_ON_LINT_ERRORS=false

Programmatic Configuration
--------------------------

When using the registry programmatically, you can create a ``Settings`` instance:

.. code-block:: python

   from griot_registry.config import Settings
   from griot_registry.server import create_app

   settings = Settings(
       mongodb_uri="mongodb://localhost:27017",
       mongodb_database="griot_registry",
       jwt_secret_key="your-secret-key",
       debug=True,
       log_level="DEBUG",
   )

   app = create_app(settings)

Docker Configuration
--------------------

When running with Docker, pass environment variables:

.. code-block:: bash

   docker run -d \
       --name griot-registry \
       -p 8000:8000 \
       -e MONGODB_URI="mongodb://host.docker.internal:27017" \
       -e MONGODB_DATABASE="griot_registry" \
       -e JWT_SECRET_KEY="your-secret-key" \
       griot-registry:latest

Or use a Docker Compose file:

.. code-block:: yaml
   :caption: docker-compose.yml

   version: '3.8'

   services:
     registry:
       image: griot-registry:latest
       ports:
         - "8000:8000"
       environment:
         MONGODB_URI: mongodb://mongodb:27017
         MONGODB_DATABASE: griot_registry
         JWT_SECRET_KEY: ${JWT_SECRET_KEY}
       depends_on:
         - mongodb

     mongodb:
       image: mongo:7
       ports:
         - "27017:27017"
       volumes:
         - mongodb_data:/data/db

   volumes:
     mongodb_data:

Production Recommendations
--------------------------

For production deployments, follow these recommendations:

1. **Use a strong JWT secret**: Generate a random key with at least 32 characters:

   .. code-block:: bash

      python -c "import secrets; print(secrets.token_urlsafe(32))"

2. **Enable TLS**: Use a reverse proxy (nginx, traefik) with TLS termination

3. **Restrict CORS origins**: Set ``CORS_ORIGINS`` to your specific domains

4. **Use MongoDB authentication**: Include credentials in ``MONGODB_URI``

5. **Set appropriate token expiration**: Balance security and user experience

6. **Enable monitoring**: Use the ``/api/v1/health`` endpoints for health checks
