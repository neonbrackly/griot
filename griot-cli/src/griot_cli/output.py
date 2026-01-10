"""Output formatting for Griot CLI.

This module provides formatters for displaying validation results,
lint issues, diffs, and other output in various formats:
- table: Human-readable table format (default)
- json: Machine-readable JSON output
- github: GitHub Actions annotation format
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from enum import Enum
from typing import Any, TextIO

import click


class OutputFormat(str, Enum):
    """Supported output formats."""

    TABLE = "table"
    JSON = "json"
    GITHUB = "github"
    MARKDOWN = "markdown"


@dataclass
class ValidationErrorDisplay:
    """Display representation of a validation error."""

    field: str
    row: int | None
    value: Any
    constraint: str
    message: str
    severity: str = "error"


@dataclass
class LintIssueDisplay:
    """Display representation of a lint issue."""

    code: str
    field: str | None
    message: str
    severity: str
    suggestion: str | None = None


def format_validation_result(
    result: Any,
    format: OutputFormat = OutputFormat.TABLE,
    max_errors: int = 100,
    file: TextIO = sys.stdout,
) -> None:
    """Format and display a validation result.

    Args:
        result: ValidationResult from griot-core.
        format: Output format.
        max_errors: Maximum number of errors to display.
        file: Output stream.
    """
    if format == OutputFormat.JSON:
        _format_validation_json(result, file)
    elif format == OutputFormat.GITHUB:
        _format_validation_github(result, max_errors, file)
    else:
        _format_validation_table(result, max_errors, file)


def _format_validation_table(result: Any, max_errors: int, file: TextIO) -> None:
    """Format validation result as a table."""
    # Header
    if result.passed:
        click.secho("Validation PASSED", fg="green", bold=True, file=file)
    else:
        click.secho("Validation FAILED", fg="red", bold=True, file=file)

    click.echo(file=file)
    click.echo(f"Rows validated: {result.row_count}", file=file)
    click.echo(f"Errors: {result.error_count}", file=file)
    click.echo(f"Error rate: {result.error_rate:.2%}", file=file)
    click.echo(f"Duration: {result.duration_ms:.2f}ms", file=file)

    if result.errors:
        click.echo(file=file)
        click.secho("Errors:", bold=True, file=file)
        click.echo("-" * 80, file=file)

        for i, error in enumerate(result.errors[:max_errors]):
            row_info = f"[row {error.row}]" if error.row is not None else "[schema]"
            # Handle both enum and string severity
            severity_str = getattr(error.severity, "value", str(error.severity)).lower()
            severity_color = "red" if severity_str == "error" else "yellow"
            click.echo(
                f"  {row_info} "
                + click.style(error.field, bold=True)
                + ": "
                + click.style(error.message, fg=severity_color),
                file=file,
            )

        if len(result.errors) > max_errors:
            remaining = len(result.errors) - max_errors
            click.echo(f"\n  ... and {remaining} more errors", file=file)


def _format_validation_json(result: Any, file: TextIO) -> None:
    """Format validation result as JSON."""
    output = result.to_dict() if hasattr(result, "to_dict") else {"result": str(result)}
    click.echo(json.dumps(output, indent=2, default=str), file=file)


def _format_validation_github(result: Any, max_errors: int, file: TextIO) -> None:
    """Format validation result as GitHub Actions annotations."""
    for error in result.errors[:max_errors]:
        # GitHub Actions workflow command format
        # Handle both enum and string severity
        severity_str = getattr(error.severity, "value", str(error.severity)).lower()
        level = "error" if severity_str == "error" else "warning"
        message = f"{error.field}: {error.message}"
        if error.row is not None:
            message = f"Row {error.row} - {message}"
        click.echo(f"::{level}::{message}", file=file)


def format_lint_issues(
    issues: list[Any],
    format: OutputFormat = OutputFormat.TABLE,
    file: TextIO = sys.stdout,
) -> None:
    """Format and display lint issues.

    Args:
        issues: List of LintIssue from griot-core.
        format: Output format.
        file: Output stream.
    """
    if format == OutputFormat.JSON:
        _format_lint_json(issues, file)
    elif format == OutputFormat.GITHUB:
        _format_lint_github(issues, file)
    else:
        _format_lint_table(issues, file)


def _format_lint_table(issues: list[Any], file: TextIO) -> None:
    """Format lint issues as a table."""
    if not issues:
        click.secho("No issues found", fg="green", file=file)
        return

    click.echo(f"Found {len(issues)} issue(s):", file=file)
    click.echo("-" * 80, file=file)

    for issue in issues:
        # Handle both enum and string severity
        severity_str = getattr(issue.severity, "value", str(issue.severity)).lower()
        severity_color = {
            "error": "red",
            "warning": "yellow",
            "info": "blue",
        }.get(severity_str, "white")

        field_info = f" ({issue.field})" if issue.field else ""
        click.echo(
            click.style(f"[{issue.code}]", bold=True)
            + click.style(f" [{severity_str}]", fg=severity_color)
            + field_info
            + f": {issue.message}",
            file=file,
        )
        if issue.suggestion:
            click.echo(f"    Suggestion: {issue.suggestion}", file=file)


def _format_lint_json(issues: list[Any], file: TextIO) -> None:
    """Format lint issues as JSON."""
    output = []
    for issue in issues:
        # Handle both enum and string severity
        severity_str = getattr(issue.severity, "value", str(issue.severity)).lower()
        item = {
            "code": issue.code,
            "severity": severity_str,
            "message": issue.message,
        }
        if issue.field:
            item["field"] = issue.field
        if issue.suggestion:
            item["suggestion"] = issue.suggestion
        output.append(item)
    click.echo(json.dumps(output, indent=2), file=file)


def _format_lint_github(issues: list[Any], file: TextIO) -> None:
    """Format lint issues as GitHub Actions annotations."""
    for issue in issues:
        # Handle both enum and string severity
        severity_str = getattr(issue.severity, "value", str(issue.severity)).lower()
        level = "error" if severity_str == "error" else "warning"
        message = f"[{issue.code}] {issue.message}"
        if issue.field:
            message = f"{issue.field}: {message}"
        click.echo(f"::{level}::{message}", file=file)


def format_diff(
    diff: Any,
    format: OutputFormat = OutputFormat.TABLE,
    file: TextIO = sys.stdout,
) -> None:
    """Format and display a contract diff.

    Args:
        diff: ContractDiff from griot-core.
        format: Output format.
        file: Output stream.
    """
    if format == OutputFormat.JSON:
        _format_diff_json(diff, file)
    elif format == OutputFormat.MARKDOWN:
        _format_diff_markdown(diff, file)
    else:
        _format_diff_table(diff, file)


def _format_diff_table(diff: Any, file: TextIO) -> None:
    """Format contract diff as a table."""
    if diff.has_breaking_changes:
        click.secho("BREAKING CHANGES DETECTED", fg="red", bold=True, file=file)
    else:
        click.secho("No breaking changes", fg="green", file=file)

    click.echo(file=file)

    if diff.added_fields:
        click.secho("Added fields:", bold=True, file=file)
        for field in diff.added_fields:
            click.echo(f"  + {field}", file=file)

    if diff.removed_fields:
        click.secho("Removed fields (BREAKING):", bold=True, fg="red", file=file)
        for field in diff.removed_fields:
            click.echo(f"  - {field}", file=file)

    if diff.type_changes:
        click.secho("Type changes:", bold=True, file=file)
        for change in diff.type_changes:
            breaking = " (BREAKING)" if change.is_breaking else ""
            click.echo(
                f"  {change.field}: {change.from_type} -> {change.to_type}{breaking}",
                file=file,
            )

    if diff.constraint_changes:
        click.secho("Constraint changes:", bold=True, file=file)
        for change in diff.constraint_changes:
            breaking = " (BREAKING)" if change.is_breaking else ""
            click.echo(
                f"  {change.field}.{change.constraint}: "
                f"{change.from_value} -> {change.to_value}{breaking}",
                file=file,
            )


def _format_diff_json(diff: Any, file: TextIO) -> None:
    """Format contract diff as JSON."""
    output = {
        "has_breaking_changes": diff.has_breaking_changes,
        "added_fields": diff.added_fields,
        "removed_fields": diff.removed_fields,
        "type_changes": [
            {
                "field": c.field,
                "from_type": c.from_type,
                "to_type": c.to_type,
                "is_breaking": c.is_breaking,
            }
            for c in diff.type_changes
        ],
        "constraint_changes": [
            {
                "field": c.field,
                "constraint": c.constraint,
                "from_value": c.from_value,
                "to_value": c.to_value,
                "is_breaking": c.is_breaking,
            }
            for c in diff.constraint_changes
        ],
    }
    click.echo(json.dumps(output, indent=2, default=str), file=file)


def _format_diff_markdown(diff: Any, file: TextIO) -> None:
    """Format contract diff as Markdown."""
    if diff.has_breaking_changes:
        click.echo("## Breaking Changes Detected", file=file)
    else:
        click.echo("## No Breaking Changes", file=file)

    if hasattr(diff, "to_markdown"):
        click.echo(diff.to_markdown(), file=file)
    else:
        _format_diff_table(diff, file)


def echo_success(message: str) -> None:
    """Print a success message in green."""
    click.secho(message, fg="green")


def echo_error(message: str) -> None:
    """Print an error message in red."""
    click.secho(message, fg="red", err=True)


def echo_warning(message: str) -> None:
    """Print a warning message in yellow."""
    click.secho(message, fg="yellow", err=True)


def echo_info(message: str) -> None:
    """Print an info message in blue."""
    click.secho(message, fg="blue")
