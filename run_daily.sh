#!/bin/bash
# Daily S&P 500 metrics extraction script
# Add to cron: 0 18 * * 1-5 /path/to/av_screener/run_daily.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment
source venv/bin/activate

# Run extraction
echo "Starting S&P 500 metrics extraction at $(date)"
python -m src.extract_sp500

echo "Completed at $(date)"
