Storage Backends
================

griot-registry supports three storage backends for persisting contracts and validation history.
Choose based on your requirements for versioning, scalability, and operational complexity.

.. contents:: Table of Contents
   :local:
   :depth: 2

Backend Comparison
------------------

.. list-table::
   :header-rows: 1
   :widths: 20 25 25 30

   * - Feature
     - Filesystem
     - Git
     - PostgreSQL
   * - **Best For**
     - Development, small teams
     - Version control, audit trails
     - Production, large scale
   * - **Versioning**
     - Manual
     - Automatic (commits)
     - Automatic (table)
   * - **Search**
     - Basic (filename)
     - Basic
     - Full-text, advanced
   * - **Scalability**
     - Limited
     - Limited
     - High
   * - **Setup Complexity**
     - Low
     - Medium
     - Medium
   * - **Dependencies**
     - None
     - GitPython
     - SQLAlchemy, asyncpg

Filesystem Backend
------------------

The simplest backend, storing contracts as YAML files on disk.

Configuration
~~~~~~~~~~~~~

.. code-block:: bash

   export GRIOT_STORAGE_BACKEND=filesystem
   export GRIOT_STORAGE_PATH=/var/lib/griot/contracts

Directory Structure
~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   /var/lib/griot/contracts/
   ├── user_profile/
   │   ├── contract.yaml          # Current version
   │   ├── metadata.json          # Contract metadata
   │   └── validations/
   │       ├── 2024-01-10_001.json
   │       └── 2024-01-10_002.json
   ├── order_events/
   │   ├── contract.yaml
   │   ├── metadata.json
   │   └── validations/
   └── .index.json                # Search index

Usage Notes
~~~~~~~~~~~

- **Pros**: Zero dependencies, easy to backup, human-readable files
- **Cons**: No built-in versioning, limited search, not suitable for high concurrency
- **Recommended for**: Local development, single-user scenarios, prototyping

Example Setup
~~~~~~~~~~~~~

.. code-block:: python

   from griot_registry.config import Settings
   from griot_registry.server import create_app

   settings = Settings(
       storage_backend="filesystem",
       storage_path="/var/lib/griot/contracts"
   )
   app = create_app(settings)

Git Backend
-----------

Stores contracts in a Git repository with automatic commits for every change.

Installation
~~~~~~~~~~~~

.. code-block:: bash

   pip install griot-registry[git]

Configuration
~~~~~~~~~~~~~

.. code-block:: bash

   export GRIOT_STORAGE_BACKEND=git
   export GRIOT_GIT_REPO_PATH=/var/lib/griot/contracts-repo
   export GRIOT_GIT_BRANCH=main

   # Optional: Remote repository
   export GRIOT_GIT_REMOTE_URL=git@github.com:your-org/contracts.git
   export GRIOT_GIT_AUTO_PUSH=true

Repository Structure
~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   /var/lib/griot/contracts-repo/
   ├── .git/
   ├── contracts/
   │   ├── user_profile/
   │   │   ├── contract.yaml
   │   │   └── metadata.json
   │   └── order_events/
   │       ├── contract.yaml
   │       └── metadata.json
   └── validations/
       └── user_profile/
           └── 2024-01-10_001.json

Git Commit Behavior
~~~~~~~~~~~~~~~~~~~

Every contract change creates a commit:

.. code-block:: text

   commit abc1234
   Author: griot-registry <registry@griot.io>
   Date:   Wed Jan 10 14:30:00 2024

       Update contract: user_profile v2.1.0

       Changes:
       - Added field: phone_number
       - Modified constraint: email (added format validation)

Version Tags
~~~~~~~~~~~~

Semantic versions are automatically tagged:

.. code-block:: bash

   git tag
   # user_profile/v1.0.0
   # user_profile/v1.1.0
   # user_profile/v2.0.0
   # order_events/v1.0.0

Usage Notes
~~~~~~~~~~~

- **Pros**: Full version history, blame/diff support, can push to remote
- **Cons**: Performance degrades with large repos, requires Git knowledge
- **Recommended for**: Teams requiring audit trails, GitOps workflows

Example Setup
~~~~~~~~~~~~~

.. code-block:: python

   from griot_registry.config import Settings
   from griot_registry.server import create_app

   settings = Settings(
       storage_backend="git",
       git_repo_path="/var/lib/griot/contracts-repo",
       git_branch="main",
       git_remote_url="git@github.com:your-org/contracts.git",
       git_auto_push=True
   )
   app = create_app(settings)

Initializing a New Repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Initialize empty repo
   mkdir -p /var/lib/griot/contracts-repo
   cd /var/lib/griot/contracts-repo
   git init
   git remote add origin git@github.com:your-org/contracts.git

   # Or clone existing
   git clone git@github.com:your-org/contracts.git /var/lib/griot/contracts-repo

PostgreSQL Backend
------------------

Production-ready backend using PostgreSQL for scalable contract storage.

Installation
~~~~~~~~~~~~

.. code-block:: bash

   pip install griot-registry[postgres]

Configuration
~~~~~~~~~~~~~

