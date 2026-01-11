"""Fetch S&P 500 constituent list from Wikipedia."""

import requests
import re


def get_sp500_tickers() -> list[str]:
    """Fetch current S&P 500 tickers from Wikipedia."""
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    html = resp.text

    # Parse the first table which contains current constituents
    # Look for ticker symbols in the table (they're in the first column)
    # Pattern matches tickers in table cells, typically formatted as:
    # <td>...<a...>TICKER</a>...</td> or just <td>TICKER</td>

    # Find the wikitable with constituents
    table_match = re.search(r'<table[^>]*class="[^"]*wikitable[^"]*sortable[^"]*"[^>]*>(.*?)</table>', html, re.DOTALL)
    if not table_match:
        # Fallback: try any wikitable
        table_match = re.search(r'<table[^>]*class="[^"]*wikitable[^"]*"[^>]*>(.*?)</table>', html, re.DOTALL)

    if not table_match:
        raise ValueError("Could not find S&P 500 table on Wikipedia")

    table_html = table_match.group(1)

    # Extract tickers from the first column of each row
    # The ticker is typically in the first <td> after <tr>, often as a link
    tickers = []
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_html, re.DOTALL)

    for row in rows:
        # Skip header rows
        if '<th' in row:
            continue

        # Get first td content
        td_match = re.search(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
        if td_match:
            cell = td_match.group(1)
            # Extract text, handling links
            # Try to get ticker from <a> tag first
            link_match = re.search(r'<a[^>]*>([A-Z.]+)</a>', cell)
            if link_match:
                ticker = link_match.group(1)
            else:
                # Fallback: get raw text
                ticker = re.sub(r'<[^>]+>', '', cell).strip()

            # Validate it looks like a ticker (1-5 uppercase letters, maybe with dot)
            if re.match(r'^[A-Z]{1,5}(\.[A-Z])?$', ticker):
                tickers.append(ticker)

    return tickers


if __name__ == "__main__":
    tickers = get_sp500_tickers()
    print(f"Found {len(tickers)} tickers")
    print(f"First 10: {tickers[:10]}")
    print(f"Last 10: {tickers[-10:]}")
