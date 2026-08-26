import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# shared styles
from utils.constants import COLORS, DIVISION_COLORS, QUADRANT_COLORS, FACTORY_COLORS, REGION_COLORS

def base_fig(figsize=(10, 5)):
    # base figure with clean style
    fig, ax = plt.subplots(figsize=figsize)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    return fig, ax

# ── Overview Charts ───────────────────────────────────────────────────────────

MONTH_ABBR = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

def monthly_trend(df):
    monthly = df.groupby(['Month', 'Month_Name']).agg(
        Revenue=('Sales', 'sum'),
        Profit=('Gross Profit', 'sum')
    ).reset_index().sort_values('Month')

    fig, ax = base_fig()
    ax.plot(monthly['Month_Name'], monthly['Revenue'],
            color=COLORS['revenue'], marker='o', linewidth=2, label='Revenue')
    ax.plot(monthly['Month_Name'], monthly['Profit'],
            color=COLORS['profit'], marker='o', linewidth=2, label='Gross Profit')
    ax.fill_between(monthly['Month_Name'], monthly['Revenue'], monthly['Profit'],
                    alpha=0.08, color=COLORS['cost'], label='Cost Gap')

    # simple linear-trend forecast for the next 2 months — needs a decent
    # amount of history behind it to mean anything
    if len(monthly) >= 6:
        import numpy as np

        x = monthly['Month'].to_numpy()
        future_x = np.array([x.max() + 1, x.max() + 2])
        future_labels = [MONTH_ABBR[(m - 1) % 12] + '*' for m in future_x]

        rev_forecast    = np.polyval(np.polyfit(x, monthly['Revenue'], 1), future_x)
        profit_forecast = np.polyval(np.polyfit(x, monthly['Profit'], 1), future_x)

        ax.plot([monthly['Month_Name'].iloc[-1]] + future_labels,
                [monthly['Revenue'].iloc[-1]] + list(rev_forecast),
                color=COLORS['revenue'], linewidth=2, linestyle='--', alpha=0.6)
        ax.plot([monthly['Month_Name'].iloc[-1]] + future_labels,
                [monthly['Profit'].iloc[-1]] + list(profit_forecast),
                color=COLORS['profit'], linewidth=2, linestyle='--', alpha=0.6,
                label='Forecast (next 2mo, linear trend)')

    ax.set_title('Monthly Revenue & Profit Trend', fontsize=13, fontweight='bold')
    ax.set_ylabel('Amount (USD)')
    ax.legend()
    plt.tight_layout()
    return fig

def quarterly_revenue(df):
    quarterly = df.groupby('Quarter').agg(
        Revenue=('Sales', 'sum'),
        Profit=('Gross Profit', 'sum')
    ).reset_index()
    quarterly['Quarter_Label'] = 'Q' + quarterly['Quarter'].astype(str)

    import numpy as np
    x, width = np.arange(len(quarterly)), 0.35
    fig, ax  = base_fig()
    ax.bar(x - width/2, quarterly['Revenue'], width,
           color=COLORS['revenue'], label='Revenue')
    ax.bar(x + width/2, quarterly['Profit'],  width,
           color=COLORS['profit'],  label='Gross Profit')
    ax.set_title('Quarterly Revenue & Profit', fontsize=13, fontweight='bold')
    ax.set_ylabel('Amount (USD)')
    ax.set_xticks(x)
    ax.set_xticklabels(quarterly['Quarter_Label'])
    ax.legend()
    plt.tight_layout()
    return fig

# ── Product Charts ────────────────────────────────────────────────────────────

def product_profit_ranking(df):
    product = df.groupby(['Product Name', 'Quadrant'])['Gross Profit']\
                .sum().reset_index().sort_values('Gross Profit', ascending=True)
    colors  = [QUADRANT_COLORS.get(q, COLORS['primary']) for q in product['Quadrant']]

    fig, ax = base_fig(figsize=(10, 6))
    ax.barh(product['Product Name'], product['Gross Profit'], color=colors)
    ax.set_title('Products Ranked by Gross Profit', fontsize=13, fontweight='bold')
    ax.set_xlabel('Total Gross Profit (USD)')
    ax.legend(handles=[
        plt.Rectangle((0,0), 1, 1, color=c, label=q)
        for q, c in QUADRANT_COLORS.items()
    ], loc='lower right', fontsize=8)
    plt.tight_layout()
    return fig

