"""griot lint command.

Check a contract for quality issues.

SDK Method: GriotModel.lint()
Status: Complete
"""
from __future__ import annotations

import sys
from pathlib import Path

import click

from griot_cli.output import OutputFormat, echo_error, format_lint_issues


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
@click.pass_context
def lint(
    ctx: click.Context,
    contract: Path,
    format: str,
    min_severity: str,
    strict: bool,
) -> None:
    """Check CONTRACT for quality issues.

    CONTRACT is the path to a contract file or directory.

    Exit codes:
      0 - No issues (or only below min-severity)
      1 - Issues found
      2 - Error

    Examples:
      griot lint contracts/customer.yaml
      griot lint contracts/ --strict
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
