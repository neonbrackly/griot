Search API
==========

The Search API provides full-text search capabilities across all contracts in
the registry.

Endpoints
---------

Basic Search
^^^^^^^^^^^^

.. code-block:: text

   GET /api/v1/search

Search across all contracts using full-text search.

**Query Parameters:**

.. list-table::
   :header-rows: 1
   :widths: 20 15 65

   * - Parameter
     - Type
     - Description
   * - ``query``
     - string
     - Search query (required, min 1 character)
   * - ``limit``
     - int
     - Maximum results to return (1-100, default: 50)

**Search Scope:**

The search queries across:

- Contract names
- Contract descriptions
- Schema names
- Field names
- Field descriptions

**Response:**

.. code-block:: json

   {
       "query": "user event",
       "items": [
           {
               "contract_id": "contract-123",
               "contract_name": "user-events",
               "version": "1.0.0",
               "status": "active",
               "score": 0.95,
               "match_type": "name",
               "snippet": "User activity **events** contract"
           },
           {
               "contract_id": "contract-456",
               "contract_name": "analytics-events",
               "version": "2.1.0",
               "status": "active",
               "score": 0.72,
               "match_type": "schema",
               "snippet": "Contains **UserEvent** schema"
           }
       ],
       "total": 2
   }

**Response Fields:**

- ``score``: Relevance score (0-1)
- ``match_type``: Where the match was found (name, description, schema, field)
- ``snippet``: Text excerpt showing match context with highlights

**Example:**

.. code-block:: bash

   # Search for contracts related to users
   curl "http://localhost:8000/api/v1/search?query=user"

   # Search for PII-related contracts
   curl "http://localhost:8000/api/v1/search?query=email%20pii"

Advanced Search
^^^^^^^^^^^^^^^

.. code-block:: text

   GET /api/v1/search/advanced

Advanced search combining text search with structured filters.

**Query Parameters:**

.. list-table::
   :header-rows: 1
   :widths: 20 15 65

   * - Parameter
     - Type
     - Description
   * - ``query``
     - string
     - Text search query (optional)
   * - ``name``
     - string
     - Filter by contract name (partial match)
   * - ``status``
     - string
     - Filter by contract status
   * - ``schema_name``
     - string
     - Filter by schema name
   * - ``owner``
     - string
     - Filter by owner/team
   * - ``has_pii``
     - boolean
     - Filter by PII presence
   * - ``limit``
     - int
     - Maximum results (default: 50)

**Response:**

Same format as basic search.

**Examples:**

.. code-block:: bash

   # Find active contracts with PII
   curl "http://localhost:8000/api/v1/search/advanced?status=active&has_pii=true"

   # Find contracts owned by data-team with 'event' in the name
   curl "http://localhost:8000/api/v1/search/advanced?owner=data-team&name=event"

   # Combine text search with filters
   curl "http://localhost:8000/api/v1/search/advanced?query=user&status=active&has_pii=false"

Search Tips
-----------

Effective Queries
^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Query Type
     - Example
   * - Single word
     - ``user`` - finds contracts with "user" anywhere
   * - Multiple words
     - ``user event`` - finds contracts matching both terms
   * - Field names
     - ``email`` - finds contracts with fields named "email"
   * - Data types
     - ``timestamp`` - finds contracts with timestamp fields

Filtering Strategies
^^^^^^^^^^^^^^^^^^^^

1. **Start broad, then filter**: Begin with a text search, then add filters
   to narrow results

2. **Use status filter**: Filter by ``status=active`` to find production
   contracts

3. **Find sensitive data**: Use ``has_pii=true`` to locate contracts with
   personally identifiable information

4. **Team discovery**: Use ``owner=team-name`` to find all contracts owned
   by a team

Python Client Examples
----------------------

.. code-block:: python

   from griot_registry import SyncRegistryClient

   with SyncRegistryClient("http://localhost:8000") as client:
       # Basic search
       results = client.search("user events")
       for hit in results:
           print(f"{hit['contract_name']}: {hit['score']:.2f}")

       # Advanced search
       results = client.search_advanced(
           query="analytics",
           status="active",
           has_pii=False
       )

       # Find schemas
       schemas = client.find_schemas(has_pii=True)
       print(f"Found {len(schemas)} schemas with PII")

Search Response Object
----------------------

.. code-block:: json

   {
       "query": "string (the search query)",
       "items": [
           {
               "contract_id": "string",
               "contract_name": "string",
               "version": "string",
               "status": "string",
               "score": "number (0-1)",
               "match_type": "string (name|description|schema|field)",
               "snippet": "string (highlighted excerpt)"
           }
       ],
       "total": "integer (total matching results)"
   }

Indexing
--------

The search index is automatically updated when:

- A contract is created
- A contract is updated
- A contract is deleted

For optimal search performance, MongoDB text indexes are created on:

- ``name``
- ``description``
- ``schemas.name``
- ``schemas.description``
- ``schemas.fields.name``
- ``schemas.fields.description``

To manually rebuild indexes (admin only):

.. code-block:: bash

   curl -X POST http://localhost:8000/api/v1/schemas/rebuild \
       -H "Authorization: Bearer $ADMIN_TOKEN"
