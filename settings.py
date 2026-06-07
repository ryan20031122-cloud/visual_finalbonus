import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")

TICKERS = ["AAPL", "MSFT", "NVDA", "GOOGL", "TSLA"]
DEFAULT_PERIOD = "1y"
NEWS_QUERY = "technology stocks OR artificial intelligence OR semiconductor OR cloud computing"
