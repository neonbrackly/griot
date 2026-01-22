"""Domain models for griot-registry.

This module contains Pydantic models for users, teams, roles, permissions,
notifications, tasks, and other entities.
"""

from griot_registry.models.users import (
    UserCreate,
    UserUpdate,
    UserInDB,
    UserResponse,
    UserListResponse,
    UserStatus,
)
from griot_registry.models.teams import (
    TeamCreate,
    TeamUpdate,
    TeamInDB,
    TeamResponse,
    TeamListResponse,
    TeamMember,
    TeamMemberCreate,
)
from griot_registry.models.roles import (
    Permission,
    PermissionCategory,
    RoleCreate,
    RoleUpdate,
    RoleInDB,
    RoleResponse,
    RoleListResponse,
    SYSTEM_PERMISSIONS,
)
from griot_registry.models.auth import (
    LoginRequest,
    SignupRequest,
    AuthResponse,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    PasswordResetToken,
)
from griot_registry.models.notifications import (
    NotificationType,
    NotificationCreate,
    NotificationInDB,
    NotificationResponse,
    NotificationListResponse,
)
from griot_registry.models.tasks import (
    TaskType,
    TaskStatus,
    TaskCreate,
    TaskUpdate,
    TaskInDB,
    TaskResponse,
    TaskListResponse,
)

__all__ = [
    # Users
    "UserCreate",
    "UserUpdate",
    "UserInDB",
    "UserResponse",
    "UserListResponse",
    "UserStatus",
    # Teams
    "TeamCreate",
    "TeamUpdate",
    "TeamInDB",
    "TeamResponse",
    "TeamListResponse",
    "TeamMember",
    "TeamMemberCreate",
    # Roles
    "Permission",
    "PermissionCategory",
    "RoleCreate",
    "RoleUpdate",
    "RoleInDB",
    "RoleResponse",
    "RoleListResponse",
    "SYSTEM_PERMISSIONS",
    # Auth
    "LoginRequest",
    "SignupRequest",
    "AuthResponse",
    "ForgotPasswordRequest",
    "ResetPasswordRequest",
    "PasswordResetToken",
    # Notifications
    "NotificationType",
    "NotificationCreate",
    "NotificationInDB",
    "NotificationResponse",
    "NotificationListResponse",
    # Tasks
    "TaskType",
    "TaskStatus",
    "TaskCreate",
    "TaskUpdate",
    "TaskInDB",
    "TaskResponse",
    "TaskListResponse",
]
