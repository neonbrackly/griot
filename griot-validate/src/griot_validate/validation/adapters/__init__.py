"""DataFrame adapter registry and factory.

This module provides the adapter registry that automatically detects
DataFrame types and returns the appropriate adapter.
"""

from __future__ import annotations

from typing import Any

from .base import DataFrameAdapter

# Import adapters conditionally
try:
    from .pandas_adapter import PandasAdapter, PANDAS_AVAILABLE
except ImportError:
    PANDAS_AVAILABLE = False
    PandasAdapter = None  # type: ignore

try:
    from .polars_adapter import PolarsAdapter, POLARS_AVAILABLE
except ImportError:
    POLARS_AVAILABLE = False
    PolarsAdapter = None  # type: ignore

try:
    from .pyspark_adapter import PySparkAdapter, PYSPARK_AVAILABLE
except ImportError:
    PYSPARK_AVAILABLE = False
    PySparkAdapter = None  # type: ignore

try:
    from .dask_adapter import DaskAdapter, DASK_AVAILABLE
except ImportError:
    DASK_AVAILABLE = False
    DaskAdapter = None  # type: ignore


class AdapterRegistry:
    """Registry for DataFrame adapters with auto-detection.

    Usage:
        adapter = AdapterRegistry.get_adapter(df)
        null_count = adapter.count_nulls("column_name")
    """

    @classmethod
    def get_adapter(cls, df: Any) -> DataFrameAdapter:
        """Get the appropriate adapter for a DataFrame.

        Args:
            df: A DataFrame (pandas, polars, pyspark, or dask)

        Returns:
            DataFrameAdapter instance for the DataFrame type

        Raises:
            TypeError: If DataFrame type is not supported
        """
        df_type = type(df).__name__
        module = type(df).__module__

        # Check pandas
        if PANDAS_AVAILABLE:
            import pandas as pd

            if isinstance(df, pd.DataFrame):
                return PandasAdapter(df)

        # Check polars
        if POLARS_AVAILABLE:
            import polars as pl

            if isinstance(df, (pl.DataFrame, pl.LazyFrame)):
                # Convert LazyFrame to DataFrame for validation
                if isinstance(df, pl.LazyFrame):
                    df = df.collect()
                return PolarsAdapter(df)

        # Check pyspark
        if PYSPARK_AVAILABLE:
            from pyspark.sql import DataFrame as SparkDataFrame

            if isinstance(df, SparkDataFrame):
                return PySparkAdapter(df)

        # Check dask
        if DASK_AVAILABLE:
            import dask.dataframe as dd

            if isinstance(df, dd.DataFrame):
                return DaskAdapter(df)

        # Unknown type
        raise TypeError(
            f"Unsupported DataFrame type: {df_type} (module: {module}). "
            f"Supported types: pandas.DataFrame, polars.DataFrame, "
            f"pyspark.sql.DataFrame, dask.dataframe.DataFrame"
        )

    @classmethod
    def is_supported(cls, df: Any) -> bool:
        """Check if a DataFrame type is supported.

        Args:
            df: A DataFrame to check

        Returns:
            True if the DataFrame type is supported
        """
        try:
            cls.get_adapter(df)
            return True
        except TypeError:
            return False

    @classmethod
    def available_backends(cls) -> list[str]:
        """List available DataFrame backends.

        Returns:
            List of available backend names
        """
        backends = []
        if PANDAS_AVAILABLE:
            backends.append("pandas")
        if POLARS_AVAILABLE:
            backends.append("polars")
        if PYSPARK_AVAILABLE:
            backends.append("pyspark")
        if DASK_AVAILABLE:
            backends.append("dask")
        return backends


# Convenience function
def get_adapter(df: Any) -> DataFrameAdapter:
    """Get the appropriate adapter for a DataFrame.

    This is a convenience function that delegates to AdapterRegistry.

    Args:
        df: A DataFrame (pandas, polars, pyspark, or dask)

    Returns:
        DataFrameAdapter instance for the DataFrame type
    """
    return AdapterRegistry.get_adapter(df)


__all__ = [
    "DataFrameAdapter",
    "AdapterRegistry",
    "get_adapter",
    "PandasAdapter",
    "PolarsAdapter",
    "PySparkAdapter",
    "DaskAdapter",
    "PANDAS_AVAILABLE",
    "POLARS_AVAILABLE",
    "PYSPARK_AVAILABLE",
    "DASK_AVAILABLE",
]
