"""Polars DataFrame adapter implementation."""

from __future__ import annotations

import re
from typing import Any

from .base import DataFrameAdapter

try:
    import polars as pl

    POLARS_AVAILABLE = True
except ImportError:
    POLARS_AVAILABLE = False
    pl = None  # type: ignore


class PolarsAdapter(DataFrameAdapter["pl.DataFrame"]):
    """Adapter for polars DataFrames."""

    # -------------------------------------------------------------------------
    # Schema Information
    # -------------------------------------------------------------------------

    def get_columns(self) -> list[str]:
        return self._df.columns

    def get_column_dtype(self, column: str) -> str:
        dtype = self._df[column].dtype
        dtype_str = str(dtype).lower()

        if "str" in dtype_str or "utf8" in dtype_str:
            return "string"
        elif "int" in dtype_str:
            return "integer"
        elif "float" in dtype_str:
            return "float"
        elif "bool" in dtype_str:
            return "boolean"
        elif "datetime" in dtype_str or "date" in dtype_str:
            return "datetime"
        else:
            return "object"

    def row_count(self) -> int:
        return len(self._df)

    # -------------------------------------------------------------------------
    # Null/Missing Value Operations
    # -------------------------------------------------------------------------

    def count_nulls(self, column: str) -> int:
        return self._df[column].null_count()

    def count_missing(
        self, column: str, missing_values: list[Any] | None = None
    ) -> int:
        series = self._df[column]
        null_count = series.null_count()

        if missing_values:
            custom_missing = series.is_in(missing_values).sum()
            return int(null_count + custom_missing)

        return int(null_count)

    # -------------------------------------------------------------------------
    # Uniqueness/Duplicate Operations
    # -------------------------------------------------------------------------

    def count_unique(self, column: str) -> int:
        return self._df[column].drop_nulls().n_unique()

    def count_duplicates(self, column: str) -> int:
        series = self._df[column]
        # Count rows where value appears more than once
        value_counts = series.value_counts()
        duplicated_values = value_counts.filter(pl.col("count") > 1)
        if len(duplicated_values) == 0:
            return 0
        # Sum up all counts for duplicated values
        return int(duplicated_values["count"].sum())

    def count_duplicate_rows(self, columns: list[str] | None = None) -> int:
        subset = columns if columns else self._df.columns
        # Count rows that are duplicated
        return int(self._df.select(subset).is_duplicated().sum())

    # -------------------------------------------------------------------------
    # Value Validation Operations
    # -------------------------------------------------------------------------

    def count_not_in_set(self, column: str, valid_values: list[Any]) -> int:
        series = self._df[column]
        not_null = series.is_not_null()
        not_in_set = ~series.is_in(valid_values)
        return int((not_null & not_in_set).sum())

    def count_not_matching_pattern(self, column: str, pattern: str) -> int:
        series = self._df[column]
        compiled = re.compile(pattern)

        # Convert to Python list for regex matching
        values = series.to_list()
        count = 0
        for val in values:
            if val is not None:
                if not compiled.match(str(val)):
                    count += 1
        return count

    def count_outside_range(
        self,
        column: str,
        min_value: Any | None = None,
        max_value: Any | None = None,
        inclusive: bool = True,
    ) -> int:
        series = self._df[column]

        if min_value is None and max_value is None:
            return 0

        not_null = series.is_not_null()

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

        outside = not_null & ~in_range
        return int(outside.sum())

    # -------------------------------------------------------------------------
    # Aggregation Operations
    # -------------------------------------------------------------------------

    def get_column_values(self, column: str, drop_nulls: bool = True) -> list[Any]:
        series = self._df[column]
        if drop_nulls:
            series = series.drop_nulls()
        return series.to_list()

    def get_min(self, column: str) -> Any:
        return self._df[column].min()

    def get_max(self, column: str) -> Any:
        return self._df[column].max()

    def get_mean(self, column: str) -> float:
        result = self._df[column].mean()
        return float(result) if result is not None else 0.0

    def get_std(self, column: str) -> float:
        result = self._df[column].std()
        return float(result) if result is not None else 0.0

    # -------------------------------------------------------------------------
    # Timestamp Operations
    # -------------------------------------------------------------------------

    def get_max_timestamp(self, column: str) -> Any:
        return self._df[column].max()

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
        series = self._df[column]

        if condition == "null":
            mask = series.is_null()
        elif condition == "duplicate":
            mask = series.is_duplicated()
        elif condition == "not_in_set":
            valid_values = kwargs.get("valid_values", [])
            mask = ~series.is_in(valid_values) & series.is_not_null()
        elif condition == "not_matching_pattern":
            pattern = kwargs.get("pattern", "")
            compiled = re.compile(pattern)
            # Create mask manually
            values = series.to_list()
            mask_list = [
                v is not None and not compiled.match(str(v)) for v in values
            ]
            mask = pl.Series(mask_list)
        elif condition == "outside_range":
            min_val = kwargs.get("min_value")
            max_val = kwargs.get("max_value")
            mask = series.is_not_null()
            if min_val is not None:
                mask = mask & (series < min_val)
            if max_val is not None:
                mask = mask | (series > max_val)
        else:
            return []

        invalid = self._df.filter(mask)[column].head(limit)
        return invalid.to_list()
