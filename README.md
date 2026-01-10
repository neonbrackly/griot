# Griot

**Data Contract Management Platform**

Griot helps organizations define, validate, and enforce data contracts across their data infrastructure.

## Components

| Component | Description | Language |
|-----------|-------------|----------|
| `griot-core` | Core library with all business logic | Python |
| `griot-cli` | Command-line interface | Python (Click) |
| `griot-enforce` | Runtime validation for orchestrators | Python |
| `griot-registry` | Contract storage and API | Python (FastAPI) |
| `griot-hub` | Web interface | TypeScript (Next.js) |

## Quick Start

```bash
# Install SDK
pip install griot-core

# Install CLI
pip install griot-cli

# Validate data
griot validate contracts/customer.yaml data/customers.csv
```

## Architecture

All business logic lives in `griot-core`. Other components are thin wrappers:

```
griot/                                    # Monorepo root
│
├── griot-core/                            # Core library (foundation)
│   ├── pyproject.toml
│   ├── README.md
│   └── src/griot_core/
│       ├── __init__.py                   # Public API exports
│       ├── models.py                     # GriotModel, Field
│       ├── contract.py                   # Contract class
│       ├── types.py                      # Enums, type definitions
│       ├── constraints.py                # Constraint logic
│       ├── validation.py                 # Validation engine
│       ├── mock.py                       # Mock data generator
│       ├── manifest.py                   # AI manifest export
│       └── exceptions.py                 # Custom exceptions
│
├── griot-cli/                            # Command-line interface
│   ├── pyproject.toml
│   └── src/griot_cli/
│       ├── __init__.py
│       ├── main.py                       # Entry point, Click app
│       ├── commands/
│       │   ├── validate.py               # griot validate
│       │   ├── lint.py                   # griot lint
│       │   ├── diff.py                   # griot diff
│       │   ├── mock.py                   # griot mock
│       │   ├── push.py                   # griot push
│       │   ├── pull.py                   # griot pull
│       │   └── manifest.py               # griot manifest
│       ├── config.py                     # Configuration handling
│       └── output.py                     # Formatting, colors
│
├── griot-enforce/                        # Runtime validation
│   ├── pyproject.toml
│   └── src/griot_enforce/
│       ├── __init__.py
│       ├── validator.py                  # Core RuntimeValidator
│       ├── airflow/
│       │   ├── __init__.py
│       │   ├── operators.py              # GriotValidateOperator
│       │   └── sensors.py                # GriotFreshnessSensor
│       ├── dagster/
│       │   ├── __init__.py
│       │   ├── resources.py              # GriotResource
│       │   └── decorators.py             # @griot_asset
│       └── prefect/
│           └── tasks.py                  # @task decorator
│
├── griot-registry/                       # Contract registry server
│   ├── pyproject.toml
│   ├── Dockerfile
│   └── src/griot_registry/
│       ├── __init__.py
│       ├── server.py                     # FastAPI app
│       ├── api/
│       │   ├── contracts.py              # CRUD endpoints
│       │   ├── validations.py            # Validation reports
│       │   └── search.py                 # Search endpoints
│       ├── storage/
│       │   ├── base.py                   # Abstract backend
│       │   ├── filesystem.py             # File-based storage
│       │   ├── git.py                    # Git-backed storage
│       │   └── postgres.py               # PostgreSQL backend
│       └── auth/
│           ├── api_key.py                # API key auth
│           └── oauth.py                  # OAuth2/OIDC
│
├── griot-hub/                            # Web UI (Next.js)
│   ├── package.json
│   ├── Dockerfile
│   └── src/
│       ├── app/                          # Next.js app router
│       │   ├── page.tsx                  # Home/dashboard
│       │   ├── contracts/                # Contract browser
│       │   ├── studio/                   # Contract Studio
│       │   ├── monitor/                  # Validation monitor
│       │   └── settings/                 # User settings
│       ├── components/                   # React components
│       │   ├── ContractCard.tsx
│       │   ├── FieldEditor.tsx
│       │   └── ValidationBadge.tsx
│       └── lib/                          # Utilities
│           ├── api.ts                    # Registry API client
│           └── types.ts                  # TypeScript types
│
├── docs/                                 # Documentation (MkDocs)
│   ├── index.md
│   ├── getting-started/
│   ├── guides/
│   └── api-reference/
│
├── examples/                             # Example contracts
│   ├── customer_churn.py
│   ├── transactions.yaml
│   └── airflow_dag/
│
├── .github/                              # GitHub workflows
│   └── workflows/
│       ├── test.yml
│       └── release.yml
│
├── pyproject.toml                        # Meta-package: pip install griot[all]
├── README.md
└── LICENSE
```

## License

Apache 2.0