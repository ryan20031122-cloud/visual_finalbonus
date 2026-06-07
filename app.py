import os
import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

st.set_page_config(
    page_title="Tech Stock & Market Sentiment Dashboard",
    page_icon="📈",
    layout="wide",
)

st.title("📈 Tech Stock & Market Sentiment Dashboard")
st.caption("A cloud-hosted dashboard integrating stock prices, volatility indicators, and news sentiment.")


def get_database_url() -> str:
    return st.secrets.get("DATABASE_URL", os.getenv("DATABASE_URL", ""))


@st.cache_data(ttl=3600)
def load_stock_data() -> pd.DataFrame:
    database_url = get_database_url()
    if not database_url:
        return pd.DataFrame()
    engine = create_engine(database_url, pool_pre_ping=True)
    query = """
        SELECT ticker, date, close, daily_return, ma_7, ma_30, volatility_7, created_at
        FROM stock_prices
        ORDER BY date ASC;
    """
    return pd.read_sql(query, engine)


@st.cache_data(ttl=3600)
def load_news_data() -> pd.DataFrame:
    database_url = get_database_url()
    if not database_url:
        return pd.DataFrame()
    engine = create_engine(database_url, pool_pre_ping=True)
    query = """
        SELECT title, source, published_at, sentiment, sentiment_score, created_at
        FROM news_sentiment
        ORDER BY published_at DESC NULLS LAST
        LIMIT 100;
    """
    return pd.read_sql(query, engine)


stocks = load_stock_data()
news = load_news_data()

if stocks.empty:
    st.warning("No database data found yet. Run `python data_pipeline/run_pipeline.py` after setting DATABASE_URL.")
    st.stop()

stocks["date"] = pd.to_datetime(stocks["date"])
latest_date = stocks["date"].max().date()
last_updated = stocks["created_at"].max() if "created_at" in stocks else "N/A"
latest = stocks.sort_values("date").groupby("ticker").tail(1)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Tracked Stocks", latest["ticker"].nunique())
col2.metric("Latest Market Date", str(latest_date))
col3.metric("Average Daily Return", f"{latest['daily_return'].mean() * 100:.2f}%")
col4.metric("Last Data Refresh", str(last_updated)[:19])

st.subheader("Stock Price Trend")
selected = st.multiselect(
    "Choose tickers",
    options=sorted(stocks["ticker"].unique()),
    default=sorted(stocks["ticker"].unique())[:3],
)
filtered = stocks[stocks["ticker"].isin(selected)]
fig = px.line(filtered, x="date", y="close", color="ticker", title="Closing Price Over Time")
st.plotly_chart(fig, use_container_width=True)

st.subheader("Latest Performance Snapshot")
snapshot = latest[["ticker", "close", "daily_return", "ma_7", "ma_30", "volatility_7"]].copy()
snapshot["daily_return"] = snapshot["daily_return"].map(lambda x: f"{x * 100:.2f}%" if pd.notnull(x) else "N/A")
snapshot["volatility_7"] = snapshot["volatility_7"].map(lambda x: f"{x * 100:.2f}%" if pd.notnull(x) else "N/A")
st.dataframe(snapshot, use_container_width=True)

if not news.empty:
    st.subheader("News Sentiment Overview")
    sentiment_counts = news["sentiment"].value_counts().reset_index()
    sentiment_counts.columns = ["sentiment", "count"]
    fig2 = px.bar(sentiment_counts, x="sentiment", y="count", title="Recent News Sentiment Distribution")
    st.plotly_chart(fig2, use_container_width=True)
    st.dataframe(news[["published_at", "source", "sentiment", "sentiment_score", "title"]].head(10), use_container_width=True)
else:
    st.info("No news sentiment data found yet.")
