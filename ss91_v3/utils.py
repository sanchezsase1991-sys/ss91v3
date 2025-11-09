import os, json, logging
from dotenv import load_dotenv
from datetime import datetime
load_dotenv()

def setup_logger(name, level=logging.INFO):
    logger = logging.getLogger(name)
    if not logger.handlers:
        ch = logging.StreamHandler()
        fmt = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")
        ch.setFormatter(fmt)
        logger.addHandler(ch)
    logger.setLevel(level)
    return logger

def load_env():
    return {
        "SUPABASE_URL": os.getenv("SUPABASE_URL"),
        "SUPABASE_KEY": os.getenv("SUPABASE_KEY"),
        "SERPAPI_KEY": os.getenv("SERPAPI_KEY"),
        "NEWSAPI_KEY": os.getenv("NEWSAPI_KEY"),
        "ALPHA_VANTAGE_API_KEY": os.getenv("ALPHA_VANTAGE_API_KEY"),
        "REDDIT_CLIENT_ID": os.getenv("REDDIT_CLIENT_ID"),
        "NLPCLOUD_API_KEY": os.getenv("NLPCLOUD_API_KEY"),
        "NTFY_TOPIC": os.getenv("NTFY_TOPIC"),
        "SYMBOL": os.getenv("SYMBOL","EURUSD=X"),
    }
