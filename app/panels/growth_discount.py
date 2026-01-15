"""Growth at a Discount panel - high NTM growth with low forward P/E."""

import streamlit as st
import pandas as pd
import numpy as np

# Filter thresholds
MKT_CAP_MIN = 100e9          # $100B market cap
FWD_PE_MAX = 25              # Forward P/E < 25
NTM_EPS_GROWTH_MIN = 0.20    # 20% NTM EPS growth
FWD_PE_HIGHLIGHT = 20        # Highlight rows with Fwd P/E < 20


def render_growth_discount_panel(df: pd.DataFrame) -> None:
    """Render panel showing high growth stocks at low valuations."""

    st.subheader("Accelerating growth at a low P/E")
    st.caption("Filters: Mkt Cap > $100B, Fwd P/E < 25, NTM EPS Gr > 20%  \nSorted by Fwd P/E | Green = Fwd P/E < 20")

    # Filter criteria
    filtered_df = df[
        (df["pe_forward"].notna()) &
        (df["pe_forward"] > 0) &
        (df["pe_forward"] < FWD_PE_MAX) &
        (df["market_cap"] > MKT_CAP_MIN) &
        (df["ntm_eps_growth"] > NTM_EPS_GROWTH_MIN)
    ].copy()

    if filtered_df.empty:
        st.warning("No stocks match the criteria.")
        return

    # Sort by forward P/E (ascending - cheapest first)
    filtered_df = filtered_df.sort_values("pe_forward", ascending=True).reset_index(drop=True)

    # Store forward P/E values for styling
    pe_values = filtered_df["pe_forward"].values

    total = len(filtered_df)

    # Create display DataFrame
    display_df = pd.DataFrame({
        "#": range(1, total + 1),
        "Symbol": filtered_df["symbol"].values,
        "Company": filtered_df["company_name"].values,
        "Fwd P/E": filtered_df["pe_forward"].values,
        "P/E TTM": filtered_df["pe_ttm"].values,
        "Mkt Cap ($B)": (filtered_df["market_cap"] / 1e9).values,
        "NTM EPS Gr (%)": (filtered_df["ntm_eps_growth"] * 100).values,
        "EPS CAGR 5Y (%)": (filtered_df["earnings_cagr_5yr"] * 100).values,
        "Rev CAGR 5Y (%)": (filtered_df["revenue_cagr_5yr"] * 100).values,
        "Margin (%)": (filtered_df["profit_margin"] * 100).values,
    })

    # Calculate height to show all rows without scrolling
    table_height = (total + 1) * 35 + 10

    # Style rows with gradient green (darker = lower P/E = better)
    highlighted_pe = pe_values[pe_values < FWD_PE_HIGHLIGHT]
    min_pe = float(np.min(highlighted_pe)) if len(highlighted_pe) > 0 else 0

    def style_row(row):
        idx = row.name
        pe = pe_values[idx] if idx < len(pe_values) else None
        if pd.notna(pe) and pe < FWD_PE_HIGHLIGHT:
            # Normalize: 0 = best (darkest), 1 = threshold (lightest)
            intensity = (pe - min_pe) / (FWD_PE_HIGHLIGHT - min_pe) if FWD_PE_HIGHLIGHT > min_pe else 0
            # Green gradient from #166534 (dark) to #86efac (light)
            r = int(22 + intensity * (134 - 22))
            g = int(101 + intensity * (239 - 101))
            b = int(52 + intensity * (172 - 52))
            return [f"background-color: rgb({r},{g},{b}); color: white"] * len(row)
        return [""] * len(row)

    styled_df = display_df.style.apply(style_row, axis=1)

    st.dataframe(
        styled_df,
        hide_index=True,
        use_container_width=True,
        height=table_height,
        column_config={
            "#": st.column_config.NumberColumn(width="small"),
            "Symbol": st.column_config.TextColumn(width="small"),
            "Company": st.column_config.TextColumn(width="medium"),
            "Fwd P/E": st.column_config.NumberColumn(format="%.1f", width="small"),
            "P/E TTM": st.column_config.NumberColumn(format="%.1f", width="small"),
            "Mkt Cap ($B)": st.column_config.NumberColumn(format="%.0f", width="small"),
            "NTM EPS Gr (%)": st.column_config.NumberColumn(format="%.1f", width="small"),
            "EPS CAGR 5Y (%)": st.column_config.NumberColumn(format="%.1f", width="small"),
            "Rev CAGR 5Y (%)": st.column_config.NumberColumn(format="%.1f", width="small"),
            "Margin (%)": st.column_config.NumberColumn(format="%.1f", width="small"),
        }
    )
