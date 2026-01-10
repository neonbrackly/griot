"""griot push command.

Push a contract to the Griot Registry.

SDK Method: Registry API call
Status: Blocked - waiting on registry T-092 (CRUD endpoints)
"""
from __future__ import annotations

import sys
from pathlib import Path

import click

from griot_cli.config import load_config
from griot_cli.output import echo_error, echo_info, echo_success


@click.command()
@click.argument("contract", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--registry",
    type=str,
    default=None,
    help="Registry URL (or GRIOT_REGISTRY_URL env var).",
)
@click.option(
    "--message",
    "-m",
    type=str,
    default=None,
    help="Change notes.",
)
@click.option(
    "--major",
    is_flag=True,
    help="Force major version bump.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be pushed.",
)
@click.pass_context
def push(
    ctx: click.Context,
    contract: Path,
    registry: str | None,
    message: str | None,
    major: bool,
    dry_run: bool,
) -> None:
    """Push CONTRACT to the Griot Registry.

    CONTRACT is the path to a contract YAML file.

    Examples:
      griot push contracts/customer.yaml -m "Added email_verified field"
      griot push contracts/customer.yaml --major -m "Breaking: removed legacy_id"
    """
    try:
        from griot_core import GriotModel
    except ImportError:
        echo_error("griot-core is not installed. Install with: pip install griot-core")
        sys.exit(2)

    # Get registry URL
    config = load_config(ctx.obj.get("config_path") if ctx.obj else None)
    registry_url = registry or config.registry_url

    if not registry_url:
        echo_error(
            "Registry URL not specified. Use --registry or set GRIOT_REGISTRY_URL env var."
        )
        sys.exit(2)

    try:
        # Load contract
        model = GriotModel.from_yaml(contract)

        if dry_run:
            echo_info("Dry run - would push:")
            echo_info(f"  Contract: {contract}")
            echo_info(f"  Registry: {registry_url}")
            echo_info(f"  Message: {message or '(none)'}")
            echo_info(f"  Major bump: {major}")
            return

        # Push to registry
        # Note: This requires a registry client which will be implemented later
        # For now, we make an HTTP request directly
        _push_to_registry(model, registry_url, message, major)

        echo_success(f"Pushed {contract.name} to {registry_url}")

    except FileNotFoundError as e:
        echo_error(f"File not found: {e}")
        sys.exit(2)
    except Exception as e:
        echo_error(f"Error: {e}")
        sys.exit(2)


def _push_to_registry(model, registry_url: str, message: str | None, major: bool) -> None:
    """Push contract to registry via HTTP API.

    Args:
        model: GriotModel instance.
        registry_url: Registry base URL.
        message: Change notes.
        major: Force major version bump.
    """
    import urllib.request
    import json

    # Prepare request
    contract_dict = model.to_dict()
    payload = {
        "contract": contract_dict,
        "message": message,
        "major": major,
    }

    url = f"{registry_url.rstrip('/')}/api/v1/contracts"
    data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
            echo_info(f"Version: {result.get('version', 'unknown')}")
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else str(e)
        raise RuntimeError(f"Registry returned {e.code}: {error_body}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"Cannot connect to registry: {e.reason}")
