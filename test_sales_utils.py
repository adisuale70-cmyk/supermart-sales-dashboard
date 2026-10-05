import unittest

import pandas as pd

from sales_utils import (
    calculate_profit_margin,
    convert_date_values,
    convert_numeric_values,
    count_orders,
)


class SalesUtilsTests(unittest.TestCase):
    def test_numeric_conversion_counts_invalid_and_missing_values(self):
        values = pd.Series(["12.5", "not a number", None])

        converted, invalid_count, missing_count = convert_numeric_values(values)

        self.assertEqual(converted.iloc[0], 12.5)
        self.assertTrue(pd.isna(converted.iloc[1]))
        self.assertEqual(invalid_count, 1)
        self.assertEqual(missing_count, 1)

    def test_date_conversion_counts_invalid_and_missing_values(self):
        values = pd.Series(["2024-01-01", "not a date", None])

        converted, invalid_count, missing_count = convert_date_values(values)

        self.assertEqual(converted.iloc[0], pd.Timestamp("2024-01-01"))
        self.assertTrue(pd.isna(converted.iloc[1]))
        self.assertEqual(invalid_count, 1)
        self.assertEqual(missing_count, 1)

    def test_profit_margin_uses_rows_with_both_values(self):
        data = pd.DataFrame(
            {"Sales": [100, 50, None], "Profit": [20, None, 10]}
        )

        self.assertEqual(calculate_profit_margin(data, "Sales", "Profit"), 0.2)

    def test_profit_margin_is_unavailable_without_nonzero_valid_sales(self):
        data = pd.DataFrame({"Sales": [0, None], "Profit": [5, 2]})

        self.assertIsNone(calculate_profit_margin(data, "Sales", "Profit"))

    def test_order_count_uses_unique_ids_or_row_count(self):
        data = pd.DataFrame({"Order ID": ["A", "A", "B"]})

        self.assertEqual(count_orders(data, "Order ID"), 2)
        self.assertEqual(count_orders(data, None), 3)


if __name__ == "__main__":
    unittest.main()
