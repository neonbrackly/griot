Architecture
============

This document describes the architecture of Griot Registry, including its
components, data model, and design principles.

System Overview
---------------

.. code-block:: text

   ┌─────────────────────────────────────────────────────────────┐
   │                        Clients                               │
   │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
   │  │ Python SDK   │  │  REST API    │  │  Web UI      │      │
   │  │ (Registry    │  │  (curl,      │  │  (future)    │      │
   │  │  Client)     │  │   httpx)     │  │              │      │
   │  └──────────────┘  └──────────────┘  └──────────────┘      │
   └─────────────────────────┬───────────────────────────────────┘
                             │
                             ▼
   ┌─────────────────────────────────────────────────────────────┐
   │                    FastAPI Server                            │
   │  ┌─────────────────────────────────────────────────────┐   │
   │  │                   API Layer                          │   │
   │  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌──────────┐  │   │
   │  │  │Contracts│ │Schemas  │ │Validat- │ │ Search   │  │   │
   │  │  │         │ │         │ │ions/Runs│ │          │  │   │
   │  │  └─────────┘ └─────────┘ └─────────┘ └──────────┘  │   │
   │  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌──────────┐  │   │
   │  │  │Issues   │ │Comments │ │Approvals│ │ Health   │  │   │
   │  │  └─────────┘ └─────────┘ └─────────┘ └──────────┘  │   │
   │  └─────────────────────────────────────────────────────┘   │
   │                            │                                │
   │  ┌─────────────────────────┴───────────────────────────┐   │
   │  │                  Service Layer                       │   │
   │  │  ┌────────────────────┐  ┌────────────────────┐    │   │
   │  │  │  ContractService   │  │ ValidationService  │    │   │
   │  │  │  - CRUD            │  │ - Lint contracts   │    │   │
   │  │  │  - Versioning      │  │ - Validate struct  │    │   │
   │  │  │  - Status mgmt     │  │ - Record results   │    │   │
   │  │  └────────────────────┘  └────────────────────┘    │   │
   │  └─────────────────────────────────────────────────────┘   │
   │                            │                                │
   │  ┌─────────────────────────┴───────────────────────────┐   │
   │  │                Authentication Layer                  │   │
   │  │  ┌────────────┐  ┌────────────┐  ┌──────────────┐  │   │
   │  │  │ JWT Auth   │  │ API Key    │  │ Role-Based   │  │   │
   │  │  │            │  │ Auth       │  │ Access Ctrl  │  │   │
   │  │  └────────────┘  └────────────┘  └──────────────┘  │   │
   │  └─────────────────────────────────────────────────────┘   │
   │                            │                                │
   │  ┌─────────────────────────┴───────────────────────────┐   │
   │  │                  Storage Layer                       │   │
   │  │  ┌────────────────────────────────────────────────┐ │   │
   │  │  │              Repository Pattern                 │ │   │
   │  │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐      │ │   │
   │  │  │  │Contracts │ │Schemas   │ │Validat-  │      │ │   │
   │  │  │  │Repository│ │Catalog   │ │ions Repo │      │ │   │
   │  │  │  └──────────┘ └──────────┘ └──────────┘      │ │   │
   │  │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐      │ │   │
   │  │  │  │Runs Repo │ │Issues    │ │Approvals │      │ │   │
   │  │  │  │          │ │Repository│ │Repository│      │ │   │
   │  │  │  └──────────┘ └──────────┘ └──────────┘      │ │   │
   │  │  └────────────────────────────────────────────────┘ │   │
   │  └─────────────────────────────────────────────────────┘   │
   └─────────────────────────────┬───────────────────────────────┘
                                 │
                                 ▼
   ┌─────────────────────────────────────────────────────────────┐
   │                        MongoDB                               │
   │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        │
   │  │  contracts   │ │   versions   │ │schema_catalog│        │
   │  └──────────────┘ └──────────────┘ └──────────────┘        │
   │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        │
   │  │ validations  │ │    runs      │ │   issues     │        │
   │  └──────────────┘ └──────────────┘ └──────────────┘        │
   │  ┌──────────────┐ ┌──────────────┐                         │
   │  │  comments    │ │  approvals   │                         │
   │  └──────────────┘ └──────────────┘                         │
   └─────────────────────────────────────────────────────────────┘

