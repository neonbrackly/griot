"""griot validate command.

Validate data against a contract definition.

SDK Method: GriotModel.validate()
Status: Complete
"""
from __future__ import annotations

import sys
from pathlib import Path

import click

from griot_cli.output import OutputFormat, echo_error, format_validation_result


@click.command()
@click.argument("contract", type=click.Path(exists=True, path_type=Path))
@click.argument("data", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--format",
    "-f",
    type=click.Choice(["table", "json", "github"]),
    default="table",
    help="Output format.",
)
@click.option(
    "--max-errors",
    type=int,
    default=100,
    help="Maximum errors to display.",
)
@click.option(
    "--fail-on-warning",
    is_flag=True,
    help="Exit with code 1 on warnings.",
)
@click.option(
    "--quiet",
    "-q",
    is_flag=True,
    help="Only output on failure.",
)
@click.pass_context
def validate(
    ctx: click.Context,
    contract: Path,
    data: Path,
    format: str,
    max_errors: int,
    fail_on_warning: bool,
    quiet: bool,
) -> None:
    """Validate DATA against CONTRACT.

    CONTRACT is the path to a contract YAML file.
    DATA is the path to a data file (CSV, JSON, or Parquet).

    Exit codes:
      0 - Validation passed
      1 - Validation failed
      2 - Error (file not found, parse error, etc.)

    Examples:
      griot validate contracts/customer.yaml data/customers.csv
      griot validate contracts/customer.yaml data/customers.json -f json
      griot validate contracts/customer.yaml data/customers.csv -f github
    """
    try:
        # Import griot-core SDK
        from griot_core import GriotModel
    except ImportError:
        echo_error("griot-core is not installed. Install with: pip install griot-core")
        sys.exit(2)

    try:
        # Load contract from YAML
        model = GriotModel.from_yaml(contract)

        # Load data (this will need pandas for CSV/Parquet)
        data_content = _load_data(data)

        # Validate data against contract
        result = model.validate(data_content)

        # Output result
        if not quiet or not result.passed:
            format_validation_result(
                result,
                format=OutputFormat(format),
                max_errors=max_errors,
            )

        # Determine exit code
        if not result.passed:
            sys.exit(1)
        elif fail_on_warning:
            # Check for warning-severity errors
            from griot_core import Severity
            has_warnings = any(
                e.severity == Severity.WARNING for e in result.errors
            )
            if has_warnings:
                sys.exit(1)
        sys.exit(0)

    except FileNotFoundError as e:
        echo_error(f"File not found: {e}")
        sys.exit(2)
    except Exception as e:
        echo_error(f"Error: {e}")
        sys.exit(2)


def _load_data(path: Path) -> list[dict]:
    """Load data from file based on extension.

    Args:
        path: Path to data file.

    Returns:
        Data as list of dictionaries.

    Raises:
        ImportError: If required library not installed.
        ValueError: If file format not supported.
    """
    suffix = path.suffix.lower()

    if suffix == ".json":
        import json

        with path.open() as f:
            data = json.load(f)
        # Handle both single record and list of records
        return data if isinstance(data, list) else [data]

    elif suffix == ".csv":
        try:
            import pandas as pd

            df = pd.read_csv(path)
            return df.to_dict(orient="records")
        except ImportError:
            raise ImportError(
                "pandas is required for CSV files. Install with: pip install griot-cli[pandas]"
            )

    elif suffix == ".parquet":
        try:
            import pandas as pd

            df = pd.read_parquet(path)
            return df.to_dict(orient="records")
        except ImportError:
            raise ImportError(
                "pandas is required for Parquet files. "
                "Install with: pip install griot-cli[pandas]"
            )

    else:
        raise ValueError(f"Unsupported file format: {suffix}. Use .json, .csv, or .parquet")
