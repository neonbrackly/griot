"""griot migrate command.

Migrate old contracts to the ODCS v1.0.0 format.

SDK Method: migrate_contract(), detect_schema_version()
Status: Complete (T-364)
"""
from __future__ import annotations

import sys
from pathlib import Path

import click
import yaml

from griot_cli.output import echo_error, echo_info, echo_success, echo_warning


@click.command()
@click.argument("contract", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    default=None,
    help="Output file path (default: stdout or <contract>_v1.yaml).",
)
@click.option(
    "--in-place",
    "-i",
    is_flag=True,
    help="Modify the input file in place.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be changed without writing.",
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["yaml", "json"]),
    default="yaml",
    help="Output format.",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Show detailed change log.",
)
@click.pass_context
def migrate(
    ctx: click.Context,
    contract: Path,
    output: Path | None,
    in_place: bool,
    dry_run: bool,
    format: str,
    verbose: bool,
) -> None:
    """Migrate CONTRACT to ODCS v1.0.0 format.

    CONTRACT is the path to a contract YAML file in v0 (legacy) format.

    The migration:
    - Adds api_version, kind, status metadata
    - Converts flat field structure to nested ODCS format
    - Maps PII/privacy fields to privacy section
    - Maps constraints to constraints section
    - Preserves lineage and residency configurations
    - Adds timestamps section

    Exit codes:
      0 - Migration successful
      1 - Already at target version (no migration needed)
      2 - Error

    Examples:
      griot migrate contracts/old_customer.yaml
      griot migrate contracts/old_customer.yaml -o contracts/customer_v1.yaml
      griot migrate contracts/old_customer.yaml --in-place
      griot migrate contracts/old_customer.yaml --dry-run -v
    """
    try:
        from griot_core.migration import detect_schema_version, migrate_contract
    except ImportError:
        echo_error("griot-core is not installed. Install with: pip install griot-core")
        sys.exit(2)

    try:
        # Load contract
        with open(contract, "r", encoding="utf-8") as f:
            contract_dict = yaml.safe_load(f)

        if contract_dict is None:
            echo_error(f"Empty or invalid YAML file: {contract}")
            sys.exit(2)

        # Detect version
        source_version = detect_schema_version(contract_dict)
        echo_info(f"Detected schema version: {source_version}")

        # Migrate
        result = migrate_contract(contract_dict, target_version="v1.0.0")

        if not result.success:
            echo_error(f"Migration failed: {', '.join(result.warnings)}")
            sys.exit(2)

        # Check if already at target version
        if source_version == "v1.0.0":
            echo_info("Contract is already at ODCS v1.0.0 format.")
            if result.warnings:
                for warning in result.warnings:
                    echo_warning(f"  {warning}")
            sys.exit(1)

        # Show migration summary
        echo_success(f"Migration: {result.source_version} -> {result.target_version}")
        echo_info(f"Changes: {len(result.changes)}")
        echo_info(f"Warnings: {len(result.warnings)}")

        if verbose or dry_run:
            if result.changes:
                echo_info("\nChanges made:")
                for change in result.changes:
                    click.secho(f"  + {change}", fg="green")

            if result.warnings:
                echo_info("\nWarnings:")
                for warning in result.warnings:
                    click.secho(f"  ! {warning}", fg="yellow")

        if dry_run:
            echo_info("\n--- Dry run - showing migrated output ---")
            _output_contract(result.contract, format)
            return

        # Determine output destination
        if in_place:
            output_path = contract
        elif output:
            output_path = output
        else:
            # Default: write to stdout
            echo_info("\n--- Migrated contract ---")
            _output_contract(result.contract, format)
            return

        # Write to file
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            if format == "json":
                import json
                json.dump(result.contract, f, indent=2, default=str)
            else:
                yaml.safe_dump(
                    result.contract,
                    f,
                    default_flow_style=False,
                    sort_keys=False,
                    allow_unicode=True,
                )

        echo_success(f"Migrated contract written to: {output_path}")

    except FileNotFoundError as e:
        echo_error(f"File not found: {e}")
        sys.exit(2)
    except yaml.YAMLError as e:
        echo_error(f"YAML parse error: {e}")
        sys.exit(2)
    except Exception as e:
        echo_error(f"Error: {e}")
        sys.exit(2)


def _output_contract(contract: dict, format: str) -> None:
    """Output contract to stdout in specified format."""
    if format == "json":
        import json
        click.echo(json.dumps(contract, indent=2, default=str))
    else:
        click.echo(yaml.safe_dump(
            contract,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
        ))
