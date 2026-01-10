"""griot mock command.

Generate synthetic mock data conforming to a contract.

SDK Method: GriotModel.mock()
Status: Blocked - waiting on core T-013 (mock generation)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from griot_cli.output import echo_error, echo_success


@click.command()
@click.argument("contract", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--rows",
    "-n",
    type=int,
    default=100,
    help="Number of rows to generate.",
)
@click.option(
    "--seed",
    type=int,
    default=None,
    help="Random seed for reproducibility.",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    default=None,
    help="Output file (default stdout).",
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["csv", "json", "parquet"]),
    default="csv",
    help="Output format.",
)
@click.pass_context
def mock(
    ctx: click.Context,
    contract: Path,
    rows: int,
    seed: int | None,
    output: Path | None,
    format: str,
) -> None:
    """Generate mock data conforming to CONTRACT.

    CONTRACT is the path to a contract YAML file.

    Examples:
      griot mock contracts/customer.yaml -n 1000 -o test_data.csv
      griot mock contracts/customer.yaml --seed 42 -f json
    """
    try:
        from griot_core import GriotModel
    except ImportError:
        echo_error("griot-core is not installed. Install with: pip install griot-core")
        sys.exit(2)

    try:
        # Load contract
        model = GriotModel.from_yaml(contract)

        # Generate mock data
        mock_data = model.mock(rows=rows, seed=seed)

        # Output based on format
        if format == "json":
            _output_json(mock_data, output)
        elif format == "parquet":
            _output_parquet(mock_data, output)
        else:
            _output_csv(mock_data, output)

        if output:
            echo_success(f"Generated {rows} rows to {output}")

    except FileNotFoundError as e:
        echo_error(f"File not found: {e}")
        sys.exit(2)
    except Exception as e:
        echo_error(f"Error: {e}")
        sys.exit(2)


def _output_csv(data, output: Path | None) -> None:
    """Output data as CSV."""
    try:
        import pandas as pd

        df = data if isinstance(data, pd.DataFrame) else pd.DataFrame(data)
        if output:
            df.to_csv(output, index=False)
        else:
            click.echo(df.to_csv(index=False))
    except ImportError:
        # Fallback without pandas
        import csv
        import io

        if isinstance(data, list) and data:
            if output:
                with output.open("w", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
            else:
                output_stream = io.StringIO()
                writer = csv.DictWriter(output_stream, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
                click.echo(output_stream.getvalue())


def _output_json(data, output: Path | None) -> None:
    """Output data as JSON."""
    try:
        import pandas as pd

        if isinstance(data, pd.DataFrame):
            json_data = data.to_dict(orient="records")
        else:
            json_data = data
    except ImportError:
        json_data = data

    json_str = json.dumps(json_data, indent=2, default=str)
    if output:
        output.write_text(json_str)
    else:
        click.echo(json_str)


def _output_parquet(data, output: Path | None) -> None:
    """Output data as Parquet."""
    try:
        import pandas as pd

        df = data if isinstance(data, pd.DataFrame) else pd.DataFrame(data)
        if output:
            df.to_parquet(output)
        else:
            echo_error("Parquet format requires an output file (-o)")
            sys.exit(2)
    except ImportError:
        echo_error(
            "pandas is required for Parquet output. Install with: pip install griot-cli[pandas]"
        )
        sys.exit(2)
