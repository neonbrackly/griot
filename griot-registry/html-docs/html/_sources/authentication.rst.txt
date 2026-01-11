Authentication
==============

griot-registry supports multiple authentication methods to secure API access.

.. contents:: Table of Contents
   :local:
   :depth: 2

Authentication Overview
-----------------------

.. list-table::
   :header-rows: 1
   :widths: 25 35 40

   * - Method
     - Best For
     - Configuration
   * - **None**
     - Development only
     - ``GRIOT_AUTH_ENABLED=false``
   * - **API Key**
     - Service-to-service, CI/CD
     - ``GRIOT_API_KEYS=[...]``
   * - **OAuth2/OIDC**
     - User authentication, SSO
     - ``GRIOT_OIDC_ISSUER=...``

Disabling Authentication
------------------------

For local development, authentication can be disabled:

.. code-block:: bash

   export GRIOT_AUTH_ENABLED=false

.. warning::

   Never disable authentication in production environments.

API Key Authentication
----------------------

Simple token-based authentication for service accounts and automation.

Configuration
~~~~~~~~~~~~~

.. code-block:: bash

   export GRIOT_AUTH_ENABLED=true
   export GRIOT_API_KEYS='["sk_live_abc123", "sk_live_def456"]'

Each key in the array is a valid API key. Generate secure keys:

.. code-block:: bash

   # Generate a random API key
   openssl rand -hex 32
   # Output: a1b2c3d4e5f6...

Using API Keys
~~~~~~~~~~~~~~

Include the key in the ``X-API-Key`` header:

.. code-block:: bash

   curl -X GET http://localhost:8000/api/v1/contracts \
     -H "X-API-Key: sk_live_abc123"

Or use the ``Authorization`` header with Bearer scheme:

.. code-block:: bash

   curl -X GET http://localhost:8000/api/v1/contracts \
     -H "Authorization: Bearer sk_live_abc123"

Python Client Example
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import httpx

   client = httpx.Client(
       base_url="http://localhost:8000/api/v1",
       headers={"X-API-Key": "sk_live_abc123"}
   )

   response = client.get("/contracts")
   contracts = response.json()

API Key Best Practices
~~~~~~~~~~~~~~~~~~~~~~

1. **Rotate keys regularly**: Replace keys every 90 days
2. **Use separate keys**: Different keys for different services/environments
3. **Store securely**: Use secrets management (Vault, AWS Secrets Manager)
4. **Monitor usage**: Log which key is used for audit trails
5. **Revoke compromised keys**: Remove from array immediately if exposed

OAuth2/OIDC Authentication
--------------------------

Enterprise-grade authentication using OpenID Connect providers.

Installation
~~~~~~~~~~~~

.. code-block:: bash

   pip install griot-registry[oauth]

Configuration
~~~~~~~~~~~~~

.. code-block:: bash

   export GRIOT_AUTH_ENABLED=true
   export GRIOT_OIDC_ISSUER=https://your-provider.com
   export GRIOT_OIDC_AUDIENCE=griot-registry
   export GRIOT_OIDC_ALGORITHMS='["RS256"]'

Provider-Specific Setup
~~~~~~~~~~~~~~~~~~~~~~~

**Okta**

.. code-block:: bash

   export GRIOT_OIDC_ISSUER=https://your-org.okta.com/oauth2/default
   export GRIOT_OIDC_AUDIENCE=api://griot

1. Create an API application in Okta Admin Console
2. Note the Issuer URI from Authorization Servers
3. Set the audience to match your API identifier
4. Configure scopes: ``openid``, ``profile``, ``griot:read``, ``griot:write``

**Auth0**

.. code-block:: bash

   export GRIOT_OIDC_ISSUER=https://your-tenant.auth0.com/
   export GRIOT_OIDC_AUDIENCE=https://api.griot.your-domain.com

1. Create an API in Auth0 Dashboard
2. Set the identifier as your audience
3. Create a Machine-to-Machine application
4. Authorize the application to access the API

**Keycloak**

.. code-block:: bash

   export GRIOT_OIDC_ISSUER=https://keycloak.your-domain.com/realms/griot
   export GRIOT_OIDC_AUDIENCE=griot-registry

1. Create a new realm called ``griot``
2. Create a client called ``griot-registry``
3. Set Access Type to ``confidential``
4. Enable Service Accounts

**Azure AD**

.. code-block:: bash

   export GRIOT_OIDC_ISSUER=https://login.microsoftonline.com/{tenant-id}/v2.0
   export GRIOT_OIDC_AUDIENCE=api://griot-registry

1. Register an application in Azure Portal
2. Expose an API and define scopes
3. Configure API permissions for client apps

Using OAuth2 Tokens
~~~~~~~~~~~~~~~~~~~

Obtain an access token from your OIDC provider and include it:

.. code-block:: bash

   # Get token (example with client credentials)
   TOKEN=$(curl -X POST https://your-provider.com/oauth/token \
     -d "grant_type=client_credentials" \
     -d "client_id=YOUR_CLIENT_ID" \
     -d "client_secret=YOUR_CLIENT_SECRET" \
     -d "audience=griot-registry" \
     | jq -r '.access_token')

   # Use token
   curl -X GET http://localhost:8000/api/v1/contracts \
     -H "Authorization: Bearer $TOKEN"

