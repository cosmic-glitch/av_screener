"""Value + Growth stocks panel - lowest forward P/E with strong growth and margins."""

import streamlit as st
import pandas as pd

# Filter thresholds
REV_CAGR_MIN = 0.08      # 8% revenue growth
EARN_CAGR_MIN = 0.08     # 8% earnings growth
MARGIN_MIN = 0.20        # 20% profit margin
MKT_CAP_MIN = 100e9      # $100B market cap
TOP_N = 20               # Show top 20


def render_value_growth_panel(df: pd.DataFrame) -> None:
    """Render panel showing lowest forward P/E stocks with strong growth and margins."""

    st.subheader("Potentially undervalued considering their growth rates")
    st.caption("Filters: Mkt Cap > $100B, Rev CAGR > 8%, EPS CAGR > 8%, Margin > 20%, No loss in 5 yrs | Sorted by Fwd P/E")

    # Filter criteria
    filtered_df = df[
        (df["pe_forward"].notna()) &
        (df["pe_forward"] > 0) &
        (df["market_cap"] > MKT_CAP_MIN) &
        (df["revenue_cagr_5yr"] > REV_CAGR_MIN) &
        (df["earnings_cagr_5yr"] > EARN_CAGR_MIN) &
        (df["profit_margin"] > MARGIN_MIN) &
        (df["no_loss_5yr"] == True)
    ].copy()

    if filtered_df.empty:
        st.warning("No stocks with valid data.")
        return

    # Sort by forward P/E
    filtered_df = filtered_df.sort_values("pe_forward", ascending=True).reset_index(drop=True)

    # Calculate ranking metrics
    filtered_df["peg"] = filtered_df["pe_forward"] / (filtered_df["earnings_cagr_5yr"] * 100)

    # Percentile combo rank (lower = better for both final ranks)
    filtered_df["pe_rank"] = filtered_df["pe_forward"].rank()
    filtered_df["growth_rank"] = filtered_df["earnings_cagr_5yr"].rank(ascending=False)
    filtered_df["combo_rank"] = (filtered_df["pe_rank"] + filtered_df["growth_rank"]) / 2

    total = len(filtered_df)

    # Create display DataFrame with raw numeric values for proper sorting
    display_df = pd.DataFrame({
        "#": range(1, total + 1),
        "Symbol": filtered_df["symbol"].values,
        "Company": filtered_df["company_name"].values,
        "Fwd P/E": filtered_df["pe_forward"].values,
        "P/E TTM": filtered_df["pe_ttm"].values,
        "Mkt Cap ($B)": (filtered_df["market_cap"] / 1e9).values,
        "Margin (%)": (filtered_df["profit_margin"] * 100).values,
        "Rev CAGR 5Y (%)": (filtered_df["revenue_cagr_5yr"] * 100).values,
        "EPS CAGR 5Y (%)": (filtered_df["earnings_cagr_5yr"] * 100).values,
        "NTM EPS Gr (%)": (filtered_df["ntm_eps_growth"] * 100).values,
        "PEG": filtered_df["peg"].values,
        "Rank": filtered_df["combo_rank"].values,
    })

    # Calculate height to show all rows without scrolling (35px per row + header + padding)
    table_height = (total + 1) * 35 + 10

    st.dataframe(
        display_df,
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
            "Margin (%)": st.column_config.NumberColumn(format="%.1f", width="small"),
            "Rev CAGR 5Y (%)": st.column_config.NumberColumn(format="%.1f", width="small"),
            "EPS CAGR 5Y (%)": st.column_config.NumberColumn(format="%.1f", width="small"),
            "NTM EPS Gr (%)": st.column_config.NumberColumn(format="%.1f", width="small"),
            "PEG": st.column_config.NumberColumn(format="%.2f", width="small"),
            "Rank": st.column_config.NumberColumn(format="%.1f", width="small"),
        }
    )
