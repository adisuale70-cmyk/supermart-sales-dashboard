from pathlib import Path

import pandas as pd
import plotly.express as px
from plotly.graph_objects import Figure
import streamlit as st

from sales_utils import (
    calculate_profit_margin,
    convert_date_values,
    convert_numeric_values,
    count_orders,
)


st.set_page_config(
    page_title="Supermart Sales Dashboard",
    page_icon="🛒",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp {
        background-color: #f6f8f7;
    }
    .block-container {
        max-width: 1440px;
        padding-top: 2.5rem;
        padding-bottom: 3rem;
    }
    [data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e5ebe8;
        border-radius: 12px;
        padding: 1rem 1.1rem;
        box-shadow: 0 2px 8px rgba(25, 55, 43, 0.04);
    }
    [data-testid="stMetricLabel"] {
        color: #66756e;
    }
    [data-testid="stMetricValue"] {
        color: #173d2b;
    }
    [data-testid="stSidebar"] {
        background-color: #eef3f0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

px.defaults.template = "plotly_white"
px.defaults.color_discrete_sequence = ["#24734a", "#73a987", "#d3a64b", "#6687a5"]


def format_currency_axis(figure: Figure) -> Figure:
    figure.update_yaxes(tickprefix="$", separatethousands=True, title_text=None)
    figure.update_layout(
        margin={"t": 20, "r": 20, "b": 20, "l": 20},
        hoverlabel={"bgcolor": "white"},
    )
    return figure


st.title("🛒 Supermart Sales Dashboard")
st.caption("Portfolio project · An interactive look at sales, profit, products, and regions.")


def build_demo_data() -> pd.DataFrame:
    """Create a small but realistic sales dataset for a quick-start dashboard."""
    records = []
    dates = pd.date_range("2023-01-01", periods=180, freq="D")
    categories = ["Office Supplies", "Furniture", "Technology"]
    regions = ["West", "East", "Central", "South"]
    products = {
        "Office Supplies": ["Notebook", "Printer", "Desk Organizer", "Stapler"],
        "Furniture": ["Chair", "Desk", "Cabinet", "Bookshelf"],
        "Technology": ["Laptop", "Monitor", "Keyboard", "Tablet"],
    }

    for index, date in enumerate(dates):
        category = categories[index % len(categories)]
        region = regions[(index * 2) % len(regions)]
        product = products[category][index % len(products[category])]
        sales = round(80 + (index * 11.5) % 430 + (len(region) * 6.2))
        profit = round(sales * (0.14 + (index % 5) * 0.03))
        records.append(
            {
                "Order ID": f"ORD-{index + 1001}",
                "Order Date": date,
                "Category": category,
                "Region": region,
                "Product": product,
                "Sales": sales,
                "Profit": profit,
            }
        )

    return pd.DataFrame.from_records(records)


def find_csv() -> Path | None:
    """Find a likely sales CSV in the project directory or its subfolders."""
    candidates = sorted(
        path
        for path in Path(".").rglob("*.csv")
        if ".venv" not in path.parts and "site-packages" not in path.parts
    )
    if not candidates:
        return None
    return next(
        (path for path in candidates if "supermart" in path.name.lower()),
        candidates[0],
    )


def read_sales_csv(source: object, name: str) -> pd.DataFrame:
    try:
        return pd.read_csv(source)
    except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError) as error:
        st.error(f"Could not read {name} as a valid CSV: {error}")
        st.stop()


uploaded_file = st.sidebar.file_uploader("Or upload your sales CSV", type="csv")
csv_path = find_csv() if uploaded_file is None else None
using_sample_data = False

if uploaded_file is not None:
    data = read_sales_csv(uploaded_file, uploaded_file.name)
    st.sidebar.success(f"Loaded {uploaded_file.name}")
elif csv_path is not None:
    data = read_sales_csv(csv_path, csv_path.name)
    st.sidebar.success(f"Loaded {csv_path.name}")
    using_sample_data = csv_path.name.lower() == "supermart_sales_sample.csv"
else:
    data = build_demo_data()
    st.sidebar.info("No sales CSV found. Using the built-in demo dataset.")
    using_sample_data = True

if using_sample_data:
    st.info(
        "This portfolio demo uses illustrative sample data. "
        "It does not represent real Supermart business results."
    )

if data.empty:
    st.error("The selected CSV contains no data rows.")
    st.stop()

data.columns = data.columns.astype(str).str.strip()
column_lookup = {column.lower(): column for column in data.columns}


def find_column(*names: str) -> str | None:
    return next(
        (column_lookup[name.lower()] for name in names if name.lower() in column_lookup),
        None,
    )


sales_column = find_column("Sales", "Revenue", "Amount")
profit_column = find_column("Profit", "Net Profit")
date_column = find_column("Order Date", "Date")
category_column = find_column("Category", "Product Category")
region_column = find_column("Region", "State", "City")
order_column = find_column("Order ID", "Order Id", "Invoice ID")
product_column = find_column("Product", "Item", "Product Name")

numeric_value_issues = {}
for column in (sales_column, profit_column):
    if column:
        converted, invalid_count, missing_count = convert_numeric_values(data[column])
        if invalid_count or missing_count:
            numeric_value_issues[column] = {
                "invalid": invalid_count,
                "missing": missing_count,
            }
        data[column] = converted

invalid_date_count = 0
missing_date_count = 0
if date_column:
    parsed_dates, invalid_date_count, missing_date_count = convert_date_values(
        data[date_column]
    )
    data[date_column] = parsed_dates

if numeric_value_issues or invalid_date_count or missing_date_count:
    issues = []
    if numeric_value_issues:
        columns = ", ".join(
            f"{column} ({counts['invalid']} invalid, {counts['missing']} missing)"
            for column, counts in numeric_value_issues.items()
        )
        issues.append(f"numeric values: {columns}")
    if invalid_date_count or missing_date_count:
        issues.append(
            f"dates ({invalid_date_count} invalid, {missing_date_count} missing)"
        )
    st.warning(
        "Some CSV values are missing or could not be interpreted; they will be "
        f"excluded from relevant totals or charts: {'; '.join(issues)}."
    )

if sales_column and data[sales_column].notna().sum() == 0:
    st.error(
        f"The '{sales_column}' column was found, but it contains no usable numeric values."
    )
    st.stop()

st.sidebar.header("Filters")
filtered = data.copy()

if date_column and date_column in filtered.columns:
    valid_dates = filtered[date_column].dropna()
    if not valid_dates.empty:
        min_date = valid_dates.min().date()
        max_date = valid_dates.max().date()
        selected_dates = st.sidebar.date_input(
            "Date range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )
        if isinstance(selected_dates, tuple):
            start_date, end_date = selected_dates
        else:
            start_date = end_date = selected_dates
        filtered = filtered[
            filtered[date_column].between(pd.Timestamp(start_date), pd.Timestamp(end_date))
        ]

for label, column in (("Category", category_column), ("Region", region_column)):
    if column:
        choices = sorted(filtered[column].dropna().astype(str).unique())
        if choices:
            selected = st.sidebar.multiselect(label, choices, default=choices)
            filtered = filtered[filtered[column].astype(str).isin(selected)]

metric_columns = st.columns(4)
if sales_column:
    if filtered.empty or filtered[sales_column].notna().any():
        metric_columns[0].metric(
            "Total Sales",
            f"${filtered[sales_column].sum(skipna=True):,.2f}",
            help="Sum of valid sales values in the selected date, category, and region filters. Values are displayed as dollars.",
        )
    else:
        metric_columns[0].metric(
            "Total Sales",
            "Unavailable",
            help="No usable sales values are available for the current filters.",
        )
else:
    metric_columns[0].metric(
        "Total Sales", "Unavailable", help="Add a Sales, Revenue, or Amount column."
    )

if profit_column:
    if filtered.empty or filtered[profit_column].notna().any():
        metric_columns[1].metric(
            "Total Profit",
            f"${filtered[profit_column].sum(skipna=True):,.2f}",
            help="Sum of valid profit values in the selected filters. Values are displayed as dollars.",
        )
    else:
        metric_columns[1].metric(
            "Total Profit",
            "Unavailable",
            help="No usable profit values are available for the current filters.",
        )
else:
    metric_columns[1].metric(
        "Total Profit", "Unavailable", help="Add a Profit or Net Profit column."
    )

if sales_column and profit_column:
    margin = calculate_profit_margin(filtered, sales_column, profit_column)
    if margin is None:
        metric_columns[2].metric(
            "Profit Margin",
            "Unavailable",
            help="Requires valid sales and profit values and a nonzero sales total.",
        )
    else:
        metric_columns[2].metric(
            "Profit Margin",
            f"{margin:.1%}",
            help="Total profit divided by total sales for rows with valid values in both columns.",
        )
else:
    metric_columns[2].metric(
        "Profit Margin",
        "Unavailable",
        help="Requires both a usable sales column and a profit column.",
    )

orders = count_orders(filtered, order_column)
metric_columns[3].metric(
    "Orders",
    f"{orders:,}",
    help=(
        "Distinct order identifiers in the selected filters."
        if order_column
        else "Number of filtered data rows; no order identifier column was found."
    ),
)

if filtered.empty:
    st.info("No rows match the current filters. Adjust the filters to see results.")

st.subheader("Sales performance")
chart_columns = st.columns(2)

if not filtered.empty and date_column and sales_column:
    dated_sales = filtered.dropna(subset=[date_column, sales_column])
    if not dated_sales.empty:
        monthly = (
            dated_sales.set_index(date_column)[sales_column]
            .resample("MS")
            .sum()
            .rename("Sales")
            .reset_index()
        )
        chart_columns[0].subheader("Sales over time")
        sales_trend = px.line(monthly, x=date_column, y="Sales", markers=True)
        sales_trend.update_xaxes(title_text="Month")
        format_currency_axis(sales_trend)
        chart_columns[0].plotly_chart(
            sales_trend,
            use_container_width=True,
        )

if not filtered.empty and category_column and sales_column:
    by_category = (
        filtered.groupby(category_column, as_index=False)[sales_column]
        .sum(min_count=1)
        .dropna(subset=[sales_column])
        .sort_values(sales_column, ascending=False)
    )
    if not by_category.empty:
        chart_columns[1].subheader("Sales by category")
        category_chart = px.bar(by_category, x=category_column, y=sales_column)
        category_chart.update_xaxes(title_text="Category")
        format_currency_axis(category_chart)
        chart_columns[1].plotly_chart(
            category_chart,
            use_container_width=True,
        )

if not filtered.empty and product_column and sales_column:
    product_sales = (
        filtered.groupby(product_column, as_index=False)[sales_column]
        .sum(min_count=1)
        .dropna(subset=[sales_column])
        .sort_values(sales_column, ascending=False)
        .head(8)
    )
    if not product_sales.empty:
        st.subheader("Product performance")
        product_chart = px.bar(
            product_sales,
            x=product_column,
            y=sales_column,
            color=sales_column,
            color_continuous_scale=["#dcebe1", "#24734a"],
        )
        product_chart.update_xaxes(title_text="Product")
        product_chart.update_yaxes(
            tickprefix="$", separatethousands=True, title_text=None
        )
        product_chart.update_layout(
            margin={"t": 20, "r": 20, "b": 20, "l": 20},
            hoverlabel={"bgcolor": "white"},
            coloraxis_colorbar_title="Sales",
            coloraxis_colorbar_tickprefix="$",
            coloraxis_colorbar_separatethousands=True,
        )
        st.plotly_chart(
            product_chart,
            use_container_width=True,
        )

if not filtered.empty and region_column and profit_column:
    by_region = (
        filtered.groupby(region_column, as_index=False)[profit_column]
        .sum(min_count=1)
        .dropna(subset=[profit_column])
        .sort_values(profit_column, ascending=False)
    )
    if not by_region.empty:
        st.subheader("Regional performance")
        region_chart = px.bar(by_region, x=region_column, y=profit_column)
        region_chart.update_xaxes(title_text="Region")
        format_currency_axis(region_chart)
        st.plotly_chart(
            region_chart,
            use_container_width=True,
        )

with st.expander("Preview the filtered data"):
    st.dataframe(filtered, use_container_width=True)
