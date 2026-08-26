import streamlit as st
from components.kpi_cards import render_product_kpis
from components.charts import (
    product_profit_ranking,
    product_quadrant_scatter,
    product_monthly_trend
)
from utils.constants import QUADRANT_EMOJI
from components.export import render_download_button

def render(df):
    st.title("🍫 Product Analysis")
    st.markdown("Product level profitability, margin ranking and quadrant classification.")
    st.markdown("---")

    # KPI cards
    render_product_kpis(df)
    st.markdown("---")

    # charts side by side
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Products Ranked by Gross Profit")
        st.pyplot(product_profit_ranking(df))

    with col2:
        st.subheader("Product Quadrant Analysis")
        st.pyplot(product_quadrant_scatter(df))

    st.markdown("---")

    # product summary table
    st.subheader("Product Summary Table")
    total_revenue = df['Sales'].sum()
    total_profit  = df['Gross Profit'].sum()

    product_table = df.groupby(['Product Name', 'Division', 'Factory', 'Quadrant']).agg(
        Total_Revenue       = ('Sales', 'sum'),
        Total_Profit        = ('Gross Profit', 'sum'),
        Avg_Margin          = ('Gross_Margin_%', 'mean'),
        Avg_Profit_per_Unit = ('Profit_per_Unit', 'mean'),
        Total_Units         = ('Units', 'sum')
    ).round(2).reset_index()

    product_table['Revenue_Share_%'] = (
        product_table['Total_Revenue'] / total_revenue * 100
    ).round(2)

    product_table['Profit_Share_%'] = (
        product_table['Total_Profit'] / total_profit * 100
    ).round(2)

    product_table = product_table.sort_values('Total_Profit', ascending=False)

    product_table.columns = [
        'Product', 'Division', 'Factory', 'Quadrant',
        'Revenue ($)', 'Profit ($)', 'Avg Margin (%)',
        'Profit/Unit ($)', 'Units',
        'Revenue Share (%)', 'Profit Share (%)'
    ]

    st.caption("💡 Click a row to drill into that product")
    selection = st.dataframe(
        product_table, use_container_width=True, hide_index=True,
        on_select="rerun", selection_mode="single-row", key="product_summary_table"
    )
    render_download_button(product_table, "product_summary.csv")

    # drill-down detail for the selected product
    selected_rows = selection.selection.rows
    if selected_rows:
        row              = product_table.iloc[selected_rows[0]]
        selected_product = row['Product']

        st.markdown("---")
        st.subheader(f"🔍 {selected_product}")

        dcol1, dcol2, dcol3, dcol4 = st.columns(4)
        dcol1.metric("Revenue", f"${row['Revenue ($)']:,.0f}")
        dcol2.metric("Profit", f"${row['Profit ($)']:,.0f}")
        dcol3.metric("Avg Margin", f"{row['Avg Margin (%)']:.1f}%")
        dcol4.metric("Quadrant", row['Quadrant'])

        st.pyplot(product_monthly_trend(df, selected_product))

        region_breakdown = df[df['Product Name'] == selected_product].groupby('Region').agg(
            Revenue = ('Sales', 'sum'),
            Profit  = ('Gross Profit', 'sum')
        ).round(2).reset_index().sort_values('Revenue', ascending=False)
        st.dataframe(region_breakdown, use_container_width=True, hide_index=True)

    st.markdown("---")

    # quadrant breakdown
    st.subheader("Quadrant Breakdown")
    col1, col2, col3, col4 = st.columns(4)

    quadrant_map = {
        'STAR'       : col1,
        'HIDDEN GEM' : col2,
        'VOLUME TRAP': col3,
        'DEAD WEIGHT': col4
    }

    for quadrant, col in quadrant_map.items():
        products = df[df['Quadrant'] == quadrant]['Product Name'].unique().tolist()
        with col:
            st.markdown(f"**{QUADRANT_EMOJI[quadrant]} {quadrant}**")
            if products:
                for p in products:
                    st.caption(f"• {p}")
            else:
                st.caption("None in current filter")

    st.markdown("---")

    # key insights
    best_margin  = df.groupby('Product Name')['Gross_Margin_%'].mean().idxmax()
    best_profit  = df.groupby('Product Name')['Gross Profit'].sum().idxmax()
    worst_margin = df.groupby('Product Name')['Gross_Margin_%'].mean().idxmin()

    st.info(
        f"💡 **Key Insights:**\n\n"
        f"- Highest margin product: **{best_margin}**\n\n"
        f"- Highest profit product: **{best_profit}**\n\n"
        f"- Lowest margin product: **{worst_margin}** — review pricing or consider discontinuation"
    )