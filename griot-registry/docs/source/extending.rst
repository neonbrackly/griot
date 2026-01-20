Extending Griot Registry
========================

This guide covers how to extend Griot Registry with custom functionality.

Adding New Resource Types
-------------------------

Griot Registry is designed to be extensible. You can add new resource types
by following the repository pattern.

Step 1: Define the Model
^^^^^^^^^^^^^^^^^^^^^^^^

Create a Pydantic model for your resource:

.. code-block:: python

   # griot_registry/models/alerts.py
   from datetime import datetime
   from pydantic import BaseModel, Field

   class Alert(BaseModel):
       """Alert for contract issues."""
       id: str | None = None
       contract_id: str
       rule_name: str
       severity: str = "warning"
       message: str
       triggered_at: datetime
       resolved_at: datetime | None = None
       metadata: dict = Field(default_factory=dict)

Step 2: Define the Repository Interface
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Add an abstract repository to the base module:

.. code-block:: python

   # griot_registry/storage/base.py
   class AlertRepository(ABC):
       """Abstract repository for alerts."""

       @abstractmethod
       async def create(self, alert: dict) -> dict:
           """Create a new alert."""

       @abstractmethod
       async def get(self, alert_id: str) -> dict | None:
           """Get an alert by ID."""

       @abstractmethod
       async def resolve(self, alert_id: str) -> dict:
           """Mark an alert as resolved."""

       @abstractmethod
       async def list(
           self,
           contract_id: str | None = None,
           resolved: bool | None = None,
           limit: int = 50,
           offset: int = 0,
       ) -> tuple[list[dict], int]:
           """List alerts with filtering."""

Step 3: Implement the Repository
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Add the MongoDB implementation:

.. code-block:: python

   # griot_registry/storage/mongodb.py
   class MongoAlertRepository(AlertRepository):
       def __init__(self, db: AsyncIOMotorDatabase):
           self._collection = db.alerts

       async def create(self, alert: dict) -> dict:
           alert["id"] = str(uuid4())
           alert["triggered_at"] = datetime.now(timezone.utc)
           await self._collection.insert_one(alert)
           return alert

       async def get(self, alert_id: str) -> dict | None:
           return await self._collection.find_one({"id": alert_id})

       async def resolve(self, alert_id: str) -> dict:
           result = await self._collection.find_one_and_update(
               {"id": alert_id},
               {"$set": {"resolved_at": datetime.now(timezone.utc)}},
               return_document=True
           )
           if not result:
               raise ValueError(f"Alert '{alert_id}' not found")
           return result

       async def list(
           self,
           contract_id: str | None = None,
           resolved: bool | None = None,
           limit: int = 50,
           offset: int = 0,
       ) -> tuple[list[dict], int]:
           query = {}
           if contract_id:
               query["contract_id"] = contract_id
           if resolved is not None:
               if resolved:
                   query["resolved_at"] = {"$ne": None}
               else:
                   query["resolved_at"] = None

           cursor = self._collection.find(query).skip(offset).limit(limit)
           items = await cursor.to_list(length=limit)
           total = await self._collection.count_documents(query)
           return items, total

Step 4: Add to Storage Backend
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Update the storage backend to include the new repository:

.. code-block:: python

   # griot_registry/storage/base.py
   class StorageBackend(ABC):
       # ... existing properties ...

       @property
       @abstractmethod
       def alerts(self) -> AlertRepository:
           """Alerts repository."""

   # griot_registry/storage/mongodb.py
   class MongoDBStorage(StorageBackend):
       def __init__(self, db: AsyncIOMotorDatabase):
           # ... existing ...
           self._alerts = MongoAlertRepository(db)

       @property
       def alerts(self) -> AlertRepository:
           return self._alerts

Step 5: Create API Endpoints
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Add a new router for the resource:

.. code-block:: python

   # griot_registry/api/alerts.py
   from fastapi import APIRouter, HTTPException, status
   from pydantic import BaseModel

   from griot_registry.api.dependencies import Storage
   from griot_registry.auth import CurrentUser

   router = APIRouter()

   class AlertCreate(BaseModel):
       contract_id: str
       rule_name: str
       severity: str = "warning"
       message: str

   class AlertResponse(BaseModel):
       id: str
       contract_id: str
       rule_name: str
       severity: str
       message: str
       triggered_at: datetime
       resolved_at: datetime | None

   @router.post("/alerts", response_model=AlertResponse, status_code=201)
   async def create_alert(
       request: AlertCreate,
       storage: Storage,
       user: CurrentUser,
   ):
       alert = await storage.alerts.create(request.model_dump())
       return AlertResponse(**alert)

   @router.post("/alerts/{alert_id}/resolve")
   async def resolve_alert(
       alert_id: str,
       storage: Storage,
       user: CurrentUser,
   ):
       try:
           alert = await storage.alerts.resolve(alert_id)
           return AlertResponse(**alert)
       except ValueError as e:
           raise HTTPException(status_code=404, detail=str(e))

   @router.get("/alerts")
   async def list_alerts(
       storage: Storage,
       user: CurrentUser,
       contract_id: str | None = None,
       resolved: bool | None = None,
   ):
       alerts, total = await storage.alerts.list(
           contract_id=contract_id,
           resolved=resolved,
       )
       return {"items": alerts, "total": total}

