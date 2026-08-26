import streamlit as st
from components.charts import pareto_profit
from components.export import render_download_button

def render(df):
    st.title("📈 Pareto Analysis")
    st.markdown("Identifying which products and divisions drive 80% of revenue and profit.")
    st.markdown("---")

    total_revenue = df['Sales'].sum()
    total_profit  = df['Gross Profit'].sum()

    # product pareto — profit
    st.subheader("Pareto Chart — Gross Profit")
    st.pyplot(pareto_profit(df))
    st.markdown("---")

    # pareto tables side by side
    col1, col2 = st.columns(2)

    # product profit pareto table
    with col1:
        st.subheader("Product Profit Pareto")
        product_profit = df.groupby('Product Name')['Gross Profit'].sum()\
                           .sort_values(ascending=False).reset_index()
        product_profit.columns = ['Product', 'Total Profit ($)']
        product_profit['Profit %']            = (
            product_profit['Total Profit ($)'] / total_profit * 100
        )
        product_profit['Cumulative %']        = product_profit['Profit %'].cumsum()
        product_profit['Profit %']            = product_profit['Profit %'].round(2)
        product_profit['Cumulative %']        = product_profit['Cumulative %'].round(2)
        product_profit['Total Profit ($)']    = product_profit['Total Profit ($)'].round(2)
        st.dataframe(product_profit, use_container_width=True, hide_index=True)
        render_download_button(product_profit, "product_profit_pareto.csv")

    # product revenue pareto table
    with col2:
        st.subheader("Product Revenue Pareto")
        product_revenue = df.groupby('Product Name')['Sales'].sum()\
                            .sort_values(ascending=False).reset_index()
        product_revenue.columns = ['Product', 'Total Revenue ($)']
        product_revenue['Revenue %']          = (
            product_revenue['Total Revenue ($)'] / total_revenue * 100
        )
        product_revenue['Cumulative %']       = product_revenue['Revenue %'].cumsum()
        product_revenue['Revenue %']          = product_revenue['Revenue %'].round(2)
        product_revenue['Cumulative %']       = product_revenue['Cumulative %'].round(2)
        product_revenue['Total Revenue ($)']  = product_revenue['Total Revenue ($)'].round(2)
        st.dataframe(product_revenue, use_container_width=True, hide_index=True)

    st.markdown("---")

    # division and factory pareto side by side
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Division Pareto — Profit")
        div_pareto = df.groupby('Division')['Gross Profit'].sum()\
                       .sort_values(ascending=False).reset_index()
        div_pareto.columns = ['Division', 'Total Profit ($)']
        div_pareto['Profit %']       = (div_pareto['Total Profit ($)'] / total_profit * 100)
        div_pareto['Cumulative %']   = div_pareto['Profit %'].cumsum()
        div_pareto['Profit %']       = div_pareto['Profit %'].round(2)
        div_pareto['Cumulative %']   = div_pareto['Cumulative %'].round(2)
        st.dataframe(div_pareto, use_container_width=True, hide_index=True)

    with col2:
        st.subheader("Factory Pareto — Profit")
        factory_pareto = df.groupby('Factory')['Gross Profit'].sum()\
                           .sort_values(ascending=False).reset_index()
        factory_pareto.columns = ['Factory', 'Total Profit ($)']
        factory_pareto['Profit %']     = (factory_pareto['Total Profit ($)'] / total_profit * 100)
        factory_pareto['Cumulative %'] = factory_pareto['Profit %'].cumsum()
        factory_pareto['Profit %']     = factory_pareto['Profit %'].round(2)
        factory_pareto['Cumulative %'] = factory_pareto['Cumulative %'].round(2)
        st.dataframe(factory_pareto, use_container_width=True, hide_index=True)

    st.markdown("---")

    # dependency risk summary
    st.subheader("Dependency Risk Summary")

    top5_profit  = df.groupby('Product Name')['Gross Profit'].sum()\
                     .sort_values(ascending=False).head(5).sum()
    bot10_profit = df.groupby('Product Name')['Gross Profit'].sum()\
                     .sort_values(ascending=False).tail(10).sum()
    top_div      = df.groupby('Division')['Gross Profit'].sum()\
                     .sort_values(ascending=False)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Top 5 Products",     f"{top5_profit / total_profit * 100:.1f}%",  "of total profit")
    col2.metric("Bottom 10 Products", f"{bot10_profit / total_profit * 100:.1f}%", "of total profit")
    col3.metric("Top Division Share", f"{top_div.iloc[0] / total_profit * 100:.1f}%",
                top_div.index[0])
    col4.metric("Top Factory Share",
                f"{df.groupby('Factory')['Gross Profit'].sum().max() / total_profit * 100:.1f}%",
                "of total profit")

    st.markdown("---")

    # key insights
    products_to_80 = 0
    cumulative     = 0
    for _, row in df.groupby('Product Name')['Gross Profit']\
                    .sum().sort_values(ascending=False).items():
        cumulative     += row / total_profit * 100
        products_to_80 += 1
        if cumulative   >= 80:
            break

    st.info(
        f"💡 **Key Insights:**\n\n"
        f"- Only **{products_to_80} out of {df['Product Name'].nunique()} products** "
        f"generate 80% of total profit.\n\n"
        f"- The bottom **{df['Product Name'].nunique() - products_to_80} products** "
        f"collectively contribute less than **20%** of profit.\n\n"
        f"- **{top_div.index[0]}** division alone accounts for "
        f"**{top_div.iloc[0] / total_profit * 100:.1f}%** of total profit — "
        f"a critical concentration risk."
    )