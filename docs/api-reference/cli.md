# griot-cli API Reference

Command-line interface documentation.

## Installation

```bash
pip install griot-cli
```

## Commands

### griot validate

Validate data against a contract.

```bash
griot validate CONTRACT DATA [OPTIONS]
```

**Arguments:**
- `CONTRACT` - Path to contract file (YAML or Python)
- `DATA` - Path to data file (CSV, JSON, Parquet)

**Options:**
- `--format` - Output format: `table`, `json`, `github` (default: `table`)
- `--strict` - Treat warnings as errors
- `--limit N` - Maximum errors to display
- `--output FILE` - Write results to file

**Examples:**
```bash
# Basic validation
griot validate customer.yaml data.csv

# JSON output
griot validate customer.yaml data.json --format json

# Strict mode
griot validate customer.yaml data.csv --strict
```

**Exit Codes:**
- `0` - Validation passed
- `1` - Validation failed
- `2` - Contract error

---

### griot lint

Check contract quality.

```bash
griot lint CONTRACT [OPTIONS]
```

**Arguments:**
- `CONTRACT` - Path to contract file

**Options:**
- `--format` - Output format: `table`, `json`, `github`
- `--severity` - Minimum severity: `info`, `warning`, `error`
- `--strict` - Treat warnings as errors

**Examples:**
```bash
# Basic lint
griot lint customer.yaml

# Only errors
griot lint customer.yaml --severity error

# GitHub Actions format
griot lint customer.yaml --format github
```

---

### griot diff

Compare contract versions.

```bash
griot diff CONTRACT1 CONTRACT2 [OPTIONS]
```

**Arguments:**
- `CONTRACT1` - Path to first contract (base)
- `CONTRACT2` - Path to second contract (target)

**Options:**
- `--format` - Output format: `table`, `json`, `markdown`
- `--breaking-only` - Show only breaking changes

**Examples:**
```bash
# Compare versions
griot diff customer_v1.yaml customer_v2.yaml

# Breaking changes only
griot diff customer_v1.yaml customer_v2.yaml --breaking-only
```

---

### griot mock

Generate mock data.

```bash
griot mock CONTRACT [OPTIONS]
```

**Arguments:**
- `CONTRACT` - Path to contract file

**Options:**
- `--rows N` - Number of rows to generate (default: 10)
- `--output FILE` - Output file path
- `--format` - Output format: `csv`, `json`, `parquet`
- `--seed N` - Random seed for reproducibility

**Examples:**
```bash
# Generate 100 rows
griot mock customer.yaml --rows 100

# Output to CSV
griot mock customer.yaml --rows 1000 --output test_data.csv

# Reproducible output
griot mock customer.yaml --rows 50 --seed 42
```

---

### griot manifest

Export contract manifest.

```bash
griot manifest CONTRACT [OPTIONS]
```

**Arguments:**
- `CONTRACT` - Path to contract file

**Options:**
- `--format` - Export format: `json_ld`, `markdown`, `llm_context`
- `--output FILE` - Output file path

**Examples:**
```bash
# JSON-LD for knowledge graphs
griot manifest customer.yaml --format json_ld

# Markdown documentation
griot manifest customer.yaml --format markdown --output docs/customer.md

# LLM context
griot manifest customer.yaml --format llm_context
```

---

### griot report

Generate reports.

```bash
griot report SUBCOMMAND CONTRACT [OPTIONS]
```

**Subcommands:**
- `analytics` - Generate analytics report
- `ai` - Generate AI readiness report
- `audit` - Generate audit report
- `all` - Generate all reports

**Options:**
- `--format` - Output format: `table`, `json`, `markdown`
- `--output DIR` - Output directory
- `--min-score N` - Minimum AI readiness score (exit 1 if below)

**Examples:**
```bash
# Analytics report
griot report analytics customer.yaml

# AI readiness with threshold
griot report ai customer.yaml --min-score 70

# All reports to directory
griot report all customer.yaml --output reports/
```

---

### griot push

Push contract to registry.

```bash
griot push CONTRACT [OPTIONS]
```

**Options:**
- `--registry URL` - Registry URL
- `--api-key KEY` - API key
- `--version VERSION` - Version tag

---

### griot pull

Pull contract from registry.

```bash
griot pull NAME [OPTIONS]
```

**Options:**
- `--registry URL` - Registry URL
- `--version VERSION` - Specific version
- `--output FILE` - Output file path

---

## Configuration

### Config File

Create `.griot.yaml` or `griot.yaml`:

```yaml
registry:
  url: https://registry.example.com
  api_key: ${GRIOT_API_KEY}

defaults:
  format: table
  strict: false
```

### Environment Variables

- `GRIOT_REGISTRY_URL` - Default registry URL
- `GRIOT_API_KEY` - API key for registry
- `GRIOT_CONFIG` - Path to config file

## Shell Completion

```bash
# Bash
eval "$(_GRIOT_COMPLETE=bash_source griot)"

# Zsh
eval "$(_GRIOT_COMPLETE=zsh_source griot)"

# Fish
_GRIOT_COMPLETE=fish_source griot | source
```
