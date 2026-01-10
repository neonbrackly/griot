# Installation

This guide covers installation options for all Griot packages.

## Requirements

- Python 3.10 or higher
- pip (Python package installer)

## Core Library

The core library has **zero external dependencies** and provides all business logic:

```bash
pip install griot-core
```

## Command-Line Interface

Install the CLI for command-line operations:

```bash
pip install griot-cli
```

This installs:
- `griot-core` (dependency)
- `click` (CLI framework)
- `rich` (terminal formatting)

## Runtime Enforcement

Install with your orchestrator of choice:

::::{tab-set}

:::{tab-item} Airflow
```bash
pip install griot-enforce[airflow]
```
:::

:::{tab-item} Dagster
```bash
pip install griot-enforce[dagster]
```
:::

:::{tab-item} Prefect
```bash
pip install griot-enforce[prefect]
```
:::

:::{tab-item} All Orchestrators
```bash
pip install griot-enforce[all]
```
:::

::::

## Registry Server

For the contract registry API:

```bash
pip install griot-registry
```

With specific storage backends:

```bash
# PostgreSQL backend
pip install griot-registry[postgres]

# Git backend
pip install griot-registry[git]

# All backends
pip install griot-registry[all]
```

## Development Installation

For contributing to Griot:

```bash
# Clone the repository
git clone https://github.com/griot/griot.git
cd griot

# Install in development mode
pip install -e "./griot/griot-core[dev]"
pip install -e "./griot/griot-cli[dev]"
pip install -e "./griot/griot-enforce[dev,all]"
pip install -e "./griot/griot-registry[dev,all]"
```

## Verifying Installation

Verify your installation:

```python
>>> import griot_core
>>> griot_core.__version__
'0.1.0'
```

Or with the CLI:

```bash
$ griot --version
griot, version 0.1.0
```

## Next Steps

- [Quick Start Tutorial](quickstart.md)
- [Create Your First Contract](first-contract.md)