def product_quadrant_scatter(df):
    product = df.groupby(['Product Name', 'Quadrant']).agg(
        Total_Revenue=('Sales', 'sum'),
        Avg_Margin=('Gross_Margin_%', 'mean')
    ).reset_index()

    fig, ax = base_fig()
    for quadrant, color in QUADRANT_COLORS.items():
        sub = product[product['Quadrant'] == quadrant]
        ax.scatter(sub['Total_Revenue'], sub['Avg_Margin'],
                   color=color, label=quadrant, s=100,
                   edgecolors='white', linewidth=0.5)

    sales_median  = product['Total_Revenue'].median()
    margin_median = product['Avg_Margin'].median()
    ax.axvline(x=sales_median,  color='grey', linestyle='--', linewidth=1)
    ax.axhline(y=margin_median, color='grey', linestyle=':',  linewidth=1)
    ax.set_title('Product Quadrant Analysis', fontsize=13, fontweight='bold')
    ax.set_xlabel('Total Revenue (USD)')
    ax.set_ylabel('Gross Margin (%)')
    ax.legend(fontsize=8)
    plt.tight_layout()
    return fig

def product_monthly_trend(df, product_name):
    # drill-down detail chart for a single selected product
    product_df = df[df['Product Name'] == product_name]
    monthly = product_df.groupby(['Month', 'Month_Name']).agg(
        Revenue=('Sales', 'sum'),
        Profit=('Gross Profit', 'sum')
    ).reset_index().sort_values('Month')

    fig, ax = base_fig(figsize=(10, 4))
    ax.plot(monthly['Month_Name'], monthly['Revenue'],
            color=COLORS['revenue'], marker='o', linewidth=2, label='Revenue')
    ax.plot(monthly['Month_Name'], monthly['Profit'],
            color=COLORS['profit'], marker='o', linewidth=2, label='Gross Profit')
    ax.set_title(f'{product_name} — Monthly Trend', fontsize=13, fontweight='bold')
    ax.set_ylabel('Amount (USD)')
    ax.legend()
    plt.tight_layout()
    return fig

# ── Division Charts ───────────────────────────────────────────────────────────

def division_revenue_vs_profit(df):
    division = df.groupby('Division').agg(
        Revenue=('Sales', 'sum'),
        Profit=('Gross Profit', 'sum')
    ).reset_index().sort_values('Revenue', ascending=False)

    import numpy as np
    x, width = np.arange(len(division)), 0.35
    fig, ax  = base_fig()
    ax.bar(x - width/2, division['Revenue'], width,
           color=[DIVISION_COLORS.get(d, COLORS['primary']) for d in division['Division']],
           alpha=1.0, label='Revenue')
    ax.bar(x + width/2, division['Profit'], width,
           color=[DIVISION_COLORS.get(d, COLORS['primary']) for d in division['Division']],
           alpha=0.5, label='Gross Profit')
    ax.set_title('Revenue vs Gross Profit by Division', fontsize=13, fontweight='bold')
    ax.set_ylabel('Amount (USD)')
    ax.set_xticks(x)
    ax.set_xticklabels(division['Division'])
    ax.legend(handles=[
        plt.Rectangle((0,0), 1, 1, color='grey', alpha=1.0, label='Revenue'),
        plt.Rectangle((0,0), 1, 1, color='grey', alpha=0.5, label='Gross Profit')
    ])
    plt.tight_layout()
    return fig

def division_margin_bar(df):
    division      = df.groupby('Division')['Gross_Margin_%'].mean().reset_index()
    company_avg   = df['Gross Profit'].sum() / df['Sales'].sum() * 100

    fig, ax = base_fig()
    ax.bar(division['Division'], division['Gross_Margin_%'],
           color=[DIVISION_COLORS.get(d, COLORS['primary']) for d in division['Division']],
           width=0.4)
    ax.axhline(y=company_avg, color=COLORS['primary'], linestyle='--', linewidth=1.5)
    ax.set_title('Average Gross Margin by Division', fontsize=13, fontweight='bold')
    ax.set_ylabel('Gross Margin (%)')
    ax.legend(handles=[
        plt.Line2D([0], [0], color=COLORS['primary'], linestyle='--',
                   label=f'Company Avg ({company_avg:.1f}%)')
    ])
    plt.tight_layout()
    return fig

# ── Pareto Charts ─────────────────────────────────────────────────────────────

def pareto_profit(df):
    total_profit  = df['Gross Profit'].sum()
    product       = df.groupby('Product Name')['Gross Profit'].sum()\
                      .sort_values(ascending=False).reset_index()
    product['Profit_%']            = product['Gross Profit'] / total_profit * 100
    product['Cumulative_Profit_%'] = product['Profit_%'].cumsum()
    product['Profit_%']            = product['Profit_%'].round(2)
    product['Cumulative_Profit_%'] = product['Cumulative_Profit_%'].round(2)

    short = lambda n: n.replace('Wonka Bar - ', 'WB - ').replace('Wonka Bar -', 'WB -')
    product['Short_Name'] = product['Product Name'].apply(short)

    bar_colors = [
        COLORS['profit'] if c <= 80 else COLORS['warning']
        for c in product['Cumulative_Profit_%']
    ]

    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax1.spines['top'].set_visible(False)
    ax1.bar(product['Short_Name'], product['Profit_%'], color=bar_colors)
    ax1.set_ylabel('Profit Share (%)')
    ax1.tick_params(axis='x', rotation=35)

    ax2 = ax1.twinx()
    ax2.plot(product['Short_Name'], product['Cumulative_Profit_%'],
             color=COLORS['cost'], marker='o', linewidth=2, label='Cumulative %')
    ax2.axhline(y=80, color='grey', linestyle='--', linewidth=1.2, label='80% Threshold')
    ax2.set_ylabel('Cumulative (%)')
    ax2.set_ylim(0, 110)

    ax1.set_title('Pareto Analysis — Gross Profit', fontsize=13, fontweight='bold')
    ax1.legend(handles=[
        plt.Rectangle((0,0), 1, 1, color=COLORS['profit'],  label='Within 80%'),
        plt.Rectangle((0,0), 1, 1, color=COLORS['warning'], label='Beyond 80%')
    ], loc='upper left', fontsize=8)
    ax2.legend(loc='center right', fontsize=8)
    plt.tight_layout()
    return fig

