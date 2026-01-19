"""PySpark DataFrame adapter implementation."""

from __future__ import annotations

import re
from typing import Any

from .base import DataFrameAdapter

try:
    from pyspark.sql import DataFrame as SparkDataFrame
    from pyspark.sql import functions as F
    from pyspark.sql.types import (
        BooleanType,
        DateType,
        DoubleType,
        FloatType,
        IntegerType,
        LongType,
        StringType,
        TimestampType,
    )

    PYSPARK_AVAILABLE = True
except ImportError:
    PYSPARK_AVAILABLE = False
    SparkDataFrame = None  # type: ignore


class PySparkAdapter(DataFrameAdapter["SparkDataFrame"]):
    """Adapter for PySpark DataFrames."""

    # -------------------------------------------------------------------------
    # Schema Information
    # -------------------------------------------------------------------------

    def get_columns(self) -> list[str]:
        return self._df.columns

    def get_column_dtype(self, column: str) -> str:
        dtype = self._df.schema[column].dataType

        if isinstance(dtype, StringType):
            return "string"
        elif isinstance(dtype, (IntegerType, LongType)):
            return "integer"
        elif isinstance(dtype, (FloatType, DoubleType)):
            return "float"
        elif isinstance(dtype, BooleanType):
            return "boolean"
        elif isinstance(dtype, TimestampType):
            return "datetime"
        elif isinstance(dtype, DateType):
            return "date"
        else:
            return "object"

    def row_count(self) -> int:
        return self._df.count()

    # -------------------------------------------------------------------------
    # Null/Missing Value Operations
    # -------------------------------------------------------------------------

    def count_nulls(self, column: str) -> int:
        return self._df.filter(F.col(column).isNull()).count()

    def count_missing(
        self, column: str, missing_values: list[Any] | None = None
    ) -> int:
        null_count = self._df.filter(F.col(column).isNull()).count()

        if missing_values:
            custom_missing = self._df.filter(
                F.col(column).isin(missing_values)
            ).count()
            return int(null_count + custom_missing)

        return int(null_count)

    # -------------------------------------------------------------------------
    # Uniqueness/Duplicate Operations
    # -------------------------------------------------------------------------

    def count_unique(self, column: str) -> int:
        return self._df.filter(F.col(column)).select(column).distinct().count()

    def count_duplicates(self, column: str) -> int:
        # Count rows where value appears more than once
        counts = self._df.groupBy(column).count().filter(F.col("count") > 1)
        if counts.count() == 0:
            return 0
        return int(counts.agg(F.sum("count")).collect()[0][0])

    def count_duplicate_rows(self, columns: list[str] | None = None) -> int:
        subset = columns if columns else self._df.columns
        total = self._df.count()
        distinct = self._df.select(subset).distinct().count()
        return total - distinct

    # -------------------------------------------------------------------------
    # Value Validation Operations
    # -------------------------------------------------------------------------

    def count_not_in_set(self, column: str, valid_values: list[Any]) -> int:
        return self._df.filter(
            F.col(column) & ~F.col(column).isin(valid_values)
        ).count()

    def count_not_matching_pattern(self, column: str, pattern: str) -> int:
        # PySpark uses Java regex, convert if needed
        return self._df.filter(
            F.col(column) & ~F.col(column).rlike(pattern)
        ).count()

    def count_outside_range(
        self,
        column: str,
        min_value: Any | None = None,
        max_value: Any | None = None,
        inclusive: bool = True,
    ) -> int:
        if min_value is None and max_value is None:
            return 0

        col = F.col(column)

        if inclusive:
            if min_value is not None and max_value is not None:
                in_range = (col >= min_value) & (col <= max_value)
            elif min_value is not None:
                in_range = col >= min_value
            else:
                in_range = col <= max_value
        else:
            if min_value is not None and max_value is not None:
                in_range = (col > min_value) & (col < max_value)
            elif min_value is not None:
                in_range = col > min_value
            else:
                in_range = col < max_value

        return self._df.filter(~in_range).count()

    # -------------------------------------------------------------------------
    # Aggregation Operations
    # -------------------------------------------------------------------------

    def get_column_values(self, column: str, drop_nulls: bool = True) -> list[Any]:
        df = self._df
        if drop_nulls:
            df = df.filter(F.col(column).isNotNull())
        return [row[0] for row in df.select(column).collect()]

    def get_min(self, column: str) -> Any:
        result = self._df.agg(F.min(column)).collect()[0][0]
        return result

    def get_max(self, column: str) -> Any:
        result = self._df.agg(F.max(column)).collect()[0][0]
        return result

    def get_mean(self, column: str) -> float:
        result = self._df.agg(F.mean(column)).collect()[0][0]
        return float(result) if result is not None else 0.0

    def get_std(self, column: str) -> float:
        result = self._df.agg(F.stddev(column)).collect()[0][0]
        return float(result) if result is not None else 0.0

    # -------------------------------------------------------------------------
    # Timestamp Operations
    # -------------------------------------------------------------------------

    def get_max_timestamp(self, column: str) -> Any:
        return self._df.agg(F.max(column)).collect()[0][0]

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
        col = F.col(column)

        if condition == "null":
            filtered = self._df.filter(col.isNull())
        elif condition == "duplicate":
            # Get values that appear more than once
            counts = self._df.groupBy(column).count().filter(F.col("count") > 1)
            dup_values = [row[0] for row in counts.select(column).collect()]
            filtered = self._df.filter(col.isin(dup_values))
        elif condition == "not_in_set":
            valid_values = kwargs.get("valid_values", [])
            filtered = self._df.filter(col.isNotNull() & ~col.isin(valid_values))
        elif condition == "not_matching_pattern":
            pattern = kwargs.get("pattern", "")
            filtered = self._df.filter(col.isNotNull() & ~col.rlike(pattern))
        elif condition == "outside_range":
            min_val = kwargs.get("min_value")
            max_val = kwargs.get("max_value")
            cond = col.isNotNull()
            if min_val is not None:
                cond = cond & (col < min_val)
            if max_val is not None:
                cond = cond | (col > max_val)
            filtered = self._df.filter(cond)
        else:
            return []

        return [row[0] for row in filtered.select(column).limit(limit).collect()]