Core Components
---------------

API Layer
^^^^^^^^^

The API layer consists of FastAPI routers that handle HTTP requests and
responses. Each router focuses on a specific resource type:

- **contracts**: Core CRUD operations for data contracts
- **schemas**: Schema catalog queries and cross-contract discovery
- **validations**: Validation record management and statistics
- **runs**: Pipeline run tracking
- **issues**: Issue management for data quality tracking
- **comments**: Collaboration through threaded discussions
- **approvals**: Workflow management for contract activation
- **search**: Full-text search across contracts

Service Layer
^^^^^^^^^^^^^

Services contain business logic and orchestrate operations:

- **ContractService**: Handles contract validation, versioning, and status
  transitions. Uses griot-core for contract parsing and validation.

- **ValidationService**: Wraps griot-core's linting and validation functions.
  Determines if validation issues should block operations based on settings.

Authentication Layer
^^^^^^^^^^^^^^^^^^^^

The auth layer supports multiple authentication methods:

- **JWT**: Stateless tokens for user sessions with configurable expiration
- **API Keys**: Long-lived keys for service-to-service communication
- **RBAC**: Role-based access control (admin, editor, viewer, service)

Storage Layer
^^^^^^^^^^^^^

The storage layer implements the repository pattern with MongoDB:

- **Abstract repositories**: Define interfaces for all storage operations
- **MongoDB implementation**: Concrete implementation using motor (async driver)
- **Collections**: Separate collections for each resource type

Data Model
----------

Contracts
^^^^^^^^^

.. code-block:: text

   Contract Document
   ├── id (string, unique)
   ├── name (string)
   ├── version (string, semver)
   ├── description (string)
   ├── owner (string)
   ├── status (enum: draft, active, deprecated, retired)
   ├── schemas[] (embedded documents)
   │   ├── name (string)
   │   ├── description (string)
   │   └── fields[] (embedded documents)
   │       ├── name (string)
   │       ├── data_type (string)
   │       ├── required (boolean)
   │       ├── pii (boolean)
   │       └── constraints (object)
   ├── sla (embedded document)
   │   ├── freshness (string)
   │   └── availability (number)
   ├── metadata (object)
   ├── created_at (datetime)
   ├── updated_at (datetime)
   └── created_by (string)

Schema Catalog
^^^^^^^^^^^^^^

A denormalized collection for efficient cross-contract queries:

.. code-block:: text

   Schema Catalog Entry
   ├── id (string, unique)
   ├── contract_id (string, indexed)
   ├── contract_name (string)
   ├── contract_version (string)
   ├── schema_name (string, indexed)
   ├── description (string)
   ├── fields[] (flattened field info)
   ├── field_count (integer)
   ├── has_pii (boolean, indexed)
   ├── pii_fields[] (string array)
   └── indexed_at (datetime)

Contract Versions
^^^^^^^^^^^^^^^^^

Historical versions stored separately:

.. code-block:: text

   Contract Version
   ├── id (string, unique)
   ├── contract_id (string, indexed)
   ├── version (string)
   ├── contract_data (complete contract snapshot)
   ├── change_notes (string)
   ├── created_at (datetime)
   └── created_by (string)

Design Principles
-----------------

1. **Separation of Concerns**: Each layer has a specific responsibility
2. **Repository Pattern**: Storage abstraction enables testing and future backends
3. **griot-core Integration**: Business logic for contracts lives in griot-core
4. **Async-First**: All I/O operations are async for scalability
5. **Stateless**: No server-side session state; all state in MongoDB and tokens
6. **Extensibility**: New resource types can be added via new repositories

Scalability Considerations
--------------------------

- **Horizontal scaling**: Stateless servers can scale horizontally behind a load
  balancer
- **MongoDB indexes**: Full-text indexes on contract content for fast search
- **Schema catalog**: Denormalized for O(1) cross-contract lookups
- **Connection pooling**: motor handles connection pooling automatically

Security Model
--------------

- **Authentication**: JWT tokens or API keys required for most operations
- **Authorization**: Role-based with granular permissions per operation
- **Input validation**: All inputs validated via Pydantic models
- **Contract validation**: griot-core validates contracts before storage
