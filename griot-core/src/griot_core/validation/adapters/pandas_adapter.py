"""Pandas DataFrame adapter implementation."""

from __future__ import annotations

import re
from typing import Any

from .base import DataFrameAdapter

try:
    import pandas as pd

    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    pd = None  # type: ignore


class PandasAdapter(DataFrameAdapter["pd.DataFrame"]):
    """Adapter for pandas DataFrames."""

    # -------------------------------------------------------------------------
    # Schema Information
    # -------------------------------------------------------------------------

    def get_columns(self) -> list[str]:
        return list(self._df.columns)

    def get_column_dtype(self, column: str) -> str:
        dtype = self._df[column].dtype
        if pd.api.types.is_string_dtype(dtype) or dtype == object:
            return "string"
        elif pd.api.types.is_integer_dtype(dtype):
            return "integer"
        elif pd.api.types.is_float_dtype(dtype):
            return "float"
        elif pd.api.types.is_bool_dtype(dtype):
            return "boolean"
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            return "datetime"
        else:
            return "object"

    def row_count(self) -> int:
        return len(self._df)

    # -------------------------------------------------------------------------
    # Null/Missing Value Operations
    # -------------------------------------------------------------------------

    def count_nulls(self, column: str) -> int:
        return int(self._df[column].isna().sum())

    def count_missing(
        self, column: str, missing_values: list[Any] | None = None
    ) -> int:
        series = self._df[column]
        null_count = series.isna().sum()

        if missing_values:
            custom_missing = series.isin(missing_values).sum()
            return int(null_count + custom_missing)

        return int(null_count)

    # -------------------------------------------------------------------------
    # Uniqueness/Duplicate Operations
    # -------------------------------------------------------------------------

    def count_unique(self, column: str) -> int:
        return int(self._df[column].nunique(dropna=True))

    def count_duplicates(self, column: str) -> int:
        return int(self._df[column].duplicated(keep=False).sum())

    def count_duplicate_rows(self, columns: list[str] | None = None) -> int:
        subset = columns if columns else None
        return int(self._df.duplicated(subset=subset, keep=False).sum())

    # -------------------------------------------------------------------------
    # Value Validation Operations
    # -------------------------------------------------------------------------

    def count_not_in_set(self, column: str, valid_values: list[Any]) -> int:
        series = self._df[column]
        not_in_set = ~series.isin(valid_values)
        return int(not_in_set.sum())

    def count_not_matching_pattern(self, column: str, pattern: str) -> int:
        series = self._df[column]
        compiled = re.compile(pattern)

        def matches(val: Any) -> bool:
            if pd.isna(val):
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
        series = self._df[column]
        if min_value is None and max_value is None:
            return 0

        if inclusive:
            if min_value is not None and max_value is not None:
                in_range = series.between(min_value, max_value)
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
        return int(outside.sum())

    # -------------------------------------------------------------------------
    # Aggregation Operations
    # -------------------------------------------------------------------------

    def get_column_values(self, column: str, drop_nulls: bool = True) -> list[Any]:
        series = self._df[column]
        if drop_nulls:
            series = series.dropna()
        return series.tolist()

    def get_min(self, column: str) -> Any:
        return self._df[column].min()

    def get_max(self, column: str) -> Any:
        return self._df[column].max()

    def get_mean(self, column: str) -> float:
        return float(self._df[column].mean())

    def get_std(self, column: str) -> float:
        return float(self._df[column].std())

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
                lambda x: pd.notna(x) and not compiled.match(str(x))
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