# ── Factory Charts ────────────────────────────────────────────────────────────

def factory_margin_vs_avg(df):
    company_avg  = df['Gross Profit'].sum() / df['Sales'].sum() * 100
    factory      = df.groupby('Factory')['Gross_Margin_%'].mean().reset_index()\
                     .sort_values('Gross_Margin_%', ascending=True)

    fig, ax = base_fig()
    ax.barh(factory['Factory'], factory['Gross_Margin_%'],
            color=[FACTORY_COLORS.get(f, COLORS['primary']) for f in factory['Factory']],
            height=0.5)
    ax.axvline(x=company_avg, color=COLORS['primary'], linestyle='--', linewidth=1.5)
    ax.set_title('Factory Margin vs Company Average', fontsize=13, fontweight='bold')
    ax.set_xlabel('Gross Margin (%)')
    ax.legend(handles=[
        plt.Rectangle((0,0), 1, 1, color=FACTORY_COLORS.get(f, COLORS['primary']), label=f)
        for f in factory['Factory']
    ] + [
        plt.Line2D([0], [0], color=COLORS['primary'], linestyle='--',
                   label=f'Company Avg ({company_avg:.1f}%)')
    ], loc='lower right', fontsize=8)
    plt.tight_layout()
    return fig

def factory_cost_vs_profit(df):
    factory = df.groupby('Factory').agg(
        Avg_Cost_per_Unit=('Cost_per_Unit', 'mean'),
        Avg_Profit_per_Unit=('Profit_per_Unit', 'mean')
    ).reset_index().sort_values('Avg_Cost_per_Unit', ascending=False)

    import numpy as np
    x, width = np.arange(len(factory)), 0.35
    fig, ax  = base_fig()
    ax.bar(x - width/2, factory['Avg_Cost_per_Unit'],   width,
           color=COLORS['cost'],   label='Avg Cost per Unit')
    ax.bar(x + width/2, factory['Avg_Profit_per_Unit'], width,
           color=COLORS['profit'], label='Avg Profit per Unit')
    ax.set_title('Cost vs Profit per Unit by Factory', fontsize=13, fontweight='bold')
    ax.set_ylabel('Amount per Unit (USD)')
    ax.set_xticks(x)
    ax.set_xticklabels(factory['Factory'], rotation=15, ha='right')
    ax.legend()
    plt.tight_layout()
    return fig

# ── Regional Charts ───────────────────────────────────────────────────────────

def region_profit_bar(df):
    region = df.groupby('Region')['Gross Profit'].sum().reset_index()\
               .sort_values('Gross Profit', ascending=True)

    fig, ax = base_fig()
    ax.barh(region['Region'], region['Gross Profit'],
            color=[REGION_COLORS.get(r, COLORS['primary']) for r in region['Region']],
            height=0.5)
    ax.set_title('Total Gross Profit by Region', fontsize=13, fontweight='bold')
    ax.set_xlabel('Gross Profit (USD)')
    ax.legend(handles=[
        plt.Rectangle((0,0), 1, 1, color=REGION_COLORS.get(r, COLORS['primary']), label=r)
        for r in region['Region']
    ], loc='lower right', fontsize=8)
    plt.tight_layout()
    return fig

def region_division_heatmap(df):
    pivot = df.groupby(['Region', 'Division'])['Gross Profit']\
              .sum().reset_index()\
              .pivot(index='Region', columns='Division', values='Gross Profit')\
              .fillna(0)

    fig, ax = plt.subplots(figsize=(8, 4))
    sns.heatmap(pivot, annot=True, fmt='.0f', cmap='Blues',
                linewidths=0.5, linecolor='white', ax=ax,
                cbar_kws={'label': 'Gross Profit (USD)'})
    ax.set_title('Profit Heatmap — Region × Division', fontsize=13, fontweight='bold')
    ax.tick_params(axis='x', rotation=0)
    ax.tick_params(axis='y', rotation=0)
    plt.tight_layout()
    return fig