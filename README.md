# Supermart Sales Dashboard

An interactive Streamlit dashboard for exploring sales, profit, products, and
regions. This project is designed as a portfolio demonstration.

> The included sample data is illustrative and does not represent real
> Supermart business results.

## Run locally

From this project folder, install the dependencies and start the app:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Streamlit will print a local URL to open in your browser. The dashboard loads
`supermart_sales_sample.csv` automatically when it is present, or you can upload
another CSV using the sidebar.

The included CSV contains 36 illustrative orders across all 12 months of 2023,
with several product categories and regions. It is synthetic demo data, not
actual Supermart business data.

Run the unit tests from the project folder with:

```bash
python -m unittest
```

## Dashboard features

- KPI cards for total sales, total profit, profit margin, and orders
- Date, category, and region filters
- Charts for sales over time, sales by category, top products, and profit by
  region
- A preview of the filtered data
- Warnings for missing or unparseable numeric values and dates, plus an
  empty-filter state
- Unit tests for data conversion and KPI calculations

## CSV data

The dashboard recognizes common column names, including:

| Data | Recognized column names |
| --- | --- |
| Sales | `Sales`, `Revenue`, `Amount` |
| Profit | `Profit`, `Net Profit` |
| Date | `Order Date`, `Date` |
| Category | `Category`, `Product Category` |
| Region | `Region`, `State`, `City` |
| Order identifier | `Order ID`, `Order Id`, `Invoice ID` |
| Product | `Product`, `Item`, `Product Name` |

Columns are optional; charts and metrics that require a missing column will not
be available. The dashboard reports missing or unparseable numeric and date
values and excludes them from related totals or charts. Total sales and profit
are sums of valid values; profit margin is total profit divided by total sales
for rows with valid values in both columns; orders is the distinct count of the
order identifier, or the row count if no identifier column is present. Dollar
signs are used for sales and profit, so provide values in dollars or adjust the
formatting for another currency.

For meaningful results, use a CSV with real data and verify that its sales,
profit, and order values match your intended definitions.
