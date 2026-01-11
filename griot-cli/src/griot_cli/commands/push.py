"""griot push command.

Push a contract to the Griot Registry.

SDK Method: Registry API call + detect_breaking_changes
Status: Complete (T-303, T-360, T-361, T-362)
"""
from __future__ import annotations

import sys
from pathlib import Path

import click

from griot_cli.config import load_config
from griot_cli.output import echo_error, echo_info, echo_success, echo_warning


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
    help="Show what would be pushed (includes breaking change check).",
)
@click.option(
    "--allow-breaking",
    is_flag=True,
    help="Allow push even if breaking changes are detected (T-361).",
)
@click.pass_context
def push(
    ctx: click.Context,
    contract: Path,
    registry: str | None,
    message: str | None,
    major: bool,
    dry_run: bool,
    allow_breaking: bool,
) -> None:
    """Push CONTRACT to the Griot Registry.

    CONTRACT is the path to a contract YAML file.

    Breaking changes are validated before push. If breaking changes are
    detected, the push is blocked unless --allow-breaking is specified.

    Exit codes:
      0 - Push successful
      1 - Breaking changes detected (blocked)
      2 - Error

    Examples:
      griot push contracts/customer.yaml -m "Added email_verified field"
      griot push contracts/customer.yaml --major -m "Breaking: removed legacy_id"
      griot push contracts/customer.yaml --allow-breaking -m "Breaking change"
      griot push contracts/customer.yaml --dry-run  # Check for breaking changes
    """
    try:
        from griot_core import GriotModel
        from griot_core.contract import detect_breaking_changes
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
        # Load the new contract
        new_model = GriotModel.from_yaml(contract)

        # Try to fetch existing contract from registry for breaking change check
        existing_model = _fetch_existing_contract(contract, registry_url)
        breaking_changes = []

        if existing_model is not None:
            # Check for breaking changes (T-303)
            breaking_changes = detect_breaking_changes(existing_model, new_model)

        if dry_run:
            # T-362: Enhanced dry-run with breaking change check
            echo_info("Dry run - would push:")
            echo_info(f"  Contract: {contract}")
            echo_info(f"  Name: {new_model.__name__}")
            echo_info(f"  Registry: {registry_url}")
            echo_info(f"  Message: {message or '(none)'}")
            echo_info(f"  Major bump: {major}")

            if breaking_changes:
                echo_warning(f"\nBreaking changes detected ({len(breaking_changes)}):")
                _display_breaking_changes(breaking_changes)
                if not allow_breaking:
                    echo_error("\nPush would be BLOCKED. Use --allow-breaking to force.")
                else:
                    echo_warning("\n--allow-breaking specified. Push would proceed.")
            else:
                echo_success("\nNo breaking changes detected.")
            return

        # T-303/T-360: Block push if breaking changes detected without --allow-breaking
        if breaking_changes and not allow_breaking:
            echo_error(f"BREAKING CHANGES DETECTED ({len(breaking_changes)}):")
            _display_breaking_changes(breaking_changes)
            echo_error("\nPush blocked. Use --allow-breaking to force push.")
            sys.exit(1)

        if breaking_changes and allow_breaking:
            echo_warning(f"Proceeding with {len(breaking_changes)} breaking change(s)...")

        # Push to registry
        _push_to_registry(contract, registry_url, message, major, allow_breaking)

        echo_success(f"Pushed {contract.name} to {registry_url}")

    except FileNotFoundError as e:
        echo_error(f"File not found: {e}")
        sys.exit(2)
    except Exception as e:
        echo_error(f"Error: {e}")
        sys.exit(2)


