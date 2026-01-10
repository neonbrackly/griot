"""
Griot Enforce - Airflow Operators

Airflow operators for validating data against Griot contracts.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Sequence

if TYPE_CHECKING:
    from airflow.utils.context import Context

__all__ = [
    "GriotValidateOperator",
]


class GriotValidateOperator:
    """
    Airflow operator for validating data against Griot contracts.

    Fails task if validation fails (configurable).

    Example:
        from griot_enforce.airflow import GriotValidateOperator

        validate_customers = GriotValidateOperator(
            task_id="validate_customers",
            contract_id="customer-profile",
            data_path="{{ ti.xcom_pull('extract_customers') }}",
            error_threshold=0.01,  # Allow 1% errors
        )

        extract >> validate_customers >> load
    """

    # Airflow template fields for Jinja rendering
    template_fields: Sequence[str] = ("data_path", "contract_id", "version")
    template_ext: Sequence[str] = ()
    ui_color = "#e4f0e8"
    ui_fgcolor = "#000000"

    def __init__(
        self,
        *,
        task_id: str,
        contract_id: str,
        data_path: str,
        registry_url: str | None = None,
        version: str | None = None,
        fail_on_error: bool = True,
        error_threshold: float | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize GriotValidateOperator.

        Args:
            task_id: Airflow task ID.
            contract_id: Contract ID in registry.
            data_path: Path to data file (supports Jinja templating).
            registry_url: Registry URL (or from Airflow connection).
            version: Specific contract version.
            fail_on_error: Fail task on validation error (default: True).
            error_threshold: Fail only if error_rate exceeds threshold.
            **kwargs: Additional BaseOperator arguments.
        """
        try:
            from airflow.models import BaseOperator
        except ImportError:
            raise ImportError(
                "apache-airflow is required for Airflow operators. "
                "Install with: pip install griot-enforce[airflow]"
            )

        # Store parameters
        self.contract_id = contract_id
        self.data_path = data_path
        self.registry_url = registry_url
        self.version = version
        self.fail_on_error = fail_on_error
        self.error_threshold = error_threshold

        # Initialize as a mixin-style class
        # We'll use __class__ dynamically to support Airflow's BaseOperator
        self._task_id = task_id
        self._kwargs = kwargs

    def __new__(cls, **kwargs: Any) -> Any:
        """Create operator instance inheriting from Airflow BaseOperator."""
        try:
            from airflow.models import BaseOperator
        except ImportError:
            raise ImportError(
                "apache-airflow is required for Airflow operators. "
                "Install with: pip install griot-enforce[airflow]"
            )

        # Create a dynamic class that inherits from both
        class _GriotValidateOperator(BaseOperator):
            template_fields: Sequence[str] = ("data_path", "contract_id", "version")
            template_ext: Sequence[str] = ()
            ui_color = "#e4f0e8"
            ui_fgcolor = "#000000"

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
                """Execute the validation operator."""
                from airflow.exceptions import AirflowException

                from griot_enforce.validator import RuntimeValidator

                # Create validator
                validator = RuntimeValidator(
                    registry_url=self.registry_url,
                    report_results=True,
                )

                # Load data from path
                data = self._load_data(self.data_path)

                # Validate (don't fail yet - we check threshold first)
                result = validator.validate(
                    self.contract_id,
                    data,
                    version=self.version,
                    fail_on_error=False,
                )

                # Check error threshold
                if self.error_threshold is not None:
                    if result.error_rate > self.error_threshold:
                        raise AirflowException(
                            f"Validation error rate {result.error_rate:.2%} "
                            f"exceeds threshold {self.error_threshold:.2%}"
                        )
                elif self.fail_on_error and not result.passed:
                    raise AirflowException(
                        f"Validation failed for contract '{self.contract_id}' "
                        f"with {result.error_count} errors"
                    )

                # Return result as dict for XCom
                return result.to_dict()

            def _load_data(self, path: str) -> list[dict[str, Any]]:
                """Load data from file path."""
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

                        df = pd.read_csv(file_path)
                        return df.to_dict("records")
                    except ImportError:
                        # Fallback to stdlib csv
                        import csv

                        with open(file_path, newline="") as f:
                            reader = csv.DictReader(f)
                            return list(reader)

                elif suffix == ".parquet":
                    try:
                        import pandas as pd

                        df = pd.read_parquet(file_path)
                        return df.to_dict("records")
                    except ImportError:
                        raise ImportError(
                            "pandas and pyarrow are required to read Parquet files. "
                            "Install with: pip install pandas pyarrow"
                        )

                else:
                    raise ValueError(f"Unsupported file format: {suffix}")

        return _GriotValidateOperator(**kwargs)
