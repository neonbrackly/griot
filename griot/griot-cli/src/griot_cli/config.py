"""Configuration handling for Griot CLI.

This module handles:
- Finding and loading configuration files (.griot.yaml, griot.yaml)
- Environment variable overrides (GRIOT_*)
- Default configuration values
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Configuration file names to search for
CONFIG_FILE_NAMES = [".griot.yaml", ".griot.yml", "griot.yaml", "griot.yml"]


@dataclass
class GriotConfig:
    """Configuration for Griot CLI.

    Attributes:
        registry_url: URL of the Griot Registry server.
        default_format: Default output format (table, json, github).
        max_errors: Maximum number of errors to display.
        color: Whether to use colored output.
    """

    registry_url: str | None = None
    default_format: str = "table"
    max_errors: int = 100
    color: bool = True
    extra: dict[str, Any] = field(default_factory=dict)


def find_config_file(start_path: Path | None = None) -> Path | None:
    """Find a Griot configuration file by searching upward from start_path.

    Args:
        start_path: Directory to start searching from. Defaults to current directory.

    Returns:
        Path to configuration file if found, None otherwise.
    """
    if start_path is None:
        start_path = Path.cwd()

    current = start_path.resolve()

    while current != current.parent:
        for name in CONFIG_FILE_NAMES:
            config_path = current / name
            if config_path.is_file():
                return config_path
        current = current.parent

    return None


def load_config(config_path: Path | None = None) -> GriotConfig:
    """Load configuration from file and environment variables.

    Priority (highest to lowest):
    1. Environment variables (GRIOT_*)
    2. Explicit config file path
    3. Auto-discovered config file
    4. Default values

    Args:
        config_path: Explicit path to configuration file.

    Returns:
        GriotConfig instance with merged configuration.
    """
    config = GriotConfig()

    # Try to load from file
    if config_path is None:
        config_path = find_config_file()

    if config_path is not None and config_path.is_file():
        config = _load_config_file(config_path, config)

    # Environment variable overrides
    config = _apply_env_overrides(config)

    return config


def _load_config_file(path: Path, config: GriotConfig) -> GriotConfig:
    """Load configuration from a YAML file.

    Args:
        path: Path to the configuration file.
        config: Existing config to update.

    Returns:
        Updated GriotConfig instance.
    """
    try:
        import yaml

        with path.open() as f:
            data = yaml.safe_load(f) or {}

        if "registry_url" in data:
            config.registry_url = data["registry_url"]
        if "default_format" in data:
            config.default_format = data["default_format"]
        if "max_errors" in data:
            config.max_errors = int(data["max_errors"])
        if "color" in data:
            config.color = bool(data["color"])

        # Store any extra configuration
        known_keys = {"registry_url", "default_format", "max_errors", "color"}
        config.extra = {k: v for k, v in data.items() if k not in known_keys}

    except ImportError:
        # PyYAML not installed, skip file loading
        pass
    except Exception:
        # Invalid YAML or other error, use defaults
        pass

    return config


def _apply_env_overrides(config: GriotConfig) -> GriotConfig:
    """Apply environment variable overrides to configuration.

    Environment variables:
    - GRIOT_REGISTRY_URL: Registry server URL
    - GRIOT_DEFAULT_FORMAT: Default output format
    - GRIOT_MAX_ERRORS: Maximum errors to display
    - GRIOT_COLOR: Enable/disable colored output (1/0, true/false)

    Args:
        config: Existing config to update.

    Returns:
        Updated GriotConfig instance.
    """
    if "GRIOT_REGISTRY_URL" in os.environ:
        config.registry_url = os.environ["GRIOT_REGISTRY_URL"]

    if "GRIOT_DEFAULT_FORMAT" in os.environ:
        config.default_format = os.environ["GRIOT_DEFAULT_FORMAT"]

    if "GRIOT_MAX_ERRORS" in os.environ:
        try:
            config.max_errors = int(os.environ["GRIOT_MAX_ERRORS"])
        except ValueError:
            pass

    if "GRIOT_COLOR" in os.environ:
        value = os.environ["GRIOT_COLOR"].lower()
        config.color = value in ("1", "true", "yes", "on")

    return config
