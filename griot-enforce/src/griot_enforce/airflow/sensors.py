"""
Griot Enforce - Airflow Sensors

Airflow sensors for monitoring data freshness and validation status.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Sequence

if TYPE_CHECKING:
    from airflow.utils.context import Context

__all__ = [
    "GriotFreshnessSensor",
]


class GriotFreshnessSensor:
    """
    Sensor that waits for fresh data based on contract SLA.

    Checks registry for recent successful validation. Pokes until
    a validation within the max_age_minutes is found.

    Example:
        from griot_enforce.airflow import GriotFreshnessSensor

        wait_for_customers = GriotFreshnessSensor(
            task_id="wait_for_customers",
            contract_id="customer-profile",
            max_age_minutes=120,
            poke_interval=300,
        )

        wait_for_customers >> process_customers
    """

    template_fields: Sequence[str] = ("contract_id", "version")
    ui_color = "#e4f0e8"
    ui_fgcolor = "#000000"

    def __new__(cls, **kwargs: Any) -> Any:
        """Create sensor instance inheriting from Airflow BaseSensorOperator."""
        try:
            from airflow.sensors.base import BaseSensorOperator
        except ImportError:
            raise ImportError(
                "apache-airflow is required for Airflow sensors. "
                "Install with: pip install griot-enforce[airflow]"
            )

        class _GriotFreshnessSensor(BaseSensorOperator):
            template_fields: Sequence[str] = ("contract_id", "version")
            ui_color = "#e4f0e8"
            ui_fgcolor = "#000000"

            def __init__(
                self,
                *,
                contract_id: str,
                max_age_minutes: int = 60,
                registry_url: str | None = None,
                version: str | None = None,
                require_passed: bool = True,
                **op_kwargs: Any,
            ) -> None:
                super().__init__(**op_kwargs)
                self.contract_id = contract_id
                self.max_age_minutes = max_age_minutes
                self.registry_url = registry_url
                self.version = version
                self.require_passed = require_passed

            def poke(self, context: Context) -> bool:
                """Check if fresh validation exists."""
                import os
                from datetime import datetime, timedelta, timezone

                try:
                    import httpx
                except ImportError:
                    raise ImportError(
                        "httpx is required for registry integration. "
                        "Install with: pip install griot-enforce"
                    )

                registry_url = self.registry_url or os.environ.get("GRIOT_REGISTRY_URL")
                if not registry_url:
                    raise ValueError(
                        "registry_url is required. "
                        "Set it in constructor or GRIOT_REGISTRY_URL env var."
                    )

                api_key = os.environ.get("GRIOT_API_KEY")
                headers = {}
                if api_key:
                    headers["X-API-Key"] = api_key

                cutoff = datetime.now(timezone.utc) - timedelta(minutes=self.max_age_minutes)

                endpoint = f"{registry_url}/api/v1/contracts/{self.contract_id}/validations"
                params: dict[str, Any] = {
                    "since": cutoff.isoformat(),
                    "limit": 1,
                }
                if self.version:
                    params["version"] = self.version
                if self.require_passed:
                    params["passed"] = "true"

                try:
                    with httpx.Client(headers=headers, timeout=30.0) as client:
                        response = client.get(endpoint, params=params)
                        response.raise_for_status()
                        data = response.json()

                        validations = data.get("validations", data.get("items", []))
                        if validations:
                            self.log.info(
                                f"Found fresh validation for '{self.contract_id}' "
                                f"from {validations[0].get('validated_at', 'unknown')}"
                            )
                            return True

                        self.log.info(
                            f"No fresh validation found for '{self.contract_id}' "
                            f"within {self.max_age_minutes} minutes"
                        )
                        return False

                except httpx.HTTPStatusError as e:
                    self.log.warning(f"Registry request failed: {e}")
                    return False
                except Exception as e:
                    self.log.error(f"Error checking freshness: {e}")
                    return False

        return _GriotFreshnessSensor(**kwargs)
