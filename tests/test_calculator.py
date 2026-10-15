import math
import unittest

from calculator import (
    calculate_projection,
    calculate_required_monthly_contribution,
    export_projection_csv,
    find_milestones,
    run_monte_carlo_simulation,
)


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

    def test_goal_planner_normal(self):
        req = calculate_required_monthly_contribution(
            target_value=50_000,
            initial_investment=5_000,
            years=5,
            annual_return=0.06,
        )
        self.assertGreater(req, 0)
        # Verify it achieves target
        res = calculate_projection(
            initial_investment=5_000,
            monthly_contribution=req,
            years=5,
            annual_return=0.06,
        )
        self.assertGreaterEqual(res.portfolio_value, 50_000)

    def test_goal_planner_zero_return(self):
        req = calculate_required_monthly_contribution(
            target_value=12_000,
            initial_investment=0,
            years=1,
            annual_return=0.0,
        )
        self.assertAlmostEqual(req, 1_000)

    def test_goal_planner_already_achieved(self):
        req = calculate_required_monthly_contribution(
            target_value=5_000,
            initial_investment=10_000,
            years=1,
            annual_return=0.05,
        )
        self.assertEqual(req, 0.0)

    def test_goal_planner_unreachable(self):
        with self.assertRaisesRegex(ValueError, "unreachable"):
            calculate_required_monthly_contribution(
                target_value=100_000_000,
                initial_investment=0,
                years=1,
                annual_return=0.01,
            )

    def test_milestones_reached(self):
        proj = calculate_projection(
            initial_investment=5_000,
            monthly_contribution=500,
            years=3,
            annual_return=0.08,
        )
        milestones = find_milestones(proj.timeline, [10_000, 25_000])
        self.assertIsNotNone(milestones[10_000])
        self.assertIsNotNone(milestones[25_000])

    def test_milestones_not_reached(self):
        proj = calculate_projection(
            initial_investment=100,
            monthly_contribution=10,
            years=1,
            annual_return=0.01,
        )
        milestones = find_milestones(proj.timeline, [100_000])
        self.assertIsNone(milestones[100_000])

    def test_export_projection_csv(self):
        proj = calculate_projection(
            initial_investment=1_000,
            monthly_contribution=100,
            years=1,
            annual_return=0.05,
        )
        csv_str = export_projection_csv(proj, annual_inflation=0.02)
        self.assertIn("Month,Year,Total Contributions (€),Projected Portfolio (€),Estimated Growth (€),Inflation-Adjusted Value (€)", csv_str)
        self.assertIn("12,", csv_str)

    def test_monte_carlo_reproducibility(self):
        res1 = run_monte_carlo_simulation(
            initial_investment=5_000,
            monthly_contribution=200,
            years=3,
            annual_return=0.07,
            annual_volatility=0.15,
            num_simulations=100,
            seed=42,
        )
        res2 = run_monte_carlo_simulation(
            initial_investment=5_000,
            monthly_contribution=200,
            years=3,
            annual_return=0.07,
            annual_volatility=0.15,
            num_simulations=100,
            seed=42,
        )
        self.assertEqual(res1.median_final_value, res2.median_final_value)
        self.assertEqual(res1.p10_final_value, res2.p10_final_value)

    def test_monte_carlo_zero_volatility(self):
        det = calculate_projection(
            initial_investment=5_000,
            monthly_contribution=200,
            years=3,
            annual_return=0.07,
        )
        mc = run_monte_carlo_simulation(
            initial_investment=5_000,
            monthly_contribution=200,
            years=3,
            annual_return=0.07,
            annual_volatility=0.0,
            num_simulations=10,
            seed=42,
        )
        self.assertAlmostEqual(det.portfolio_value, mc.median_final_value, places=2)

    def test_monte_carlo_dimensions(self):
        mc = run_monte_carlo_simulation(
            initial_investment=1_000,
            monthly_contribution=100,
            years=2,
            annual_return=0.06,
            num_simulations=50,
            seed=123,
        )
        self.assertEqual(len(mc.percentile_timeline), 25)
        self.assertGreaterEqual(mc.p90_final_value, mc.median_final_value)
        self.assertGreaterEqual(mc.median_final_value, mc.p10_final_value)

    def test_monte_carlo_invalid_inputs(self):
        with self.assertRaises(ValueError):
            run_monte_carlo_simulation(100, 10, 1, 0.05, annual_volatility=-0.1)
        with self.assertRaises(ValueError):
            run_monte_carlo_simulation(100, 10, 1, 0.05, num_simulations=0)

    def test_monte_carlo_goal_probability(self):
        mc = run_monte_carlo_simulation(
            initial_investment=10_000,
            monthly_contribution=500,
            years=5,
            annual_return=0.08,
            annual_volatility=0.15,
            num_simulations=200,
            target_goal=30_000,
            seed=99,
        )
        self.assertIsNotNone(mc.goal_attainment_probability)
        self.assertGreaterEqual(mc.goal_attainment_probability, 0.0)
        self.assertLessEqual(mc.goal_attainment_probability, 100.0)


if __name__ == "__main__":
    unittest.main()
