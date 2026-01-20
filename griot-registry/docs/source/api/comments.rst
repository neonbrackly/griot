Comments API
============

The Comments API enables collaboration through threaded discussions on contracts.
Comments can be associated with specific sections or fields within a contract.

Endpoints
---------

Create Comment
^^^^^^^^^^^^^^

.. code-block:: text

   POST /api/v1/comments

Create a new comment on a contract.

**Request Body:**

.. code-block:: json

   {
       "contract_id": "contract-123",
       "content": "Should we add validation for email format?",
       "thread_id": null,
       "section": "schemas",
       "field_path": "UserEvent.email"
   }

**Parameters:**

- ``contract_id`` (required): The contract to comment on
- ``content`` (required): Comment text (1-5000 characters)
- ``thread_id`` (optional): ID of parent comment for replies
- ``section`` (optional): Contract section (schemas, sla, metadata, etc.)
- ``field_path`` (optional): Specific field being discussed

**Response:** (201 Created)

.. code-block:: json

   {
       "id": "comment-456",
       "contract_id": "contract-123",
       "content": "Should we add validation for email format?",
       "thread_id": null,
       "section": "schemas",
       "field_path": "UserEvent.email",
       "reactions": {},
       "created_at": "2024-01-15T10:30:00Z",
       "created_by": "user-789"
   }

**Example:**

.. code-block:: bash

   # Create a new comment
   curl -X POST http://localhost:8000/api/v1/comments \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer $TOKEN" \
       -d '{
           "contract_id": "contract-123",
           "content": "Should we add validation for email format?"
       }'

   # Reply to a comment
   curl -X POST http://localhost:8000/api/v1/comments \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer $TOKEN" \
       -d '{
           "contract_id": "contract-123",
           "content": "Yes, we should use RFC 5322 validation",
           "thread_id": "comment-456"
       }'

Get Comment
^^^^^^^^^^^

.. code-block:: text

   GET /api/v1/comments/{comment_id}

Retrieve a specific comment by ID.

**Path Parameters:**

- ``comment_id``: The comment's unique identifier

**Response:**

Full comment object.

Update Comment
^^^^^^^^^^^^^^

.. code-block:: text

   PATCH /api/v1/comments/{comment_id}

Update a comment's content.

**Path Parameters:**

- ``comment_id``: The comment's unique identifier

**Request Body:**

.. code-block:: json

   {
       "content": "Updated comment text"
   }

**Response:**

The updated comment object with ``updated_at`` and ``updated_by`` fields set.

Delete Comment
^^^^^^^^^^^^^^

.. code-block:: text

   DELETE /api/v1/comments/{comment_id}

Delete a comment.

**Path Parameters:**

- ``comment_id``: The comment's unique identifier

**Response:** 204 No Content

Add Reaction
^^^^^^^^^^^^

.. code-block:: text

   POST /api/v1/comments/{comment_id}/reactions

Add a reaction to a comment.

**Path Parameters:**

- ``comment_id``: The comment's unique identifier

**Request Body:**

.. code-block:: json

   {
       "reaction": "thumbsup"
   }

**Supported Reactions:**

- ``thumbsup`` / ``thumbsdown``
- ``heart``
- ``eyes``
- ``rocket``
- ``thinking``

**Response:**

The comment with updated reactions:

.. code-block:: json

   {
       "id": "comment-456",
       "reactions": {
           "thumbsup": ["user-789", "user-012"],
           "heart": ["user-345"]
       }
   }

List Contract Comments
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: text

   GET /api/v1/contracts/{contract_id}/comments

List all comments for a contract.

**Path Parameters:**

- ``contract_id``: The contract's unique identifier

**Query Parameters:**

.. list-table::
   :header-rows: 1
   :widths: 20 15 65

   * - Parameter
     - Type
     - Description
   * - ``thread_id``
     - string
     - Filter to a specific thread (get replies)
   * - ``limit``
     - int
     - Maximum comments to return (default: 50)
   * - ``offset``
     - int
     - Number to skip (default: 0)

**Response:**

.. code-block:: json

   {
       "items": [
           {
               "id": "comment-456",
               "content": "Should we add validation?",
               "thread_id": null,
               "created_at": "2024-01-15T10:30:00Z",
               "created_by": "user-789",
               "reactions": {"thumbsup": ["user-012"]}
           },
           {
               "id": "comment-457",
               "content": "Yes, use RFC 5322",
               "thread_id": "comment-456",
               "created_at": "2024-01-15T11:00:00Z",
               "created_by": "user-012"
           }
       ],
       "total": 2,
       "limit": 50,
       "offset": 0
   }

**Example:**

.. code-block:: bash

   # Get all comments for a contract
   curl http://localhost:8000/api/v1/contracts/contract-123/comments

   # Get replies to a specific comment
   curl "http://localhost:8000/api/v1/contracts/contract-123/comments?thread_id=comment-456"

Comment Object Schema
---------------------

.. code-block:: json

   {
       "id": "string (auto-generated)",
       "contract_id": "string (required)",
       "content": "string (required, 1-5000 chars)",
       "thread_id": "string (optional, parent comment ID)",
       "section": "string (optional)",
       "field_path": "string (optional)",
       "reactions": {
           "reaction_name": ["user_id_1", "user_id_2"]
       },
       "created_at": "datetime",
       "updated_at": "datetime (if edited)",
       "created_by": "string",
       "updated_by": "string (if edited)"
   }

Threading Model
---------------

Comments support threading for organized discussions:

.. code-block:: text

   Comment A (thread_id: null)      <- Root comment
   ├── Comment B (thread_id: A)     <- Reply to A
   ├── Comment C (thread_id: A)     <- Another reply to A
   └── Comment D (thread_id: A)     <- Third reply

To create a thread:

1. Create a root comment with ``thread_id: null``
2. Reply by setting ``thread_id`` to the root comment's ID
3. All replies share the same ``thread_id`` (flat threading)

Field-Specific Comments
-----------------------

Comments can be associated with specific fields for precise discussions:

.. code-block:: python

   from griot_registry import SyncRegistryClient

   with SyncRegistryClient("http://localhost:8000") as client:
       # Comment on a specific field
       client.create_comment(
           contract_id="contract-123",
           content="This field should be marked as PII",
           section="schemas",
           field_path="UserEvent.email"
       )

       # Comment on the SLA section
       client.create_comment(
           contract_id="contract-123",
           content="Can we tighten the freshness SLA to 30 minutes?",
           section="sla"
       )
