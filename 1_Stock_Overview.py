import os
import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

st.set_page_config(page_title="Stock Overview", layout="wide")
st.title("Stock Overview")


def get_database_url() -> str:
    return st.secrets.get("DATABASE_URL", os.getenv("DATABASE_URL", ""))


@st.cache_data(ttl=3600)
def load_data() -> pd.DataFrame:
    engine = create_engine(get_database_url(), pool_pre_ping=True)
    return pd.read_sql("SELECT * FROM stock_prices ORDER BY date ASC", engine)


df = load_data()
df["date"] = pd.to_datetime(df["date"])

ticker = st.selectbox("Select a ticker", sorted(df["ticker"].unique()))
filtered = df[df["ticker"] == ticker]

fig = px.line(filtered, x="date", y=["close", "ma_7", "ma_30"], title=f"{ticker} Close Price and Moving Averages")
st.plotly_chart(fig, use_container_width=True)

fig2 = px.bar(filtered, x="date", y="daily_return", title=f"{ticker} Daily Return")
st.plotly_chart(fig2, use_container_width=True)
