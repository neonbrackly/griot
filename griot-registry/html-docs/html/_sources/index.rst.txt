griot-registry Documentation
=============================

**griot-registry** is the central API server for storing, versioning, and managing Griot data contracts.
It provides a RESTful API for contract lifecycle management, validation history tracking, and multi-backend storage.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   getting-started
   deployment
   api-reference
   storage
   authentication
   administration
   client-integration

Features
--------

- **Contract Management**: Full CRUD operations for data contracts
- **Version Control**: Semantic versioning with diff capabilities
- **Validation History**: Track validation results over time
- **Multi-Backend Storage**: Filesystem, Git, or PostgreSQL backends
- **Authentication**: API key and OAuth2/OIDC support
- **Approval Workflows**: Multi-step approval chains for contract changes
- **Report Generation**: Analytics, AI readiness, and audit reports

Quick Links
-----------

- :doc:`getting-started` - Installation and first steps
- :doc:`deployment` - Production deployment guides
- :doc:`api-reference` - Complete API documentation
- :doc:`storage` - Storage backend configuration
- :doc:`authentication` - Security setup
- :doc:`client-integration` - Client libraries and examples

Requirements
------------

- Python 3.10+
- FastAPI 0.100+
- griot-core (for contract parsing)

Optional dependencies based on storage backend:

- **Git backend**: GitPython
- **PostgreSQL backend**: SQLAlchemy, asyncpg
- **OAuth2**: python-jose, httpx

Installation
------------

.. code-block:: bash

   # Basic installation
   pip install griot-registry

   # With Git storage support
   pip install griot-registry[git]

   # With PostgreSQL support
   pip install griot-registry[postgres]

   # With OAuth2/OIDC support
   pip install griot-registry[oauth]

   # All optional dependencies
   pip install griot-registry[all]

License
-------

Apache 2.0 License. See LICENSE file for details.
