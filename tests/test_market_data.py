"""Automated unit tests for market data calculations and retrieval in InvestPath."""

from datetime import datetime
from unittest.mock import patch
import pandas as pd
import pytest

from market_data import (
    ASSET_REGISTRY,
    calculate_cagr,
    calculate_total_return,
    fetch_market_history,
)


def test_calculate_total_return_normal():
    ret = calculate_total_return(100.0, 150.0)
    assert ret == 0.50


def test_calculate_total_return_invalid():
    assert calculate_total_return(0.0, 150.0) is None
    assert calculate_total_return(-10.0, 150.0) is None
    assert calculate_total_return(float("nan"), 150.0) is None


def test_calculate_cagr_normal():
    # Exactly 2 years elapsed (730.5 days / 365.25 = 2.0 years)
    # (121 / 100) ** (1/2) - 1 = sqrt(1.21) - 1 = 1.1 - 1 = 0.10 (10%)
    cagr = calculate_cagr(100.0, 121.0, "2020-01-01", "2022-01-01")
    assert cagr is not None
    assert abs(cagr - 0.10) < 1e-4


def test_calculate_cagr_invalid_dates():
    # Start date after end date
    assert calculate_cagr(100.0, 121.0, "2022-01-01", "2020-01-01") is None
    # Same date
    assert calculate_cagr(100.0, 121.0, "2020-01-01", "2020-01-01") is None


def test_calculate_cagr_zero_price():
    assert calculate_cagr(0.0, 121.0, "2020-01-01", "2022-01-01") is None
    assert calculate_cagr(100.0, -50.0, "2020-01-01", "2022-01-01") is None


@patch("market_data.yf.Ticker")
def test_fetch_market_history_mocked(mock_ticker_class):
    mock_instance = mock_ticker_class.return_value
    mock_df = pd.DataFrame(
        {"Close": [100.0, 105.0, 110.0]},
        index=pd.to_datetime(["2023-01-01", "2023-01-02", "2023-01-03"]),
    )
    mock_instance.history.return_value = mock_df

    df = fetch_market_history("AAPL", period="1y")
    assert not df.empty
    assert len(df) == 3
    assert list(df["Close"]) == [100.0, 105.0, 110.0]


@patch("market_data.yf.Ticker")
def test_fetch_market_history_error(mock_ticker_class):
    mock_instance = mock_ticker_class.return_value
    mock_instance.history.side_effect = Exception("API error")

    df = fetch_market_history("INVALID", period="1y")
    assert df.empty
