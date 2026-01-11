from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class StockMetrics:
    """Container for all extracted stock metrics."""
    symbol: str
    company_name: Optional[str] = None
    market_cap: Optional[float] = None
    ttm_revenue: Optional[float] = None
    ttm_earnings: Optional[float] = None
    pe_ttm: Optional[float] = None
    pe_forward: Optional[float] = None
    profit_margin: Optional[float] = None
    revenue_cagr_5yr: Optional[float] = None
    earnings_cagr_5yr: Optional[float] = None
    no_loss_5yr: Optional[bool] = None  # True if no annual loss in last 5 years
    price: Optional[float] = None
    extraction_date: str = ""

    def __post_init__(self):
        if not self.extraction_date:
            self.extraction_date = datetime.now().strftime("%Y-%m-%d")

    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "company_name": self.company_name,
            "market_cap": self.market_cap,
            "ttm_revenue": self.ttm_revenue,
            "ttm_earnings": self.ttm_earnings,
            "pe_ttm": self.pe_ttm,
            "pe_forward": self.pe_forward,
            "profit_margin": self.profit_margin,
            "revenue_cagr_5yr": self.revenue_cagr_5yr,
            "earnings_cagr_5yr": self.earnings_cagr_5yr,
            "no_loss_5yr": self.no_loss_5yr,
            "price": self.price,
            "extraction_date": self.extraction_date,
        }


def calculate_cagr(start_value: float, end_value: float, years: int) -> Optional[float]:
    """Calculate Compound Annual Growth Rate."""
    if start_value <= 0 or end_value <= 0 or years <= 0:
        return None
    return (end_value / start_value) ** (1 / years) - 1


def extract_metrics(
    symbol: str,
    profile: Optional[dict],
    ratios: Optional[dict],
    income_annual: Optional[list],
    income_quarterly: Optional[list],
    estimates: Optional[list],
) -> StockMetrics:
    """Extract all metrics from raw FMP API data."""

    metrics = StockMetrics(symbol=symbol)
    current_year = datetime.now().year

    # From profile
    if profile:
        metrics.company_name = profile.get("companyName")
        metrics.market_cap = profile.get("marketCap")
        metrics.price = profile.get("price")

    # From ratios (TTM)
    if ratios:
        metrics.profit_margin = ratios.get("netProfitMargin")

    # TTM from quarterly income statements
    if income_quarterly and len(income_quarterly) >= 4:
        metrics.ttm_revenue = sum(q.get("revenue", 0) or 0 for q in income_quarterly[:4])
        metrics.ttm_earnings = sum(q.get("netIncome", 0) or 0 for q in income_quarterly[:4])
        ttm_eps = sum(q.get("eps", 0) or 0 for q in income_quarterly[:4])

        # Calculate P/E TTM
        if metrics.price and ttm_eps > 0:
            metrics.pe_ttm = metrics.price / ttm_eps

        # Calculate profit margin if not available from ratios
        if metrics.profit_margin is None and metrics.ttm_revenue and metrics.ttm_revenue > 0:
            metrics.profit_margin = metrics.ttm_earnings / metrics.ttm_revenue

    # 5-year CAGR from annual income statements
    if income_annual and len(income_annual) >= 6:
        latest = income_annual[0]
        five_years_ago = income_annual[5]

        rev_latest = latest.get("revenue", 0) or 0
        rev_old = five_years_ago.get("revenue", 0) or 0
        eps_latest = latest.get("eps", 0) or 0
        eps_old = five_years_ago.get("eps", 0) or 0

        metrics.revenue_cagr_5yr = calculate_cagr(rev_old, rev_latest, 5)
        metrics.earnings_cagr_5yr = calculate_cagr(eps_old, eps_latest, 5)  # EPS CAGR

        # Check if any loss in last 5 years (using netIncome from years 0-4)
        has_loss = False
        for year_data in income_annual[:5]:
            net_income = year_data.get("netIncome", 0) or 0
            if net_income < 0:
                has_loss = True
                break
        metrics.no_loss_5yr = not has_loss

    # Forward P/E from analyst estimates
    # Use next fiscal year estimate (skip if less than 30 days away)
    if estimates and metrics.price:
        from datetime import timedelta
        today = datetime.now()
        min_date = today + timedelta(days=30)  # At least 30 days out

        future_estimates = []
        for est in estimates:
            est_date_str = est.get("date", "")
            if est_date_str:
                try:
                    est_date = datetime.strptime(est_date_str[:10], "%Y-%m-%d")
                    eps = est.get("epsAvg")
                    if est_date > min_date and eps and eps > 0:
                        future_estimates.append((est_date, eps))
                except ValueError:
                    continue

        if future_estimates:
            future_estimates.sort(key=lambda x: x[0])
            _, fwd_eps = future_estimates[0]
            metrics.pe_forward = metrics.price / fwd_eps

    return metrics
