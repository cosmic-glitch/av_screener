import requests
import time
from typing import Optional
from .config import FMP_API_KEY, FMP_BASE_URL, REQUEST_DELAY


class FMPClient:
    """Client for Financial Modeling Prep API."""

    def __init__(self, api_key: str = FMP_API_KEY):
        self.api_key = api_key
        self.base_url = FMP_BASE_URL
        self.last_request_time = 0

    def _rate_limit(self):
        """Enforce rate limiting between requests."""
        elapsed = time.time() - self.last_request_time
        if elapsed < REQUEST_DELAY:
            time.sleep(REQUEST_DELAY - elapsed)
        self.last_request_time = time.time()

    def _get(self, endpoint: str, params: Optional[dict] = None) -> Optional[dict]:
        """Make a GET request to the FMP API."""
        self._rate_limit()

        if params is None:
            params = {}
        params["apikey"] = self.api_key

        url = f"{self.base_url}/{endpoint}"
        try:
            resp = requests.get(url, params=params, timeout=30)
            if resp.status_code != 200:
                return None
            return resp.json()
        except Exception:
            return None

    def get_sp500_constituents(self) -> list[str]:
        """Fetch current S&P 500 constituent tickers."""
        data = self._get("sp500_constituent")
        if not data:
            return []
        return [item["symbol"] for item in data]

    def get_profile(self, symbol: str) -> Optional[dict]:
        """Get company profile with market cap."""
        data = self._get("profile", {"symbol": symbol})
        if data and isinstance(data, list) and len(data) > 0:
            return data[0]
        return None

    def get_ratios_ttm(self, symbol: str) -> Optional[dict]:
        """Get TTM financial ratios."""
        data = self._get("ratios", {"symbol": symbol, "period": "ttm"})
        if data and isinstance(data, list) and len(data) > 0:
            return data[0]
        return None

    def get_income_statement_annual(self, symbol: str, limit: int = 6) -> Optional[list]:
        """Get annual income statements for CAGR calculation."""
        return self._get("income-statement", {
            "symbol": symbol,
            "period": "annual",
            "limit": limit
        })

    def get_income_statement_quarterly(self, symbol: str, limit: int = 4) -> Optional[list]:
        """Get quarterly income statements for TTM calculation."""
        return self._get("income-statement", {
            "symbol": symbol,
            "period": "quarter",
            "limit": limit
        })

    def get_analyst_estimates(self, symbol: str, limit: int = 10) -> Optional[list]:
        """Get analyst estimates for forward P/E."""
        return self._get("analyst-estimates", {
            "symbol": symbol,
            "period": "annual",
            "limit": limit
        })
