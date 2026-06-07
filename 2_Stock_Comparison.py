import os
import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

st.set_page_config(page_title="Stock Comparison", layout="wide")
st.title("Stock Comparison")


def get_database_url() -> str:
    return st.secrets.get("DATABASE_URL", os.getenv("DATABASE_URL", ""))


@st.cache_data(ttl=3600)
def load_data() -> pd.DataFrame:
    engine = create_engine(get_database_url(), pool_pre_ping=True)
    return pd.read_sql("SELECT * FROM stock_prices ORDER BY date ASC", engine)


df = load_data()
df["date"] = pd.to_datetime(df["date"])

selected = st.multiselect("Select tickers", sorted(df["ticker"].unique()), default=sorted(df["ticker"].unique()))
filtered = df[df["ticker"].isin(selected)].copy()
filtered["cumulative_return"] = filtered.groupby("ticker")["daily_return"].transform(lambda s: (1 + s.fillna(0)).cumprod() - 1)

fig = px.line(filtered, x="date", y="cumulative_return", color="ticker", title="Cumulative Return Comparison")
st.plotly_chart(fig, use_container_width=True)

latest = filtered.sort_values("date").groupby("ticker").tail(1)
fig2 = px.bar(latest, x="ticker", y="volatility_7", title="Latest 7-Day Volatility")
st.plotly_chart(fig2, use_container_width=True)
