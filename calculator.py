"""Transparent investment projection calculations used by InvestPath."""

from __future__ import annotations

import csv
from dataclasses import dataclass
import io
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
    contribution_timing: str
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
    contribution_timing: str = "end",
) -> Projection:
    """Project monthly investing using effective annual rates.

    All rates are decimals (for example, 0.06 means 6%). The simplified model
    subtracts the annual fee from the assumed annual return, then converts that
    net effective annual rate to an effective monthly rate. Contributions are
    deposited at the end of each month by default. Set contribution_timing to
    "beginning" to deposit before that month's growth.
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

    if contribution_timing not in {"beginning", "end"}:
        raise ValueError("Contribution timing must be 'beginning' or 'end'.")
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
        if contribution_timing == "beginning":
            balance += monthly_contribution
            balance *= 1 + monthly_rate
        else:
            # Month-end deposits begin growing in the following month.
            balance *= 1 + monthly_rate
            balance += monthly_contribution
        contributions += monthly_contribution
        timeline.append(ProjectionPoint(month, contributions, balance))

    inflation_adjusted_value = balance / ((1 + annual_inflation) ** years)

    return Projection(
        years=years,
        monthly_rate=monthly_rate,
        contribution_timing=contribution_timing,
        total_contributions=contributions,
        portfolio_value=balance,
        estimated_gain=balance - contributions,
        inflation_adjusted_value=inflation_adjusted_value,
        timeline=tuple(timeline),
    )


def calculate_required_monthly_contribution(
    target_value: float,
    initial_investment: float,
    years: int,
    annual_return: float,
    annual_fee: float = 0.0,
    annual_inflation: float = 0.0,
    contribution_timing: str = "end",
) -> float:
    """Calculate the required monthly contribution to reach a target future portfolio value."""
    _require_finite("Target value", target_value)
    if target_value <= 0:
        raise ValueError("Target value must be greater than zero.")
    if initial_investment < 0:
        raise ValueError("Initial investment cannot be negative.")

    # Check if initial investment alone achieves or exceeds target
    proj_zero = calculate_projection(
        initial_investment=initial_investment,
        monthly_contribution=0.0,
        years=years,
        annual_return=annual_return,
        annual_fee=annual_fee,
        annual_inflation=annual_inflation,
        contribution_timing=contribution_timing,
    )
    if proj_zero.portfolio_value >= target_value:
        return 0.0

    MAX_MONTHLY_CONTRIBUTION = 1_000_000.0
    proj_max = calculate_projection(
        initial_investment=initial_investment,
        monthly_contribution=MAX_MONTHLY_CONTRIBUTION,
        years=years,
        annual_return=annual_return,
        annual_fee=annual_fee,
        annual_inflation=annual_inflation,
        contribution_timing=contribution_timing,
    )
    if proj_max.portfolio_value < target_value:
        raise ValueError(
            "Target value is unreachable within the selected horizon and maximum contribution limits."
        )

    # Binary search for required monthly contribution
    low = 0.0
    high = MAX_MONTHLY_CONTRIBUTION

    for _ in range(100):
        mid = (low + high) / 2.0
        proj_mid = calculate_projection(
            initial_investment=initial_investment,
            monthly_contribution=mid,
            years=years,
            annual_return=annual_return,
            annual_fee=annual_fee,
            annual_inflation=annual_inflation,
            contribution_timing=contribution_timing,
        )
        if proj_mid.portfolio_value >= target_value:
            high = mid
        else:
            low = mid

    return round(high, 2)


def find_milestones(
    timeline: tuple[ProjectionPoint, ...],
    milestones: list[float] | None = None,
) -> dict[float, int | None]:
    """Find the month each milestone is reached within the projection timeline."""
    if milestones is None:
        milestones = [10_000.0, 25_000.0, 50_000.0, 100_000.0]

    results: dict[float, int | None] = {}
    for milestone in milestones:
        reached_month: int | None = None
        for point in timeline:
            if point.portfolio_value >= milestone:
                reached_month = point.month
                break
        results[milestone] = reached_month
    return results


def export_projection_csv(projection: Projection, annual_inflation: float = 0.0) -> str:
    """Export monthly projection data as an Excel-compatible CSV string."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Month",
        "Year",
        "Total Contributions (€)",
        "Projected Portfolio (€)",
        "Estimated Growth (€)",
        "Inflation-Adjusted Value (€)",
    ])

    for point in projection.timeline:
        month = point.month
        year = round(month / 12, 2)
        contributions = round(point.total_contributions, 2)
        portfolio = round(point.portfolio_value, 2)
        growth = round(portfolio - contributions, 2)
        inflation_adjusted = round(
            portfolio / ((1 + annual_inflation) ** (month / 12)), 2
        )
        writer.writerow([
            month,
            year,
            contributions,
            portfolio,
            growth,
            inflation_adjusted,
        ])

    return output.getvalue()