Role-Based Access Control
-------------------------

griot-registry supports role-based access control (RBAC) with three built-in roles.

Roles
~~~~~

.. list-table::
   :header-rows: 1
   :widths: 20 30 50

   * - Role
     - Claim Value
     - Permissions
   * - **Admin**
     - ``griot:admin``
     - Full access, user management, settings
   * - **Editor**
     - ``griot:editor``
     - Create, update, delete contracts
   * - **Viewer**
     - ``griot:viewer``
     - Read-only access to contracts

Configuring Roles
~~~~~~~~~~~~~~~~~

Roles are read from the JWT claims. Configure the claim name:

.. code-block:: bash

   export GRIOT_OIDC_ROLES_CLAIM=roles
   # Or for nested claims
   export GRIOT_OIDC_ROLES_CLAIM=resource_access.griot.roles

JWT Claims Example
~~~~~~~~~~~~~~~~~~

.. code-block:: json

   {
     "sub": "user123",
     "email": "user@example.com",
     "roles": ["griot:editor"],
     "exp": 1704931200
   }

Endpoint Permissions
~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 40 20 20 20

   * - Endpoint
     - Viewer
     - Editor
     - Admin
   * - ``GET /contracts``
     - Yes
     - Yes
     - Yes
   * - ``GET /contracts/{id}``
     - Yes
     - Yes
     - Yes
   * - ``POST /contracts``
     - No
     - Yes
     - Yes
   * - ``PUT /contracts/{id}``
     - No
     - Yes
     - Yes
   * - ``DELETE /contracts/{id}``
     - No
     - No
     - Yes
   * - ``POST /approvals/{id}/decision``
     - No
     - Yes
     - Yes
   * - ``GET /admin/*``
     - No
     - No
     - Yes

Custom Role Requirements
~~~~~~~~~~~~~~~~~~~~~~~~

Protect endpoints with specific roles:

.. code-block:: python

   from fastapi import Depends
   from griot_registry.auth.oauth import require_role, AdminRole, EditorRole

   @router.delete("/contracts/{contract_id}")
   async def delete_contract(
       contract_id: str,
       _: None = Depends(require_role(AdminRole))
   ):
       # Only admins can delete
       ...

   @router.post("/contracts")
   async def create_contract(
       contract: ContractCreate,
       _: None = Depends(require_role(EditorRole))
   ):
       # Editors and admins can create
       ...

Scope-Based Access Control
--------------------------

For finer-grained control, use OAuth2 scopes.

Configuring Scopes
~~~~~~~~~~~~~~~~~~

Define required scopes for operations:

.. code-block:: bash

   export GRIOT_REQUIRED_SCOPES='{"read": "griot:read", "write": "griot:write", "admin": "griot:admin"}'

Using Scopes
~~~~~~~~~~~~

.. code-block:: python

   from griot_registry.auth.oauth import require_scope

   @router.get("/contracts")
   async def list_contracts(
       _: None = Depends(require_scope("griot:read"))
   ):
       ...

   @router.post("/contracts")
   async def create_contract(
       _: None = Depends(require_scope("griot:write"))
   ):
       ...

Security Headers
----------------

griot-registry sets security headers by default:

.. code-block:: text

   X-Content-Type-Options: nosniff
   X-Frame-Options: DENY
   X-XSS-Protection: 1; mode=block
   Strict-Transport-Security: max-age=31536000; includeSubDomains

Configure additional headers:

.. code-block:: bash

   export GRIOT_SECURITY_HEADERS='{"X-Custom-Header": "value"}'

CORS Configuration
------------------

Configure Cross-Origin Resource Sharing for web clients:

.. code-block:: bash

   # Allow specific origins
   export GRIOT_CORS_ORIGINS='["https://hub.griot.io", "http://localhost:3000"]'

   # Allow all origins (development only!)
   export GRIOT_CORS_ORIGINS='["*"]'

   # Additional CORS settings
   export GRIOT_CORS_ALLOW_CREDENTIALS=true
   export GRIOT_CORS_ALLOW_METHODS='["GET", "POST", "PUT", "DELETE"]'
   export GRIOT_CORS_ALLOW_HEADERS='["*"]'

Troubleshooting
---------------

**"401 Unauthorized" with valid API key**

- Verify the key is in ``GRIOT_API_KEYS`` array
- Check for whitespace in the key
- Ensure ``GRIOT_AUTH_ENABLED=true``

**"401 Unauthorized" with valid JWT**

- Check token expiration (``exp`` claim)
- Verify issuer matches ``GRIOT_OIDC_ISSUER``
- Confirm audience matches ``GRIOT_OIDC_AUDIENCE``
- Test token at https://jwt.io

**"403 Forbidden" - insufficient permissions**

- Check user's roles in JWT claims
- Verify roles claim path (``GRIOT_OIDC_ROLES_CLAIM``)
- Ensure user has required role for endpoint

**CORS errors in browser**

- Add your frontend origin to ``GRIOT_CORS_ORIGINS``
- Check for protocol mismatch (http vs https)
- Verify credentials setting matches frontend
