import streamlit as st

from utils.constants import AT_RISK_MARGIN_THRESHOLD, REVENUE_DROP_THRESHOLD


def render_at_risk_alert(df, threshold=AT_RISK_MARGIN_THRESHOLD):
    # warns about any product whose avg margin has dropped below threshold,
    # worst margin first
    at_risk = df.groupby('Product Name')['Gross_Margin_%'].mean()
    at_risk = at_risk[at_risk < threshold].sort_values()

    if at_risk.empty:
        return

    products = ", ".join(f"{name} ({margin:.1f}%)" for name, margin in at_risk.items())
    count    = len(at_risk)

    st.warning(
        f"⚠️ **{count} product{'s' if count != 1 else ''} at risk** — "
        f"margin below {threshold}%: {products}"
    )


def render_revenue_anomaly_alert(df, threshold=REVENUE_DROP_THRESHOLD):
    # warns about any month where revenue dropped sharply vs the prior
    # month — flags real drops only, not normal seasonal upswings
    monthly = df.groupby(['Month', 'Month_Name'])['Sales'].sum().reset_index().sort_values('Month')

    if len(monthly) < 2:
        return

    monthly['MoM_%'] = monthly['Sales'].pct_change() * 100
    drops = monthly[monthly['MoM_%'] <= -threshold]

    if drops.empty:
        return

    months = ", ".join(f"{row['Month_Name']} ({row['MoM_%']:+.1f}%)"
                        for _, row in drops.iterrows())
    count  = len(drops)

    st.warning(
        f"📉 **{count} month{'s' if count != 1 else ''} with a revenue anomaly** — "
        f"dropped {threshold}%+ vs prior month: {months}"
    )
