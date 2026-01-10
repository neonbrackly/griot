"""
Griot Enforce - Airflow Operators

Airflow operators for validating data against Griot contracts.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Sequence

if TYPE_CHECKING:
    from airflow.utils.context import Context

__all__ = ["GriotValidateOperator"]


class GriotValidateOperator:
    """
    Airflow operator for validating data against Griot contracts.

    Example:
        validate_customers = GriotValidateOperator(
            task_id="validate_customers",
            contract_id="customer-profile",
            data_path="{{ ti.xcom_pull('extract') }}",
            error_threshold=0.01,
        )
    """

    template_fields: Sequence[str] = ("data_path", "contract_id", "version")
    ui_color = "#e4f0e8"

    def __new__(cls, **kwargs: Any) -> Any:
        """Create operator inheriting from Airflow BaseOperator."""
        try:
            from airflow.models import BaseOperator
        except ImportError:
            raise ImportError(
                "apache-airflow required. Install with: pip install griot-enforce[airflow]"
            )

        class _GriotValidateOperator(BaseOperator):
            template_fields: Sequence[str] = ("data_path", "contract_id", "version")
            ui_color = "#e4f0e8"

            def __init__(
                self,
                *,
                contract_id: str,
                data_path: str,
                registry_url: str | None = None,
                version: str | None = None,
                fail_on_error: bool = True,
                error_threshold: float | None = None,
                **op_kwargs: Any,
            ) -> None:
                super().__init__(**op_kwargs)
                self.contract_id = contract_id
                self.data_path = data_path
                self.registry_url = registry_url
                self.version = version
                self.fail_on_error = fail_on_error
                self.error_threshold = error_threshold

            def execute(self, context: Context) -> dict[str, Any]:
                """Execute validation."""
                from airflow.exceptions import AirflowException
                from griot_enforce.validator import RuntimeValidator

                validator = RuntimeValidator(
                    registry_url=self.registry_url, report_results=True
                )
                data = self._load_data(self.data_path)
                result = validator.validate(
                    self.contract_id, data, version=self.version, fail_on_error=False
                )

                if self.error_threshold is not None:
                    if result.error_rate > self.error_threshold:
                        raise AirflowException(
                            f"Error rate {result.error_rate:.2%} exceeds {self.error_threshold:.2%}"
                        )
                elif self.fail_on_error and not result.passed:
                    raise AirflowException(
                        f"Validation failed with {result.error_count} errors"
                    )

                return result.to_dict()

            def _load_data(self, path: str) -> list[dict[str, Any]]:
                """Load data from file."""
                import json
                from pathlib import Path

                file_path = Path(path)
                if not file_path.exists():
                    raise FileNotFoundError(f"Data file not found: {path}")

                suffix = file_path.suffix.lower()
                if suffix == ".json":
                    with open(file_path) as f:
                        data = json.load(f)
                    return data if isinstance(data, list) else [data]
                elif suffix == ".csv":
                    try:
                        import pandas as pd
                        return pd.read_csv(file_path).to_dict("records")
                    except ImportError:
                        import csv
                        with open(file_path, newline="") as f:
                            return list(csv.DictReader(f))
                elif suffix == ".parquet":
                    import pandas as pd
                    return pd.read_parquet(file_path).to_dict("records")
                else:
                    raise ValueError(f"Unsupported format: {suffix}")

        return _GriotValidateOperator(**kwargs)
