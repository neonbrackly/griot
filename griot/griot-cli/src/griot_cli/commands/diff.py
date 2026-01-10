"""griot diff command.

Compare two contract versions and detect breaking changes.

SDK Method: GriotModel.diff()
Status: Blocked - waiting on core T-011 (contract diffing)
"""
from __future__ import annotations

import sys
from pathlib import Path

import click

from griot_cli.output import OutputFormat, echo_error, format_diff


@click.command()
@click.argument("contract_old", type=click.Path(exists=True, path_type=Path))
@click.argument("contract_new", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--format",
    "-f",
    type=click.Choice(["table", "json", "markdown"]),
    default="table",
    help="Output format.",
)
@click.option(
    "--fail-on-breaking",
    is_flag=True,
    help="Exit with code 1 if breaking changes detected.",
)
@click.pass_context
def diff(
    ctx: click.Context,
    contract_old: Path,
    contract_new: Path,
    format: str,
    fail_on_breaking: bool,
) -> None:
    """Compare CONTRACT_OLD with CONTRACT_NEW.

    CONTRACT_OLD is the path to the old contract version.
    CONTRACT_NEW is the path to the new contract version.

    Exit codes:
      0 - No breaking changes (or --fail-on-breaking not set)
      1 - Breaking changes detected
      2 - Error

    Examples:
      griot diff contracts/v1/customer.yaml contracts/v2/customer.yaml
      griot diff old.yaml new.yaml --fail-on-breaking
    """
    try:
        from griot_core import GriotModel
    except ImportError:
        echo_error("griot-core is not installed. Install with: pip install griot-core")
        sys.exit(2)

    try:
        # Load both contracts
        old_model = GriotModel.from_yaml(contract_old)
        new_model = GriotModel.from_yaml(contract_new)

        # Compute diff
        contract_diff = old_model.diff(new_model)

        # Output result
        format_diff(contract_diff, format=OutputFormat(format))

        # Determine exit code
        if fail_on_breaking and contract_diff.has_breaking_changes:
            sys.exit(1)
        else:
            sys.exit(0)

    except FileNotFoundError as e:
        echo_error(f"File not found: {e}")
        sys.exit(2)
    except Exception as e:
        echo_error(f"Error: {e}")
        sys.exit(2)
