import streamlit as st
from data.loader import load_data
from components.alerts import render_at_risk_alert, render_revenue_anomaly_alert

# import all pages upfront — avoids import inside if block issues
from views.overview import render as render_overview
from views.product_analysis import render as render_product
from views.division_analysis import render as render_division
from views.pareto_analysis import render as render_pareto
from views.factory_analysis import render as render_factory
from views.regional_analysis import render as render_regional

# page config
st.set_page_config(
    page_title="Nassau Candy Distributor",
    page_icon="🍬",
    layout="wide"
)

# load data once — shared across all pages
df = load_data()

# sidebar filters
st.sidebar.title("🍬 Nassau Candy")
st.sidebar.markdown("---")

# division filter
divisions = ['All'] + sorted(df['Division'].unique().tolist())
selected_division = st.sidebar.selectbox("Division", divisions)

# region filter
regions = ['All'] + sorted(df['Region'].unique().tolist())
selected_region = st.sidebar.selectbox("Region", regions)

# month range filter
months        = sorted(df['Month'].unique().tolist())
selected_months = st.sidebar.select_slider(
    "Month Range",
    options=months,
    value=(months[0], months[-1])
)

# margin threshold filter
margin_threshold = st.sidebar.slider(
    "Margin Threshold (%)",
    min_value=0,
    max_value=100,
    value=0,
    step=5
)

st.sidebar.markdown("---")
st.sidebar.caption("Nassau Candy Distributor | 2025")

# apply filters to dataframe
filtered_df = df.copy()

if selected_division != 'All':
    filtered_df = filtered_df[filtered_df['Division'] == selected_division]

if selected_region != 'All':
    filtered_df = filtered_df[filtered_df['Region'] == selected_region]

filtered_df = filtered_df[
    (filtered_df['Month'] >= selected_months[0]) &
    (filtered_df['Month'] <= selected_months[1])
]

if margin_threshold > 0:
    filtered_df = filtered_df[filtered_df['Gross_Margin_%'] >= margin_threshold]

# no data matches current filters — charts can't render on an empty frame
if filtered_df.empty:
    st.warning("No data matches the selected filters. Try widening Division, Region, Month Range, or Margin Threshold.")
    st.stop()

# alert banners — shown above every page
render_at_risk_alert(filtered_df)
render_revenue_anomaly_alert(filtered_df)

# page navigation
st.sidebar.markdown("---")
page = st.sidebar.radio("Navigate", [
    "📊 Overview",
    "🍫 Product Analysis",
    "🏢 Division Analysis",
    "📈 Pareto Analysis",
    "🏭 Factory Analysis",
    "🗺️ Regional Analysis"
])

# routing
if page == "📊 Overview":
    render_overview(filtered_df)
elif page == "🍫 Product Analysis":
    render_product(filtered_df)
elif page == "🏢 Division Analysis":
    render_division(filtered_df)
elif page == "📈 Pareto Analysis":
    render_pareto(filtered_df)
elif page == "🏭 Factory Analysis":
    render_factory(filtered_df)
elif page == "🗺️ Regional Analysis":
    render_regional(filtered_df)