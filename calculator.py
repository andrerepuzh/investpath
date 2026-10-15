"""Transparent investment projection calculations used by InvestPath."""

from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class ProjectionPoint:
    month: int
    total_contributions: float
    portfolio_value: float


@dataclass(frozen=True)
class Projection:
    years: int
    monthly_rate: float
    total_contributions: float
    portfolio_value: float
    estimated_gain: float
    inflation_adjusted_value: float
    timeline: tuple[ProjectionPoint, ...]


def _require_finite(name: str, value: float) -> None:
    if not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number.")


def calculate_projection(
    initial_investment: float,
    monthly_contribution: float,
    years: int,
    annual_return: float,
    annual_fee: float = 0.0,
    annual_inflation: float = 0.0,
) -> Projection:
    """Project monthly investing using effective annual rates.

    All rates are decimals (for example, 0.06 means 6%). The simplified model
    subtracts the annual fee from the assumed annual return, then converts that
    net effective annual rate to an effective monthly rate. Contributions are
    deposited at the end of each month, after that month's growth.
    """
    values = {
        "Initial investment": initial_investment,
        "Monthly contribution": monthly_contribution,
        "Annual return": annual_return,
        "Annual fee": annual_fee,
        "Annual inflation": annual_inflation,
    }
    for name, value in values.items():
        _require_finite(name, value)

    if initial_investment < 0:
        raise ValueError("Initial investment cannot be negative.")
    if monthly_contribution < 0:
        raise ValueError("Monthly contribution cannot be negative.")
    if annual_fee < 0:
        raise ValueError("Annual fee cannot be negative.")
    if isinstance(years, bool) or not isinstance(years, int) or years < 1:
        raise ValueError("Investment duration must be a whole number of years.")

    net_annual_return = annual_return - annual_fee
    if net_annual_return < -1:
        raise ValueError("Annual return minus fee cannot be below -100%.")
    if annual_inflation <= -1:
        raise ValueError("Annual inflation must be greater than -100%.")

    monthly_rate = (1 + net_annual_return) ** (1 / 12) - 1
    months = years * 12
    balance = initial_investment
    contributions = initial_investment
    timeline = [ProjectionPoint(0, contributions, balance)]

    for month in range(1, months + 1):
        # Grow the existing balance first, then add this month's contribution.
        balance *= 1 + monthly_rate
        balance += monthly_contribution
        contributions += monthly_contribution
        timeline.append(ProjectionPoint(month, contributions, balance))

    inflation_adjusted_value = balance / ((1 + annual_inflation) ** years)

    return Projection(
        years=years,
        monthly_rate=monthly_rate,
        total_contributions=contributions,
        portfolio_value=balance,
        estimated_gain=balance - contributions,
        inflation_adjusted_value=inflation_adjusted_value,
        timeline=tuple(timeline),
    )
