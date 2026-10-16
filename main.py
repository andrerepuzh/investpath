"""InvestPath: an educational, premium investment dashboard & financial planning tool."""

import datetime
import pandas as pd
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


def render_tradingview_widget(ticker: str, height: int = 420):
    """Embed official TradingView advanced real-time chart widget."""
    tv_symbol_map = {
        "^GSPC": "SP:SPX",
        "^NDX": "NASDAQ:NDX",
        "AAPL": "NASDAQ:AAPL",
        "MSFT": "NASDAQ:MSFT",
        "TSLA": "NASDAQ:TSLA",
        "SPY": "AMEX:SPY",
        "VOO": "NYSE:VOO",
        "QQQ": "NASDAQ:QQQ",
        "BTC-USD": "BINANCE:BTCUSDT",
        "ETH-USD": "BINANCE:ETHUSDT",
    }
    tv_symbol = tv_symbol_map.get(ticker, f"NASDAQ:{ticker}")

    html_code = f"""
    <div class="tradingview-widget-container" style="height:{height}px;width:100%">
      <div id="tradingview_widget" style="height:100%;width:100%"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget(
      {{
        "width": "100%",
        "height": "{height}",
        "symbol": "{tv_symbol}",
        "interval": "D",
        "timezone": "Etc/UTC",
        "theme": "light",
        "style": "1",
        "locale": "en",
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": false,
        "allow_symbol_change": true,
        "container_id": "tradingview_widget"
      }}
      );
      </script>
    </div>
    """
    st.components.v1.html(html_code, height=height + 10)


