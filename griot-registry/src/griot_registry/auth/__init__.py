"""Authentication modules for griot-registry."""

from griot_registry.auth.api_key import ApiKeyAuth, api_key_auth, get_api_key_header

__all__ = [
    "api_key_auth",
    "get_api_key_header",
    "ApiKeyAuth",
]

# OAuth exports available when oauth extra is installed
try:
    from griot_registry.auth.oauth import (
        AdminRole,
        EditorRole,
        OAuth2Auth,
        OAuthProvider,
        OAuthSettings,
        TokenClaims,
        ViewerRole,
        oauth2_auth,
    )

    __all__.extend([
        "oauth2_auth",
        "OAuth2Auth",
        "OAuthProvider",
        "OAuthSettings",
        "TokenClaims",
        "AdminRole",
        "EditorRole",
        "ViewerRole",
    ])
except ImportError:
    # OAuth dependencies not installed
    pass
