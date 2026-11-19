# app.py
# The ERP sales dashboard: four KPI cards, three charts, and date and product filters.
# It only reads the views from views.sql, never the raw tables.
# Run it from PowerShell with: .venv\Scripts\python.exe -m streamlit run app.py

import os

import pandas as pd
import psycopg
import streamlit as st
from dotenv import load_dotenv
from psycopg.types.numeric import FloatLoader

load_dotenv()
st.set_page_config(page_title="ERP Sales Dashboard", layout="wide")


# Reads one view from the database into a pandas table.
# Streamlit keeps the result for 10 minutes, so clicking a filter doesn't ask the database again.
@st.cache_data(ttl=600)
def load_view(view_name):
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        # Turn database decimals into normal Python numbers, so pandas can add them up and chart them.
        conn.adapters.register_loader("numeric", FloatLoader)
        cur = conn.execute(f"SELECT * FROM {view_name}")
        columns = [col.name for col in cur.description]
        return pd.DataFrame(cur.fetchall(), columns=columns)


margin = load_view("gross_margin")
products = load_view("top_products")
status = load_view("order_status")
low_stock = load_view("low_stock")

# Sidebar filters: a range of months, and any number of products (empty means all products).
st.sidebar.header("Filters")
months = sorted(margin["month"].unique())
start, end = st.sidebar.select_slider("Months", options=months, value=(months[0], months[-1]),
                                      format_func=lambda m: m.strftime("%b %Y"))
chosen = st.sidebar.multiselect("Products (leave empty for all)", sorted(margin["product_name"].unique()))


# Keeps only the rows inside the chosen months and, if products were picked, only those products.
def apply_filters(df, use_products=True):
    df = df[(df["month"] >= start) & (df["month"] <= end)]
    if use_products and chosen:
        df = df[df["product_name"].isin(chosen)]
    return df


# Low stock has no month, so only the product filter applies to it.
low = low_stock[low_stock["product_name"].isin(chosen)] if chosen else low_stock

st.title("ERP Sales Dashboard")
st.caption("Synthetic data covering 12 months. Cancelled orders are left out of revenue and profit.")

# KPI cards: revenue, profit and margin % come from gross_margin, the reorder count from low_stock.
m = apply_filters(margin)
revenue = m["revenue"].sum()
profit = m["margin"].sum()
margin_pct = 100 * profit / revenue if revenue else 0

card1, card2, card3, card4 = st.columns(4)
card1.metric("Revenue", f"€{revenue:,.0f}")
card2.metric("Gross profit", f"€{profit:,.0f}")
card3.metric("Gross margin", f"{margin_pct:.1f}%")
card4.metric("Products to reorder", len(low))

# Chart 1: revenue per month, as a line.
p = apply_filters(products)
st.subheader("Revenue per month")
st.line_chart(p.groupby("month")["revenue"].sum())

# Chart 2: the 10 products with the most revenue, biggest first.
st.subheader("Top 10 products by revenue")
top10 = p.groupby("product_name")["revenue"].sum().nlargest(10).reset_index()
st.bar_chart(top10, x="product_name", y="revenue", horizontal=True, sort="-revenue")

# Chart 3: number of orders per status. Only the date filter applies, because one order can hold many products.
s = apply_filters(status, use_products=False)
st.subheader("Orders by status")
st.bar_chart(s.groupby("status")["orders"].sum())
