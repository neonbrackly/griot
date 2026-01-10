Deployment Guide
================

This guide covers deploying griot-registry in production environments.

.. contents:: Table of Contents
   :local:
   :depth: 2

Standalone Deployment
---------------------

For simple deployments, run griot-registry directly with uvicorn or gunicorn.

**Using uvicorn:**

.. code-block:: bash

   pip install griot-registry[all]

   # Production settings
   export GRIOT_DEBUG=false
   export GRIOT_LOG_LEVEL=WARNING
   export GRIOT_STORAGE_BACKEND=postgres
   export GRIOT_DATABASE_URL=postgresql+asyncpg://user:pass@localhost/griot

   uvicorn griot_registry.server:create_app \
     --factory \
     --host 0.0.0.0 \
     --port 8000 \
     --workers 4

**Using gunicorn with uvicorn workers:**

.. code-block:: bash

   pip install gunicorn

   gunicorn griot_registry.server:create_app \
     --worker-class uvicorn.workers.UvicornWorker \
     --workers 4 \
     --bind 0.0.0.0:8000 \
     --factory

Docker Deployment
-----------------

Dockerfile
~~~~~~~~~~

Create a ``Dockerfile`` for griot-registry:

.. code-block:: dockerfile

   FROM python:3.11-slim

   WORKDIR /app

   # Install system dependencies
   RUN apt-get update && apt-get install -y \
       git \
       libpq-dev \
       && rm -rf /var/lib/apt/lists/*

   # Install Python dependencies
   COPY pyproject.toml .
   RUN pip install --no-cache-dir ".[all]"

   # Copy application code
   COPY src/ src/

   # Create non-root user
   RUN useradd -m -u 1000 griot
   USER griot

   # Default environment
   ENV GRIOT_HOST=0.0.0.0
   ENV GRIOT_PORT=8000
   ENV GRIOT_STORAGE_BACKEND=filesystem
   ENV GRIOT_STORAGE_PATH=/data/contracts

   EXPOSE 8000

   CMD ["uvicorn", "griot_registry.server:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]

Docker Compose
~~~~~~~~~~~~~~

For a complete deployment with PostgreSQL:

.. code-block:: yaml

   # docker-compose.yml
   version: '3.8'

   services:
     registry:
       build: ./griot-registry
       ports:
         - "8000:8000"
       environment:
         GRIOT_STORAGE_BACKEND: postgres
         GRIOT_DATABASE_URL: postgresql+asyncpg://griot:griot@db:5432/griot
         GRIOT_AUTH_ENABLED: "true"
         GRIOT_API_KEYS: '["your-secure-api-key"]'
       depends_on:
         db:
           condition: service_healthy
       volumes:
         - contracts:/data/contracts
       restart: unless-stopped

     db:
       image: postgres:15-alpine
       environment:
         POSTGRES_USER: griot
         POSTGRES_PASSWORD: griot
         POSTGRES_DB: griot
       volumes:
         - pgdata:/var/lib/postgresql/data
       healthcheck:
         test: ["CMD-SHELL", "pg_isready -U griot"]
         interval: 5s
         timeout: 5s
         retries: 5

   volumes:
     contracts:
     pgdata:

Run with:

.. code-block:: bash

   docker-compose up -d

Kubernetes Deployment
---------------------

Deployment Manifest
~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # kubernetes/deployment.yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: griot-registry
     labels:
       app: griot-registry
   spec:
     replicas: 3
     selector:
       matchLabels:
         app: griot-registry
     template:
       metadata:
         labels:
           app: griot-registry
       spec:
         containers:
         - name: registry
           image: your-registry/griot-registry:latest
           ports:
           - containerPort: 8000
           env:
           - name: GRIOT_STORAGE_BACKEND
             value: postgres
           - name: GRIOT_DATABASE_URL
             valueFrom:
               secretKeyRef:
                 name: griot-secrets
                 key: database-url
           - name: GRIOT_API_KEYS
             valueFrom:
               secretKeyRef:
                 name: griot-secrets
                 key: api-keys
           resources:
             requests:
               memory: "256Mi"
               cpu: "250m"
             limits:
               memory: "512Mi"
               cpu: "500m"
           livenessProbe:
             httpGet:
               path: /api/v1/health
               port: 8000
             initialDelaySeconds: 10
             periodSeconds: 30
           readinessProbe:
             httpGet:
               path: /api/v1/health
               port: 8000
             initialDelaySeconds: 5
             periodSeconds: 10

Service Manifest
~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # kubernetes/service.yaml
   apiVersion: v1
   kind: Service
   metadata:
     name: griot-registry
   spec:
     selector:
       app: griot-registry
     ports:
     - port: 80
       targetPort: 8000
     type: ClusterIP

Ingress Configuration
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # kubernetes/ingress.yaml
   apiVersion: networking.k8s.io/v1
   kind: Ingress
   metadata:
     name: griot-registry
     annotations:
       kubernetes.io/ingress.class: nginx
       cert-manager.io/cluster-issuer: letsencrypt-prod
   spec:
     tls:
     - hosts:
       - registry.your-domain.com
       secretName: griot-registry-tls
     rules:
     - host: registry.your-domain.com
       http:
         paths:
         - path: /
           pathType: Prefix
           backend:
             service:
               name: griot-registry
               port:
                 number: 80

Secrets Management
~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # kubernetes/secrets.yaml
   apiVersion: v1
   kind: Secret
   metadata:
     name: griot-secrets
   type: Opaque
   stringData:
     database-url: postgresql+asyncpg://user:password@postgres:5432/griot
     api-keys: '["key1", "key2"]'

Apply with:

.. code-block:: bash

   kubectl apply -f kubernetes/

Helm Chart
~~~~~~~~~~

For more complex deployments, use the Griot Helm chart:

.. code-block:: bash

   helm repo add griot https://charts.griot.io
   helm install griot-registry griot/griot-registry \
     --set storage.backend=postgres \
     --set postgresql.enabled=true \
     --set auth.enabled=true

Production Checklist
--------------------

Before deploying to production, ensure:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Item
     - Description
   * - **TLS/HTTPS**
     - Enable TLS termination at load balancer or ingress
   * - **Authentication**
     - Enable API key or OAuth2 authentication
   * - **Database**
     - Use PostgreSQL for production (not filesystem)
   * - **Backups**
     - Configure database backups and contract exports
   * - **Monitoring**
     - Set up health checks and metrics collection
   * - **Logging**
     - Configure structured logging to your log aggregator
   * - **Rate Limiting**
     - Configure rate limiting at the API gateway level
   * - **CORS**
     - Restrict CORS origins to known frontends

Environment Variables Reference
-------------------------------

.. list-table::
   :header-rows: 1
   :widths: 30 20 50

   * - Variable
     - Default
     - Description
   * - ``GRIOT_HOST``
     - ``127.0.0.1``
     - Server bind host
   * - ``GRIOT_PORT``
     - ``8000``
     - Server bind port
   * - ``GRIOT_DEBUG``
     - ``false``
     - Enable debug mode
   * - ``GRIOT_LOG_LEVEL``
     - ``INFO``
     - Logging level
   * - ``GRIOT_API_V1_PREFIX``
     - ``/api/v1``
     - API version prefix
   * - ``GRIOT_STORAGE_BACKEND``
     - ``filesystem``
     - Storage backend type
   * - ``GRIOT_STORAGE_PATH``
     - ``./data``
     - Filesystem storage path
   * - ``GRIOT_DATABASE_URL``
     - —
     - PostgreSQL connection URL
   * - ``GRIOT_GIT_REPO_PATH``
     - —
     - Git repository path
   * - ``GRIOT_AUTH_ENABLED``
     - ``false``
     - Enable authentication
   * - ``GRIOT_API_KEYS``
     - ``[]``
     - JSON array of API keys
   * - ``GRIOT_OIDC_ISSUER``
     - —
     - OIDC issuer URL
   * - ``GRIOT_CORS_ORIGINS``
     - ``["*"]``
     - Allowed CORS origins
