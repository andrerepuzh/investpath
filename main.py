"""InvestPath: an educational, beginner-friendly investment calculator & market explorer."""

import streamlit as st

from calculator import (
    Projection,
    calculate_projection,
    calculate_required_monthly_contribution,
    export_projection_csv,
    find_milestones,
    run_monte_carlo_simulation,
)
from market_data import (
    ASSET_REGISTRY,
    calculate_cagr,
    calculate_total_return,
    fetch_market_history,
)
from styles import apply_styles


SCENARIOS = (
    ("Cautious", 0.03, "A conservative annual growth assumption."),
    ("Balanced", 0.06, "A middle-of-the-road annual growth assumption."),
    ("Optimistic", 0.09, "A higher-growth annual return assumption."),
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
        st.caption(f"{annual_return:.0%} assumed yearly growth · illustrative")
        st.metric("Estimated final value", format_euros(projection.portfolio_value))
        st.caption(description)


@st.cache_data(ttl=3600)
def get_cached_market_history(ticker: str, period: str):
    """Retrieve historical market prices with 1-hour caching."""
    return fetch_market_history(ticker, period=period)


def main() -> None:
    st.set_page_config(
        page_title="InvestPath — Investment Learning & Market Explorer",
        layout="wide",
    )
    apply_styles()

    st.markdown(
        """
        <section class="ip-hero" aria-label="InvestPath introduction">
            <div class="ip-hero__content">
                <p class="ip-hero__eyebrow">InvestPath · learn investing by exploring</p>
                <h1>Your future,<br><span>in focus.</span></h1>
                <p class="ip-hero__description">
                    Understand how time, regular savings, and compounding grow your money.
                    Explore real historical market assets, set financial goals, and learn investing at your own pace.
                </p>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )
    st.warning(
        "All results and historical data are for education only, and are not personalized "
        "financial advice. Real investments can go down as well as up."
    )

    with st.sidebar:
        st.header("Your plan")
        st.caption("Adjust these numbers to see how your future changes.")
        
        initial_investment = st.number_input(
            "Money you invest at the start (€)",
            min_value=0.0,
            max_value=10_000_000.0,
            value=5_000.0,
            step=500.0,
            help="The amount you start with on day one.",
        )
        monthly_contribution = st.number_input(
            "How much you add each month (€)",
            min_value=0.0,
            max_value=1_000_000.0,
            value=200.0,
            step=50.0,
            help="Regular savings added every month.",
        )
        contribution_timing_label = st.selectbox(
            "When do you add your monthly savings?",
            options=("End of each month", "Start of each month"),
            index=0,
            help=(
                "At month-end, deposits start earning returns the following month. "
                "At start-of-month, they start earning right away."
            ),
        )
        contribution_timing = (
            "beginning"
            if contribution_timing_label == "Start of each month"
            else "end"
        )
        years = st.number_input(
            "How long you plan to invest (years)",
            min_value=1,
            max_value=60,
            value=20,
            step=1,
        )
        annual_return_percent = st.number_input(
            "Assumed yearly growth (%)",
            min_value=-50.0,
            max_value=30.0,
            value=6.0,
            step=0.25,
            format="%.2f",
            help="Expected average yearly growth before fees.",
        )
        annual_fee_percent = st.number_input(
            "Yearly investment fee (%)",
            min_value=0.0,
            max_value=10.0,
            value=0.25,
            step=0.05,
            format="%.2f",
            help="Annual management fee deducted from your returns.",
        )
        apply_inflation = st.checkbox(
            "Adjust for inflation (purchasing power)",
            value=True,
            help="Turn off to see nominal future amounts without price inflation adjustment.",
        )
        annual_inflation_percent = st.number_input(
            "Assumed yearly inflation (%)",
            min_value=0.0,
            max_value=20.0,
            value=2.0,
            step=0.25,
            format="%.2f",
            help="Estimated yearly increase in prices of goods and services.",
            disabled=not apply_inflation,
        )

        st.divider()
        st.header("Simulation settings")
        monte_carlo_volatility = st.number_input(
            "Market variability / Volatility (%)",
            min_value=0.0,
            max_value=50.0,
            value=15.0,
            step=1.0,
            help="How unpredictable or bumpy yearly returns might be.",
        )
        monte_carlo_runs = st.number_input(
            "Number of simulated futures",
            min_value=100,
            max_value=10_000,
            value=1000,
            step=100,
            help="Number of randomized market paths generated for testing.",
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

    # 6 Beginner-Friendly Navigation Tabs (Including Market Explorer)
    tab_home, tab_calc, tab_goals, tab_whatif, tab_market, tab_learn = st.tabs([
        "🏠 Home",
        "📈 Calculator",
        "🎯 Goals",
        "🎲 What If?",
        "📊 Market Explorer",
        "💡 Learn",
    ])

    with tab_home:
        st.markdown('<p class="ip-section-label">Overview</p>', unsafe_allow_html=True)
        st.subheader("Welcome to InvestPath — Your Money, Explained")
        st.markdown(
            "InvestPath is an interactive learning tool designed to help you understand how investing works. "
            "Whether you are saving for a house, retirement, or financial independence, seeing how money grows over time makes your future feel clearer."
        )

        col_h1, col_h2, col_h3 = st.columns(3)
        with col_h1:
            with st.container(border=True):
                st.markdown("### 📈 See Your Money Grow")
                st.write("Explore your personalized projection based on your starting money, monthly savings, and time horizon.")
                st.metric("Estimated portfolio", format_euros(projection.portfolio_value))
        with col_h2:
            with st.container(border=True):
                st.markdown("### 📊 Explore Real Markets")
                st.write("Inspect historical price data and returns for major indices, stocks, ETFs, and cryptocurrencies.")
                st.metric("Total contributions", format_euros(projection.total_contributions))
        with col_h3:
            with st.container(border=True):
                st.markdown("### 🎲 Explore Different Futures")
                st.write("Run simulations to see how market ups and downs could affect your final wealth outcome.")
                st.metric("Estimated growth", format_euros(projection.estimated_gain))

        st.markdown("---")
        st.info("👉 **Tip:** Use the sidebar on the left to adjust your starting money, monthly additions, and time horizon at any time!")

    with tab_calc:
        st.markdown('<p class="ip-section-label">Calculator</p>', unsafe_allow_html=True)
        st.subheader("See Your Money Grow")
        st.caption(
            f"Over {int(years)} years, starting with {format_euros(initial_investment)} and adding "
            f"{format_euros(monthly_contribution)} each month."
        )

        metric_columns = st.columns(4)
        metric_columns[0].metric("Estimated portfolio", format_euros(projection.portfolio_value))
        metric_columns[1].metric("Money you contributed", format_euros(projection.total_contributions))
        metric_columns[2].metric("Estimated growth", format_euros(projection.estimated_gain))
        metric_columns[3].metric(
            "What it's worth in today's prices",
            (
                format_euros(projection.inflation_adjusted_value)
                if apply_inflation
                else "Not applied"
            ),
            help="Estimated purchasing power after accounting for yearly inflation.",
        )

        gain_description = (
            f"Out of your total estimated portfolio of {format_euros(projection.portfolio_value)}, "
            f"{format_euros(projection.total_contributions)} is money you personally saved and deposited. "
            f"The remaining {format_euros(abs(projection.estimated_gain))} is earned growth generated by compounding returns."
        )
        st.markdown(f"**Breakdown:** {gain_description}")

        chart_data = [
            {
                "Year": point.month / 12,
                "Money you contributed": point.total_contributions,
                "Estimated portfolio": point.portfolio_value,
            }
            for point in projection.timeline
        ]
        with st.container(border=True):
            st.markdown(
                '<p class="ip-section-label">Growth chart</p>',
                unsafe_allow_html=True,
            )
            st.subheader("Your wealth over time")
            st.line_chart(
                chart_data,
                x="Year",
                y=["Money you contributed", "Estimated portfolio"],
                color=["#64748b", "#059669"],
                height=380,
            )

        csv_data = export_projection_csv(projection, annual_inflation=effective_annual_inflation)
        st.download_button(
            label="📥 Export month-by-month table (CSV)",
            data=csv_data,
            file_name="investpath_projection.csv",
            mime="text/csv",
            help="Download your monthly schedule in a format compatible with Excel or Google Sheets.",
        )

    with tab_goals:
        st.markdown('<p class="ip-section-label">Goals & Milestones</p>', unsafe_allow_html=True)
        st.subheader("Plan Your Financial Goals")
        st.caption("Set a target amount and find out what monthly savings rate you need to reach it.")

        with st.container(border=True):
            st.markdown("### 🎯 Goal Planner")
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                goal_target_value = st.number_input(
                    "Target future amount (€)",
                    min_value=1_000.0,
                    max_value=50_000_000.0,
                    value=max(100_000.0, round(projection.portfolio_value * 1.5, -3)),
                    step=5_000.0,
                    help="The total wealth goal you want to achieve.",
                )
            with col_g2:
                goal_years = st.number_input(
                    "Years to reach target",
                    min_value=1,
                    max_value=60,
                    value=int(years),
                    step=1,
                    help="Your deadline for reaching this goal.",
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
                            f"✅ **You are on track!** Your current monthly savings ({format_euros(monthly_contribution)}/mo) "
                            f"exceeds the required **{format_euros(required_monthly)}/mo** to reach {format_euros(goal_target_value)} in {int(goal_years)} years."
                        )
                    else:
                        st.info(
                            f"💡 To reach **{format_euros(goal_target_value)}** in {int(goal_years)} years, you need to save "
                            f"**{format_euros(required_monthly)} per month** (an increase of +{format_euros(abs(diff))}/mo over your current €{monthly_contribution:,.0f}/mo contribution)."
                        )
            except ValueError as e:
                st.warning(str(e))

        st.markdown("---")
        st.subheader("🏆 Wealth Milestones")
        st.caption("Estimated timeline when your portfolio crosses major milestones based on your current plan.")

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

    with tab_whatif:
        st.markdown('<p class="ip-section-label">What If?</p>', unsafe_allow_html=True)
        st.subheader("Explore Different Futures")
        st.caption("Real markets go up and down. Run simulations to see a range of possible outcomes.")

        with st.container(border=True):
            st.markdown("### 🎲 Monte Carlo Market Simulator")
            st.markdown(
                f"We simulated **{int(monte_carlo_runs):,} possible market futures** using **{monte_carlo_volatility:.1f}% annual market variability**. "
                "Because future returns are never exact, this helps you see a realistic range of outcomes."
            )

            target_for_mc = goal_target_value if 'goal_target_value' in locals() else 100_000.0
            mc_result = run_monte_carlo_simulation(
                initial_investment=initial_investment,
                monthly_contribution=monthly_contribution,
                years=int(years),
                annual_return=annual_return_percent / 100,
                annual_fee=annual_fee_percent / 100,
                annual_volatility=monte_carlo_volatility / 100,
                contribution_timing=contribution_timing,
                num_simulations=int(monte_carlo_runs),
                target_goal=target_for_mc,
                seed=42,
            )

            mc_cols = st.columns(4)
            mc_cols[0].metric("Median outcome (50/50)", format_euros(mc_result.median_final_value))
            mc_cols[1].metric("Cautious outcome (lower 10%)", format_euros(mc_result.p10_final_value))
            mc_cols[2].metric("Optimistic outcome (top 10%)", format_euros(mc_result.p90_final_value))
            if mc_result.goal_attainment_probability is not None:
                mc_cols[3].metric("Goal probability", f"{mc_result.goal_attainment_probability}%", f"Target: {format_euros(target_for_mc)}")
            else:
                mc_cols[3].metric("Goal probability", "N/A")

            mc_chart_data = [
                {
                    "Year": pt.month / 12,
                    "Cautious outcome (lower range)": pt.p10,
                    "25th percentile": pt.p25,
                    "Median outcome (expected)": pt.p50,
                    "75th percentile": pt.p75,
                    "Optimistic outcome (higher range)": pt.p90,
                    "Money you contributed": pt.total_contributions,
                }
                for pt in mc_result.percentile_timeline
            ]

            st.markdown("**How outcomes spread out over time:**")
            st.line_chart(
                mc_chart_data,
                x="Year",
                y=[
                    "Cautious outcome (lower range)",
                    "25th percentile",
                    "Median outcome (expected)",
                    "75th percentile",
                    "Optimistic outcome (higher range)",
                    "Money you contributed",
                ],
                color=["#94a3b8", "#cbd5e1", "#059669", "#cbd5e1", "#94a3b8", "#334155"],
                height=380,
            )
            st.caption(
                "In 80% of simulated market paths, your final outcome lands between the cautious and optimistic range. "
                "This model is for education and helps illustrate market risk."
            )

        st.markdown("---")
        st.subheader("Three Growth Scenarios")
        st.caption("Compare how different average yearly growth rates change your ending wealth.")
        scenario_columns = st.columns(3)
        for column, (name, annual_return, description) in zip(scenario_columns, SCENARIOS):
            scenario_projection = calculate_projection(
                **assumptions,
                annual_return=annual_return,
            )
            with column:
                render_scenario(name, annual_return, description, scenario_projection)

    with tab_market:
        st.markdown('<p class="ip-section-label">Market Explorer</p>', unsafe_allow_html=True)
        st.subheader("Explore Real Market History")
        st.caption("Inspect historical price performance, total returns, and annualized growth rates (CAGR) for major financial assets.")

        col_m1, col_m2 = st.columns(2)
        with col_m1:
            category = st.selectbox("Select asset category", options=list(ASSET_REGISTRY.keys()))
        with col_m2:
            asset_options = ASSET_REGISTRY[category]
            selected_asset = st.selectbox(
                "Select asset",
                options=asset_options,
                format_func=lambda x: f"{x['name']} ({x['ticker']})",
            )

        # Display asset metadata card
        with st.container(border=True):
            m_meta1, m_meta2, m_meta3, m_meta4 = st.columns(4)
            m_meta1.markdown(f"**Asset:** {selected_asset['name']}")
            m_meta2.markdown(f"**Ticker:** `{selected_asset['ticker']}`")
            m_meta3.markdown(f"**Type:** {selected_asset['type']}")
            m_meta4.markdown(f"**Currency:** {selected_asset['currency']} ({selected_asset['source']})")

        time_range = st.selectbox(
            "Select time range",
            options=["1 year", "3 years", "5 years", "Max history"],
            index=3,
        )
        period_map = {
            "1 year": "1y",
            "3 years": "3y",
            "5 years": "5y",
            "Max history": "max",
        }

        with st.spinner(f"Retrieving historical data for {selected_asset['ticker']}..."):
            hist_df = get_cached_market_history(selected_asset["ticker"], period_map[time_range])

        if hist_df.empty:
            st.error(f"Could not retrieve historical data for {selected_asset['ticker']}. Please check your internet connection or try another asset.")
        else:
            start_price = float(hist_df["Close"].iloc[0])
            end_price = float(hist_df["Close"].iloc[-1])
            start_date = hist_df.index[0]
            end_date = hist_df.index[-1]

            tot_ret = calculate_total_return(start_price, end_price)
            cagr = calculate_cagr(start_price, end_price, start_date, end_date)

            # 1-year return if available
            one_yr_ret = None
            if len(hist_df) >= 252:
                p_1yr_ago = float(hist_df["Close"].iloc[-252])
                one_yr_ret = calculate_total_return(p_1yr_ago, end_price)

            res_cols = st.columns(4)
            res_cols[0].metric("Latest price", f"{end_price:,.2f} {selected_asset['currency']}", f"As of {end_date.strftime('%Y-%m-%d')}")
            res_cols[1].metric("Total return", f"{tot_ret*100:+.2f}%" if tot_ret is not None else "N/A", f"From {start_date.strftime('%Y-%m-%d')}")
            res_cols[2].metric("Annualized return (CAGR)", f"{cagr*100:+.2f}%" if cagr is not None else "N/A", "Actual elapsed time")
            res_cols[3].metric("1-Year return", f"{one_yr_ret*100:+.2f}%" if one_yr_ret is not None else "N/A", "Trailing 252 trading days")

            st.markdown(f"**Historical price chart ({time_range}):**")
            chart_chart_data = pd.DataFrame({
                "Date": hist_df.index,
                "Close Price": hist_df["Close"].values,
            }).set_index("Date")
            st.line_chart(chart_chart_data)

            st.caption(
                f"Data source: {selected_asset['source']} ({selected_asset['ticker']}). "
                f"Note: Historical returns are past performance and **do not guarantee future results**. "
                f"Data retrieved via cached market feed."
            )

    with tab_learn:
        st.markdown('<p class="ip-section-label">Education</p>', unsafe_allow_html=True)
        st.subheader("Learn Investing Basics")
        st.caption("Key concepts every beginner should know before starting.")

        col_l1, col_l2 = st.columns(2)
        with col_l1:
            with st.container(border=True):
                st.markdown("### 🔄 The Power of Compounding")
                st.write(
                    "Compounding happens when your investment earnings start generating their own earnings. "
                    "Over long periods of time, this snowball effect is what turns regular savings into substantial wealth."
                )
            with st.container(border=True):
                st.markdown("### 💸 Fees Matter")
                st.write(
                    "Even a small yearly investment fee (like 0.5% vs 1.5%) can deduct thousands of euros from your final total over decades. "
                    "Keeping fees low lets you keep more of your returns."
                )
        with col_l2:
            with st.container(border=True):
                st.markdown("### 🛒 Inflation & Purchasing Power")
                st.write(
                    "Inflation means prices rise over time, so a euro in 30 years won't buy as much as a euro today. "
                    "InvestPath adjusts for inflation so you can see what your future money will actually be able to buy."
                )
            with st.container(border=True):
                st.markdown("### 🎢 Market Variability")
                st.write(
                    "Investments like stocks do not grow in a straight line. They experience ups and downs (volatility). "
                    "Staying invested for the long term helps smooth out these bumps."
                )

    st.markdown("---")
    st.info(
        "Investing involves risk, including the possible loss of money you invest. "
        "InvestPath is an educational learning tool and does not provide financial advice."
    )
    st.caption("Your inputs are used only in your browser session and are never saved or shared.")


if __name__ == "__main__":
    main()
