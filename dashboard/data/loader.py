from pathlib import Path

import pandas as pd
import streamlit as st

# resolved relative to this file, not the process's cwd — Streamlit Cloud
# runs the app with cwd set to the repo root, not dashboard/
DATA_DIR = Path(__file__).resolve().parent.parent.parent / 'data'

# factory mapping from project brief
FACTORY_MAP = {
    'Wonka Bar - Nutty Crunch Surprise'  : "Lot's O' Nuts",
    'Wonka Bar - Fudge Mallows'          : "Lot's O' Nuts",
    'Wonka Bar -Scrumdiddlyumptious'     : "Lot's O' Nuts",
    'Wonka Bar - Milk Chocolate'         : "Wicked Choccy's",
    'Wonka Bar - Triple Dazzle Caramel'  : "Wicked Choccy's",
    'Laffy Taffy'                        : 'Sugar Shack',
    'SweeTARTS'                          : 'Sugar Shack',
    'Nerds'                              : 'Sugar Shack',
    'Fun Dip'                            : 'Sugar Shack',
    'Fizzy Lifting Drinks'               : 'Sugar Shack',
    'Everlasting Gobstopper'             : 'Secret Factory',
    'Hair Toffee'                        : 'The Other Factory',
    'Lickable Wallpaper'                 : 'Secret Factory',
    'Wonka Gum'                          : 'Secret Factory',
    'Kazookles'                          : 'The Other Factory'
}

def add_kpis(df):
    df['Gross_Margin_%']         = (df['Gross Profit'] / df['Sales']) * 100
    df['Profit_per_Unit']        = df['Gross Profit'] / df['Units']
    df['Cost_per_Unit']          = df['Cost'] / df['Units']
    df['Revenue_Contribution_%'] = (df['Sales'] / df['Sales'].sum()) * 100
    df['Profit_Contribution_%']  = (df['Gross Profit'] / df['Gross Profit'].sum()) * 100
    return df

def add_classifications(df):
    df['Factory'] = df['Product Name'].map(FACTORY_MAP)
    df['Month']      = df['Order Date'].dt.month
    df['Month_Name'] = df['Order Date'].dt.strftime('%b')
    df['Quarter']    = df['Order Date'].dt.quarter

    # quadrant classification
    sales_median  = df.groupby('Product Name')['Sales'].sum().median()
    margin_median = df.groupby('Product Name')['Gross_Margin_%'].mean().median()

    product_stats = df.groupby('Product Name').agg(
        Total_Revenue = ('Sales', 'sum'),
        Avg_Margin    = ('Gross_Margin_%', 'mean')
    )

    def classify(row):
        high_sales  = row['Total_Revenue'] >= sales_median
        high_margin = row['Avg_Margin']    >= margin_median
        if high_sales and high_margin:     return 'STAR'
        elif not high_sales and high_margin: return 'HIDDEN GEM'
        elif high_sales and not high_margin: return 'VOLUME TRAP'
        else:                              return 'DEAD WEIGHT'

    product_stats['Quadrant'] = product_stats.apply(classify, axis=1)
    df = df.merge(product_stats[['Quadrant']], on='Product Name', how='left')
    return df

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_DIR / 'Nassau_Candy_Distributor.csv')
    df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True)

    # Raw data spans 2024-01-02 to 2025-12-31 — scope restricted to FY2025
    # only, matching the notebook pipeline (see notebooks/02_data_clensing.ipynb)
    df = df[df['Order Date'].dt.year == 2025].reset_index(drop=True)

    df = add_kpis(df)
    df = add_classifications(df)
    return df