#!/usr/bin/env python3
"""
S&P 500 Metrics Extractor

Fetches key financial metrics for all S&P 500 companies and saves to CSV.
Designed to run daily via cron.
"""

import csv
import sys
from datetime import datetime
from pathlib import Path

# Add parent to path for imports when run directly
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import DATA_DIR
from src.fmp_client import FMPClient
from src.metrics import extract_metrics, StockMetrics
from src.sp500_list import get_sp500_tickers


def fetch_stock_metrics(client: FMPClient, symbol: str) -> StockMetrics:
    """Fetch all required data and extract metrics for a single stock."""
    profile = client.get_profile(symbol)
    ratios = client.get_ratios_ttm(symbol)
    income_annual = client.get_income_statement_annual(symbol, limit=6)
    income_quarterly = client.get_income_statement_quarterly(symbol, limit=4)
    estimates = client.get_analyst_estimates(symbol, limit=10)

    return extract_metrics(
        symbol=symbol,
        profile=profile,
        ratios=ratios,
        income_annual=income_annual,
        income_quarterly=income_quarterly,
        estimates=estimates,
    )


def save_to_csv(metrics_list: list[StockMetrics], output_path: Path):
    """Save metrics to CSV file."""
    if not metrics_list:
        print("No metrics to save")
        return

    fieldnames = list(metrics_list[0].to_dict().keys())

    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for m in metrics_list:
            writer.writerow(m.to_dict())

    print(f"Saved {len(metrics_list)} records to {output_path}")


def main(symbols: list[str] = None):
    """Main extraction routine."""
    client = FMPClient()

    # Get S&P 500 tickers if not provided
    if symbols is None:
        print("Fetching S&P 500 constituents from Wikipedia...")
        symbols = get_sp500_tickers()
        if not symbols:
            print("ERROR: Could not fetch S&P 500 list")
            sys.exit(1)
        print(f"Found {len(symbols)} tickers")

    # Extract metrics for each stock
    metrics_list = []
    failed = []
    total = len(symbols)

    print(f"\nExtracting metrics for {total} stocks...")
    print("-" * 50)

    for i, symbol in enumerate(symbols, 1):
        try:
            metrics = fetch_stock_metrics(client, symbol)
            metrics_list.append(metrics)

            # Progress indicator
            if i % 25 == 0 or i == total:
                pct = (i / total) * 100
                print(f"Progress: {i}/{total} ({pct:.1f}%) - Last: {symbol}")

        except Exception as e:
            failed.append((symbol, str(e)))
            print(f"  FAILED: {symbol} - {e}")

    # Summary
    print("-" * 50)
    print(f"Completed: {len(metrics_list)} success, {len(failed)} failed")

    if failed:
        print(f"Failed tickers: {[f[0] for f in failed]}")

    # Save to CSV
    date_str = datetime.now().strftime("%Y-%m-%d")
    output_path = DATA_DIR / f"sp500_metrics_{date_str}.csv"
    save_to_csv(metrics_list, output_path)

    return metrics_list


if __name__ == "__main__":
    # Allow passing specific symbols for testing
    if len(sys.argv) > 1:
        test_symbols = sys.argv[1].split(",")
        main(test_symbols)
    else:
        main()
