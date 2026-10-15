"""InvestPath: an educational, hypothetical investment calculator."""

import streamlit as st

from calculator import (
    Projection,
    calculate_projection,
    calculate_required_monthly_contribution,
    export_projection_csv,
    find_milestones,
)
from styles import apply_styles


SCENARIOS = (
    ("Low", 0.03, "A cautious illustrative return assumption."),
    ("Base", 0.06, "A middle illustrative return assumption."),
    ("High", 0.09, "A more optimistic illustrative return assumption."),
)


def format_euros(amount: float) -> str:
    """Format euros consistently, using a period for decimals."""
    return f"€{amount:,.0f}"


def render_scenario(name: str, annual_return: float, description: str, projection: Projection) -> None:
    with st.container(border=True):
        st.markdown(
            f'<span class="ip-scenario-tag">{name} scenario</span>',
            unsafe_allow_html=True,
        )
        st.subheader(name)
        st.caption(f"{annual_return:.0%} assumed annual return · illustrative")
        st.metric("Projected value", format_euros(projection.portfolio_value))
        st.caption(description)


def main() -> None:
    st.set_page_config(
        page_title="InvestPath — Investment Calculator",
        layout="wide",
    )
    apply_styles()

    st.markdown(
        """
        <section class="ip-hero" aria-label="InvestPath introduction">
            <div class="ip-hero__content">
                <p class="ip-hero__eyebrow">InvestPath · intelligent wealth modeling</p>
                <h1>Your future,<br><span>in focus.</span></h1>
                <p class="ip-hero__description">
                    Explore how time, regular contributions, and disciplined compounding
                    shape your financial horizon. Adjust your assumptions below and watch your projection update instantly.
                </p>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )
    st.warning(
        "All results are hypothetical, not guaranteed, and are not personalized "
        "investment advice. Real investments can lose value."
    )

    with st.sidebar:
        st.header("Your assumptions")
        st.caption("Fine-tune your parameters to simulate your financial trajectory.")
        initial_investment = st.number_input(
            "Initial investment (€)",
            min_value=0.0,
            max_value=10_000_000.0,
            value=5_000.0,
            step=500.0,
            help="The amount invested at the beginning of the first month.",
        )
        monthly_contribution = st.number_input(
            "Monthly contribution (€)",
            min_value=0.0,
            max_value=1_000_000.0,
            value=200.0,
            step=50.0,
            help="Added at the selected time each month.",
        )
        contribution_timing_label = st.selectbox(
            "When is each monthly contribution added?",
            options=("End of each month", "Beginning of each month"),
            index=0,
            help=(
                "At month-end, a deposit starts growing next month. At month-start, "
                "it grows during the month it is added."
            ),
        )
        contribution_timing = (
            "beginning"
            if contribution_timing_label == "Beginning of each month"
            else "end"
        )
        years = st.number_input(
            "Investment duration (years)",
            min_value=1,
            max_value=60,
            value=20,
            step=1,
        )
        annual_return_percent = st.number_input(
            "Assumed annual return (%)",
            min_value=-50.0,
            max_value=30.0,
            value=6.0,
            step=0.25,
            format="%.2f",
            help="An illustrative effective annual return before the fee.",
        )
        annual_fee_percent = st.number_input(
            "Annual fee (%)",
            min_value=0.0,
            max_value=10.0,
            value=0.25,
            step=0.05,
            format="%.2f",
            help="A simplified annual fee deducted from the assumed return.",
        )
        apply_inflation = st.checkbox(
            "Adjust the future value for inflation",
            value=True,
            help="Turn this off to hide the purchasing-power estimate.",
        )
        annual_inflation_percent = st.number_input(
            "Assumed annual inflation (%)",
            min_value=0.0,
            max_value=20.0,
            value=2.0,
            step=0.25,
            format="%.2f",
            help="Used only to estimate what the future amount may buy in today's euros.",
            disabled=not apply_inflation,
        )

    effective_annual_inflation = (
        annual_inflation_percent / 100 if apply_inflation else 0.0
    )
    assumptions = {
        "initial_investment": initial_investment,
        "monthly_contribution": monthly_contribution,
        "years": int(years),
        "annual_fee": annual_fee_percent / 100,
        "annual_inflation": effective_annual_inflation,
        "contribution_timing": contribution_timing,
    }
    projection = calculate_projection(
        **assumptions,
        annual_return=annual_return_percent / 100,
    )

    st.markdown('<p class="ip-section-label">Your projection</p>', unsafe_allow_html=True)
    st.subheader(f"A {years}-year financial horizon")
    timing_display = (
        "beginning" if contribution_timing == "beginning" else "end"
    )
    inflation_summary = (
        f"{annual_inflation_percent:.2f}% per year"
        if apply_inflation
        else "off"
    )
    st.caption(
        f"Starting with {format_euros(initial_investment)}, adding "
        f"{format_euros(monthly_contribution)} at the {timing_display} of each "
        f"month for {int(years)} years. Gross return: {annual_return_percent:.2f}% "
        f"per year; annual fee: {annual_fee_percent:.2f}%; "
        f"inflation adjustment: {inflation_summary}."
    )

    metric_columns = st.columns(4)
    metric_columns[0].metric("Projected portfolio", format_euros(projection.portfolio_value))
    metric_columns[1].metric("Total contributions", format_euros(projection.total_contributions))
    metric_columns[2].metric("Estimated gain", format_euros(projection.estimated_gain))
    metric_columns[3].metric(
        "Value in today's euros",
        (
            format_euros(projection.inflation_adjusted_value)
            if apply_inflation
            else "Not applied"
        ),
        help=(
            "Projected value adjusted for the assumed inflation over the full period. "
            "Enable the inflation adjustment to show it."
        ),
    )

    gain_description = (
        f"Of the projected {format_euros(projection.portfolio_value)}, "
        f"{format_euros(projection.total_contributions)} comes from your initial "
        f"investment and regular monthly deposits. The remaining "
        f"{format_euros(abs(projection.estimated_gain))} represents modeled "
        f"{'growth' if projection.estimated_gain >= 0 else 'decline'} under your chosen assumptions."
    )
    st.markdown(f"**Breakdown:** {gain_description}")

    chart_data = [
        {
            "Year": point.month / 12,
            "Total contributions": point.total_contributions,
            "Projected portfolio": point.portfolio_value,
        }
        for point in projection.timeline
    ]
    with st.container(border=True):
        st.markdown(
            '<p class="ip-section-label">Growth over time</p>',
            unsafe_allow_html=True,
        )
        st.subheader("How your wealth could compound")
        st.line_chart(
            chart_data,
            x="Year",
            y=["Total contributions", "Projected portfolio"],
            color=["#64748b", "#059669"],
            height=380,
        )

    # Feature 3: Downloadable Projection CSV
    csv_data = export_projection_csv(projection, annual_inflation=effective_annual_inflation)
    st.download_button(
        label="📥 Export monthly projection table (CSV)",
        data=csv_data,
        file_name="investpath_projection.csv",
        mime="text/csv",
        help="Download month-by-month financial projection table compatible with Excel and Google Sheets.",
    )

    st.caption(
        "The slate line tracks your total cash contributions (principal), while "
        "the emerald line shows your total portfolio value over time. The expanding "
        "gap between them highlights cumulative compounding growth."
    )

    # Feature 1: Financial Goal Planner Section
    with st.container(border=True):
        st.markdown('<p class="ip-section-label">Goal planner</p>', unsafe_allow_html=True)
        st.subheader("🎯 Calculate required monthly contribution")
        st.caption("Specify your target future wealth goal and see what monthly savings rate is required under your current return and fee assumptions.")
        
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            goal_target_value = st.number_input(
                "Target future portfolio value (€)",
                min_value=1_000.0,
                max_value=50_000_000.0,
                value=max(100_000.0, round(projection.portfolio_value * 1.5, -3)),
                step=5_000.0,
                help="The desired future value you want to achieve.",
            )
        with col_g2:
            goal_years = st.number_input(
                "Years to reach target",
                min_value=1,
                max_value=60,
                value=int(years),
                step=1,
                help="Time horizon for achieving your financial goal.",
            )

        try:
            required_monthly = calculate_required_monthly_contribution(
                target_value=goal_target_value,
                initial_investment=initial_investment,
                years=int(goal_years),
                annual_return=annual_return_percent / 100,
                annual_fee=annual_fee_percent / 100,
                annual_inflation=effective_annual_inflation,
                contribution_timing=contribution_timing,
            )
            if required_monthly == 0.0:
                st.success("🎉 Your initial investment alone already achieves or exceeds this target within your timeframe!")
            else:
                diff = monthly_contribution - required_monthly
                if diff >= 0:
                    st.success(
                        f"✅ **You are on track!** Your current monthly contribution ({format_euros(monthly_contribution)}/mo) "
                        f"exceeds the required **{format_euros(required_monthly)}/mo** to reach {format_euros(goal_target_value)} in {int(goal_years)} years."
                    )
                else:
                    st.info(
                        f"💡 To reach **{format_euros(goal_target_value)}** in {int(goal_years)} years, you need to save "
                        f"**{format_euros(required_monthly)} per month** (an increase of +{format_euros(abs(diff))}/mo over your current €{monthly_contribution:,.0f}/mo contribution)."
                    )
        except ValueError as e:
            st.warning(str(e))

    # Feature 2: Investment Milestones Section
    with st.container(border=True):
        st.markdown('<p class="ip-section-label">Milestones</p>', unsafe_allow_html=True)
        st.subheader("🏆 Wealth Milestones")
        st.caption("Estimated timeline when your portfolio crosses major wealth thresholds under your current assumptions.")

        milestones_dict = find_milestones(projection.timeline, [10_000.0, 25_000.0, 50_000.0, 100_000.0])
        m_cols = st.columns(4)
        milestone_thresholds = [10_000.0, 25_000.0, 50_000.0, 100_000.0]
        
        for idx, threshold in enumerate(milestone_thresholds):
            month_reached = milestones_dict[threshold]
            col = m_cols[idx]
            with col:
                if month_reached is not None:
                    yrs_val = month_reached / 12
                    st.metric(
                        f"Target: {format_euros(threshold)}",
                        f"Month {month_reached}",
                        f"~{yrs_val:.1f} years"
                    )
                else:
                    st.metric(
                        f"Target: {format_euros(threshold)}",
                        "Not reached",
                        f"Within {years} yrs"
                    )

    st.subheader("Three illustrative return scenarios")
    scenario_columns = st.columns(3)
    for column, (name, annual_return, description) in zip(scenario_columns, SCENARIOS):
        scenario_projection = calculate_projection(
            **assumptions,
            annual_return=annual_return,
        )
        with column:
            render_scenario(name, annual_return, description, scenario_projection)

    with st.expander("How the calculations work"):
        st.markdown(
            """
            - **Total contributions** = initial investment + monthly contribution ×
              number of months.
            - **Net annual return** = assumed annual return − annual fee. This is a
              simplified fee model, not a quote of how a particular provider charges.
            - **Monthly return** = `(1 + net annual return)^(1/12) − 1`. This converts
              the effective annual assumption to a monthly rate, so 12 months of
              compounding equal one year at the net annual rate.
            - **Projected portfolio** is calculated one month at a time. With an
              end-of-month deposit: `new balance = old balance × (1 + monthly return)
              + deposit`. With a beginning-of-month deposit: `new balance =
              (old balance + deposit) × (1 + monthly return)`.
            - **Estimated gain** = projected portfolio − total contributions. It
              can be negative if the assumptions produce a loss.
            - **Value in today's euros** = projected portfolio ÷
              `(1 + annual inflation)^years`. This adjusts the nominal value for
              assumed loss of purchasing power; it is not money you receive today.

            The model assumes the same return, fee, and inflation every year. It
            does not model market ups and downs, taxes, or changes in costs.
            """
        )

    with st.expander("Investing ideas in plain English"):
        st.markdown(
            """
            - **Compound growth:** When returns stay invested, later returns can
              apply to both your original money and earlier growth. The calculator
              illustrates this with a steady monthly rate; real returns vary.
            - **Regular contributions:** Depositing regularly adds money to the
              plan over time. Earlier deposits have more time to grow, but neither
              regular deposits nor this illustration remove investment risk.
            - **Return and uncertainty:** A higher assumed return creates a larger
              projection, but higher potential returns usually come with greater
              uncertainty and the possibility of larger losses. The high scenario
              is not a recommended target.
            - **Inflation and buying power:** If prices rise, a future euro may buy
              less than a euro today. The inflation-adjusted figure expresses the
              projection in today's purchasing power.
            - **Scenarios are not predictions:** Low, base, and high values simply
              show how different return assumptions change the illustration.
              They are not forecasts, probabilities, or guarantees.
            """
        )

    st.info(
        "Investing involves risk, including the possible loss of your initial "
        "investment. These examples are for education only; they are hypothetical, "
        "not guaranteed, and not personalized investment advice."
    )
    st.caption(
        "Your assumptions are used only to calculate this page. InvestPath does not "
        "create an account or save your financial inputs."
    )


if __name__ == "__main__":
    main()
