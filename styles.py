"""Small, local style layer for InvestPath's Streamlit interface."""

import streamlit as st


def apply_styles() -> None:
    """Give Streamlit an elite, institutional-grade fintech dashboard aesthetic with supreme readability."""
    st.markdown(
        """
        <style>
        :root {
            --ip-bg: #f8fafc;
            --ip-surface: #ffffff;
            --ip-card: #ffffff;
            --ip-border: #e2e8f0;
            --ip-text: #0f172a;
            --ip-muted: #64748b;
            --ip-emerald: #059669;
            --ip-emerald-light: #ecfdf5;
            --ip-emerald-glow: rgba(5, 150, 105, 0.15);
        }

        .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"] {
            background: var(--ip-bg);
            color: var(--ip-text);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            font-size: 16px;
            line-height: 1.6;
        }

        [data-testid="stHeader"] {
            background: transparent;
        }

        [data-testid="stMainBlockContainer"] {
            max-width: 1360px;
            padding: 2.5rem clamp(1.25rem, 4vw, 4rem) 5rem;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #f1f5f9 0%, #e2e8f0 100%);
            border-right: 1px solid #cbd5e1;
        }

        [data-testid="stSidebar"] > div:first-child {
            background: transparent;
        }

        [data-testid="stSidebar"] h2 {
            color: #0f172a;
            font-size: 1.35rem;
            font-weight: 700;
            letter-spacing: -0.025em;
        }

        [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
            color: #334155;
            font-size: 0.92rem;
            font-weight: 600;
        }

        [data-testid="stSidebar"] input,
        [data-testid="stSidebar"] [data-baseweb="select"] div {
            border: 1px solid #cbd5e1;
            border-radius: 10px;
            background: #ffffff;
            color: #0f172a;
            font-size: 0.95rem;
        }

        [data-testid="stSidebar"] input:focus {
            border-color: var(--ip-emerald);
            box-shadow: 0 0 0 3px var(--ip-emerald-glow);
        }

        .ip-hero {
            position: relative;
            isolation: isolate;
            overflow: hidden;
            margin: 0 0 2rem;
            padding: clamp(2.5rem, 5vw, 4.25rem) clamp(2rem, 4vw, 4rem);
            border: 1px solid #047857;
            border-radius: 24px;
            background: linear-gradient(135deg, #064e3b 0%, #065f46 50%, #047857 100%);
            box-shadow: 0 20px 45px rgba(6, 78, 59, 0.2);
            color: #ffffff;
        }

        .ip-hero__eyebrow {
            margin: 0 0 0.85rem;
            color: #a7f3d0;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.16em;
            text-transform: uppercase;
        }

        .ip-hero h1 {
            margin: 0;
            color: #ffffff;
            font-size: clamp(2.4rem, 4.8vw, 3.8rem);
            font-weight: 750;
            letter-spacing: -0.04em;
            line-height: 1.1;
        }

        .ip-hero h1 span {
            color: #6ee7b7;
            font-weight: 450;
        }

        .ip-hero__description {
            max-width: 620px;
            margin: 1.15rem 0 0;
            color: rgba(255, 255, 255, 0.9);
            font-size: clamp(1.05rem, 1.6vw, 1.2rem);
            line-height: 1.65;
        }

        .ip-section-label {
            margin: 0 0 0.4rem;
            color: #059669;
            font-size: 0.75rem;
            font-weight: 750;
            letter-spacing: 0.14em;
            text-transform: uppercase;
        }

        [data-testid="stMetric"] {
            min-height: 125px;
            padding: 1.35rem 1.45rem;
            border: 1px solid var(--ip-border);
            border-radius: 18px;
            background: var(--ip-card);
            box-shadow: 0 4px 20px rgba(15, 23, 42, 0.05);
            transition: transform 160ms ease, box-shadow 160ms ease, border-color 160ms ease;
        }

        [data-testid="stMetric"]:hover {
            transform: translateY(-2px);
            border-color: #cbd5e1;
            box-shadow: 0 10px 30px rgba(15, 23, 42, 0.09);
        }

        [data-testid="stMetricLabel"] p {
            color: var(--ip-muted);
            font-size: 0.88rem;
            font-weight: 600;
        }

        [data-testid="stMetricValue"] {
            color: var(--ip-text);
            font-size: clamp(1.6rem, 2.5vw, 2.25rem);
            font-weight: 750;
            letter-spacing: -0.035em;
        }

        [data-testid="stVerticalBlockBorderWrapper"] {
            border-color: var(--ip-border) !important;
            border-radius: 20px !important;
            background: var(--ip-surface) !important;
            box-shadow: 0 6px 25px rgba(15, 23, 42, 0.04);
        }

        [data-testid="stAlert"] {
            border: 1px solid #a7f3d0;
            border-radius: 14px;
            background: #ecfdf5;
            color: #065f46;
            font-size: 0.95rem;
            font-weight: 500;
        }

        [data-testid="stAlert"] p {
            color: #065f46;
        }

        .ip-scenario-tag {
            display: inline-block;
            margin: 0.15rem 0 0.5rem;
            padding: 0.35rem 0.75rem;
            border: 1px solid #a7f3d0;
            border-radius: 999px;
            background: #ecfdf5;
            color: #065f46;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.04em;
        }

        [data-testid="stExpander"] {
            border-color: var(--ip-border);
            border-radius: 16px;
            background: var(--ip-surface);
            box-shadow: 0 2px 10px rgba(15, 23, 42, 0.03);
        }

        h2, h3 {
            color: var(--ip-text);
            letter-spacing: -0.03em;
            font-weight: 700;
        }

        @media (max-width: 760px) {
            [data-testid="stMainBlockContainer"] {
                padding: 1.25rem 1rem 3rem;
            }

            .ip-hero {
                margin-bottom: 1.25rem;
                padding: 2rem 1.35rem;
                border-radius: 20px;
            }

            [data-testid="stMetric"] {
                min-height: 105px;
                padding: 1rem;
            }
        }

        @media (prefers-reduced-motion: reduce) {
            [data-testid="stMetric"] {
                transition: none;
            }

            [data-testid="stMetric"]:hover {
                transform: none;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
