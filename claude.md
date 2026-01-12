# AV Screener

S&P 500 stock screener that identifies potentially undervalued stocks based on forward P/E, growth rates, and profitability metrics.

## Live App
**URL:** https://avscreener.streamlit.app/

## Repository
**GitHub:** https://github.com/cosmic-glitch/av_screener

## Deployment

### Streamlit Cloud
- Auto-deploys from `main` branch on push
- Main file: `app/screener.py`

### GitHub Actions (Weekly Extraction)
- **Workflow:** `.github/workflows/weekly_extraction.yml`
- **Schedule:** Sundays at 6 AM UTC
- **Secret required:** `FMP_API_KEY` (repository secret)
- Extracts S&P 500 metrics from FMP API and commits updated CSV

## Project Structure

```
av_screener/
├── app/
│   ├── screener.py          # Main Streamlit app
│   ├── data_loader.py       # CSV loading utilities
│   └── panels/
│       ├── big_tech.py      # Panel 1: Best of Big Tech
│       └── value_growth.py  # Panel 2: Undervalued stocks
├── src/
│   ├── extract_sp500.py     # Main extraction script
│   ├── fmp_client.py        # FMP API client
│   ├── metrics.py           # Metrics extraction & CAGR calculation
│   ├── sp500_list.py        # Wikipedia scraper for S&P 500 list
│   └── config.py            # Configuration (API keys, paths)
├── data/
│   └── sp500_metrics_*.csv  # Extracted metrics (date-stamped)
└── .github/workflows/
    └── weekly_extraction.yml
```

## Key Metrics

- **Forward P/E:** Price / Next fiscal year estimated EPS (30+ days out)
- **EPS CAGR 5Y:** 5-year compound annual growth rate of EPS
- **Revenue CAGR 5Y:** 5-year compound annual growth rate of revenue
- **Profit Margin:** Net income / Revenue (TTM)
- **PEG:** Forward P/E / EPS CAGR
- **EY+G:** Earnings Yield (1/PE) + EPS Growth Rate
- **no_loss_5yr:** True if no annual net income loss in last 5 years

## Panel Filters

### Panel 1: Best of Big Tech
- Stocks: AAPL, MSFT, GOOGL, AMZN, META, NVDA
- Sorted by Forward P/E (ascending)
- Green highlight if Fwd P/E < 25

### Panel 2: Potentially Undervalued
- Market Cap > $100B
- Revenue CAGR > 8%
- EPS CAGR > 8%
- Profit Margin > 20%
- No loss in last 5 years
- Sorted by Forward P/E (ascending)

## Data Source
**Financial Modeling Prep (FMP) API**
- Endpoints: `/stable/profile`, `/stable/ratios-ttm`, `/stable/income-statement`, `/stable/analyst-estimates`
- Rate limit: 250 requests/minute
