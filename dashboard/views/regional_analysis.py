import streamlit as st
from components.kpi_cards import render_region_kpis
from components.charts import (
    region_profit_bar,
    region_division_heatmap
)
from components.export import render_download_button

def render(df):
    st.title("🗺️ Regional Analysis")
    st.markdown("Regional breakdown of revenue, profit, margin and shipping performance.")
    st.markdown("---")

    # KPI cards
    render_region_kpis(df)
    st.markdown("---")

    # charts side by side
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Gross Profit by Region")
        st.pyplot(region_profit_bar(df))

    with col2:
        st.subheader("Profit Heatmap — Region × Division")
        st.pyplot(region_division_heatmap(df))

    st.markdown("---")

    # region summary table
    st.subheader("Region Summary Table")
    total_revenue = df['Sales'].sum()
    total_profit  = df['Gross Profit'].sum()

    region_table = df.groupby('Region').agg(
        Total_Revenue = ('Sales', 'sum'),
        Total_Profit  = ('Gross Profit', 'sum'),
        Total_Cost    = ('Cost', 'sum'),
        Total_Units   = ('Units', 'sum'),
        Total_Orders  = ('Order ID', 'nunique'),
        Avg_Margin    = ('Gross_Margin_%', 'mean')
    ).round(2).reset_index()

    region_table['Revenue_Share_%'] = (
        region_table['Total_Revenue'] / total_revenue * 100
    ).round(2)

    region_table['Profit_Share_%'] = (
        region_table['Total_Profit'] / total_profit * 100
    ).round(2)

    region_table['Margin_vs_Company'] = (
        region_table['Avg_Margin'] - (total_profit / total_revenue * 100)
    ).round(2)

    region_table = region_table.sort_values('Total_Profit', ascending=False)
    region_table.columns = [
        'Region', 'Revenue ($)', 'Profit ($)', 'Cost ($)',
        'Units', 'Orders', 'Avg Margin (%)',
        'Revenue Share (%)', 'Profit Share (%)',
        'Margin vs Company (%)'
    ]
    st.dataframe(region_table, use_container_width=True, hide_index=True)
    render_download_button(region_table, "region_summary.csv")
    st.markdown("---")

    # quarterly trend by region
    st.subheader("Quarterly Revenue by Region")
    quarterly_region = df.groupby(['Region', 'Quarter']).agg(
        Revenue = ('Sales', 'sum'),
        Profit  = ('Gross Profit', 'sum'),
        Margin  = ('Gross_Margin_%', 'mean')
    ).round(2).reset_index()
    quarterly_region['Quarter_Label'] = 'Q' + quarterly_region['Quarter'].astype(str)

    pivot = quarterly_region.pivot(
        index='Quarter_Label',
        columns='Region',
        values='Revenue'
    ).round(2).fillna(0)

    st.dataframe(pivot, use_container_width=True)
    st.markdown("---")

    # ship mode breakdown by region
    st.subheader("Ship Mode Distribution by Region")
    ship_region = df.groupby(['Region', 'Ship Mode'])['Order ID']\
                    .nunique().reset_index()
    ship_region.columns = ['Region', 'Ship Mode', 'Orders']

    ship_pivot = ship_region.pivot(
        index='Region',
        columns='Ship Mode',
        values='Orders'
    ).fillna(0).astype(int)

    st.dataframe(ship_pivot, use_container_width=True)
    st.markdown("---")

    # top products per region
    st.subheader("Top Product by Profit in Each Region")
    col1, col2, col3, col4 = st.columns(4)

    regions = df['Region'].unique().tolist()
    cols    = [col1, col2, col3, col4]

    for i, region in enumerate(sorted(regions)):
        region_df   = df[df['Region'] == region]
        top_product = region_df.groupby('Product Name')['Gross Profit']\
                               .sum().idxmax()
        top_profit  = region_df.groupby('Product Name')['Gross Profit']\
                               .sum().max()
        top_margin  = region_df[region_df['Product Name'] == top_product]\
                               ['Gross_Margin_%'].mean()

        with cols[i]:
            st.markdown(f"**{region}**")
            st.caption(f"📦 {top_product}")
            st.caption(f"💰 ${top_profit:,.2f} profit")
            st.caption(f"📊 {top_margin:.1f}% margin")

    st.markdown("---")

    # key insights
    company_avg_margin = total_profit / total_revenue * 100
    top_region         = df.groupby('Region')['Gross Profit'].sum().idxmax()
    top_region_share   = df.groupby('Region')['Gross Profit'].sum().max() / total_profit * 100
    top_region_margin  = df[df['Region'] == top_region]['Gross_Margin_%'].mean()
    margins            = df.groupby('Region')['Gross_Margin_%'].mean()
    consistent         = (margins.max() - margins.min()) < 2

    st.info(
        f"💡 **Key Insights:**\n\n"
        f"- **{top_region}** is the strongest region with "
        f"**{top_region_share:.1f}%** of total profit "
        f"and **{top_region_margin:.1f}%** avg margin.\n\n"
        f"- Margins are {'remarkably consistent' if consistent else 'notably varied'} "
        f"across regions — ranging from "
        f"**{margins.min():.1f}%** to **{margins.max():.1f}%**.\n\n"
        f"- Margin consistency suggests pricing is centrally controlled — "
        f"regional profit differences are driven by **volume, not pricing strategy**."
    )