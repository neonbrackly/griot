"""Dask DataFrame adapter implementation."""

from __future__ import annotations

import re
from typing import Any

from .base import DataFrameAdapter

try:
    import dask.dataframe as dd

    DASK_AVAILABLE = True
except ImportError:
    DASK_AVAILABLE = False
    dd = None  # type: ignore


class DaskAdapter(DataFrameAdapter["dd.DataFrame"]):
    """Adapter for Dask DataFrames.

    Note: Many operations require .compute() which materializes the data.
    Use with caution on very large datasets.
    """

    # -------------------------------------------------------------------------
    # Schema Information
    # -------------------------------------------------------------------------

    def get_columns(self) -> list[str]:
        return list(self._df.columns)

    def get_column_dtype(self, column: str) -> str:
        dtype = self._df[column].dtype
        dtype_str = str(dtype).lower()

        if "str" in dtype_str or "object" in dtype_str:
            return "string"
        elif "int" in dtype_str:
            return "integer"
        elif "float" in dtype_str:
            return "float"
        elif "bool" in dtype_str:
            return "boolean"
        elif "datetime" in dtype_str:
            return "datetime"
        else:
            return "object"

    def row_count(self) -> int:
        return int(len(self._df))

    # -------------------------------------------------------------------------
    # Null/Missing Value Operations
    # -------------------------------------------------------------------------

    def count_nulls(self, column: str) -> int:
        return int(self._df[column].isna().sum().compute())

    def count_missing(
        self, column: str, missing_values: list[Any] | None = None
    ) -> int:
        series = self._df[column]
        null_count = series.isna().sum().compute()

        if missing_values:
            custom_missing = series.isin(missing_values).sum().compute()
            return int(null_count + custom_missing)

        return int(null_count)

    # -------------------------------------------------------------------------
    # Uniqueness/Duplicate Operations
    # -------------------------------------------------------------------------

    def count_unique(self, column: str) -> int:
        return int(self._df[column].nunique().compute())

    def count_duplicates(self, column: str) -> int:
        # Dask doesn't have direct duplicated() on series
        # Compute value counts and sum those > 1
        series = self._df[column]
        value_counts = series.value_counts().compute()
        duplicated = value_counts[value_counts > 1]
        return int(duplicated.sum())

    def count_duplicate_rows(self, columns: list[str] | None = None) -> int:
        subset = columns if columns else list(self._df.columns)
        # Compute on pandas
        pdf = self._df[subset].compute()
        return int(pdf.duplicated(keep=False).sum())

    # -------------------------------------------------------------------------
    # Value Validation Operations
    # -------------------------------------------------------------------------

    def count_not_in_set(self, column: str, valid_values: list[Any]) -> int:
        series = self._df[column]

        not_in_set = ~series.isin(valid_values)
        return int(not_in_set.sum().compute())

    def count_not_matching_pattern(self, column: str, pattern: str) -> int:
        # Compute to pandas for regex matching
        series = self._df[column].compute()
        compiled = re.compile(pattern)

        def matches(val: Any) -> bool:
            if val is None or (isinstance(val, float) and val != val):
                return True  # Nulls handled separately
            return bool(compiled.match(str(val)))

        not_matching = ~series.apply(matches)
        return int(not_matching.sum())

    def count_outside_range(
        self,
        column: str,
        min_value: Any | None = None,
        max_value: Any | None = None,
        inclusive: bool = True,
    ) -> int:
        if min_value is None and max_value is None:
            return 0

        series = self._df[column]

        if inclusive:
            if min_value is not None and max_value is not None:
                in_range = (series >= min_value) & (series <= max_value)
            elif min_value is not None:
                in_range = series >= min_value
            else:
                in_range = series <= max_value  # type: ignore
        else:
            if min_value is not None and max_value is not None:
                in_range = (series > min_value) & (series < max_value)
            elif min_value is not None:
                in_range = series > min_value
            else:
                in_range = series < max_value  # type: ignore

        outside = ~in_range
        return int(outside.sum().compute())

    # -------------------------------------------------------------------------
    # Aggregation Operations
    # -------------------------------------------------------------------------

    def get_column_values(self, column: str, drop_nulls: bool = False) -> list[Any]:
        series = self._df[column].compute()
        if drop_nulls:
            series = series.dropna()
        return series.tolist()

    def get_min(self, column: str) -> Any:
        return self._df[column].min().compute()

    def get_max(self, column: str) -> Any:
        return self._df[column].max().compute()

    def get_mean(self, column: str) -> float:
        result = self._df[column].mean().compute()
        return float(result) if result is not None else 0.0

    def get_std(self, column: str) -> float:
        result = self._df[column].std().compute()
        return float(result) if result is not None else 0.0

    # -------------------------------------------------------------------------
    # Timestamp Operations
    # -------------------------------------------------------------------------

    def get_max_timestamp(self, column: str) -> Any:
        return self._df[column].max().compute()

    # -------------------------------------------------------------------------
    # Sampling
    # -------------------------------------------------------------------------

    def sample_invalid_values(
        self,
        column: str,
        condition: str,
        limit: int = 5,
        **kwargs: Any,
    ) -> list[Any]:
        # Compute to pandas for filtering
        series = self._df[column].compute()

        if condition == "null":
            mask = series.isna()
        elif condition == "duplicate":
            mask = series.duplicated(keep=False)
        elif condition == "not_in_set":
            valid_values = kwargs.get("valid_values", [])
            mask = ~series.isin(valid_values) & series.notna()
        elif condition == "not_matching_pattern":
            pattern = kwargs.get("pattern", "")
            compiled = re.compile(pattern)
            mask = series.apply(
                lambda x: x is not None
                and not (isinstance(x, float) and x != x)
                and not compiled.match(str(x))
            )
        elif condition == "outside_range":
            min_val = kwargs.get("min_value")
            max_val = kwargs.get("max_value")
            mask = series.notna()
            if min_val is not None:
                mask = mask & (series < min_val)
            if max_val is not None:
                mask = mask | (series > max_val)
        else:
            return []

        invalid = series[mask].head(limit)
        return invalid.tolist()
