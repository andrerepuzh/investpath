"""Small, local style layer for InvestPath's Streamlit interface."""

import streamlit as st


def apply_styles() -> None:
    """Give the built-in Streamlit components a softer, more focused look."""
    st.markdown(
        """
        <style>
        :root {
            --ip-ink: #173b33;
            --ip-muted: #64766e;
            --ip-green: #28634f;
            --ip-line: #e3eae3;
            --ip-paper: #f5f8f4;
            --ip-white: #ffffff;
        }

        .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"] {
            background: var(--ip-paper);
            color: var(--ip-ink);
        }

        [data-testid="stHeader"] {
            background: transparent;
        }

        [data-testid="stMainBlockContainer"] {
            max-width: 1320px;
            padding: 2rem clamp(1rem, 3.5vw, 3.25rem) 4rem;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #edf4ed 0%, #f3f6f1 100%);
            border-right: 1px solid #e4ece4;
        }

        [data-testid="stSidebar"] > div:first-child {
            background: transparent;
        }

        [data-testid="stSidebar"] h2 {
            color: var(--ip-ink);
            letter-spacing: -0.025em;
        }

        [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
            color: #40564d;
            font-size: 0.88rem;
        }

        [data-testid="stSidebar"] input {
            border: 1px solid #d9e5da;
            border-radius: 12px;
            background: rgba(255, 255, 255, 0.88);
        }

        [data-testid="stSidebar"] input:focus {
            border-color: #6f9f84;
            box-shadow: 0 0 0 3px rgba(79, 133, 100, 0.14);
        }

        .ip-hero {
            position: relative;
            isolation: isolate;
            overflow: hidden;
            margin: 0 0 1.15rem;
            padding: clamp(2rem, 5vw, 4rem) clamp(1.5rem, 4vw, 3.5rem) 5.5rem;
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 28px;
            background: linear-gradient(122deg, #153d34 0%, #245e4b 58%, #528a70 100%);
            box-shadow: 0 16px 40px rgba(24, 66, 53, 0.11);
            color: #f7fbf6;
        }

        .ip-hero::before {
            position: absolute;
            z-index: -1;
            top: -13rem;
            right: -4rem;
            width: 30rem;
            height: 30rem;
            border: 1px solid rgba(235, 248, 235, 0.15);
            border-radius: 50%;
            background:
                radial-gradient(circle at 44% 56%, rgba(208, 235, 213, 0.2), transparent 65%);
            content: "";
        }

        .ip-hero__content {
            position: relative;
            z-index: 1;
            max-width: 680px;
        }

        .ip-hero__eyebrow {
            margin: 0 0 1rem;
            color: #c8e0d0;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.14em;
            text-transform: uppercase;
        }

        .ip-hero h1 {
            margin: 0;
            color: #ffffff;
            font-size: clamp(2.4rem, 5vw, 4rem);
            font-weight: 650;
            letter-spacing: -0.055em;
            line-height: 1.04;
        }

        .ip-hero h1 span {
            color: #d1e9d7;
            font-weight: 450;
        }

        .ip-hero__description {
            max-width: 560px;
            margin: 1rem 0 0;
            color: rgba(247, 251, 246, 0.84);
            font-size: clamp(1rem, 1.6vw, 1.15rem);
            line-height: 1.65;
        }

        .ip-hero__wave {
            position: absolute;
            right: 0;
            bottom: -1px;
            left: 0;
            display: block;
            width: 100%;
            height: 66px;
        }

        .ip-hero__wave path {
            fill: var(--ip-paper);
        }

        .ip-section-label {
            margin: 0 0 0.35rem;
            color: #708278;
            font-size: 0.7rem;
            font-weight: 750;
            letter-spacing: 0.13em;
            text-transform: uppercase;
        }

        [data-testid="stMetric"] {
            min-height: 115px;
            padding: 1.1rem 1.15rem;
            border: 1px solid var(--ip-line);
            border-radius: 18px;
            background: rgba(255, 255, 255, 0.92);
            box-shadow: 0 6px 20px rgba(37, 67, 54, 0.035);
            transition: transform 160ms ease, box-shadow 160ms ease;
        }

        [data-testid="stMetric"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 24px rgba(37, 67, 54, 0.075);
        }

        [data-testid="stMetricLabel"] p {
            color: var(--ip-muted);
            font-size: 0.82rem;
        }

        [data-testid="stMetricValue"] {
            color: var(--ip-ink);
            font-size: clamp(1.35rem, 2.2vw, 2rem);
            font-weight: 650;
            letter-spacing: -0.035em;
        }

        [data-testid="stVerticalBlockBorderWrapper"] {
            border-color: var(--ip-line) !important;
            border-radius: 20px !important;
            background: rgba(255, 255, 255, 0.72);
        }

        [data-testid="stAlert"] {
            border: 1px solid #dce9dc;
            border-radius: 15px;
            background: #edf5ed;
            color: #2f5543;
        }

        [data-testid="stAlert"] p {
            color: #2f5543;
        }

        .ip-scenario-tag {
            display: inline-block;
            margin: 0.15rem 0 0.5rem;
            padding: 0.3rem 0.62rem;
            border: 1px solid #dce8de;
            border-radius: 999px;
            background: #f2f7f1;
            color: #365e4a;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.035em;
        }

        [data-testid="stExpander"] {
            border-color: var(--ip-line);
            border-radius: 16px;
            background: rgba(255, 255, 255, 0.64);
        }

        h2, h3 {
            color: var(--ip-ink);
            letter-spacing: -0.035em;
        }

        @media (max-width: 760px) {
            [data-testid="stMainBlockContainer"] {
                padding: 1rem 0.85rem 2.5rem;
            }

            .ip-hero {
                margin-bottom: 0.8rem;
                padding: 1.75rem 1.3rem 4.5rem;
                border-radius: 22px;
            }

            .ip-hero::before {
                top: -12rem;
                right: -15rem;
            }

            .ip-hero__wave {
                height: 46px;
            }

            [data-testid="stMetric"] {
                min-height: 96px;
                padding: 0.85rem;
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
