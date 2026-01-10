# Getting Started

Welcome to Griot! This section will help you get up and running quickly.

```{toctree}
:maxdepth: 2

installation
quickstart
first-contract
```

## What is Griot?

Griot is a comprehensive data contract framework designed for AI/ML pipelines. It helps you:

- **Define schemas** for your data using Python classes or YAML
- **Validate data** against contracts with detailed error reporting
- **Track privacy** with built-in PII categories and sensitivity levels
- **Enforce compliance** with data residency and masking requirements
- **Generate reports** on data quality and AI readiness

## Architecture

Griot follows a **Core-First** architecture:

```
griot-core (foundation)
    ├── griot-cli (wrapper)
    ├── griot-enforce (runtime)
    ├── griot-registry (API)
    └── griot-hub (UI)
```

All business logic lives in `griot-core`. Other packages are thin wrappers that call core methods.

## Next Steps

1. [Install Griot](installation.md)
2. [Quick Start Tutorial](quickstart.md)
3. [Create Your First Contract](first-contract.md)
