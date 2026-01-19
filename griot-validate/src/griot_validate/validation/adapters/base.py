"""Abstract base class for DataFrame adapters.

This module defines the interface that all DataFrame adapters must implement.
The adapter pattern allows us to separate framework-specific code from
validation logic.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

# Generic type for DataFrame
DF = TypeVar("DF")


class DataFrameAdapter(ABC, Generic[DF]):
    """Abstract adapter for framework-specific DataFrame operations.

    This is the ONLY place where framework-specific code lives.
    All methods return Python primitives (int, float, list, bool).

    Implementations:
        - PandasAdapter
        - PolarsAdapter
        - PySparkAdapter
        - DaskAdapter
    """

    def __init__(self, df: DF):
        self._df = df

    @property
    def dataframe(self) -> DF:
        """Access the underlying DataFrame."""
        return self._df

    # -------------------------------------------------------------------------
    # Schema Information
    # -------------------------------------------------------------------------

    @abstractmethod
    def get_columns(self) -> list[str]:
        """Return list of column names."""
        ...

    @abstractmethod
    def get_column_dtype(self, column: str) -> str:
        """Return the dtype of a column as a normalized string.

        Returns one of: 'string', 'integer', 'float', 'boolean',
        'datetime', 'date', 'object'
        """
        ...

    @abstractmethod
    def row_count(self) -> int:
        """Return total number of rows."""
        ...

    def has_column(self, column: str) -> bool:
        """Check if column exists."""
        return column in self.get_columns()

    # -------------------------------------------------------------------------
    # Null/Missing Value Operations
    # -------------------------------------------------------------------------

    @abstractmethod
    def count_nulls(self, column: str) -> int:
        """Count null/None/NaN values in column."""
        ...

    @abstractmethod
    def count_missing(
        self, column: str, missing_values: list[Any] | None = None
    ) -> int:
        """Count missing values (nulls + custom missing indicators).

        Args:
            column: Column name
            missing_values: Additional values to treat as missing
                           (e.g., "", "N/A", -999)
        """
        ...

    # -------------------------------------------------------------------------
    # Uniqueness/Duplicate Operations
    # -------------------------------------------------------------------------

    @abstractmethod
    def count_unique(self, column: str) -> int:
        """Count unique non-null values in column."""
        ...

    @abstractmethod
    def count_duplicates(self, column: str) -> int:
        """Count duplicate values (rows with values that appear more than once)."""
        ...

    @abstractmethod
    def count_duplicate_rows(self, columns: list[str] | None = None) -> int:
        """Count duplicate rows across specified columns (or all columns)."""
        ...

    # -------------------------------------------------------------------------
    # Value Validation Operations
    # -------------------------------------------------------------------------

    @abstractmethod
    def count_not_in_set(self, column: str, valid_values: list[Any]) -> int:
        """Count non-null values not in the allowed set."""
        ...

    @abstractmethod
    def count_not_matching_pattern(self, column: str, pattern: str) -> int:
        """Count non-null values not matching regex pattern."""
        ...

    @abstractmethod
    def count_outside_range(
        self,
        column: str,
        min_value: Any | None = None,
        max_value: Any | None = None,
        inclusive: bool = True,
    ) -> int:
        """Count non-null values outside the specified range."""
        ...

    # -------------------------------------------------------------------------
    # Aggregation Operations (for distribution checks, etc.)
    # -------------------------------------------------------------------------

    @abstractmethod
    def get_column_values(self, column: str, drop_nulls: bool = True) -> list[Any]:
        """Get column values as Python list (for statistical tests).

        Warning: Materializes data. Use only when necessary
        (e.g., distribution tests).
        """
        ...

    @abstractmethod
    def get_min(self, column: str) -> Any:
        """Get minimum value in column."""
        ...

    @abstractmethod
    def get_max(self, column: str) -> Any:
        """Get maximum value in column."""
        ...

    @abstractmethod
    def get_mean(self, column: str) -> float:
        """Get mean of numeric column."""
        ...

    @abstractmethod
    def get_std(self, column: str) -> float:
        """Get standard deviation of numeric column."""
        ...

    # -------------------------------------------------------------------------
    # Timestamp Operations (for freshness checks)
    # -------------------------------------------------------------------------

    @abstractmethod
    def get_max_timestamp(self, column: str) -> Any:
        """Get maximum timestamp value (most recent)."""
        ...

    # -------------------------------------------------------------------------
    # Sampling (for error details)
    # -------------------------------------------------------------------------

    @abstractmethod
    def sample_invalid_values(
        self,
        column: str,
        condition: str,  # "null", "duplicate", "not_in_set", etc.
        limit: int = 5,
        **kwargs: Any,
    ) -> list[Any]:
        """Sample invalid values for error reporting.

        Args:
            column: Column name
            condition: Type of invalidity to sample
            limit: Maximum number of samples
            **kwargs: Condition-specific parameters
                     (e.g., valid_values, pattern)
        """
        ...