def main() -> None:
    st.set_page_config(
        page_title="InvestPath — Investment Dashboard & Planning",
        layout="wide",
    )
    apply_styles()

    st.markdown(
        """
        <section class="ip-hero" aria-label="InvestPath introduction">
            <div class="ip-hero__content">
                <p class="ip-hero__eyebrow">InvestPath · intelligent wealth modeling & market analysis</p>
                <h1>Your future,<br><span>in focus.</span></h1>
                <p class="ip-hero__description">
                    Explore real-world market performance, track your portfolio holdings, and model your long-term financial growth with professional clarity.
                </p>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )
    st.warning(
        "All market data and financial projections are for education only, and are not personalized "
        "financial advice. Real investments can go down as well as up."
    )

    with st.sidebar:
        st.header("Your plan settings")
        st.caption("Configure your core baseline assumptions.")
        
        initial_investment = st.number_input(
            "Money you invest at the start (€)",
            min_value=0.0,
            max_value=10_000_000.0,
            value=10_000.0,
            step=500.0,
            help="Starting capital for projections.",
        )
        monthly_contribution = st.number_input(
            "How much you add each month (€)",
            min_value=0.0,
            max_value=1_000_000.0,
            value=300.0,
            step=50.0,
            help="Regular monthly savings deposit.",
        )
        contribution_timing_label = st.selectbox(
            "Monthly contribution timing",
            options=("End of each month", "Start of each month"),
            index=0,
        )
        contribution_timing = (
            "beginning"
            if contribution_timing_label == "Start of each month"
            else "end"
        )
        years = st.number_input(
            "Investment horizon (years)",
            min_value=1,
            max_value=60,
            value=20,
            step=1,
        )
        annual_return_percent = st.number_input(
            "Assumed yearly growth (%)",
            min_value=-50.0,
            max_value=30.0,
            value=6.5,
            step=0.25,
            format="%.2f",
        )
        annual_fee_percent = st.number_input(
            "Yearly investment fee (%)",
            min_value=0.0,
            max_value=10.0,
            value=0.20,
            step=0.05,
            format="%.2f",
        )
        apply_inflation = st.checkbox(
            "Adjust for inflation",
            value=True,
        )
        annual_inflation_percent = st.number_input(
            "Assumed yearly inflation (%)",
            min_value=0.0,
            max_value=20.0,
            value=2.0,
            step=0.25,
            format="%.2f",
            disabled=not apply_inflation,
        )

        st.divider()
        st.header("Simulation settings")
        monte_carlo_volatility = st.number_input(
            "Market volatility (%)",
            min_value=0.0,
            max_value=50.0,
            value=15.0,
            step=1.0,
        )
        monte_carlo_runs = st.number_input(
            "Simulation paths",
            min_value=100,
            max_value=10_000,
            value=1000,
            step=100,
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

    if "portfolio_holdings" not in st.session_state:
        st.session_state.portfolio_holdings = [
            {"ticker": "SPY", "shares": 25.0, "avg_cost": 420.0},
            {"ticker": "AAPL", "shares": 15.0, "avg_cost": 175.0},
        ]

    tab_dashboard, tab_portfolio, tab_planning = st.tabs([
        "📊 Dashboard",
        "💼 My Portfolio",
        "📐 Planning",
    ])

    with tab_dashboard:
        st.markdown('<p class="ip-section-label">Market Overview</p>', unsafe_allow_html=True)
        st.subheader("Explore Asset Performance")
        st.caption("Select an asset category and search or select an instrument to review historical returns, trends, and pricing.")

        flat_assets = []
        for cat, assets in ASSET_REGISTRY.items():
            for a in assets:
                flat_assets.append({**a, "category": cat})

        col_d1, col_d2 = st.columns([1, 2])
        with col_d1:
            selected_category = st.selectbox(
                "Filter by category",
                options=["All Categories"] + list(ASSET_REGISTRY.keys()),
            )
        with col_d2:
            filtered_assets = (
                flat_assets
                if selected_category == "All Categories"
                else [a for a in flat_assets if a["category"] == selected_category]
            )
            selected_asset = st.selectbox(
                "Select asset",
                options=filtered_assets,
                format_func=lambda x: f"{x['name']} ({x['ticker']}) — {x['type']}",
            )

        time_range = st.selectbox(
            "Time horizon",
            options=["1 year", "3 years", "5 years", "Max history"],
            index=3,
        )
        period_map = {
            "1 year": "1y",
            "3 years": "3y",
            "5 years": "5y",
            "Max history": "max",
        }

        with st.spinner(f"Loading historical market data for {selected_asset['ticker']}..."):
            hist_df = get_cached_market_history(selected_asset["ticker"], period_map[time_range])

        if hist_df.empty or "Close" not in hist_df.columns:
            st.error(f"Unable to load historical price data for {selected_asset['ticker']}. Please check your internet connection or try another asset.")
        else:
            hist_df = hist_df.sort_index()
            hist_df = hist_df.dropna(subset=["Close"])

            start_price = float(hist_df["Close"].iloc[0])
            end_price = float(hist_df["Close"].iloc[-1])
            start_date = hist_df.index[0]
            end_date = hist_df.index[-1]

            tot_ret = calculate_total_return(start_price, end_price)
            cagr = calculate_cagr(start_price, end_price, start_date, end_date)

            one_yr_ret = None
            if len(hist_df) >= 252:
                p_1yr_ago = float(hist_df["Close"].iloc[-252])
                one_yr_ret = calculate_total_return(p_1yr_ago, end_price)

            trend_desc = "upward trend" if (tot_ret or 0) >= 0 else "downward movement"
            st.markdown(f"**Market Context:** `{selected_asset['name']}` ({selected_asset['ticker']}) reflects a **{trend_desc}** over the selected {time_range} period.")

            d_cols = st.columns(4)
            d_cols[0].metric("Latest price", f"{end_price:,.2f} {selected_asset['currency']}", f"As of {end_date.strftime('%Y-%m-%d')}")
            d_cols[1].metric("Total return", f"{tot_ret*100:+.2f}%" if tot_ret is not None else "N/A", f"Since {start_date.strftime('%Y-%m-%d')}")
            d_cols[2].metric("Annualized return (CAGR)", f"{cagr*100:+.2f}%" if cagr is not None else "N/A", "Actual elapsed time")
            d_cols[3].metric("1-Year return", f"{one_yr_ret*100:+.2f}%" if one_yr_ret is not None else "N/A", "Trailing 252 trading days")

            # Chart view options: InvestPath Historical Chart vs TradingView Interactive Widget
            chart_view_mode = st.radio(
                "Chart Provider",
                options=["InvestPath Historical Line Chart", "TradingView Interactive Advanced Chart"],
                horizontal=True,
            )

            if chart_view_mode == "InvestPath Historical Line Chart":
                st.markdown(f"**Historical Price Chart ({selected_asset['name']} - {time_range})**")
                chart_data = pd.DataFrame({
                    "Date": hist_df.index,
                    "Close Price": hist_df["Close"].values,
                }).set_index("Date")
                st.line_chart(chart_data)
            else:
                st.markdown(f"**Interactive TradingView Chart ({selected_asset['name']})**")
                render_tradingview_widget(selected_asset["ticker"])

            st.caption(
                f"Asset: {selected_asset['name']} ({selected_asset['ticker']}) | Type: {selected_asset['type']} | "
                f"Source: {selected_asset['source']}. Historical performance is past data and does not guarantee future results."
            )

    with tab_portfolio:
        st.markdown('<p class="ip-section-label">Portfolio Tracker</p>', unsafe_allow_html=True)
        st.subheader("My Portfolio")
        st.caption("Track your personal holdings, quantity, cost basis, and estimated current value based on live market feeds.")

        with st.expander("➕ Add or Edit Portfolio Holding"):
            with st.form("portfolio_form"):
                p_col1, p_col2, p_col3 = st.columns(3)
                with p_col1:
                    add_asset = st.selectbox(
                        "Choose asset",
                        options=flat_assets,
                        format_func=lambda x: f"{x['name']} ({x['ticker']})",
                    )
                with p_col2:
                    add_shares = st.number_input("Number of shares / units", min_value=0.001, value=10.0, step=1.0)
                with p_col3:
                    add_cost = st.number_input("Average purchase price (€ / $)", min_value=0.01, value=100.0, step=5.0)

                submitted = st.form_submit_button("Add to Portfolio")
                if submitted:
                    existing = next((h for h in st.session_state.portfolio_holdings if h["ticker"] == add_asset["ticker"]), None)
                    if existing:
                        existing["shares"] = add_shares
                        existing["avg_cost"] = add_cost
                    else:
                        st.session_state.portfolio_holdings.append({
                            "ticker": add_asset["ticker"],
                            "shares": add_shares,
                            "avg_cost": add_cost,
                        })
                    st.success(f"Successfully updated holding for {add_asset['ticker']}!")

        if not st.session_state.portfolio_holdings:
            st.info("Your portfolio is currently empty. Add holdings above to track performance.")
        else:
            total_portfolio_value = 0.0
            total_cost_basis = 0.0
            holding_rows = []

            for h in st.session_state.portfolio_holdings:
                ticker = h["ticker"]
                shares = h["shares"]
                avg_cost = h["avg_cost"]
                cost_basis = shares * avg_cost
                total_cost_basis += cost_basis

                df_h = get_cached_market_history(ticker, period="5d")
                current_price = avg_cost
                if not df_h.empty and "Close" in df_h.columns:
                    current_price = float(df_h["Close"].iloc[-1])

                market_val = shares * current_price
                total_portfolio_value += market_val
                unrealized_pnl = market_val - cost_basis
                pnl_pct = (unrealized_pnl / cost_basis) * 100 if cost_basis > 0 else 0.0

                meta = next((a for a in flat_assets if a["ticker"] == ticker), {"name": ticker, "type": "Asset"})

                holding_rows.append({
                    "Asset": meta["name"],
                    "Ticker": ticker,
                    "Shares": shares,
                    "Avg Cost": format_euros(avg_cost),
                    "Current Price": format_euros(current_price),
                    "Market Value": format_euros(market_val),
                    "Profit / Loss": f"{format_euros(unrealized_pnl)} ({pnl_pct:+.2f}%)",
                })

            p_cols = st.columns(3)
            p_cols[0].metric("Total Portfolio Value", format_euros(total_portfolio_value))
            p_cols[1].metric("Total Cost Basis", format_euros(total_cost_basis))
            total_pnl = total_portfolio_value - total_cost_basis
            total_pnl_pct = (total_pnl / total_cost_basis) * 100 if total_cost_basis > 0 else 0.0
            p_cols[2].metric("Unrealized Profit / Loss", f"{format_euros(total_pnl)} ({total_pnl_pct:+.2f}%)")

            st.markdown("### Portfolio Holdings")
            st.table(holding_rows)

    with tab_planning:
        st.markdown('<p class="ip-section-label">Financial Planning</p>', unsafe_allow_html=True)
        st.subheader("Wealth Projections & Goals")
        st.caption("Model your long-term wealth accumulation, check financial goals, run risk simulations, and export schedules.")

        sub_calc, sub_goals, sub_sim, sub_learn = st.tabs([
            "📈 Projection Calculator",
            "🎯 Goal Planner",
            "🎲 Monte Carlo Risk",
            "💡 Learning Hub",
        ])

        with sub_calc:
            st.subheader(f"Deterministic Projection ({years}-Year Horizon)")
            metric_columns = st.columns(4)
            metric_columns[0].metric("Estimated portfolio", format_euros(projection.portfolio_value))
            metric_columns[1].metric("Total contributions", format_euros(projection.total_contributions))
            metric_columns[2].metric("Estimated growth", format_euros(projection.estimated_gain))
            metric_columns[3].metric(
                "Today's purchasing power",
                format_euros(projection.inflation_adjusted_value) if apply_inflation else "Not applied",
            )

            chart_proj_data = [
                {
                    "Year": point.month / 12,
                    "Total contributions": point.total_contributions,
                    "Projected portfolio": point.portfolio_value,
                }
                for point in projection.timeline
            ]
            st.line_chart(
                chart_proj_data,
                x="Year",
                y=["Total contributions", "Projected portfolio"],
                color=["#64748b", "#0d9488"],
                height=360,
            )

            csv_data = export_projection_csv(projection, annual_inflation=effective_annual_inflation)
            st.download_button(
                label="📥 Export monthly schedule (CSV)",
                data=csv_data,
                file_name="investpath_projection.csv",
                mime="text/csv",
            )

        with sub_goals:
            st.subheader("Goal Planner & Milestones")
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                goal_target_value = st.number_input(
                    "Target future portfolio value (€)",
                    min_value=1_000.0,
                    max_value=50_000_000.0,
                    value=max(100_000.0, round(projection.portfolio_value * 1.5, -3)),
                    step=5_000.0,
                )
            with col_g2:
                goal_years = st.number_input(
                    "Years to target",
                    min_value=1,
                    max_value=60,
                    value=int(years),
                    step=1,
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
                    st.success("🎉 Your initial investment alone achieves or exceeds this target!")
                else:
                    diff = monthly_contribution - required_monthly
                    if diff >= 0:
                        st.success(f"✅ On track! Current savings ({format_euros(monthly_contribution)}/mo) exceed required **{format_euros(required_monthly)}/mo**.")
                    else:
                        st.info(f"💡 Required savings: **{format_euros(required_monthly)}/mo** to reach {format_euros(goal_target_value)} in {int(goal_years)} years (delta: +{format_euros(abs(diff))}/mo).")
            except ValueError as e:
                st.warning(str(e))

            st.markdown("### Wealth Milestones")
            milestones_dict = find_milestones(projection.timeline, [10_000.0, 25_000.0, 50_000.0, 100_000.0])
            m_cols = st.columns(4)
            for idx, threshold in enumerate([10_000.0, 25_000.0, 50_000.0, 100_000.0]):
                m_reached = milestones_dict[threshold]
                with m_cols[idx]:
                    if m_reached is not None:
                        st.metric(format_euros(threshold), f"Month {m_reached}", f"~{m_reached/12:.1f} yrs")
                    else:
                        st.metric(format_euros(threshold), "Not reached", f"Within {years} yrs")

        with sub_sim:
            st.subheader("Monte Carlo Risk Simulator")
            mc_result = run_monte_carlo_simulation(
                initial_investment=initial_investment,
                monthly_contribution=monthly_contribution,
                years=int(years),
                annual_return=annual_return_percent / 100,
                annual_fee=annual_fee_percent / 100,
                annual_volatility=monte_carlo_volatility / 100,
                contribution_timing=contribution_timing,
                num_simulations=int(monte_carlo_runs),
                target_goal=goal_target_value if 'goal_target_value' in locals() else 100_000.0,
                seed=42,
            )
            mc_cols = st.columns(4)
            mc_cols[0].metric("Median (P50)", format_euros(mc_result.median_final_value))
            mc_cols[1].metric("Cautious (P10)", format_euros(mc_result.p10_final_value))
            mc_cols[2].metric("Optimistic (P90)", format_euros(mc_result.p90_final_value))
            if mc_result.goal_attainment_probability is not None:
                mc_cols[3].metric("Goal Probability", f"{mc_result.goal_attainment_probability}%")
            else:
                mc_cols[3].metric("Goal Probability", "N/A")

            mc_chart_data = [
                {
                    "Year": pt.month / 12,
                    "Cautious (P10)": pt.p10,
                    "Median (P50)": pt.p50,
                    "Optimistic (P90)": pt.p90,
                    "Contributions": pt.total_contributions,
                }
                for pt in mc_result.percentile_timeline
            ]
            st.line_chart(mc_chart_data, x="Year", y=["Cautious (P10)", "Median (P50)", "Optimistic (P90)", "Contributions"], height=340)

        with sub_learn:
            st.subheader("Learning Hub")
            st.write("Understand compounding, management fees, inflation, and market volatility through clear educational guides.")

    st.markdown("---")
    st.info("InvestPath is an educational learning tool and does not provide financial advice.")


if __name__ == "__main__":
    main()
