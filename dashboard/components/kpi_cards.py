import streamlit as st

# colors for delta indicators
from utils.constants import POSITIVE, NEGATIVE, NEUTRAL

def render_card(col, label, value, delta=None, prefix="", suffix=""):
    # renders a single KPI metric card in a given column
    with col:
        st.metric(
            label=label,
            value=f"{prefix}{value}{suffix}",
            delta=delta
        )

def render_business_kpis(df):
    # top level business KPIs — shown on overview page
    total_revenue = df['Sales'].sum()
    total_profit  = df['Gross Profit'].sum()
    total_cost    = df['Cost'].sum()
    avg_margin    = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
    total_units   = df['Units'].sum()
    total_orders  = df['Order ID'].nunique()

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    render_card(col1, "Total Revenue",    f"{total_revenue:,.0f}",  prefix="$")
    render_card(col2, "Total Profit",     f"{total_profit:,.0f}",   prefix="$")
    render_card(col3, "Total Cost",       f"{total_cost:,.0f}",     prefix="$")
    render_card(col4, "Gross Margin",     f"{avg_margin:.1f}",      suffix="%")
    render_card(col5, "Units Sold",       f"{total_units:,}")
    render_card(col6, "Total Orders",     f"{total_orders:,}")

def render_division_kpis(df):
    # division level KPIs — shown on division page
    total_revenue = df['Sales'].sum()
    total_profit  = df['Gross Profit'].sum()
    avg_margin    = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
    num_products  = df['Product Name'].nunique()

    col1, col2, col3, col4 = st.columns(4)

    render_card(col1, "Division Revenue", f"{total_revenue:,.0f}", prefix="$")
    render_card(col2, "Division Profit",  f"{total_profit:,.0f}",  prefix="$")
    render_card(col3, "Avg Margin",       f"{avg_margin:.1f}",     suffix="%")
    render_card(col4, "Products",         f"{num_products}")

def render_product_kpis(df):
    # product level KPIs — shown on product page
    total_revenue       = df['Sales'].sum()
    total_profit        = df['Gross Profit'].sum()
    avg_margin          = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
    avg_profit_per_unit = df['Profit_per_Unit'].mean()

    col1, col2, col3, col4 = st.columns(4)

    render_card(col1, "Total Revenue",      f"{total_revenue:,.0f}",    prefix="$")
    render_card(col2, "Total Profit",       f"{total_profit:,.0f}",     prefix="$")
    render_card(col3, "Avg Margin",         f"{avg_margin:.1f}",        suffix="%")
    render_card(col4, "Avg Profit / Unit",  f"{avg_profit_per_unit:.2f}", prefix="$")

def render_factory_kpis(df):
    # factory level KPIs — shown on factory page
    total_revenue      = df['Sales'].sum()
    total_profit       = df['Gross Profit'].sum()
    avg_margin         = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
    num_factories      = df['Factory'].nunique()

    col1, col2, col3, col4 = st.columns(4)

    render_card(col1, "Total Revenue",  f"{total_revenue:,.0f}", prefix="$")
    render_card(col2, "Total Profit",   f"{total_profit:,.0f}",  prefix="$")
    render_card(col3, "Avg Margin",     f"{avg_margin:.1f}",     suffix="%")
    render_card(col4, "Factories",      f"{num_factories}")

def render_region_kpis(df):
    # region level KPIs — shown on regional page
    total_revenue = df['Sales'].sum()
    total_profit  = df['Gross Profit'].sum()
    avg_margin    = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
    total_orders  = df['Order ID'].nunique()

    col1, col2, col3, col4 = st.columns(4)

    render_card(col1, "Total Revenue", f"{total_revenue:,.0f}", prefix="$")
    render_card(col2, "Total Profit",  f"{total_profit:,.0f}",  prefix="$")
    render_card(col3, "Avg Margin",    f"{avg_margin:.1f}",     suffix="%")
    render_card(col4, "Total Orders",  f"{total_orders:,}")