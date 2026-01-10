"""Griot CLI - Command-line interface for data contract management.

This package provides a thin wrapper over griot-core, handling only:
- Argument parsing (via Click)
- Output formatting (table, JSON, GitHub Actions)
- Exit codes

All business logic is delegated to griot-core.
"""
from __future__ import annotations

__version__ = "0.1.0"
