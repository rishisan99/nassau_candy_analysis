import streamlit as st
from components.kpi_cards import render_division_kpis
from components.charts import (
    division_revenue_vs_profit,
    division_margin_bar
)
from components.export import render_download_button

def render(df):
    st.title("🏢 Division Analysis")
    st.markdown("Division level revenue, profit and margin performance comparison.")
    st.markdown("---")

    # KPI cards
    render_division_kpis(df)
    st.markdown("---")

    # charts side by side
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Revenue vs Profit by Division")
        st.pyplot(division_revenue_vs_profit(df))

    with col2:
        st.subheader("Average Margin by Division")
        st.pyplot(division_margin_bar(df))

    st.markdown("---")

    # division summary table
    st.subheader("Division Summary Table")
    total_revenue = df['Sales'].sum()
    total_profit  = df['Gross Profit'].sum()

    division_table = df.groupby('Division').agg(
        Total_Revenue = ('Sales', 'sum'),
        Total_Profit  = ('Gross Profit', 'sum'),
        Total_Cost    = ('Cost', 'sum'),
        Total_Units   = ('Units', 'sum'),
        Total_Orders  = ('Order ID', 'nunique'),
        Num_Products  = ('Product Name', 'nunique'),
        Avg_Margin    = ('Gross_Margin_%', 'mean')
    ).round(2).reset_index()

    division_table['Revenue_Share_%'] = (
        division_table['Total_Revenue'] / total_revenue * 100
    ).round(2)

    division_table['Profit_Share_%'] = (
        division_table['Total_Profit'] / total_profit * 100
    ).round(2)

    division_table['Profit_Efficiency'] = (
        division_table['Total_Profit'] / division_table['Total_Revenue']
    ).round(4)

    division_table = division_table.sort_values('Total_Revenue', ascending=False)

    division_table.columns = [
        'Division', 'Revenue ($)', 'Profit ($)', 'Cost ($)',
        'Units', 'Orders', 'Products', 'Avg Margin (%)',
        'Revenue Share (%)', 'Profit Share (%)', 'Profit Efficiency'
    ]

    st.dataframe(division_table, use_container_width=True, hide_index=True)
    render_download_button(division_table, "division_summary.csv")
    st.markdown("---")

    # quarterly trend by division
    st.subheader("Quarterly Revenue by Division")
    quarterly_div = df.groupby(['Division', 'Quarter']).agg(
        Revenue=('Sales', 'sum'),
        Profit =('Gross Profit', 'sum')
    ).reset_index()
    quarterly_div['Quarter_Label'] = 'Q' + quarterly_div['Quarter'].astype(str)

    # pivot for clean table view
    pivot = quarterly_div.pivot(
        index='Quarter_Label',
        columns='Division',
        values='Revenue'
    ).round(2).fillna(0)

    st.dataframe(pivot, use_container_width=True)
    st.markdown("---")

    # revenue vs profit imbalance callout
    st.subheader("Revenue vs Profit Share Imbalance")
    col1, col2, col3 = st.columns(3)

    div_stats = df.groupby('Division').agg(
        Revenue=('Sales', 'sum'),
        Profit =('Gross Profit', 'sum')
    ).reset_index()

    div_stats['Rev_Share_%']    = (div_stats['Revenue'] / total_revenue * 100).round(2)
    div_stats['Profit_Share_%'] = (div_stats['Profit']  / total_profit  * 100).round(2)
    div_stats['Diff']           = (div_stats['Profit_Share_%'] - div_stats['Rev_Share_%']).round(2)

    cols = [col1, col2, col3]
    for i, (_, row) in enumerate(div_stats.iterrows()):
        direction = "punches above weight ✅" if row['Diff'] > 0 else "underperforms on profit ⚠️"
        with cols[i]:
            st.metric(
                label=row['Division'],
                value=f"Profit Share: {row['Profit_Share_%']}%",
                delta=f"{row['Diff']:+.2f}% vs Revenue Share"
            )
            st.caption(direction)

    st.markdown("---")

    # key insights
    top_div    = div_stats.sort_values('Profit_Share_%', ascending=False).iloc[0]
    bottom_div = div_stats.sort_values('Profit_Share_%', ascending=True).iloc[0]

    st.info(
        f"💡 **Key Insights:**\n\n"
        f"- **{top_div['Division']}** dominates with "
        f"**{top_div['Profit_Share_%']}%** of total profit "
        f"from **{top_div['Rev_Share_%']}%** of revenue.\n\n"
        f"- **{bottom_div['Division']}** contributes only "
        f"**{bottom_div['Profit_Share_%']}%** of profit — "
        f"portfolio diversification is needed to reduce concentration risk."
    )