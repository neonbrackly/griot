Administration
==============

This guide covers administrative tasks for griot-registry operators.

.. contents:: Table of Contents
   :local:
   :depth: 2

Approval Chains
---------------

Approval chains enable multi-step review processes for contract changes, ensuring governance and compliance.

How Approval Chains Work
~~~~~~~~~~~~~~~~~~~~~~~~

1. A user creates or updates a contract
2. An approval chain is created with designated approvers
3. Each approver reviews and approves/rejects
4. Once all required approvals are received, the contract is published
5. If rejected, the submitter can revise and resubmit

Creating an Approval Chain
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   curl -X POST http://localhost:8000/api/v1/contracts/user_profile/versions/2.0.0/approval-chain \
     -H "X-API-Key: admin-key" \
     -H "Content-Type: application/json" \
     -d '{
       "approvers": [
         {"user": "data-owner@example.com", "role": "data-owner"},
         {"user": "security@example.com", "role": "security"},
         {"user": "compliance@example.com", "role": "compliance"}
       ],
       "require_all": true,
       "sequential": false,
       "expires_in_days": 7
     }'

Configuration Options
~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Option
     - Default
     - Description
   * - ``require_all``
     - true
     - All approvers must approve (vs. any one)
   * - ``sequential``
     - false
     - Approvals must be in order
   * - ``expires_in_days``
     - 30
     - Days before approval request expires
   * - ``auto_approve_owner``
     - false
     - Auto-approve if submitter is an approver

Checking Approval Status
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   curl http://localhost:8000/api/v1/contracts/user_profile/versions/2.0.0/approval-status \
     -H "X-API-Key: your-key"

Response:

.. code-block:: json

   {
     "contract": "user_profile",
     "version": "2.0.0",
     "status": "pending",
     "progress": "2/3",
     "approvals": [
       {
         "user": "data-owner@example.com",
         "role": "data-owner",
         "status": "approved",
         "comment": "Looks good",
         "decided_at": "2024-01-10T14:00:00Z"
       },
       {
         "user": "security@example.com",
         "role": "security",
         "status": "approved",
         "comment": "PII handling verified",
         "decided_at": "2024-01-10T15:00:00Z"
       },
       {
         "user": "compliance@example.com",
         "role": "compliance",
         "status": "pending"
       }
     ],
     "expires_at": "2024-01-17T14:00:00Z"
   }

Submitting a Decision
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Approve
   curl -X POST http://localhost:8000/api/v1/approvals/apr_xyz789/decision \
     -H "X-API-Key: approver-key" \
     -H "Content-Type: application/json" \
     -d '{
       "decision": "approved",
       "comment": "LGTM - compliance requirements met"
     }'

   # Reject
   curl -X POST http://localhost:8000/api/v1/approvals/apr_xyz789/decision \
     -H "X-API-Key: approver-key" \
     -H "Content-Type: application/json" \
     -d '{
       "decision": "rejected",
       "comment": "Missing data retention policy for PII fields"
     }'

Canceling an Approval Chain
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   curl -X DELETE http://localhost:8000/api/v1/contracts/user_profile/versions/2.0.0/approval-chain \
     -H "X-API-Key: admin-key"

User Management
---------------

With OAuth2/OIDC authentication, user management is handled by your identity provider.

Viewing Active Sessions
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   curl http://localhost:8000/api/v1/admin/sessions \
     -H "X-API-Key: admin-key"

Response:

.. code-block:: json

   {
     "active_sessions": 42,
     "sessions": [
       {
         "user": "alice@example.com",
         "last_active": "2024-01-10T14:30:00Z",
         "ip_address": "192.168.1.100"
       }
     ]
   }

Revoking API Keys
~~~~~~~~~~~~~~~~~

To revoke an API key, remove it from the configuration:

.. code-block:: bash

   # Before
   export GRIOT_API_KEYS='["key1", "key2", "compromised-key"]'

   # After (key revoked)
   export GRIOT_API_KEYS='["key1", "key2"]'

   # Restart the server to apply
   systemctl restart griot-registry

Audit Logging
-------------

griot-registry logs all administrative actions for audit purposes.

Log Format
~~~~~~~~~~

.. code-block:: json

   {
     "timestamp": "2024-01-10T14:30:00.123Z",
     "level": "INFO",
     "event": "contract_created",
     "user": "alice@example.com",
     "ip_address": "192.168.1.100",
     "details": {
       "contract": "user_profile",
       "version": "1.0.0"
     }
   }

Logged Events
~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Event
     - Description
   * - ``auth_success``
     - Successful authentication
   * - ``auth_failure``
     - Failed authentication attempt
   * - ``contract_created``
     - New contract created
   * - ``contract_updated``
     - Contract updated (new version)
   * - ``contract_deprecated``
     - Contract deprecated
   * - ``approval_requested``
     - Approval chain created
   * - ``approval_decision``
     - Approval decision submitted
   * - ``validation_recorded``
     - Validation result recorded
   * - ``admin_action``
     - Administrative action performed

Configuring Log Output
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Log level
   export GRIOT_LOG_LEVEL=INFO

   # JSON format for log aggregators
   export GRIOT_LOG_FORMAT=json

   # Output to file
   export GRIOT_LOG_FILE=/var/log/griot/registry.log

Sending Logs to External Systems
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Elasticsearch/ELK:**

.. code-block:: bash

   # Use Filebeat to ship logs
   filebeat -e -c /etc/filebeat/filebeat.yml

