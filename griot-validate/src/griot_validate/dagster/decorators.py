"""
Griot Enforce - Dagster Decorators

Decorators for automatic validation of Dagster assets.
"""
from __future__ import annotations

from functools import wraps
from typing import Any, Callable, TypeVar

__all__ = [
    "griot_asset",
    "griot_op",
]

F = TypeVar("F", bound=Callable[..., Any])


def griot_asset(
    contract_id: str,
    version: str | None = None,
    fail_on_error: bool = True,
    registry_url: str | None = None,
) -> Callable[[F], F]:
    """
    Decorator that wraps a Dagster asset with automatic validation.

    Validates the output of the decorated function against the specified
    contract before returning it.

    Args:
        contract_id: Contract ID in the registry.
        version: Specific contract version (default: latest).
        fail_on_error: Raise exception on validation failure (default: True).
        registry_url: Override registry URL (default: from resource).

    Returns:
        Decorated asset function.

    Example:
        from griot_validate.dagster import griot_asset

        @griot_asset(contract_id="customer-profile")
        def customers():
            return extract_customers()

        # Or with Dagster's @asset decorator:
        from dagster import asset

        @asset
        @griot_asset(contract_id="customer-profile")
        def customers():
            return extract_customers()
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)

            if result is None:
                return result

            griot = kwargs.get("griot")

            if griot is not None:
                griot.validate(
                    contract_id,
                    result,
                    version=version,
                    fail_on_error=fail_on_error,
                )
            else:
                from griot_validate.validator import RuntimeValidator

                validator = RuntimeValidator(
                    registry_url=registry_url,
                    report_results=True,
                )
                validator.validate(
                    contract_id,
                    result,
                    version=version,
                    fail_on_error=fail_on_error,
                )

            return result

        return wrapper  # type: ignore[return-value]

    return decorator


def griot_op(
    contract_id: str,
    version: str | None = None,
    fail_on_error: bool = True,
    registry_url: str | None = None,
) -> Callable[[F], F]:
    """
    Decorator that wraps a Dagster op with automatic validation.

    Same as griot_asset but named for ops.

    Args:
        contract_id: Contract ID in the registry.
        version: Specific contract version (default: latest).
        fail_on_error: Raise exception on validation failure (default: True).
        registry_url: Override registry URL (default: from resource).

    Returns:
        Decorated op function.
    """
    return griot_asset(
        contract_id=contract_id,
        version=version,
        fail_on_error=fail_on_error,
        registry_url=registry_url,
    )
