"""Big Tech stocks panel - ranked by Forward P/E."""

import streamlit as st
import pandas as pd
import numpy as np

# Big Tech stock tickers (excluding Tesla)
BIG_TECH_TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA"]

# Threshold for highlighting
FWD_PE_THRESHOLD = 25


def render_big_tech_panel(df: pd.DataFrame) -> None:
    """Render the Big Tech panel showing stocks ranked by forward P/E."""

    st.subheader("Big Tech firms at a good valuation")
    st.caption("Filters: AAPL, MSFT, GOOGL, AMZN, META, NVDA  \nSorted by Forward P/E | Green = Fwd P/E < 25")

    # Filter to Big Tech only
    tech_df = df[df["symbol"].isin(BIG_TECH_TICKERS)].copy()

    if tech_df.empty:
        st.warning("No Big Tech stocks found in the data.")
        return

    # Sort by forward P/E (ascending - cheapest first)
    tech_df = tech_df.sort_values("pe_forward", ascending=True).reset_index(drop=True)

    total = len(tech_df)

    # Store forward P/E values for styling
    pe_values = tech_df["pe_forward"].values

    # Create display DataFrame with formatted columns
    display_df = pd.DataFrame({
        "Rank": range(1, total + 1),
        "Symbol": tech_df["symbol"].values,
        "Company": tech_df["company_name"].values,
        "Fwd P/E": tech_df["pe_forward"].apply(lambda x: f"{x:.1f}" if pd.notna(x) else "N/A").values,
        "P/E TTM": tech_df["pe_ttm"].apply(lambda x: f"{x:.1f}" if pd.notna(x) else "N/A").values,
        "Mkt Cap": tech_df["market_cap"].apply(lambda x: f"${x/1e12:.2f}T" if pd.notna(x) else "N/A").values,
        "TTM Rev": tech_df["ttm_revenue"].apply(lambda x: f"${x/1e9:.0f}B" if pd.notna(x) else "N/A").values,
        "TTM Earn": tech_df["ttm_earnings"].apply(lambda x: f"${x/1e9:.0f}B" if pd.notna(x) else "N/A").values,
        "Margin": tech_df["profit_margin"].apply(lambda x: f"{x*100:.1f}%" if pd.notna(x) else "N/A").values,
        "Rev CAGR 5Y": tech_df["revenue_cagr_5yr"].apply(lambda x: f"{x*100:.1f}%" if pd.notna(x) else "N/A").values,
        "EPS CAGR 5Y": tech_df["earnings_cagr_5yr"].apply(lambda x: f"{x*100:.1f}%" if pd.notna(x) else "N/A").values,
    })

    # Style rows with gradient green (darker = lower P/E = better)
    highlighted_pe = pe_values[pe_values < FWD_PE_THRESHOLD]
    min_pe = float(np.min(highlighted_pe)) if len(highlighted_pe) > 0 else 0

    def style_row(row):
        idx = row.name
        pe = pe_values[idx] if idx < len(pe_values) else None
        if pd.notna(pe) and pe < FWD_PE_THRESHOLD:
            # Normalize: 0 = best (darkest), 1 = threshold (lightest)
            intensity = (pe - min_pe) / (FWD_PE_THRESHOLD - min_pe) if FWD_PE_THRESHOLD > min_pe else 0
            # Green gradient from #166534 (dark) to #86efac (light)
            r = int(22 + intensity * (134 - 22))
            g = int(101 + intensity * (239 - 101))
            b = int(52 + intensity * (172 - 52))
            return [f"background-color: rgb({r},{g},{b}); color: white"] * len(row)
        return [""] * len(row)

    styled_df = display_df.style.apply(style_row, axis=1)

    # Display the styled table
    st.dataframe(
        styled_df,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Rank": st.column_config.NumberColumn(width="small"),
            "Symbol": st.column_config.TextColumn(width="small"),
            "Company": st.column_config.TextColumn(width="medium"),
            "Fwd P/E": st.column_config.TextColumn(width="small"),
            "P/E TTM": st.column_config.TextColumn(width="small"),
            "Mkt Cap": st.column_config.TextColumn(width="small"),
            "TTM Rev": st.column_config.TextColumn(width="small"),
            "TTM Earn": st.column_config.TextColumn(width="small"),
            "Margin": st.column_config.TextColumn(width="small"),
            "Rev CAGR 5Y": st.column_config.TextColumn(width="small"),
            "EPS CAGR 5Y": st.column_config.TextColumn(width="small"),
        }
    )
