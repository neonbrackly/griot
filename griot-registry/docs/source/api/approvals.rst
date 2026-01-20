Approvals API
=============

The Approvals API manages approval workflows for contracts. Before a contract
can be activated, it may require approval from designated reviewers.

Endpoints
---------

Create Approval Request
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: text

   POST /api/v1/approvals

Create a new approval request for a contract.

**Request Body:**

.. code-block:: json

   {
       "contract_id": "contract-123",
       "approvers": ["user-456", "user-789"],
       "notes": "Please review the new PII fields"
   }

**Parameters:**

- ``contract_id`` (required): The contract requiring approval
- ``approvers`` (required): List of user IDs who must approve
- ``notes`` (optional): Notes for the approvers

**Response:** (201 Created)

.. code-block:: json

   {
       "id": "approval-001",
       "contract_id": "contract-123",
       "requested_by": "user-123",
       "approvers": ["user-456", "user-789"],
       "notes": "Please review the new PII fields",
       "status": "pending",
       "approvals": [],
       "rejections": [],
       "created_at": "2024-01-15T10:00:00Z"
   }

**Approval Status Values:**

- ``pending``: Waiting for approvals
- ``approved``: All approvers have approved
- ``rejected``: At least one approver rejected

**Example:**

.. code-block:: bash

   curl -X POST http://localhost:8000/api/v1/approvals \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer $TOKEN" \
       -d '{
           "contract_id": "contract-123",
           "approvers": ["user-456", "user-789"]
       }'

Get Approval Request
^^^^^^^^^^^^^^^^^^^^

.. code-block:: text

   GET /api/v1/approvals/{request_id}

Retrieve an approval request by ID.

**Path Parameters:**

- ``request_id``: The approval request's unique identifier

**Response:**

.. code-block:: json

   {
       "id": "approval-001",
       "contract_id": "contract-123",
       "requested_by": "user-123",
       "approvers": ["user-456", "user-789"],
       "notes": "Please review the new PII fields",
       "status": "pending",
       "approvals": [
           {
               "approver": "user-456",
               "comments": "Looks good!",
               "approved_at": "2024-01-15T11:00:00Z"
           }
       ],
       "rejections": [],
       "created_at": "2024-01-15T10:00:00Z",
       "updated_at": "2024-01-15T11:00:00Z"
   }

Approve
^^^^^^^

.. code-block:: text

   POST /api/v1/approvals/{request_id}/approve

Approve an approval request.

**Path Parameters:**

- ``request_id``: The approval request's unique identifier

**Request Body:**

.. code-block:: json

   {
       "comments": "Reviewed and approved. Nice work!"
   }

**Authorization:** Only users listed in ``approvers`` can approve.

**Response:**

The updated approval request. When all approvers have approved:
- Status changes to ``approved``
- Contract status is automatically updated to ``active``

**Example:**

.. code-block:: bash

   curl -X POST http://localhost:8000/api/v1/approvals/approval-001/approve \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer $TOKEN" \
       -d '{"comments": "LGTM!"}'

Reject
^^^^^^

.. code-block:: text

   POST /api/v1/approvals/{request_id}/reject

Reject an approval request.

**Path Parameters:**

- ``request_id``: The approval request's unique identifier

**Request Body:**

.. code-block:: json

   {
       "reason": "Missing description for the 'email' field. Please add documentation."
   }

**Authorization:** Only users listed in ``approvers`` can reject.

**Response:**

The updated approval request with status ``rejected``.

**Example:**

.. code-block:: bash

   curl -X POST http://localhost:8000/api/v1/approvals/approval-001/reject \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer $TOKEN" \
       -d '{"reason": "Missing PII classification for email field"}'

List Pending Approvals
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: text

   GET /api/v1/approvals/pending

List pending approval requests.

**Query Parameters:**

.. list-table::
   :header-rows: 1
   :widths: 20 15 65

   * - Parameter
     - Type
     - Description
   * - ``contract_id``
     - string
     - Filter by contract ID
   * - ``my_approvals``
     - boolean
     - Only show requests where current user is an approver

**Response:**

.. code-block:: json

   {
       "items": [
           {
               "id": "approval-001",
               "contract_id": "contract-123",
               "requested_by": "user-123",
               "approvers": ["user-456", "user-789"],
               "status": "pending",
               "created_at": "2024-01-15T10:00:00Z"
           }
       ]
   }

**Example:**

.. code-block:: bash

   # List all pending approvals
   curl http://localhost:8000/api/v1/approvals/pending \
       -H "Authorization: Bearer $TOKEN"

   # List only my pending approvals
   curl "http://localhost:8000/api/v1/approvals/pending?my_approvals=true" \
       -H "Authorization: Bearer $TOKEN"

Approval Request Object
-----------------------

.. code-block:: json

   {
       "id": "string (auto-generated)",
       "contract_id": "string (required)",
       "requested_by": "string (from auth)",
       "approvers": ["string (user IDs)"],
       "notes": "string (optional)",
       "status": "string (pending|approved|rejected)",
       "approvals": [
           {
               "approver": "string (user ID)",
               "comments": "string (optional)",
               "approved_at": "datetime"
           }
       ],
       "rejections": [
           {
               "rejector": "string (user ID)",
               "reason": "string (required)",
               "rejected_at": "datetime"
           }
       ],
       "created_at": "datetime",
       "updated_at": "datetime",
       "completed_at": "datetime (when approved or rejected)"
   }

Approval Workflow
-----------------

.. code-block:: text

   1. Contract created in "draft" status
                    │
                    ▼
   2. Request approval with list of approvers
                    │
                    ▼
   3. Each approver reviews and approves/rejects
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
   4a. All approve        4b. Any rejection
          │                   │
          ▼                   ▼
   5a. Status → "approved" 5b. Status → "rejected"
       Contract → "active"     Contract stays "draft"

Multiple Approvers
------------------

When multiple approvers are required:

- **All must approve**: The request is only approved when every listed approver
  has approved
- **One rejection suffices**: A single rejection marks the entire request as
  rejected
- **Partial approvals are tracked**: You can see who has approved even if the
  request is still pending

Integration Example
-------------------

.. code-block:: python

   from griot_registry import SyncRegistryClient

   with SyncRegistryClient("http://localhost:8000", token=TOKEN) as client:
       # Create a contract
       contract = client.create(my_contract)

       # Request approval
       approval = client.create_approval_request(
           contract_id=contract.id,
           approvers=["lead-engineer", "data-owner"],
           notes="New contract for user analytics"
       )

       print(f"Approval request created: {approval['id']}")

       # Check pending approvals (as an approver)
       pending = client.list_pending_approvals(my_approvals=True)
       for req in pending:
           print(f"Pending: {req['contract_id']}")

       # Approve (as an approver)
       client.approve(approval['id'], comments="Approved after review")
