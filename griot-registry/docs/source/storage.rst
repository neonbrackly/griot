Storage Module
==============

The storage module implements the repository pattern for data persistence.
It provides abstract interfaces and a MongoDB implementation.

Repository Pattern
------------------

The repository pattern abstracts storage operations, enabling:

- **Testing**: Mock repositories for unit tests
- **Flexibility**: Swap storage backends without changing business logic
- **Consistency**: Uniform API across all resource types

Abstract Interfaces
-------------------

StorageBackend
^^^^^^^^^^^^^^

The main storage backend interface aggregates all repositories:

.. code-block:: python

   from abc import ABC, abstractmethod

   class StorageBackend(ABC):
       """Abstract storage backend with all repositories."""

       @property
       @abstractmethod
       def contracts(self) -> ContractRepository:
           """Contract storage repository."""

       @property
       @abstractmethod
       def schema_catalog(self) -> SchemaCatalogRepository:
           """Schema catalog repository."""

       @property
       @abstractmethod
       def validations(self) -> ValidationRecordRepository:
           """Validation records repository."""

       @property
       @abstractmethod
       def runs(self) -> RunRepository:
           """Pipeline runs repository."""

       @property
       @abstractmethod
       def issues(self) -> IssueRepository:
           """Issues repository."""

       @property
       @abstractmethod
       def comments(self) -> CommentRepository:
           """Comments repository."""

       @property
       @abstractmethod
       def approvals(self) -> ApprovalRepository:
           """Approvals repository."""

       @abstractmethod
       async def close(self) -> None:
           """Close connections and cleanup resources."""

ContractRepository
^^^^^^^^^^^^^^^^^^

.. code-block:: python

   class ContractRepository(ABC):
       """Abstract repository for contract storage."""

       @abstractmethod
       async def create(self, contract: Contract) -> Contract:
           """Create a new contract."""

       @abstractmethod
       async def get(self, contract_id: str) -> Contract | None:
           """Get a contract by ID."""

       @abstractmethod
       async def update(self, contract: Contract) -> Contract:
           """Update an existing contract."""

       @abstractmethod
       async def delete(self, contract_id: str) -> bool:
           """Delete a contract."""

       @abstractmethod
       async def list(
           self,
           limit: int = 50,
           offset: int = 0,
           status: str | None = None,
           schema_name: str | None = None,
           owner: str | None = None,
       ) -> tuple[list[Contract], int]:
           """List contracts with optional filtering."""

       @abstractmethod
       async def search(
           self,
           query: str,
           limit: int = 50,
       ) -> list[dict[str, Any]]:
           """Full-text search across contracts."""

MongoDB Implementation
----------------------

The MongoDB implementation uses ``motor`` for async operations.

Collections
^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Collection
     - Description
   * - ``contracts``
     - Current version of each contract
   * - ``contract_versions``
     - Historical versions for rollback/audit
   * - ``schema_catalog``
     - Denormalized schema index
   * - ``validation_records``
     - Validation history
   * - ``runs``
     - Pipeline execution records
   * - ``issues``
     - Data quality issues
   * - ``comments``
     - Collaboration comments
   * - ``approvals``
     - Approval workflow records

Indexes
^^^^^^^

The MongoDB implementation creates the following indexes:

**contracts collection:**

.. code-block:: javascript

   // Unique name index
   db.contracts.createIndex({name: 1}, {unique: true})

   // Status filter
   db.contracts.createIndex({status: 1})

   // Owner filter
   db.contracts.createIndex({owner: 1})

   // Full-text search
   db.contracts.createIndex({
       name: "text",
       description: "text",
       "schemas.name": "text",
       "schemas.fields.name": "text",
       "schemas.fields.description": "text"
   })

**schema_catalog collection:**

.. code-block:: javascript

   // Contract lookup
   db.schema_catalog.createIndex({contract_id: 1})

   // Schema name search
   db.schema_catalog.createIndex({schema_name: 1})

   // PII filter
   db.schema_catalog.createIndex({has_pii: 1})

   // Field name search
   db.schema_catalog.createIndex({"fields.name": 1})

Usage Example
^^^^^^^^^^^^^

.. code-block:: python

   from griot_registry.storage import create_storage
   from griot_registry.config import Settings

   async def main():
       settings = Settings(
           mongodb_uri="mongodb://localhost:27017",
           mongodb_database="griot_registry",
       )

       # Create storage backend
       storage = await create_storage(settings)

       try:
           # Use repositories
           contracts, total = await storage.contracts.list(limit=10)
           print(f"Found {total} contracts")

           # Search contracts
           results = await storage.contracts.search("user event")
           print(f"Search found {len(results)} results")

       finally:
           await storage.close()

Custom Storage Backends
-----------------------

To implement a custom storage backend:

1. Create repository classes implementing the abstract interfaces
2. Create a storage backend class implementing ``StorageBackend``
3. Register the backend in ``storage/__init__.py``

Example PostgreSQL backend (sketch):

.. code-block:: python

   from griot_registry.storage.base import StorageBackend, ContractRepository

   class PostgresContractRepository(ContractRepository):
       def __init__(self, pool):
           self._pool = pool

       async def create(self, contract: Contract) -> Contract:
           async with self._pool.acquire() as conn:
               await conn.execute(
                   "INSERT INTO contracts (id, name, data) VALUES ($1, $2, $3)",
                   contract.id, contract.name, contract.to_dict()
               )
           return contract

       # ... implement other methods ...

   class PostgresStorage(StorageBackend):
       def __init__(self, pool):
           self._pool = pool
           self._contracts = PostgresContractRepository(pool)

       @property
       def contracts(self) -> ContractRepository:
           return self._contracts

       # ... implement other repositories ...

Testing with Mock Storage
-------------------------

For testing, create mock implementations:

.. code-block:: python

   from griot_registry.storage.base import StorageBackend, ContractRepository

   class InMemoryContractRepository(ContractRepository):
       def __init__(self):
           self._contracts: dict[str, Contract] = {}

       async def create(self, contract: Contract) -> Contract:
           self._contracts[contract.id] = contract
           return contract

       async def get(self, contract_id: str) -> Contract | None:
           return self._contracts.get(contract_id)

       async def list(self, **kwargs) -> tuple[list[Contract], int]:
           contracts = list(self._contracts.values())
           return contracts, len(contracts)

       # ... other methods ...

   # Use in tests
   @pytest.fixture
   def mock_storage():
       return InMemoryStorage()

   async def test_create_contract(mock_storage):
       contract = Contract(name="test", version="1.0.0")
       created = await mock_storage.contracts.create(contract)
       assert created.id is not None