Step 6: Register the Router
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Add the router to the server:

.. code-block:: python

   # griot_registry/server.py
   from griot_registry.api import alerts

   def create_app(settings: Settings | None = None) -> FastAPI:
       # ... existing code ...

       # Add alerts router
       app.include_router(alerts.router, prefix=api_prefix, tags=["alerts"])

       return app

Custom Authentication
---------------------

You can add custom authentication backends:

.. code-block:: python

   # griot_registry/auth/oauth.py
   from griot_registry.auth.models import User, AuthMethod

   class OAuthAuthenticator:
       def __init__(self, settings):
           self.client_id = settings.oauth_client_id
           self.client_secret = settings.oauth_client_secret

       async def authenticate(self, token: str) -> User | None:
           # Validate token with OAuth provider
           user_info = await self._validate_token(token)
           if not user_info:
               return None

           return User(
               id=user_info["sub"],
               email=user_info["email"],
               name=user_info.get("name"),
               roles=self._map_roles(user_info.get("groups", [])),
               auth_method=AuthMethod.OAUTH,
           )

       def _map_roles(self, groups: list[str]) -> list[str]:
           # Map OAuth groups to registry roles
           role_mapping = {
               "admins": "admin",
               "data-engineers": "editor",
               "analysts": "viewer",
           }
           return [role_mapping.get(g, "viewer") for g in groups]

Custom Validation Rules
-----------------------

Add custom validation rules by extending the ValidationService:

.. code-block:: python

   # griot_registry/services/custom_validation.py
   from griot_registry.services.validation import ValidationService

   class CustomValidationService(ValidationService):
       def __init__(self, settings):
           super().__init__(settings)
           self.custom_rules = [
               self._check_naming_convention,
               self._check_pii_classification,
               self._check_owner_exists,
           ]

       async def validate(self, contract):
           # Run base validation
           result = await super().validate(contract)

           # Run custom rules
           for rule in self.custom_rules:
               issues = await rule(contract)
               for issue in issues:
                   if issue["severity"] == "error":
                       result.errors.append(issue)
                   else:
                       result.warnings.append(issue)

           result.valid = len(result.errors) == 0
           return result

       async def _check_naming_convention(self, contract):
           issues = []
           # Check contract name follows convention
           if not contract.name.islower() or "_" in contract.name:
               issues.append({
                   "code": "NAMING_CONVENTION",
                   "message": "Contract name should be lowercase with hyphens",
                   "severity": "warning",
                   "path": "name",
               })
           return issues

       async def _check_pii_classification(self, contract):
           issues = []
           # Ensure PII fields have classification
           for schema in contract.schemas:
               for field in schema.fields:
                   if getattr(field, 'pii', False) and not getattr(field, 'classification', None):
                       issues.append({
                           "code": "PII_NO_CLASSIFICATION",
                           "message": f"PII field '{field.name}' missing classification",
                           "severity": "error",
                           "path": f"schemas.{schema.name}.fields.{field.name}",
                       })
           return issues

Webhooks and Event Hooks
------------------------

Add webhooks for external integrations:

.. code-block:: python

   # griot_registry/hooks/webhooks.py
   import httpx
   from typing import Callable, Awaitable

   EventHandler = Callable[[str, dict], Awaitable[None]]

   class WebhookManager:
       def __init__(self):
           self._handlers: dict[str, list[EventHandler]] = {}

       def register(self, event_type: str, handler: EventHandler):
           if event_type not in self._handlers:
               self._handlers[event_type] = []
           self._handlers[event_type].append(handler)

       async def emit(self, event_type: str, data: dict):
           for handler in self._handlers.get(event_type, []):
               try:
                   await handler(event_type, data)
               except Exception as e:
                   # Log error but don't fail the operation
                   print(f"Webhook error: {e}")

   # HTTP webhook handler
   async def http_webhook(url: str):
       async def handler(event_type: str, data: dict):
           async with httpx.AsyncClient() as client:
               await client.post(url, json={
                   "event": event_type,
                   "data": data,
               })
       return handler

   # Usage in services
   class ContractServiceWithHooks(ContractService):
       def __init__(self, storage, settings, webhooks: WebhookManager):
           super().__init__(storage, settings)
           self.webhooks = webhooks

       async def create(self, contract, user, **kwargs):
           result = await super().create(contract, user, **kwargs)

           # Emit event
           await self.webhooks.emit("contract.created", {
               "contract_id": result.id,
               "name": result.name,
               "version": result.version,
               "created_by": user.id,
           })

           return result
