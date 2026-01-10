"""Griot CLI report commands.

Commands for generating contract analysis reports.
All business logic delegated to griot-core.
"""
from __future__ import annotations

import sys
from pathlib import Path

import click

from griot_cli.output import echo_error, echo_info, echo_success


@click.group()
def report() -> None:
    """Generate contract analysis reports.

    Create analytics, AI readiness, and audit reports for data contracts.
    """


@report.command()
@click.argument("contract", type=click.Path(exists=True))
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file path. If not specified, prints to stdout.",
)
@click.option(
    "--format",
    "-f",
    "output_format",
    type=click.Choice(["json", "markdown"]),
    default="markdown",
    help="Output format (default: markdown).",
)
def analytics(contract: str, output: str | None, output_format: str) -> None:
    """Generate analytics report for a contract.

    Provides detailed statistics about contract structure, field types,
    constraints, and data quality metrics.

    CONTRACT is the path to a contract YAML file or Python module.

    Examples:

        griot report analytics customer.yaml

        griot report analytics contracts/order.yaml -f json

        griot report analytics customer.yaml -o report.md
    """
    from griot_core import generate_analytics_report, load_contract

    try:
        # Load contract
        contract_path = Path(contract)
        echo_info(f"Loading contract from {contract_path}...")
        model = load_contract(str(contract_path))

        # Generate report
        echo_info("Generating analytics report...")
        report_data = generate_analytics_report(model)

        # Format output
        if output_format == "json":
            result = report_data.to_json(indent=2)
        else:
            result = report_data.to_markdown()

        # Output
        if output:
            output_path = Path(output)
            output_path.write_text(result)
            echo_success(f"Report saved to {output_path}")
        else:
            click.echo(result)

    except Exception as e:
        echo_error(f"Failed to generate analytics report: {e}")
        sys.exit(1)


@report.command()
@click.argument("contract", type=click.Path(exists=True))
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file path. If not specified, prints to stdout.",
)
@click.option(
    "--format",
    "-f",
    "output_format",
    type=click.Choice(["json", "markdown"]),
    default="markdown",
    help="Output format (default: markdown).",
)
@click.option(
    "--min-score",
    type=float,
    default=None,
    help="Exit with error if readiness score is below this threshold (0-100).",
)
def ai(
    contract: str,
    output: str | None,
    output_format: str,
    min_score: float | None,
) -> None:
    """Generate AI readiness report for a contract.

    Evaluates how well the contract is documented and structured
    for consumption by AI/ML systems. Provides scores and recommendations.

    CONTRACT is the path to a contract YAML file or Python module.

    Examples:

        griot report ai customer.yaml

        griot report ai contracts/order.yaml -f json

        griot report ai customer.yaml --min-score 70

        griot report ai customer.yaml -o ai_report.md
    """
    from griot_core import generate_ai_readiness_report, load_contract

    try:
        # Load contract
        contract_path = Path(contract)
        echo_info(f"Loading contract from {contract_path}...")
        model = load_contract(str(contract_path))

        # Generate report
        echo_info("Generating AI readiness report...")
        report_data = generate_ai_readiness_report(model)

        # Format output
        if output_format == "json":
            result = report_data.to_json(indent=2)
        else:
            result = report_data.to_markdown()

        # Output
        if output:
            output_path = Path(output)
            output_path.write_text(result)
            echo_success(f"Report saved to {output_path}")
        else:
            click.echo(result)

        # Check minimum score threshold
        if min_score is not None and report_data.readiness_score < min_score:
            echo_error(
                f"AI readiness score ({report_data.readiness_score:.1f}) "
                f"is below minimum threshold ({min_score})"
            )
            sys.exit(1)

        # Display grade summary
        if output:  # Already printed if no output file
            echo_info(
                f"AI Readiness: {report_data.readiness_score:.1f}/100 "
                f"(Grade: {report_data.readiness_grade})"
            )

    except Exception as e:
        echo_error(f"Failed to generate AI readiness report: {e}")
        sys.exit(1)
