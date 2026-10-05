import pandas as pd


def convert_numeric_values(values: pd.Series) -> tuple[pd.Series, int, int]:
    """Convert values to numbers and report invalid and missing counts."""
    converted = pd.to_numeric(values, errors="coerce")
    invalid_count = int((values.notna() & converted.isna()).sum())
    missing_count = int(values.isna().sum())
    return converted, invalid_count, missing_count


def convert_date_values(values: pd.Series) -> tuple[pd.Series, int, int]:
    """Convert values to dates and report invalid and missing counts."""
    converted = pd.to_datetime(values, errors="coerce")
    invalid_count = int((values.notna() & converted.isna()).sum())
    missing_count = int(values.isna().sum())
    return converted, invalid_count, missing_count


def calculate_profit_margin(
    data: pd.DataFrame, sales_column: str, profit_column: str
) -> float | None:
    """Return total profit divided by total sales where both values are valid."""
    valid_rows = data.dropna(subset=[sales_column, profit_column])
    total_sales = valid_rows[sales_column].sum()
    if valid_rows.empty or total_sales == 0:
        return None
    return float(valid_rows[profit_column].sum() / total_sales)


def count_orders(data: pd.DataFrame, order_column: str | None) -> int:
    """Count unique order IDs, or rows when no order identifier is available."""
    return int(data[order_column].nunique()) if order_column else len(data)
