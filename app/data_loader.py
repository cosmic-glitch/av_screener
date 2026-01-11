"""Data loading utilities for AV Screener."""

import streamlit as st
import pandas as pd
from pathlib import Path


def get_data_dir() -> Path:
    """Get the data directory path."""
    return Path(__file__).parent.parent / "data"


def find_latest_csv() -> Path:
    """Find the most recent sp500_metrics CSV file."""
    data_dir = get_data_dir()
    csv_files = sorted(data_dir.glob("sp500_metrics_*.csv"), reverse=True)
    if not csv_files:
        raise FileNotFoundError(f"No sp500_metrics CSV files found in {data_dir}")
    return csv_files[0]


@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_latest_metrics() -> pd.DataFrame:
    """Load the most recent metrics CSV into a DataFrame."""
    csv_path = find_latest_csv()
    df = pd.read_csv(csv_path)
    return df


def get_extraction_date() -> str:
    """Get the extraction date from the most recent CSV filename."""
    csv_path = find_latest_csv()
    # Extract date from filename: sp500_metrics_2026-01-09.csv -> 2026-01-09
    return csv_path.stem.replace("sp500_metrics_", "")


def format_currency(value: float, billions: bool = True) -> str:
    """Format a number as currency."""
    if pd.isna(value):
        return "N/A"
    if billions:
        return f"${value / 1e9:.1f}B"
    return f"${value:,.0f}"


def format_percentage(value: float) -> str:
    """Format a decimal as percentage."""
    if pd.isna(value):
        return "N/A"
    return f"{value * 100:.1f}%"


def format_ratio(value: float) -> str:
    """Format a ratio (P/E, etc.)."""
    if pd.isna(value):
        return "N/A"
    return f"{value:.1f}"
