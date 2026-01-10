"""griot manifest command.

Export contract metadata for AI/LLM consumption.

SDK Method: GriotModel.to_manifest()
Status: Blocked - waiting on core T-014 (manifest generation)
"""
from __future__ import annotations

import sys
from pathlib import Path

import click

from griot_cli.output import echo_error, echo_success


@click.command()
@click.argument("contract", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json_ld", "markdown", "llm_context"]),
    default="json_ld",
    help="Output format.",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    default=None,
    help="Output file (default stdout).",
)
@click.pass_context
def manifest(
    ctx: click.Context,
    contract: Path,
    format: str,
    output: Path | None,
) -> None:
    """Export CONTRACT metadata for AI/LLM consumption.

    CONTRACT is the path to a contract YAML file.

    Formats:
      json_ld     - JSON-LD schema for semantic web
      markdown    - Human-readable Markdown documentation
      llm_context - Compact format optimized for LLM context windows

    Examples:
      griot manifest contracts/customer.yaml -f markdown
      griot manifest contracts/customer.yaml -f llm_context -o context.txt
    """
    try:
        from griot_core import GriotModel
    except ImportError:
        echo_error("griot-core is not installed. Install with: pip install griot-core")
        sys.exit(2)

    try:
        # Load contract
        model = GriotModel.from_yaml(contract)

        # Generate manifest
        manifest_content = model.to_manifest(format=format)

        # Output
        if output:
            output.write_text(manifest_content)
            echo_success(f"Manifest written to {output}")
        else:
            click.echo(manifest_content)

    except FileNotFoundError as e:
        echo_error(f"File not found: {e}")
        sys.exit(2)
    except Exception as e:
        echo_error(f"Error: {e}")
        sys.exit(2)
