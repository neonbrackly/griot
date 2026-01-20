Authentication
==============

Griot Registry uses JWT (JSON Web Token) authentication for securing API endpoints.

Authentication Methods
----------------------

JWT Bearer Token
^^^^^^^^^^^^^^^^

JSON Web Tokens (JWT) are the primary authentication method. Tokens are obtained
from the auth endpoint and included in API requests.

**Obtaining a Token**

.. code-block:: bash

   # Get a token with viewer role (read-only access)
   curl -X POST "http://localhost:8000/api/v1/auth/token?user_id=myuser&roles=viewer"

   # Get a token with editor role (create/update contracts)
   curl -X POST "http://localhost:8000/api/v1/auth/token?user_id=myuser&roles=editor"

   # Get a token with admin role (full access)
   curl -X POST "http://localhost:8000/api/v1/auth/token?user_id=myuser&roles=admin"

   # Get a token with multiple roles
   curl -X POST "http://localhost:8000/api/v1/auth/token?user_id=myuser&roles=editor&roles=admin"

Response:

.. code-block:: json

   {
       "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
       "token_type": "bearer"
   }

**Using the Token**

Include the token in the ``Authorization`` header:

.. code-block:: bash

   curl http://localhost:8000/api/v1/contracts \
       -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."

   # Create a contract (requires editor role)
   curl -X POST http://localhost:8000/api/v1/contracts \
       -H "Authorization: Bearer $TOKEN" \
       -H "Content-Type: application/json" \
       -d '{...}'

**Verifying Your Token**

Check the current user information:

.. code-block:: bash

   curl http://localhost:8000/api/v1/auth/me \
       -H "Authorization: Bearer $TOKEN"

Response:

.. code-block:: json

   {
       "id": "myuser",
       "roles": ["editor"],
       "auth_method": "jwt"
   }

Anonymous Access
^^^^^^^^^^^^^^^^

Some endpoints allow anonymous access for read operations:

- ``GET /api/v1/contracts`` - List contracts
- ``GET /api/v1/contracts/{id}`` - Get a contract
- ``GET /api/v1/contracts/{id}/versions`` - List versions
- ``POST /api/v1/contracts/validate`` - Validate a contract

Anonymous users cannot create, update, or delete contracts.

Using Authentication in Python
------------------------------

With the Async Client
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   import httpx
   from griot_registry import RegistryClient

   # Get a token (POST request)
   response = httpx.post(
       "http://localhost:8000/api/v1/auth/token",
       params={"user_id": "myuser", "roles": "editor"}
   )
   token = response.json()["access_token"]

   # Use the token with the async client
   async with RegistryClient(
       "http://localhost:8000",
       token=token
   ) as client:
       contracts, total = await client.list_contracts()
       print(f"Found {total} contracts")

       # Create a contract (requires editor role)
       from griot_core import load_contract_from_dict
       contract = load_contract_from_dict({
           "apiVersion": "v1.0.0",
           "kind": "DataContract",
           "id": "my-contract",
           "name": "my_contract",
           "version": "1.0.0",
           "status": "draft",
           "schema": []
       })
       created = await client.create(contract)

With the Sync Client
^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   import httpx
   from griot_registry import SyncRegistryClient

   # Get a token (POST request)
   response = httpx.post(
       "http://localhost:8000/api/v1/auth/token",
       params={"user_id": "myuser", "roles": "admin"}
   )
   token = response.json()["access_token"]

   # Use the token with the sync client
   with SyncRegistryClient(
       "http://localhost:8000",
       token=token
   ) as client:
       contracts, total = client.list_contracts()
       print(f"Found {total} contracts")

Using Custom Headers
^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from griot_registry import SyncRegistryClient

   # Pass authorization via custom headers
   with SyncRegistryClient(
       "http://localhost:8000",
       headers={"Authorization": "Bearer your-token-here"}
   ) as client:
       contracts, total = client.list_contracts()

User Roles and Permissions
--------------------------

Griot Registry uses role-based access control (RBAC) with the following roles:

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Role
     - Permissions
   * - ``admin``
     - Full access to all operations including approvals and user management
   * - ``editor``
     - Create, read, update contracts; manage validations
   * - ``viewer``
     - Read-only access to contracts and related data