.. code-block:: bash

   export GRIOT_STORAGE_BACKEND=postgres
   export GRIOT_DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/griot

   # Connection pool settings (optional)
   export GRIOT_DB_POOL_SIZE=10
   export GRIOT_DB_MAX_OVERFLOW=20

Database Schema
~~~~~~~~~~~~~~~

The backend automatically creates these tables on startup:

**contracts**

.. code-block:: sql

   CREATE TABLE contracts (
       id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       name VARCHAR(255) UNIQUE NOT NULL,
       description TEXT,
       owner VARCHAR(255),
       current_version VARCHAR(50),
       status VARCHAR(50) DEFAULT 'active',
       fields JSONB NOT NULL,
       metadata JSONB,
       created_at TIMESTAMP DEFAULT NOW(),
       updated_at TIMESTAMP DEFAULT NOW()
   );

   CREATE INDEX idx_contracts_name ON contracts(name);
   CREATE INDEX idx_contracts_owner ON contracts(owner);
   CREATE INDEX idx_contracts_status ON contracts(status);
   CREATE INDEX idx_contracts_fields ON contracts USING GIN(fields);

**contract_versions**

.. code-block:: sql

   CREATE TABLE contract_versions (
       id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       contract_id UUID REFERENCES contracts(id) ON DELETE CASCADE,
       version VARCHAR(50) NOT NULL,
       fields JSONB NOT NULL,
       changelog TEXT,
       created_by VARCHAR(255),
       created_at TIMESTAMP DEFAULT NOW(),
       UNIQUE(contract_id, version)
   );

   CREATE INDEX idx_versions_contract ON contract_versions(contract_id);

**validations**

.. code-block:: sql

   CREATE TABLE validations (
       id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       contract_id UUID REFERENCES contracts(id) ON DELETE CASCADE,
       version VARCHAR(50),
       status VARCHAR(50) NOT NULL,
       total_rows INTEGER,
       valid_rows INTEGER,
       error_count INTEGER,
       errors JSONB,
       stats JSONB,
       validated_at TIMESTAMP DEFAULT NOW(),
       validated_by VARCHAR(255)
   );

   CREATE INDEX idx_validations_contract ON validations(contract_id);
   CREATE INDEX idx_validations_status ON validations(status);
   CREATE INDEX idx_validations_date ON validations(validated_at);

Running Migrations
~~~~~~~~~~~~~~~~~~

Tables are created automatically on first startup. For manual migration:

.. code-block:: python

   from griot_registry.storage.postgres import PostgresStorage

   async def init_db():
       storage = PostgresStorage(database_url="postgresql+asyncpg://...")
       await storage.initialize()
       await storage.close()

   import asyncio
   asyncio.run(init_db())

Usage Notes
~~~~~~~~~~~

- **Pros**: Scalable, ACID compliant, advanced querying, full-text search
- **Cons**: Requires PostgreSQL setup and maintenance
- **Recommended for**: Production deployments, teams with multiple users

Example Setup
~~~~~~~~~~~~~

.. code-block:: python

   from griot_registry.config import Settings
   from griot_registry.server import create_app

   settings = Settings(
       storage_backend="postgres",
       database_url="postgresql+asyncpg://griot:password@localhost:5432/griot",
       db_pool_size=10,
       db_max_overflow=20
   )
   app = create_app(settings)

Advanced Queries
~~~~~~~~~~~~~~~~

The PostgreSQL backend supports advanced search capabilities:

.. code-block:: bash

   # Search by field name (uses JSONB containment)
   curl "http://localhost:8000/api/v1/search?field_name=email"

   # Full-text search on descriptions
   curl "http://localhost:8000/api/v1/search?q=user+authentication"

   # Filter by owner
   curl "http://localhost:8000/api/v1/contracts?owner=data-team"

Switching Backends
------------------

To migrate contracts between backends:

1. **Export from source**:

   .. code-block:: bash

      # Using the CLI
      griot pull --all --output ./contracts-backup/

2. **Switch configuration**:

   .. code-block:: bash

      export GRIOT_STORAGE_BACKEND=postgres
      export GRIOT_DATABASE_URL=postgresql+asyncpg://...

3. **Import to target**:

   .. code-block:: bash

      # Using the CLI
      griot push --dir ./contracts-backup/

Custom Storage Backend
----------------------

Implement a custom backend by extending ``StorageBackend``:

.. code-block:: python

   from griot_registry.storage.base import StorageBackend
   from griot_registry.storage.models import Contract, ValidationRecord

   class CustomStorage(StorageBackend):
       async def initialize(self) -> None:
           """Initialize the storage backend."""
           pass

       async def close(self) -> None:
           """Clean up resources."""
           pass

       async def health_check(self) -> bool:
           """Return True if backend is healthy."""
           return True

       async def create_contract(self, contract: Contract) -> Contract:
           """Create a new contract."""
           ...

       async def get_contract(self, name: str) -> Contract | None:
           """Get contract by name."""
           ...

       async def list_contracts(
           self,
           owner: str | None = None,
           status: str | None = None,
           limit: int = 100,
           offset: int = 0
       ) -> list[Contract]:
           """List contracts with optional filters."""
           ...

       # Implement remaining abstract methods...

Register your backend in ``storage/__init__.py``:

.. code-block:: python

   BACKENDS["custom"] = CustomStorage
