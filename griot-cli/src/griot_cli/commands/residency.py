"""Griot CLI residency commands.

Commands for checking data residency compliance.
All business logic delegated to griot-core.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from griot_cli.output import echo_error, echo_info, echo_success, echo_warning


@click.group()
def residency() -> None:
    """Data residency compliance commands.

    Check and verify geographic data storage compliance for contracts.
    """


@residency.command()
@click.argument("contract", type=click.Path(exists=True))
@click.argument("region")
@click.option(
    "--format",
    "-f",
    "output_format",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format (default: table).",
)
@click.option(
    "--strict",
    is_flag=True,
    help="Exit with error if any field violates residency rules.",
)
def check(contract: str, region: str, output_format: str, strict: bool) -> None:
    """Check data residency compliance for a region.

    Validates if a contract's fields can be stored in the specified region
    based on configured residency rules.

    CONTRACT is the path to a contract YAML file or Python module.

    REGION is the target region code (e.g., us, eu, uk, apac).

    Examples:

        griot residency check customer.yaml eu

        griot residency check contracts/order.yaml us --strict

        griot residency check customer.yaml germany -f json

    Available regions: us, us-east, us-west, canada, brazil, latam, eu,
    eu-west, eu-central, uk, germany, france, switzerland, apac, japan,
    australia, singapore, india, china, hong_kong, south_korea, mea, uae,
    south_africa, global, any
    """
    from griot_core import DataRegion, load_contract

    try:
        # Parse region
        try:
            data_region = DataRegion(region.lower().replace("-", "_"))
        except ValueError:
            valid_regions = [r.value for r in DataRegion]
            echo_error(f"Unknown region: {region}")
            echo_info(f"Valid regions: {', '.join(valid_regions)}")
            sys.exit(1)

        # Load contract
        contract_path = Path(contract)
        echo_info(f"Loading contract from {contract_path}...")
        model = load_contract(str(contract_path))

        # Check residency
        echo_info(f"Checking residency compliance for region: {data_region.value}...")
        result = model.check_residency(data_region)

        # Format output
        if output_format == "json":
            click.echo(json.dumps(result, indent=2))
        else:
            _format_residency_table(model.__name__, data_region.value, result)

        # Exit code based on compliance
        if strict and not result["compliant"]:
            sys.exit(1)

    except Exception as e:
        echo_error(f"Failed to check residency: {e}")
        sys.exit(1)


def _format_residency_table(
    contract_name: str, region: str, result: dict
) -> None:
    """Format residency check result as a table."""
    click.echo()
    click.echo(f"Residency Check: {contract_name}")
    click.echo(f"Target Region: {region}")
    click.echo("=" * 60)

    if result["compliant"]:
        echo_success("COMPLIANT - All fields can be stored in this region")
    else:
        echo_error("NON-COMPLIANT - Some fields cannot be stored in this region")

    click.echo()

    # Show violations
    violations = result.get("violations", [])
    if violations:
        click.echo("Violations:")
        click.echo("-" * 40)
        for violation in violations:
            field = violation.get("field", "unknown")
            message = violation.get("message", "")
            click.echo(f"  {click.style(field, fg='red')}: {message}")
        click.echo()

    # Show warnings
    warnings = result.get("warnings", [])
    if warnings:
        click.echo("Warnings:")
        click.echo("-" * 40)
        for warning in warnings:
            echo_warning(f"  {warning}")
        click.echo()

    # Show config summary if available
    config = result.get("config")
    if config:
        click.echo("Configuration Summary:")
        click.echo("-" * 40)

        default_rule = config.get("default_rule")
        if default_rule:
            allowed = default_rule.get("allowed_regions", [])
            forbidden = default_rule.get("forbidden_regions", [])
            if allowed:
                click.echo(f"  Default allowed regions: {', '.join(allowed)}")
            if forbidden:
                click.echo(f"  Default forbidden regions: {', '.join(forbidden)}")

        frameworks = config.get("compliance_frameworks", [])
        if frameworks:
            click.echo(f"  Compliance frameworks: {', '.join(frameworks)}")

        controller = config.get("data_controller")
        if controller:
            click.echo(f"  Data controller: {controller}")

        dpo = config.get("dpo_contact")
        if dpo:
            click.echo(f"  DPO contact: {dpo}")

        click.echo()

    # Summary
    total_fields = result.get("total_fields", 0)
    violation_count = len(violations)
    compliant_count = total_fields - violation_count

    click.echo("Summary:")
    click.echo("-" * 40)
    click.echo(f"  Total fields: {total_fields}")
    click.echo(
        f"  Compliant: {click.style(str(compliant_count), fg='green')}"
    )
    if violation_count > 0:
        click.echo(
            f"  Non-compliant: {click.style(str(violation_count), fg='red')}"
        )
    click.echo()


@residency.command(name="list-regions")
def list_regions() -> None:
    """List all available region codes.

    Shows all valid region codes that can be used with the check command.

    Example:

        griot residency list-regions
    """
    from griot_core import DataRegion

    click.echo("Available Regions:")
    click.echo("=" * 60)
    click.echo()

    # Group regions by category
    categories = {
        "Americas": ["us", "us_east", "us_west", "canada", "brazil", "latam"],
        "Europe": [
            "eu",
            "eu_west",
            "eu_central",
            "uk",
            "germany",
            "france",
            "switzerland",
        ],
        "Asia Pacific": [
            "apac",
            "japan",
            "australia",
            "singapore",
            "india",
            "china",
            "hong_kong",
            "south_korea",
        ],
        "Middle East & Africa": ["mea", "uae", "south_africa"],
        "Global": ["global", "any"],
    }

    for category, region_values in categories.items():
        click.echo(f"{category}:")
        for region_value in region_values:
            try:
                region = DataRegion(region_value)
                # Format for display (replace underscores with hyphens)
                display_name = region.value.replace("_", "-")
                click.echo(f"  - {display_name}")
            except ValueError:
                pass
        click.echo()
