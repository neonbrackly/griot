"""PII detection patterns for automatic identification.

Patterns organized by region/standard:
- Kenya: National ID, KRA PIN, Safaricom numbers
- EU: IBAN, VAT numbers, National IDs
- Universal: Email, credit card, phone, etc.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable

from griot_core.types import PIIType, ComplianceFramework


@dataclass
class PIIPattern:
    """Pattern definition for PII detection."""

    name: str
    """Human-readable name for this pattern."""

    pii_type: PIIType
    """Type of PII this pattern detects."""

    pattern: str
    """Regex pattern string."""

    description: str
    """Description of what this pattern matches."""

    confidence: float = 0.9
    """Confidence level (0-1) that a match is actually PII."""

    validator: Callable[[str], bool] | None = None
    """Optional function to validate matches (e.g., Luhn check for credit cards)."""

    frameworks: list[ComplianceFramework] | None = None
    """Compliance frameworks this pattern is relevant to."""

    region: str = "universal"
    """Geographic region this pattern applies to."""

    def __post_init__(self):
        """Compile the regex pattern."""
        self._compiled = re.compile(self.pattern, re.IGNORECASE)

    def match(self, value: str) -> bool:
        """Check if value matches this pattern."""
        if not isinstance(value, str):
            return False

        if not self._compiled.search(value):
            return False

        # Run additional validation if provided
        if self.validator:
            return self.validator(value)

        return True

    def find_all(self, text: str) -> list[str]:
        """Find all matches in text."""
        if not isinstance(text, str):
            return []
        return self._compiled.findall(text)


# ============================================================================
# Validation functions
# ============================================================================


def luhn_check(card_number: str) -> bool:
    """Validate credit card number using Luhn algorithm."""
    # Extract digits only
    digits = re.sub(r"\D", "", card_number)
    if len(digits) < 13 or len(digits) > 19:
        return False

    # Luhn algorithm
    total = 0
    reverse_digits = digits[::-1]
    for i, digit in enumerate(reverse_digits):
        n = int(digit)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n

    return total % 10 == 0


def kenya_id_check(id_number: str) -> bool:
    """Validate Kenya National ID format."""
    # Kenya IDs are 7-8 digits
    digits = re.sub(r"\D", "", id_number)
    return 7 <= len(digits) <= 8


def kra_pin_check(pin: str) -> bool:
    """Validate Kenya KRA PIN format."""
    # Format: A followed by 9 digits and a letter
    pattern = r"^[A-Z]\d{9}[A-Z]$"
    return bool(re.match(pattern, pin.upper()))


def iban_check(iban: str) -> bool:
    """Validate IBAN using mod 97 check."""
    # Remove spaces and convert to uppercase
    iban = iban.replace(" ", "").upper()

    # Basic format check
    if len(iban) < 15 or len(iban) > 34:
        return False

    # Move first 4 chars to end
    rearranged = iban[4:] + iban[:4]

    # Convert letters to numbers (A=10, B=11, etc.)
    numeric = ""
    for char in rearranged:
        if char.isdigit():
            numeric += char
        else:
            numeric += str(ord(char) - ord("A") + 10)

    # Check mod 97
    return int(numeric) % 97 == 1


# ============================================================================
# Kenya-specific patterns
# ============================================================================

KENYA_PATTERNS = [
    PIIPattern(
        name="Kenya National ID",
        pii_type=PIIType.NATIONAL_ID,
        pattern=r"\b\d{7,8}\b",
        description="Kenya National ID number (7-8 digits)",
        confidence=0.7,  # Lower confidence as it's just digits
        validator=kenya_id_check,
        frameworks=[ComplianceFramework.KENYA_DPA],
        region="kenya",
    ),
    PIIPattern(
        name="KRA PIN",
        pii_type=PIIType.TAX_ID,
        pattern=r"\b[A-Z]\d{9}[A-Z]\b",
        description="Kenya Revenue Authority PIN (e.g., A123456789B)",
        confidence=0.95,
        validator=kra_pin_check,
        frameworks=[ComplianceFramework.KENYA_DPA],
        region="kenya",
    ),
    PIIPattern(
        name="Kenya Phone (Safaricom)",
        pii_type=PIIType.PHONE,
        pattern=r"\b(?:\+?254|0)?7[0-9]{8}\b",
        description="Kenya mobile number (Safaricom format)",
        confidence=0.9,
        frameworks=[ComplianceFramework.KENYA_DPA],
        region="kenya",
    ),
    PIIPattern(
        name="Kenya Phone (Airtel)",
        pii_type=PIIType.PHONE,
        pattern=r"\b(?:\+?254|0)?(?:73|78|75)[0-9]{7}\b",
        description="Kenya mobile number (Airtel format)",
        confidence=0.9,
        frameworks=[ComplianceFramework.KENYA_DPA],
        region="kenya",
    ),
    PIIPattern(
        name="Kenya Phone (Telkom)",
        pii_type=PIIType.PHONE,
        pattern=r"\b(?:\+?254|0)?77[0-9]{7}\b",
        description="Kenya mobile number (Telkom format)",
        confidence=0.9,
        frameworks=[ComplianceFramework.KENYA_DPA],
        region="kenya",
    ),
]


# ============================================================================
# EU-specific patterns
# ============================================================================

EU_PATTERNS = [
    PIIPattern(
        name="IBAN",
        pii_type=PIIType.IBAN,
        pattern=r"\b[A-Z]{2}\d{2}[A-Z0-9]{4,30}\b",
        description="International Bank Account Number",
        confidence=0.85,
        validator=iban_check,
        frameworks=[ComplianceFramework.GDPR],
        region="eu",
    ),
    PIIPattern(
        name="EU VAT Number",
        pii_type=PIIType.TAX_ID,
        pattern=r"\b[A-Z]{2}\d{8,12}\b",
        description="EU VAT registration number",
        confidence=0.8,
        frameworks=[ComplianceFramework.GDPR],
        region="eu",
    ),
    PIIPattern(
        name="German ID (Personalausweis)",
        pii_type=PIIType.NATIONAL_ID,
        pattern=r"\b[CFGHJKLMNPRTVWXYZ0-9]{9}\b",
        description="German personal ID number",
        confidence=0.7,
        frameworks=[ComplianceFramework.GDPR],
        region="eu",
    ),
    PIIPattern(
        name="French INSEE",
        pii_type=PIIType.NATIONAL_ID,
        pattern=r"\b[12]\d{2}(?:0[1-9]|1[0-2])\d{8}\b",
        description="French social security number (INSEE)",
        confidence=0.85,
        frameworks=[ComplianceFramework.GDPR],
        region="eu",
    ),
    PIIPattern(
        name="UK National Insurance",
        pii_type=PIIType.NATIONAL_ID,
        pattern=r"\b[A-CEGHJ-PR-TW-Z]{2}\d{6}[A-D]\b",
        description="UK National Insurance Number",
        confidence=0.9,
        frameworks=[ComplianceFramework.GDPR],
        region="eu",
    ),
]


# ============================================================================
# Universal patterns
# ============================================================================

UNIVERSAL_PATTERNS = [
    PIIPattern(
        name="Email Address",
        pii_type=PIIType.EMAIL,
        pattern=r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        description="Email address",
        confidence=0.95,
        region="universal",
    ),
    PIIPattern(
        name="Credit Card (Visa)",
        pii_type=PIIType.CREDIT_CARD,
        pattern=r"\b4[0-9]{12}(?:[0-9]{3})?\b",
        description="Visa credit card number",
        confidence=0.9,
        validator=luhn_check,
        frameworks=[ComplianceFramework.PCI_DSS],
        region="universal",
    ),
    PIIPattern(
        name="Credit Card (Mastercard)",
        pii_type=PIIType.CREDIT_CARD,
        pattern=r"\b(?:5[1-5][0-9]{2}|222[1-9]|22[3-9][0-9]|2[3-6][0-9]{2}|27[01][0-9]|2720)[0-9]{12}\b",
        description="Mastercard credit card number",
        confidence=0.9,
        validator=luhn_check,
        frameworks=[ComplianceFramework.PCI_DSS],
        region="universal",
    ),
    PIIPattern(
        name="Credit Card (Amex)",
        pii_type=PIIType.CREDIT_CARD,
        pattern=r"\b3[47][0-9]{13}\b",
        description="American Express credit card number",
        confidence=0.9,
        validator=luhn_check,
        frameworks=[ComplianceFramework.PCI_DSS],
        region="universal",
    ),
    PIIPattern(
        name="Credit Card (Generic)",
        pii_type=PIIType.CREDIT_CARD,
        pattern=r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
        description="Credit card number (generic format with separators)",
        confidence=0.8,
        validator=luhn_check,
        frameworks=[ComplianceFramework.PCI_DSS],
        region="universal",
    ),
    PIIPattern(
        name="US SSN",
        pii_type=PIIType.SSN,
        pattern=r"\b\d{3}-\d{2}-\d{4}\b",
        description="US Social Security Number",
        confidence=0.9,
        frameworks=[ComplianceFramework.CCPA],
        region="us",
    ),
    PIIPattern(
        name="Phone (International)",
        pii_type=PIIType.PHONE,
        # Requires '+' OR a long string of digits (7-15) starting with a non-zero
        pattern=r"\b(\+[1-9]\d{6,14}|[1-9]\d{8,14})\b",
        description="International phone number (Minimum 7-9 digits to avoid IDs)",
        confidence=0.7,
        region="universal",
    ),
    PIIPattern(
        name="Phone (US/Canada)",
        pii_type=PIIType.PHONE,
        pattern=r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
        description="US/Canada phone number",
        confidence=0.85,
        region="universal",
    ),
    PIIPattern(
        name="IPv4 Address",
        pii_type=PIIType.IP_ADDRESS,
        pattern=r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b",
        description="IPv4 address",
        confidence=0.95,
        region="universal",
    ),
    PIIPattern(
        name="IPv6 Address",
        pii_type=PIIType.IP_ADDRESS,
        pattern=r"\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b",
        description="IPv6 address (full format)",
        confidence=0.95,
        region="universal",
    ),
    PIIPattern(
        name="MAC Address",
        pii_type=PIIType.MAC_ADDRESS,
        pattern=r"\b(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b",
        description="MAC address",
        confidence=0.95,
        region="universal",
    ),
    PIIPattern(
        name="Date of Birth",
        pii_type=PIIType.DATE_OF_BIRTH,
        pattern=r"\b(?:19|20)\d{2}[-/](?:0[1-9]|1[0-2])[-/](?:0[1-9]|[12]\d|3[01])\b",
        description="Date in YYYY-MM-DD format (potential DOB)",
        confidence=0.5,  # Low confidence as it could be any date
        region="universal",
    ),
    PIIPattern(
        name="US Passport",
        pii_type=PIIType.PASSPORT,
        pattern=r"\b[A-Z]\d{8}\b",
        description="US passport number",
        confidence=0.75,
        region="us",
    ),
]


# ============================================================================
# Pattern Registry
# ============================================================================


class PIIPatternRegistry:
    """Registry of PII detection patterns.

    Usage:
        registry = PIIPatternRegistry()
        registry.add_patterns(KENYA_PATTERNS)

        # Detect PII in a value
        matches = registry.detect(value)
        for pattern, confidence in matches:
            print(f"Detected {pattern.pii_type}: {confidence}")
    """

    def __init__(self):
        """Initialize empty registry."""
        self._patterns: list[PIIPattern] = []

    def add_pattern(self, pattern: PIIPattern) -> None:
        """Add a single pattern to registry."""
        self._patterns.append(pattern)

    def add_patterns(self, patterns: list[PIIPattern]) -> None:
        """Add multiple patterns to registry."""
        self._patterns.extend(patterns)

    def detect(self, value: str) -> list[tuple[PIIPattern, float]]:
        """Detect PII in a value.

        Args:
            value: String value to check

        Returns:
            List of (pattern, confidence) tuples for matches
        """
        if not isinstance(value, str) or not value:
            return []

        matches = []
        for pattern in self._patterns:
            if pattern.match(value):
                matches.append((pattern, pattern.confidence))

        # Sort by confidence (highest first)
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches

    def detect_in_column(
        self, values: list[str], sample_size: int = 100
    ) -> dict[PIIType, float]:
        """Detect PII types in a column of values.

        Samples values and returns PII types with their detection rates.

        Args:
            values: List of string values
            sample_size: Number of values to sample

        Returns:
            Dict mapping PIIType to detection rate (0-1)
        """
        if not values:
            return {}

        # Sample values
        import random

        sample = random.sample(values, min(sample_size, len(values)))

        # Count detections by type
        type_counts: dict[PIIType, int] = {}
        total_checked = 0

        for value in sample:
            if value is None or (isinstance(value, float) and value != value):
                continue  # Skip None and NaN

            total_checked += 1
            matches = self.detect(str(value))
            for pattern, _ in matches:
                type_counts[pattern.pii_type] = type_counts.get(pattern.pii_type, 0) + 1

        if total_checked == 0:
            return {}

        # Convert to rates
        return {
            pii_type: count / total_checked for pii_type, count in type_counts.items()
        }

    def get_patterns_by_region(self, region: str) -> list[PIIPattern]:
        """Get patterns for a specific region."""
        return [p for p in self._patterns if p.region == region]

    def get_patterns_by_framework(
        self, framework: ComplianceFramework
    ) -> list[PIIPattern]:
        """Get patterns relevant to a compliance framework."""
        return [
            p
            for p in self._patterns
            if p.frameworks and framework in p.frameworks
        ]

    def get_patterns_by_type(self, pii_type: PIIType) -> list[PIIPattern]:
        """Get patterns for a specific PII type."""
        return [p for p in self._patterns if p.pii_type == pii_type]

    @property
    def all_patterns(self) -> list[PIIPattern]:
        """Get all registered patterns."""
        return self._patterns.copy()


# Default registry with all patterns
def create_default_registry() -> PIIPatternRegistry:
    """Create registry with all built-in patterns."""
    registry = PIIPatternRegistry()
    registry.add_patterns(KENYA_PATTERNS)
    registry.add_patterns(EU_PATTERNS)
    registry.add_patterns(UNIVERSAL_PATTERNS)
    return registry


# Global default registry
DEFAULT_REGISTRY = create_default_registry()


def detect_pii(value: str) -> list[tuple[PIIPattern, float]]:
    """Detect PII in a value using default patterns.

    Args:
        value: String value to check

    Returns:
        List of (pattern, confidence) tuples for matches
    """
    return DEFAULT_REGISTRY.detect(value)


def detect_pii_in_column(
    values: list[str], sample_size: int = 100
) -> dict[PIIType, float]:
    """Detect PII types in a column using default patterns.

    Args:
        values: List of string values
        sample_size: Number of values to sample

    Returns:
        Dict mapping PIIType to detection rate
    """
    return DEFAULT_REGISTRY.detect_in_column(values, sample_size)
