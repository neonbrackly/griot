"""Griot CLI commands package.

Each command is a thin wrapper that:
1. Parses arguments with Click
2. Calls the corresponding griot-core SDK method
3. Formats and displays the result

NO BUSINESS LOGIC should be implemented here.
"""
from __future__ import annotations

from griot_cli.commands import diff, init, lint, manifest, mock, pull, push, report, residency, validate

__all__ = ["validate", "lint", "diff", "mock", "manifest", "push", "pull", "report", "residency", "init"]
