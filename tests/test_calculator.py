import math
import unittest

from calculator import calculate_projection


class CalculateProjectionTests(unittest.TestCase):
    def test_zero_return_adds_contributions_without_interest(self):
        result = calculate_projection(
            initial_investment=1_000,
            monthly_contribution=100,
            years=1,
            annual_return=0,
        )

        self.assertEqual(result.total_contributions, 2_200)
        self.assertEqual(result.portfolio_value, 2_200)
        self.assertEqual(result.estimated_gain, 0)
        self.assertEqual(result.monthly_rate, 0)

    def test_effective_annual_return_converts_to_consistent_monthly_rate(self):
        result = calculate_projection(
            initial_investment=1_000,
            monthly_contribution=0,
            years=1,
            annual_return=0.12,
        )

        self.assertAlmostEqual((1 + result.monthly_rate) ** 12, 1.12)
        self.assertAlmostEqual(result.portfolio_value, 1_120)

    def test_month_end_contributions_do_not_grow_in_the_month_they_are_added(self):
        result = calculate_projection(
            initial_investment=1_000,
            monthly_contribution=100,
            years=1,
            annual_return=0.12,
        )
        expected = 1_000 * 1.12 + 100 * sum(
            (1 + result.monthly_rate) ** month for month in range(12)
        )

        self.assertAlmostEqual(result.portfolio_value, expected)
        self.assertEqual(result.timeline[0].month, 0)
        self.assertEqual(result.timeline[0].portfolio_value, 1_000)
        self.assertEqual(result.timeline[1].total_contributions, 1_100)

    def test_month_start_contributions_grow_from_the_month_they_are_added(self):
        result = calculate_projection(
            initial_investment=0,
            monthly_contribution=100,
            years=1,
            annual_return=0.12,
            contribution_timing="beginning",
        )
        expected = 100 * sum(
            (1 + result.monthly_rate) ** month for month in range(1, 13)
        )

        self.assertAlmostEqual(result.total_contributions, 1_200)
        self.assertAlmostEqual(result.portfolio_value, expected)
        self.assertGreater(result.portfolio_value, 1_200)

    def test_rejects_unknown_contribution_timing(self):
        with self.assertRaisesRegex(ValueError, "Contribution timing"):
            calculate_projection(100, 10, 1, 0.05, contribution_timing="mid-month")

    def test_fee_is_subtracted_from_annual_return_before_monthly_conversion(self):
        result = calculate_projection(
            initial_investment=1_000,
            monthly_contribution=0,
            years=1,
            annual_return=0.06,
            annual_fee=0.01,
        )

        self.assertAlmostEqual((1 + result.monthly_rate) ** 12, 1.05)
        self.assertAlmostEqual(result.portfolio_value, 1_050)

    def test_inflation_adjusted_value_is_separate_from_nominal_value(self):
        result = calculate_projection(
            initial_investment=1_000,
            monthly_contribution=0,
            years=2,
            annual_return=0,
            annual_inflation=0.10,
        )

        self.assertEqual(result.portfolio_value, 1_000)
        self.assertTrue(
            math.isclose(result.inflation_adjusted_value, 1_000 / (1.10**2))
        )

    def test_rejects_negative_contributions(self):
        with self.assertRaisesRegex(ValueError, "cannot be negative"):
            calculate_projection(-1, 100, 1, 0.05)

    def test_rejects_negative_annual_fee(self):
        with self.assertRaisesRegex(ValueError, "Annual fee cannot be negative"):
            calculate_projection(100, 10, 1, 0.05, annual_fee=-0.01)

    def test_rejects_non_integer_duration(self):
        with self.assertRaisesRegex(ValueError, "whole number"):
            calculate_projection(100, 10, 1.5, 0.05)  # type: ignore[arg-type]

    def test_rejects_non_finite_assumptions(self):
        with self.assertRaisesRegex(ValueError, "finite"):
            calculate_projection(100, 10, 1, math.inf)


if __name__ == "__main__":
    unittest.main()
