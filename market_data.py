"""Market data retrieval and historical return calculations for InvestPath."""

from __future__ import annotations

import math
from typing import Any
import pandas as pd
import yfinance as yf

ASSET_REGISTRY = {
    "Stock Indices": [
        {"ticker": "^GSPC", "name": "S&P 500 Index", "type": "Index", "currency": "USD", "source": "Yahoo Finance"},
        {"ticker": "^NDX", "name": "Nasdaq-100 Index", "type": "Index", "currency": "USD", "source": "Yahoo Finance"},
    ],
    "Individual Stocks": [
        {"ticker": "AAPL", "name": "Apple Inc.", "type": "Stock", "currency": "USD", "source": "Yahoo Finance"},
        {"ticker": "MSFT", "name": "Microsoft Corporation", "type": "Stock", "currency": "USD", "source": "Yahoo Finance"},
        {"ticker": "TSLA", "name": "Tesla, Inc.", "type": "Stock", "currency": "USD", "source": "Yahoo Finance"},
    ],
    "ETFs": [
        {"ticker": "SPY", "name": "SPDR S&P 500 ETF Trust", "type": "ETF", "currency": "USD", "source": "Yahoo Finance"},
        {"ticker": "VOO", "name": "Vanguard S&P 500 ETF", "type": "ETF", "currency": "USD", "source": "Yahoo Finance"},
        {"ticker": "QQQ", "name": "Invesco QQQ Trust", "type": "ETF", "currency": "USD", "source": "Yahoo Finance"},
    ],
    "Cryptocurrencies": [
        {"ticker": "BTC-USD", "name": "Bitcoin", "type": "Crypto", "currency": "USD", "source": "Yahoo Finance"},
        {"ticker": "ETH-USD", "name": "Ethereum", "type": "Crypto", "currency": "USD", "source": "Yahoo Finance"},
    ],
}

def calculate_total_return(start_price: float, end_price: float) -> float | None:
    """Calculate total percentage return between start and end prices."""
    if not math.isfinite(start_price) or not math.isfinite(end_price):
        return None
    if start_price <= 0:
        return None
    return (end_price - start_price) / start_price

def calculate_cagr(start_price: float, end_price: float, start_date: Any, end_date: Any) -> float | None:
    """Calculate Compound Annual Growth Rate (CAGR) based on actual elapsed time."""
    if not math.isfinite(start_price) or not math.isfinite(end_price):
        return None
    if start_price <= 0 or end_price <= 0:
        return None
    try:
        s_date = pd.to_datetime(start_date)
        e_date = pd.to_datetime(end_date)
        days = (e_date - s_date).days
        if days <= 0:
            return None
        years = days / 365.25
        if years <= 0:
            return None
        return (end_price / start_price) ** (1 / years) - 1
    except Exception:
        return None

def fetch_market_history(ticker: str, period: str = "max") -> pd.DataFrame:
    """Fetch historical daily price data for a ticker using yfinance, ensuring sorted, tz-naive, and valid numeric values."""
    try:
        t = yf.Ticker(ticker)
        df = t.history(period=period)
        if df is None or df.empty:
            return pd.DataFrame()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        if "Close" not in df.columns:
            return pd.DataFrame()
        df = df.dropna(subset=["Close"])
        df = df[pd.to_numeric(df["Close"], errors="coerce").notnull()]
        df = df.sort_index()
        if isinstance(df.index, pd.DatetimeIndex) and df.index.tz is not None:
            df.index = df.index.tz_localize(None)
        if df.empty:
            return pd.DataFrame()
        return df
    except Exception:
        return pd.DataFrame()
