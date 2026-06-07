import os
import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

st.set_page_config(page_title="News Sentiment", layout="wide")
st.title("News Sentiment")


def get_database_url() -> str:
    return st.secrets.get("DATABASE_URL", os.getenv("DATABASE_URL", ""))


@st.cache_data(ttl=3600)
def load_data() -> pd.DataFrame:
    engine = create_engine(get_database_url(), pool_pre_ping=True)
    return pd.read_sql("SELECT * FROM news_sentiment ORDER BY published_at DESC NULLS LAST", engine)


df = load_data()

if df.empty:
    st.info("No news data available.")
    st.stop()

fig = px.pie(df, names="sentiment", title="News Sentiment Share")
st.plotly_chart(fig, use_container_width=True)

fig2 = px.histogram(df, x="sentiment_score", nbins=20, title="Sentiment Score Distribution")
st.plotly_chart(fig2, use_container_width=True)

st.dataframe(df[["published_at", "source", "sentiment", "sentiment_score", "title"]], use_container_width=True)
