"""griot lint command.

Check a contract for quality issues including ODCS compliance.

SDK Method: GriotModel.lint()
Status: Complete (T-366: ODCS quality rules support)
"""
from __future__ import annotations

import sys
from pathlib import Path

import click

from griot_cli.output import OutputFormat, echo_error, echo_info, format_lint_issues


# ODCS-specific lint rule codes (G006+)
ODCS_RULE_CODES = {"G006", "G007", "G008", "G009", "G010", "G011", "G012", "G013", "G014", "G015"}


@click.command()
@click.argument("contract", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--format",
    "-f",
    type=click.Choice(["table", "json", "github"]),
    default="table",
    help="Output format.",
)
@click.option(
    "--min-severity",
    type=click.Choice(["error", "warning", "info"]),
    default="info",
    help="Minimum severity to show.",
)
@click.option(
    "--strict",
    is_flag=True,
    help="Fail on warnings (for CI).",
)
@click.option(
    "--odcs-only",
    is_flag=True,
    help="Show only ODCS-specific issues (quality, compliance, governance).",
)
@click.option(
    "--summary",
    is_flag=True,
    help="Show summary of issues by category.",
)
@click.pass_context
def lint(
    ctx: click.Context,
    contract: Path,
    format: str,
    min_severity: str,
    strict: bool,
    odcs_only: bool,
    summary: bool,
) -> None:
    """Check CONTRACT for quality issues including ODCS compliance.

    CONTRACT is the path to a contract file or directory.

    Lint Rules:
      G001-G005: Basic schema rules (primary key, descriptions, constraints)
      G006-G015: ODCS quality rules (quality section, SLA, governance, etc.)

    ODCS Quality Rules (T-366):
      G006: No quality rules defined
      G007: Completeness rule missing min_percent
      G008: Freshness rule missing timestamp_field
      G009: Custom check missing definition
      G010: No description.purpose defined
      G011: No SLA section defined
      G012: No governance.producer defined
      G013: Missing team information
      G014: No legal.jurisdiction defined
      G015: No compliance.data_classification defined

    Exit codes:
      0 - No issues (or only below min-severity)
      1 - Issues found
      2 - Error

    Examples:
      griot lint contracts/customer.yaml
      griot lint contracts/ --strict
      griot lint contracts/customer.yaml --odcs-only
      griot lint contracts/ --summary
    """
    try:
        from griot_core import GriotModel, Severity
    except ImportError:
        echo_error("griot-core is not installed. Install with: pip install griot-core")
        sys.exit(2)

    try:
        # Handle directory or single file
        if contract.is_dir():
            all_issues = []
            for yaml_file in contract.glob("**/*.yaml"):
                model = GriotModel.from_yaml(yaml_file)
                issues = model.lint()
                all_issues.extend(issues)
            for yml_file in contract.glob("**/*.yml"):
                model = GriotModel.from_yaml(yml_file)
                issues = model.lint()
                all_issues.extend(issues)
        else:
            model = GriotModel.from_yaml(contract)
            all_issues = model.lint()

        # Filter by severity (Severity is an enum)
        severity_order = {
            Severity.ERROR: 0,
            Severity.WARNING: 1,
            Severity.INFO: 2,
        }
        min_level = {"error": 0, "warning": 1, "info": 2}.get(min_severity, 2)
        filtered_issues = [
            issue
            for issue in all_issues
            if severity_order.get(issue.severity, 2) <= min_level
        ]

        # T-366: Filter for ODCS-only issues if requested
        if odcs_only:
            filtered_issues = [
                issue
                for issue in filtered_issues
                if issue.code in ODCS_RULE_CODES
            ]

        # T-366: Show summary by category if requested
        if summary:
            _show_lint_summary(filtered_issues, Severity)

        # Output result
        format_lint_issues(filtered_issues, format=OutputFormat(format))

        # Determine exit code
        has_errors = any(i.severity == Severity.ERROR for i in filtered_issues)
        has_warnings = any(i.severity == Severity.WARNING for i in filtered_issues)

        if has_errors:
            sys.exit(1)
        elif strict and has_warnings:
            sys.exit(1)
        else:
            sys.exit(0)

    except FileNotFoundError as e:
        echo_error(f"File not found: {e}")
        sys.exit(2)
    except Exception as e:
        echo_error(f"Error: {e}")
        sys.exit(2)


def _show_lint_summary(issues: list, severity_enum: type) -> None:
    """Display a summary of lint issues by category (T-366)."""
    if not issues:
        echo_info("No lint issues found.")
        return

    # Count by severity
    error_count = sum(1 for i in issues if i.severity == severity_enum.ERROR)
    warning_count = sum(1 for i in issues if i.severity == severity_enum.WARNING)
    info_count = sum(1 for i in issues if i.severity == severity_enum.INFO)

    # Count by category
    schema_issues = sum(1 for i in issues if i.code in {"G001", "G002", "G003", "G004", "G005"})
    odcs_issues = sum(1 for i in issues if i.code in ODCS_RULE_CODES)

    echo_info("\n=== Lint Summary ===")
    echo_info(f"Total issues: {len(issues)}")
    echo_info("")
    echo_info("By Severity:")
    if error_count:
        click.secho(f"  Errors:   {error_count}", fg="red")
    if warning_count:
        click.secho(f"  Warnings: {warning_count}", fg="yellow")
    if info_count:
        click.secho(f"  Info:     {info_count}", fg="blue")
    echo_info("")
    echo_info("By Category:")
    echo_info(f"  Schema Rules (G001-G005): {schema_issues}")
    echo_info(f"  ODCS Rules (G006-G015):   {odcs_issues}")
    echo_info("")
