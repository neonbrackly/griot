"""Contract validation service.

Uses griot-core's validation functions to validate contracts
before storage operations.
"""

from dataclasses import dataclass
from typing import Any

from griot_core import (
    Contract,
    Severity,
    lint_contract,
    LintIssue,
    validate_contract_structure,
    ContractStructureResult,
)

from griot_registry.config import Settings


@dataclass
class ValidationResult:
    """Result of contract validation."""

    is_valid: bool
    has_errors: bool
    has_warnings: bool
    lint_issues: list[LintIssue]
    structure_result: ContractStructureResult
    blocking_issues: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "is_valid": self.is_valid,
            "has_errors": self.has_errors,
            "has_warnings": self.has_warnings,
            "error_count": sum(1 for i in self.lint_issues if i.severity == Severity.ERROR),
            "warning_count": sum(1 for i in self.lint_issues if i.severity == Severity.WARNING),
            "lint_issues": [
                {
                    "code": i.code,
                    "field": i.field,
                    "message": i.message,
                    "severity": i.severity.value,
                    "suggestion": i.suggestion,
                }
                for i in self.lint_issues
            ],
            "structure": self.structure_result.to_dict(),
            "blocking_issues": self.blocking_issues,
        }


class ValidationService:
    """Service for validating contracts using griot-core.

    This service wraps griot-core's validation functions and
    provides a unified interface for the registry API.
    """

    def __init__(self, settings: Settings):
        self.settings = settings

    def validate(self, contract: Contract) -> ValidationResult:
        """Validate a contract using griot-core.

        Runs both lint_contract and validate_contract_structure from griot-core.

        Args:
            contract: The Contract to validate

        Returns:
            ValidationResult with all issues found
        """
        # Run griot-core validation
        lint_issues = lint_contract(contract)
        structure_result = validate_contract_structure(contract)

        # Determine if there are errors/warnings
        has_errors = any(i.severity == Severity.ERROR for i in lint_issues)
        has_warnings = any(i.severity == Severity.WARNING for i in lint_issues)

        # Also check structure result
        if not structure_result.is_valid:
            has_errors = True

        # Determine blocking issues based on settings
        blocking_issues: list[dict[str, Any]] = []

        if self.settings.block_on_lint_errors:
            blocking_issues.extend([
                {
                    "code": i.code,
                    "field": i.field,
                    "message": i.message,
                    "severity": "error",
                    "suggestion": i.suggestion,
                }
                for i in lint_issues
                if i.severity == Severity.ERROR
            ])

        if self.settings.block_on_lint_warnings:
            blocking_issues.extend([
                {
                    "code": i.code,
                    "field": i.field,
                    "message": i.message,
                    "severity": "warning",
                    "suggestion": i.suggestion,
                }
                for i in lint_issues
                if i.severity == Severity.WARNING
            ])

        # Add structure issues to blocking if they're errors
        if self.settings.block_on_lint_errors:
            for issue in structure_result.issues:
                if issue.severity == Severity.ERROR:
                    blocking_issues.append({
                        "code": issue.code,
                        "field": issue.path,
                        "message": issue.message,
                        "severity": "error",
                        "suggestion": issue.suggestion,
                    })

        # Determine overall validity
        is_valid = not blocking_issues

        return ValidationResult(
            is_valid=is_valid,
            has_errors=has_errors,
            has_warnings=has_warnings,
            lint_issues=lint_issues,
            structure_result=structure_result,
            blocking_issues=blocking_issues,
        )

    def should_validate_on_create(self) -> bool:
        """Check if validation should run on contract creation."""
        return self.settings.validate_on_create

    def should_validate_on_update(self) -> bool:
        """Check if validation should run on contract update."""
        return self.settings.validate_on_update
