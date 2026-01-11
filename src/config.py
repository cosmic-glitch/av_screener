import os
from pathlib import Path

# API Configuration
FMP_API_KEY = os.environ.get("FMP_API_KEY", "a2OESdUYu2jWddK8MdJpRZUzT7OdqtrQ")
FMP_BASE_URL = "https://financialmodelingprep.com/stable"

# Rate limiting (Starter plan: 300 calls/min)
REQUESTS_PER_MINUTE = 250  # Stay under limit
REQUEST_DELAY = 60 / REQUESTS_PER_MINUTE  # ~0.24 seconds between requests

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)
