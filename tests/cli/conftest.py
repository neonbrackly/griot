"""
Griot CLI Test Suite - Shared Fixtures and Configuration

Provides common fixtures for testing griot-cli.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Add griot-cli and griot-core to path for testing
GRIOT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(GRIOT_ROOT / "griot-cli" / "src"))
sys.path.insert(0, str(GRIOT_ROOT / "griot-core" / "src"))