def _fetch_existing_contract(
    contract_path: Path,
    registry_url: str,
) -> type | None:
    """Fetch existing contract from registry for comparison.

    Args:
        contract_path: Path to the contract YAML file (to extract ID).
        registry_url: Registry base URL.

    Returns:
        GriotModel subclass if contract exists, None otherwise.
    """
    import json
    import urllib.request

    import yaml

    from griot_core import GriotModel
    from griot_core.contract import load_contract_from_dict

    # Load the local YAML to get the contract ID
    with open(contract_path, "r", encoding="utf-8") as f:
        raw_contract = yaml.safe_load(f)

    contract_id = raw_contract.get("id")
    if not contract_id:
        # New contract, no existing version to compare
        return None

    # Try to fetch from registry
    url = f"{registry_url.rstrip('/')}/api/v1/contracts/{contract_id}"

    try:
        request = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(request, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
            # Convert registry response to GriotModel
            return load_contract_from_dict(data)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            # Contract doesn't exist yet
            return None
        # Other errors - log and continue
        return None
    except urllib.error.URLError:
        # Cannot connect to registry - skip breaking change check
        return None


def _display_breaking_changes(breaking_changes: list) -> None:
    """Display breaking changes with details and migration hints.

    Args:
        breaking_changes: List of BreakingChange objects from griot-core.
    """
    import click

    for change in breaking_changes:
        # Format: [change_type] field: description
        field_info = f" on '{change.field}'" if change.field else ""
        click.secho(f"  [{change.change_type.value}]{field_info}", fg="red", bold=True)
        click.echo(f"    {change.description}")
        if change.migration_hint:
            click.echo(f"    Hint: {change.migration_hint}")


def _push_to_registry(
    contract_path: Path,
    registry_url: str,
    message: str | None,
    major: bool,
    allow_breaking: bool = False,
) -> None:
    """Push contract to registry via HTTP API.

    Args:
        contract_path: Path to the contract YAML file.
        registry_url: Registry base URL.
        message: Change notes.
        major: Force major version bump.
        allow_breaking: Whether to allow breaking changes.
    """
    import urllib.request
    import json

    import yaml

    # Load the raw YAML to preserve registry metadata (id, version, status, owner)
    with open(contract_path, "r", encoding="utf-8") as f:
        raw_contract = yaml.safe_load(f)

    # Get the contract ID from the YAML (required for registry)
    contract_id = raw_contract.get("id")

    # Build the payload in registry-compatible format
    # Fields should be a list, not a dict
    fields_data = raw_contract.get("fields", [])

    # Normalize fields to list format if it's a dict (legacy format)
    if isinstance(fields_data, dict):
        fields_list = []
        for field_name, field_def in fields_data.items():
            if isinstance(field_def, dict):
                field_def["name"] = field_name
                fields_list.append(field_def)
        fields_data = fields_list

    # Ensure each field has required structure
    normalized_fields = []
    for field in fields_data:
        normalized_field = {
            "name": field.get("name"),
            "type": field.get("type", "string"),
            "description": field.get("description", ""),
            "nullable": field.get("nullable", False),
            "primary_key": field.get("primary_key", False),
            "unique": field.get("unique", False),
            "constraints": field.get("constraints") or {},
            "metadata": field.get("metadata"),
        }
        normalized_fields.append(normalized_field)

    if contract_id:
        # Update existing contract (PUT)
        payload = {
            "name": raw_contract.get("name"),
            "description": raw_contract.get("description"),
            "fields": normalized_fields,
            "change_type": "major" if major else "minor",
            "change_notes": message,
        }
        # T-372: Add allow_breaking query param for registry
        base_url = f"{registry_url.rstrip('/')}/api/v1/contracts/{contract_id}"
        url = f"{base_url}?allow_breaking=true" if allow_breaking else base_url
        method = "PUT"
    else:
        # Create new contract (POST)
        # Generate an ID from the name if not provided
        name = raw_contract.get("name", "unnamed")
        generated_id = name.lower().replace(" ", "-").replace("_", "-")

        payload = {
            "id": generated_id,
            "name": name,
            "description": raw_contract.get("description"),
            "owner": raw_contract.get("owner"),
            "fields": normalized_fields,
        }
        url = f"{registry_url.rstrip('/')}/api/v1/contracts"
        method = "POST"

    data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method=method,
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
