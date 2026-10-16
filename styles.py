"""Small, local style layer for InvestPath's Streamlit interface."""

import streamlit as st


def apply_styles() -> None:
    """Give Streamlit a sophisticated, warm off-white fintech aesthetic with restrained emerald accents."""
    st.markdown(
        """
        <style>
        :root {
            --ip-bg: #fbfbfa;
            --ip-surface: #ffffff;
            --ip-card: #ffffff;
            --ip-border: #e4e4df;
            --ip-text: #1c1c1a;
            --ip-muted: #6b6b63;
            --ip-emerald: #0d9488;
            --ip-emerald-light: #f0fdf4;
            --ip-emerald-glow: rgba(13, 148, 136, 0.12);
        }

        .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"] {
            background: var(--ip-bg);
            color: var(--ip-text);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            font-size: 15.5px;
            line-height: 1.6;
        }

        [data-testid="stHeader"] {
            background: transparent;
        }

        [data-testid="stMainBlockContainer"] {
            max-width: 1320px;
            padding: 2.2rem clamp(1.2rem, 3.5vw, 3.5rem) 5rem;
        }

        [data-testid="stSidebar"] {
            background: #f4f4f0;
            border-right: 1px solid var(--ip-border);
        }

        [data-testid="stSidebar"] > div:first-child {
            background: transparent;
        }

        [data-testid="stSidebar"] h2 {
            color: #1c1c1a;
            font-size: 1.25rem;
            font-weight: 650;
            letter-spacing: -0.02em;
        }

        [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
            color: #4b4b43;
            font-size: 0.9rem;
            font-weight: 550;
        }

        [data-testid="stSidebar"] input,
        [data-testid="stSidebar"] [data-baseweb="select"] div {
            border: 1px solid var(--ip-border);
            border-radius: 8px;
            background: #ffffff;
            color: #1c1c1a;
            font-size: 0.92rem;
        }

        [data-testid="stSidebar"] input:focus {
            border-color: var(--ip-emerald);
            box-shadow: 0 0 0 2px var(--ip-emerald-glow);
        }

        .ip-hero {
            margin: 0 0 1.75rem;
            padding: clamp(2rem, 4vw, 3.25rem) clamp(1.75rem, 3.5vw, 3.5rem);
            border: 1px solid var(--ip-border);
            border-radius: 16px;
            background: #ffffff;
            box-shadow: 0 4px 20px rgba(28, 28, 26, 0.03);
        }

        .ip-hero__eyebrow {
            margin: 0 0 0.6rem;
            color: #0d9488;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.14em;
            text-transform: uppercase;
        }

        .ip-hero h1 {
            margin: 0;
            color: #1c1c1a;
            font-size: clamp(2.2rem, 4.2vw, 3.4rem);
            font-weight: 700;
            letter-spacing: -0.035em;
            line-height: 1.15;
        }

        .ip-hero h1 span {
            color: #0d9488;
            font-weight: 450;
        }

        .ip-hero__description {
            max-width: 580px;
            margin: 0.9rem 0 0;
            color: var(--ip-muted);
            font-size: clamp(1rem, 1.5vw, 1.12rem);
            line-height: 1.6;
        }

        .ip-section-label {
            margin: 0 0 0.35rem;
            color: #0d9488;
            font-size: 0.72rem;
            font-weight: 750;
            letter-spacing: 0.14em;
            text-transform: uppercase;
        }

        [data-testid="stMetric"] {
            min-height: 110px;
            padding: 1.1rem 1.25rem;
            border: 1px solid var(--ip-border);
            border-radius: 14px;
            background: var(--ip-card);
            box-shadow: 0 2px 12px rgba(28, 28, 26, 0.02);
            transition: border-color 140ms ease;
        }

        [data-testid="stMetric"]:hover {
            border-color: #cbd5e1;
        }

        [data-testid="stMetricLabel"] p {
            color: var(--ip-muted);
            font-size: 0.85rem;
            font-weight: 550;
        }

        [data-testid="stMetricValue"] {
            color: var(--ip-text);
            font-size: clamp(1.4rem, 2.2vw, 1.95rem);
            font-weight: 700;
            letter-spacing: -0.03em;
        }

        [data-testid="stVerticalBlockBorderWrapper"] {
            border-color: var(--ip-border) !important;
            border-radius: 16px !important;
            background: var(--ip-surface) !important;
            box-shadow: 0 4px 18px rgba(28, 28, 26, 0.03);
        }

        [data-testid="stAlert"] {
            border: 1px solid #99f6e4;
            border-radius: 12px;
            background: #f0fdf4;
            color: #134e4a;
            font-size: 0.92rem;
        }

        [data-testid="stAlert"] p {
            color: #134e4a;
        }

        .ip-scenario-tag {
            display: inline-block;
            margin: 0.1rem 0 0.4rem;
            padding: 0.25rem 0.6rem;
            border: 1px solid #99f6e4;
            border-radius: 999px;
            background: #f0fdf4;
            color: #134e4a;
            font-size: 0.74rem;
            font-weight: 700;
            letter-spacing: 0.03em;
        }

        [data-testid="stExpander"] {
            border-color: var(--ip-border);
            border-radius: 14px;
            background: var(--ip-surface);
            box-shadow: 0 2px 8px rgba(28, 28, 26, 0.02);
        }

        h2, h3 {
            color: var(--ip-text);
            letter-spacing: -0.025em;
            font-weight: 650;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
