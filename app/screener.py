"""
AV Screener - Investment Screening Tool

Run with: streamlit run app/screener.py
"""

import streamlit as st
from data_loader import load_latest_metrics, get_extraction_date
from panels.big_tech import render_big_tech_panel
from panels.value_growth import render_value_growth_panel


# Page configuration
st.set_page_config(
    page_title="AV Screener",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
)

# Title
st.title("AV Screener")

# Load data
try:
    df = load_latest_metrics()
    extraction_date = get_extraction_date()
    st.caption(f"Data as of: {extraction_date} | {len(df)} stocks")
except FileNotFoundError as e:
    st.error(f"Data not found: {e}")
    st.stop()

# Divider
st.divider()

# Section 1: Big Tech
render_big_tech_panel(df)

st.divider()

# Section 2: Value + Growth
render_value_growth_panel(df)
