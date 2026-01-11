"""Griot CLI - Data Contract Management Command-Line Interface.

This module provides the main entry point for the griot CLI application.
All business logic is delegated to griot-core; this module only handles
argument parsing, output formatting, and exit codes.
"""
from __future__ import annotations

import sys

import click

from griot_cli.commands import diff, init, lint, manifest, migrate, mock, pull, push, report, residency, validate


@click.group()
@click.version_option(package_name="griot-cli")
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    help="Path to configuration file.",
)
@click.pass_context
def cli(ctx: click.Context, config: str | None) -> None:
    """Griot - Data Contract Management CLI.

    Define, validate, and manage data contracts with confidence.
    """
    ctx.ensure_object(dict)
    ctx.obj["config_path"] = config


cli.add_command(init.init)
cli.add_command(validate.validate)
cli.add_command(lint.lint)
cli.add_command(diff.diff)
cli.add_command(mock.mock)
cli.add_command(manifest.manifest)
cli.add_command(push.push)
cli.add_command(pull.pull)
cli.add_command(migrate.migrate)
cli.add_command(report.report)
cli.add_command(residency.residency)


def main() -> int:
    """Main entry point for the CLI."""
    try:
        cli()
        return 0
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        return 2


if __name__ == "__main__":
    sys.exit(main())
