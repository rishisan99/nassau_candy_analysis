import streamlit as st
from components.kpi_cards import render_factory_kpis
from components.charts import (
    factory_margin_vs_avg,
    factory_cost_vs_profit
)
from components.export import render_download_button

# factory coordinates from project brief
FACTORY_COORDS = {
    "Lot's O' Nuts"    : {"lat": 32.881893, "lon": -111.768036, "state": "Arizona"},
    "Wicked Choccy's"  : {"lat": 32.076176, "lon": -81.088371,  "state": "Georgia"},
    "Sugar Shack"      : {"lat": 48.119140, "lon": -96.181150,  "state": "Minnesota"},
    "Secret Factory"   : {"lat": 41.446333, "lon": -90.565487,  "state": "Illinois"},
    "The Other Factory": {"lat": 35.117500, "lon": -89.971107,  "state": "Tennessee"}
}

def render(df):
    st.title("🏭 Factory Analysis")
    st.markdown("Factory level cost structure, margin performance and product diagnostics.")
    st.markdown("---")

    # KPI cards
    render_factory_kpis(df)
    st.markdown("---")

    # charts side by side
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Factory Margin vs Company Average")
        st.pyplot(factory_margin_vs_avg(df))

    with col2:
        st.subheader("Cost vs Profit per Unit by Factory")
        st.pyplot(factory_cost_vs_profit(df))

    st.markdown("---")

    # factory summary table
    st.subheader("Factory Performance Table")
    total_revenue      = df['Sales'].sum()
    total_profit       = df['Gross Profit'].sum()
    company_avg_margin = total_profit / total_revenue * 100

    factory_table = df.groupby('Factory').agg(
        Total_Revenue       = ('Sales', 'sum'),
        Total_Profit        = ('Gross Profit', 'sum'),
        Total_Cost          = ('Cost', 'sum'),
        Avg_Margin          = ('Gross_Margin_%', 'mean'),
        Avg_Cost_per_Unit   = ('Cost_per_Unit', 'mean'),
        Avg_Profit_per_Unit = ('Profit_per_Unit', 'mean'),
        Num_Products        = ('Product Name', 'nunique')
    ).round(2).reset_index()

    factory_table['Revenue_Share_%']     = (
        factory_table['Total_Revenue'] / total_revenue * 100
    ).round(2)
    factory_table['Profit_Share_%']      = (
        factory_table['Total_Profit'] / total_profit * 100
    ).round(2)
    factory_table['Margin_vs_Company']   = (
        factory_table['Avg_Margin'] - company_avg_margin
    ).round(2)

    factory_table = factory_table.sort_values('Avg_Margin', ascending=False)
    factory_table.columns = [
        'Factory', 'Revenue ($)', 'Profit ($)', 'Cost ($)',
        'Avg Margin (%)', 'Cost/Unit ($)', 'Profit/Unit ($)',
        'Products', 'Revenue Share (%)', 'Profit Share (%)',
        'Margin vs Company (%)'
    ]
    st.dataframe(factory_table, use_container_width=True, hide_index=True)
    render_download_button(factory_table, "factory_summary.csv")
    st.markdown("---")

    # product margin by factory breakdown
    st.subheader("Product Margins by Factory")
    product_factory = df.groupby(['Factory', 'Product Name']).agg(
        Avg_Margin    = ('Gross_Margin_%', 'mean'),
        Total_Profit  = ('Gross Profit', 'sum'),
        Total_Revenue = ('Sales', 'sum')
    ).round(2).reset_index().sort_values(['Factory', 'Avg_Margin'], ascending=[True, False])

    product_factory.columns = [
        'Factory', 'Product', 'Avg Margin (%)', 'Profit ($)', 'Revenue ($)'
    ]
    st.dataframe(product_factory, use_container_width=True, hide_index=True)
    st.markdown("---")

    # factory map
    st.subheader("Factory Locations")
    available = [f for f in FACTORY_COORDS if f in df['Factory'].unique()]

    map_data = []
    for factory in available:
        coords  = FACTORY_COORDS[factory]
        stats   = df[df['Factory'] == factory]
        margin  = stats['Gross_Margin_%'].mean()
        profit  = stats['Gross Profit'].sum()
        map_data.append({
            'Factory' : factory,
            'State'   : coords['state'],
            'lat'     : coords['lat'],
            'lon'     : coords['lon'],
            'Margin'  : round(margin, 2),
            'Profit'  : round(profit, 2)
        })

    import pandas as pd
    map_df = pd.DataFrame(map_data)
    st.map(map_df[['lat', 'lon']])

    # factory location table below map
    st.dataframe(
        map_df[['Factory', 'State', 'Margin', 'Profit']].rename(columns={
            'Margin': 'Avg Margin (%)', 'Profit': 'Total Profit ($)'
        }),
        use_container_width=True, hide_index=True
    )
    st.markdown("---")

    # key insights
    worst_factory = df.groupby('Factory')['Gross_Margin_%'].mean().idxmin()
    worst_margin  = df.groupby('Factory')['Gross_Margin_%'].mean().min()
    best_factory  = df.groupby('Factory')['Gross_Margin_%'].mean().idxmax()
    best_margin   = df.groupby('Factory')['Gross_Margin_%'].mean().max()

    st.info(
        f"💡 **Key Insights:**\n\n"
        f"- **{best_factory}** is the most efficient factory with "
        f"**{best_margin:.1f}%** avg margin.\n\n"
        f"- **{worst_factory}** is critically underperforming at "
        f"**{worst_margin:.1f}%** avg margin — "
        f"**{company_avg_margin - worst_margin:.1f}%** below company average.\n\n"
        f"- The margin gap between best and worst factory is "
        f"**{best_margin - worst_margin:.1f} percentage points** — "
        f"this is a cost structure problem, not a sales problem."
    )