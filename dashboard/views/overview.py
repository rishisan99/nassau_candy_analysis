import streamlit as st
from components.kpi_cards import render_business_kpis
from components.charts import (
    monthly_trend,
    quarterly_revenue,
    division_revenue_vs_profit
)
from components.export import render_download_button

def render(df):
    st.title("📊 Business Overview")
    st.markdown("High level summary of Nassau Candy's financial performance in 2025.")
    st.markdown("---")

    # KPI cards
    render_business_kpis(df)
    st.markdown("---")

    # monthly trend
    st.subheader("Monthly Revenue & Profit Trend")
    st.pyplot(monthly_trend(df))
    st.markdown("---")

    # quarterly and division side by side
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Quarterly Performance")
        st.pyplot(quarterly_revenue(df))

    with col2:
        st.subheader("Revenue vs Profit by Division")
        st.pyplot(division_revenue_vs_profit(df))

    st.markdown("---")

    # quick summary table
    st.subheader("Division Summary Table")
    division_table = df.groupby('Division').agg(
        Total_Revenue = ('Sales', 'sum'),
        Total_Profit  = ('Gross Profit', 'sum'),
        Avg_Margin    = ('Gross_Margin_%', 'mean'),
        Total_Orders  = ('Order ID', 'nunique'),
        Num_Products  = ('Product Name', 'nunique')
    ).round(2).reset_index().sort_values('Total_Revenue', ascending=False)

    division_table.columns = [
        'Division', 'Revenue ($)', 'Profit ($)',
        'Avg Margin (%)', 'Orders', 'Products'
    ]
    st.dataframe(division_table, use_container_width=True, hide_index=True)
    render_download_button(division_table, "division_summary.csv")

    # key insight callout
    st.markdown("---")
    top_division = division_table.iloc[0]['Division']
    top_share    = (
        df[df['Division'] == top_division]['Gross Profit'].sum()
        / df['Gross Profit'].sum() * 100
    )
    st.info(
        f"💡 **Key Insight:** The {top_division} division accounts for "
        f"**{top_share:.1f}%** of total gross profit. "
        f"This concentration represents a structural risk to the business."
    )