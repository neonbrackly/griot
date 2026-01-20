Changelog
=========

All notable changes to Griot Registry are documented here.

The format is based on `Keep a Changelog <https://keepachangelog.com/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/>`_.

[0.2.0] - 2024-01-20
--------------------

Complete rewrite with MongoDB storage and enhanced features.

Added
^^^^^

- **MongoDB Storage**: Full MongoDB backend using motor async driver
- **Repository Pattern**: Abstract storage interfaces for extensibility
- **JWT Authentication**: Stateless authentication with access/refresh tokens
- **API Key Authentication**: Long-lived keys for service accounts
- **Role-Based Access Control**: Admin, editor, viewer, and service roles
- **Schema Catalog**: Denormalized schema index for cross-contract queries
- **Validation Records**: Track validation history with statistics
- **Pipeline Runs**: Run tracking for data pipeline integrations
- **Issue Management**: Track and resolve data quality issues
- **Comments**: Threaded discussions on contracts with reactions
- **Approval Workflows**: Multi-approver workflow for contract activation
- **Full-Text Search**: MongoDB text search across contracts
- **Advanced Search**: Filtered search with PII detection
- **Python Clients**: Async (RegistryClient) and sync (SyncRegistryClient)
- **Contract Versioning**: Automatic version bump with breaking change detection
- **griot-core Integration**: Uses griot-core for validation and linting

Changed
^^^^^^^

- Storage backend now exclusively uses MongoDB
- API endpoints restructured under ``/api/v1`` prefix
- Authentication required for most operations
- Contract validation happens before storage (never trust clients)

Removed
^^^^^^^

- Filesystem storage backend
- Git storage backend
- PostgreSQL storage backend
- Old synchronous API

Migration
^^^^^^^^^

Contracts from previous versions need to be re-imported. Use the migration
script:

.. code-block:: bash

   griot-registry migrate --from-json ./old-contracts/

[0.1.0] - 2024-01-01
--------------------

Initial release.

Added
^^^^^

- Basic contract storage and retrieval
- Multiple storage backends (filesystem, git, postgres)
- Simple validation
- REST API

[Unreleased]
------------

Planned
^^^^^^^

- Web UI for contract management
- GraphQL API
- Metrics and monitoring endpoints
- Contract lineage tracking
- Schema evolution tools
- Notification system (email, Slack, webhooks)
- Audit logging
- Contract templates
- Import/export tools