**Datadog:**

.. code-block:: bash

   export DD_LOGS_ENABLED=true
   export DD_LOGS_CONFIG_CONTAINER_COLLECT_ALL=true

Backup and Recovery
-------------------

Filesystem Backend
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Backup
   tar -czvf griot-backup-$(date +%Y%m%d).tar.gz /var/lib/griot/contracts/

   # Restore
   tar -xzvf griot-backup-20240110.tar.gz -C /

Git Backend
~~~~~~~~~~~

.. code-block:: bash

   # Backup (push to remote)
   cd /var/lib/griot/contracts-repo
   git push origin main

   # Restore (clone from remote)
   git clone git@github.com:your-org/contracts.git /var/lib/griot/contracts-repo

PostgreSQL Backend
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Backup
   pg_dump -h localhost -U griot -d griot > griot-backup-$(date +%Y%m%d).sql

   # Restore
   psql -h localhost -U griot -d griot < griot-backup-20240110.sql

   # Using pg_dump with compression
   pg_dump -h localhost -U griot -d griot | gzip > griot-backup-$(date +%Y%m%d).sql.gz

Export/Import Contracts
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Export all contracts via CLI
   griot pull --all --output ./contracts-export/

   # Export specific contract
   griot pull user_profile --output ./contracts-export/

   # Import contracts
   griot push --dir ./contracts-export/

Monitoring
----------

Health Checks
~~~~~~~~~~~~~

Configure health check endpoints in your monitoring system:

.. code-block:: yaml

   # Prometheus blackbox exporter
   modules:
     griot_health:
       prober: http
       timeout: 5s
       http:
         valid_http_versions: ["HTTP/1.1", "HTTP/2"]
         valid_status_codes: [200]
         method: GET
         headers:
           Accept: application/json

Metrics Endpoint
~~~~~~~~~~~~~~~~

If metrics are enabled, Prometheus metrics are available at ``/metrics``:

.. code-block:: bash

   export GRIOT_METRICS_ENABLED=true

   curl http://localhost:8000/metrics

Available metrics:

.. code-block:: text

   # HELP griot_requests_total Total HTTP requests
   # TYPE griot_requests_total counter
   griot_requests_total{method="GET",endpoint="/contracts",status="200"} 1234

   # HELP griot_request_duration_seconds Request duration histogram
   # TYPE griot_request_duration_seconds histogram
   griot_request_duration_seconds_bucket{le="0.1"} 980

   # HELP griot_contracts_total Total number of contracts
   # TYPE griot_contracts_total gauge
   griot_contracts_total{status="active"} 150

   # HELP griot_validations_total Total validations recorded
   # TYPE griot_validations_total counter
   griot_validations_total{status="passed"} 5000

Alerting
~~~~~~~~

Example Prometheus alerting rules:

.. code-block:: yaml

   groups:
   - name: griot-registry
     rules:
     - alert: GriotRegistryDown
       expr: up{job="griot-registry"} == 0
       for: 1m
       labels:
         severity: critical
       annotations:
         summary: "Griot Registry is down"

     - alert: GriotHighErrorRate
       expr: |
         rate(griot_requests_total{status=~"5.."}[5m])
         / rate(griot_requests_total[5m]) > 0.05
       for: 5m
       labels:
         severity: warning
       annotations:
         summary: "High error rate on Griot Registry"

     - alert: GriotStorageUnhealthy
       expr: griot_storage_healthy == 0
       for: 1m
       labels:
         severity: critical
       annotations:
         summary: "Griot storage backend unhealthy"

Maintenance Tasks
-----------------

Cleaning Up Old Validations
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: sql

   -- PostgreSQL: Delete validations older than 90 days
   DELETE FROM validations
   WHERE validated_at < NOW() - INTERVAL '90 days';

   -- Keep only last 100 validations per contract
   DELETE FROM validations v1
   WHERE v1.id NOT IN (
     SELECT id FROM (
       SELECT id, ROW_NUMBER() OVER (
         PARTITION BY contract_id ORDER BY validated_at DESC
       ) as rn
       FROM validations
     ) v2
     WHERE v2.rn <= 100
   );

Reindexing Search
~~~~~~~~~~~~~~~~~

For PostgreSQL with full-text search:

.. code-block:: sql

   REINDEX INDEX idx_contracts_search;
   VACUUM ANALYZE contracts;

Database Maintenance
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # PostgreSQL maintenance
   vacuumdb -h localhost -U griot -d griot --analyze

   # Check table sizes
   psql -h localhost -U griot -d griot -c "
     SELECT relname, pg_size_pretty(pg_total_relation_size(relid))
     FROM pg_catalog.pg_statio_user_tables
     ORDER BY pg_total_relation_size(relid) DESC;
   "

Upgrading
---------

Rolling Upgrade (Kubernetes)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Update image tag
   kubectl set image deployment/griot-registry \
     registry=your-registry/griot-registry:v1.2.0

   # Monitor rollout
   kubectl rollout status deployment/griot-registry

   # Rollback if needed
   kubectl rollout undo deployment/griot-registry

Database Migrations
~~~~~~~~~~~~~~~~~~~

Migrations run automatically on startup. For manual control:

.. code-block:: bash

   # Check current migration version
   griot-registry migrate status

   # Run pending migrations
   griot-registry migrate up

   # Rollback last migration
   griot-registry migrate down
