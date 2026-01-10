"""griot pull command.

Pull a contract from the Griot Registry.

SDK Method: Registry API call
Status: Blocked - waiting on registry T-092 (CRUD endpoints)
"""
from __future__ import annotations

import sys
from pathlib import Path

import click

from griot_cli.config import load_config
from griot_cli.output import echo_error, echo_success


@click.command()
@click.argument("contract_id", type=str)
@click.option(
    "--registry",
    type=str,
    default=None,
    help="Registry URL.",
)
@click.option(
    "--version",
    type=str,
    default=None,
    help="Specific version (default latest).",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    default=None,
    help="Output file.",
)
@click.pass_context
def pull(
    ctx: click.Context,
    contract_id: str,
    registry: str | None,
    version: str | None,
    output: Path | None,
) -> None:
    """Pull CONTRACT_ID from the Griot Registry.

    CONTRACT_ID is the contract identifier in the registry.

    Examples:
      griot pull customer-profile -o contracts/customer.yaml
      griot pull customer-profile --version 1.2.0
    """
    # Get registry URL
    config = load_config(ctx.obj.get("config_path") if ctx.obj else None)
    registry_url = registry or config.registry_url

    if not registry_url:
        echo_error(
            "Registry URL not specified. Use --registry or set GRIOT_REGISTRY_URL env var."
        )
        sys.exit(2)

    try:
        # Pull from registry
        contract_yaml = _pull_from_registry(registry_url, contract_id, version)

        # Output
        if output:
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(contract_yaml)
            echo_success(f"Pulled {contract_id} to {output}")
        else:
            click.echo(contract_yaml)

    except Exception as e:
        echo_error(f"Error: {e}")
        sys.exit(2)


def _pull_from_registry(registry_url: str, contract_id: str, version: str | None) -> str:
    """Pull contract from registry via HTTP API.

    Args:
        registry_url: Registry base URL.
        contract_id: Contract identifier.
        version: Specific version or None for latest.

    Returns:
        Contract YAML string.
    """
    import urllib.request
    import json

    # Build URL
    url = f"{registry_url.rstrip('/')}/api/v1/contracts/{contract_id}"
    if version:
        url += f"?version={version}"

    request = urllib.request.Request(
        url,
        headers={"Accept": "application/x-yaml"},
        method="GET",
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            content_type = response.headers.get("Content-Type", "")
            body = response.read().decode("utf-8")

            # If response is JSON, extract the YAML from it
            if "application/json" in content_type:
                data = json.loads(body)
                if "yaml" in data:
                    return data["yaml"]
                elif "contract" in data:
                    # Convert contract dict to YAML
                    try:
                        import yaml

                        return yaml.safe_dump(data["contract"], default_flow_style=False)
                    except ImportError:
                        return json.dumps(data["contract"], indent=2)
                else:
                    return body
            else:
                return body

    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise RuntimeError(f"Contract '{contract_id}' not found in registry")
        error_body = e.read().decode("utf-8") if e.fp else str(e)
        raise RuntimeError(f"Registry returned {e.code}: {error_body}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"Cannot connect to registry: {e.reason}")