Permission Matrix
^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 40 15 15 15

   * - Operation
     - Admin
     - Editor
     - Viewer
   * - List contracts
     - Yes
     - Yes
     - Yes
   * - Get contract
     - Yes
     - Yes
     - Yes
   * - Create contract
     - Yes
     - Yes
     - No
   * - Update contract
     - Yes
     - Yes
     - No
   * - Delete (deprecate) contract
     - Yes
     - Yes
     - No
   * - Update contract status
     - Yes
     - Yes
     - No
   * - Create approval request
     - Yes
     - Yes
     - No
   * - Approve/reject requests
     - Yes
     - No
     - No
   * - Validate contract
     - Yes
     - Yes
     - Yes

JWT Token Structure
-------------------

JWT tokens contain the following claims:

.. code-block:: json

   {
       "sub": "user-id",
       "roles": ["editor"],
       "type": "access",
       "iat": 1704067200,
       "exp": 1704069000
   }

- ``sub``: User identifier (from ``user_id`` parameter)
- ``roles``: List of user roles
- ``type``: Token type ("access")
- ``iat``: Issued at timestamp
- ``exp``: Expiration timestamp

Tokens are signed using the algorithm configured via ``JWT_ALGORITHM`` (default: HS256)
and the secret key from ``JWT_SECRET_KEY``.

Token Expiration
^^^^^^^^^^^^^^^^

Access tokens expire after 30 minutes by default. This can be configured via
the ``JWT_ACCESS_TOKEN_EXPIRE_MINUTES`` environment variable.

When a token expires, obtain a new one from the auth endpoint.

Security Best Practices
-----------------------

1. **Use HTTPS in production**: Always use TLS to encrypt authentication headers

2. **Use strong JWT secret**: Generate a random key with at least 32 characters:

   .. code-block:: bash

      python -c "import secrets; print(secrets.token_urlsafe(32))"

3. **Set appropriate token expiration**: Balance security and usability

4. **Use minimum required roles**: Request only the roles you need

5. **Don't expose tokens**: Never log or expose JWT tokens in client-side code

6. **Rotate secrets periodically**: Change the JWT secret key regularly

Configuration
-------------

Authentication is configured via environment variables:

.. list-table::
   :header-rows: 1
   :widths: 35 15 50

   * - Variable
     - Default
     - Description
   * - ``JWT_SECRET_KEY``
     - *required*
     - Secret key for signing JWT tokens
   * - ``JWT_ALGORITHM``
     - ``HS256``
     - Algorithm for JWT signing
   * - ``JWT_ACCESS_TOKEN_EXPIRE_MINUTES``
     - ``30``
     - Token expiration time in minutes

Example configuration:

.. code-block:: bash

   export JWT_SECRET_KEY="your-very-secure-secret-key-here"
   export JWT_ALGORITHM="HS256"
   export JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

Auth API Endpoints
------------------

Get Token
^^^^^^^^^

.. code-block:: text

   GET /api/v1/auth/token

Generate a JWT token for API access.

**Query Parameters:**

- ``user_id`` (required): User identifier
- ``roles`` (optional, repeatable): User roles (viewer, editor, admin)

**Response:**

.. code-block:: json

   {
       "access_token": "eyJhbGciOiJIUzI1NiIs...",
       "token_type": "bearer"
   }

**Example:**

.. code-block:: bash

   # Simple token request
   curl -X POST "http://localhost:8000/api/v1/auth/token?user_id=myuser"

   # With roles
   curl -X POST "http://localhost:8000/api/v1/auth/token?user_id=myuser&roles=editor"

   # Multiple roles
   curl -X POST "http://localhost:8000/api/v1/auth/token?user_id=myuser&roles=editor&roles=admin"

Get Current User
^^^^^^^^^^^^^^^^

.. code-block:: text

   GET /api/v1/auth/me

Get information about the current authenticated user.

**Headers:**

- ``Authorization``: Bearer token

**Response:**

.. code-block:: json

   {
       "id": "myuser",
       "roles": ["editor"],
       "auth_method": "jwt"
   }

**Example:**

.. code-block:: bash

   curl http://localhost:8000/api/v1/auth/me \
       -H "Authorization: Bearer $TOKEN"
