#!/usr/bin/env python3
import os, json, base64, time
import requests
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf
import pandas_ta as ta
from dotenv import load_dotenv

load_dotenv()

# ENV
NTFY_TOPIC = os.getenv("NTFY_TOPIC", "ss91_alertas")
GITHUB_USER = os.getenv("GITHUB_USER")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
DATA_REPO = os.getenv("DATA_REPO", "SS91-V3-DATA")

# --------------------
# Utilities
# --------------------
def send_to_ntfy(title: str, message: str):
    if not NTFY_TOPIC:
        print("[WARN] NTFY_TOPIC no configurado.")
        return
    url = f"https://ntfy.sh/{NTFY_TOPIC}"
    headers = {"Title": title, "Priority": "high"}
    try:
        r = requests.post(url, data=message.encode("utf-8"), headers=headers, timeout=10)
        print("📢 ntfy:", r.status_code, r.text[:200])
    except Exception as e:
        print(f"[ERROR] ntfy failed: {e}")

def upload_to_github(path: str, content_str: str, branch="main", message=None):
    """
    Sube/actualiza archivo a https://api.github.com/repos/{GITHUB_USER}/{DATA_REPO}/contents/{path}
    """
    if not (GITHUB_USER and GITHUB_TOKEN and DATA_REPO):
        print("[WARN] GitHub variables not set — skipping upload.")
        return {"ok": False, "reason": "no_credentials"}

    api_base = f"https://api.github.com/repos/{GITHUB_USER}/{DATA_REPO}/contents/{path}"
    headers = {"Accept": "application/vnd.github+json"}
    auth = (GITHUB_USER, GITHUB_TOKEN)
    if not message:
        message = f"Add/update {path}"

    # Check if file exists to get sha
    r = requests.get(api_base, auth=auth, headers=headers, timeout=10)
    content_b64 = base64.b64encode(content_str.encode()).decode()
    payload = {"message": message, "content": content_b64, "branch": branch}

    if r.status_code == 200:
        sha = r.json().get("sha")
        payload["sha"] = sha

    r2 = requests.put(api_base, auth=auth, headers=headers, json=payload, timeout=15)
    if r2.status_code in (200,201):
        print(f"[GITHUB] {path} uploaded (status {r2.status_code})")
        return {"ok": True, "status": r2.status_code, "data": r2.json()}
    else:
        print(f"[GITHUB ERROR] {r2.status_code}: {r2.text[:400]}")
        return {"ok": False, "status": r2.status_code, "text": r2.text}

# --------------------
# Market fetch + indicators
# --------------------
def fetch_ohlcv(symbol="EURUSD=X", period="3y", interval="1d"):
    df = yf.download(symbol, period=period, interval=interval, progress=False, auto_adjust=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    df.columns = [c.lower().replace(" ", "_") for c in df.columns]

    required = {"open", "high", "low", "close"}
    if not required.issubset(set(df.columns)):
        raise ValueError(f"Required OHLC columns missing for {symbol}: {df.columns}")

    # indicators
    try:
        df.ta.atr(length=14, append=True)
        df.ta.rsi(length=14, append=True)
        df.ta.ema(length=20, append=True)
    except Exception as e:
        print("[WARN] pandas_ta indicators error:", e)

    df = df.ffill().bfill()
    return df

def compute_fibonacci_context(df):
    high_1y = df['close'].rolling(window=252, min_periods=1).max().iloc[-1]
    low_1y = df['close'].rolling(window=252, min_periods=1).min().iloc[-1]
    diff = high_1y - low_1y if (high_1y - low_1y) != 0 else 1.0
    current = df['close'].iloc[-1]
    fibo_levels = {
        "0.0%": high_1y,
        "23.6%": high_1y - 0.236 * diff,
        "38.2%": high_1y - 0.382 * diff,
        "50.0%": high_1y - 0.5 * diff,
        "61.8%": high_1y - 0.618 * diff,
        "78.6%": high_1y - 0.786 * diff,
        "100%": low_1y
    }
    closest = min(fibo_levels.items(), key=lambda kv: abs(kv[1] - current))
    ratio = (current - low_1y) / diff
    return {
        "fibo_levels": fibo_levels,
        "nearest_level": closest[0],
        "nearest_value": float(closest[1]),
        "position_ratio": float(ratio),
        "current_price": float(current),
        "high_1y": float(high_1y),
        "low_1y": float(low_1y)
    }

def get_all_marginal_factors(symbol="EURUSD=X"):
    df = fetch_ohlcv(symbol=symbol, period="3y")
    last = df.iloc[-1].to_dict()
    # minimal macros placeholder
    macros = {"timestamp": datetime.utcnow().isoformat()}
    fibo = compute_fibonacci_context(df)
    # normalize numeric values to primitives
    last_clean = {k: (float(v) if (isinstance(v,(int,float)) or (hasattr(v,'__float__'))) else str(v)) for k,v in last.items()}
    payload = {"symbol": symbol, "snapshot_time": datetime.utcnow().isoformat(), "ohlc": last_clean, "macros": macros, "fibo": fibo}
    return payload

# --------------------
# FX opportunities detection from fx_config.json
# --------------------
def detect_fx_opportunities(config_path="fx_config.json"):
    cfg_path = os.path.join(os.getcwd(), config_path)
    if not os.path.exists(cfg_path):
        print("[WARN] fx_config.json not found:", cfg_path)
        return []

    try:
        with open(cfg_path, "r") as f:
            cfg = json.load(f)
    except Exception as e:
        print("[WARN] fx_config.json parse error:", e)
        return []

    params = cfg.get("indicators", {})
    lookback = params.get("lookback_period_days", 180)

    assets = cfg.get("related_assets", [])
    opportunities = []
    for a in assets:
        sym = a.get("symbol")
        try:
            df = fetch_ohlcv(sym, period=f"{lookback}d", interval="1d")
            rsi_col = [c for c in df.columns if c.lower().startswith("rsi")]
            if not rsi_col:
                continue
            rsi_val = float(df[rsi_col[-1]].iloc[-1])
            high_th = params.get("momentum_threshold_high", 70)
            low_th = params.get("momentum_threshold_low", 30)
            if rsi_val >= high_th or rsi_val <= low_th:
                opp = {"symbol": sym, "rsi": round(rsi_val,2),
                       "momentum": "alcista" if rsi_val>high_th else "bajista",
                       "relation": a.get("relation","")}
                opportunities.append(opp)
        except Exception as e:
            print(f"[WARN] detect fx {sym} failed: {e}")
            continue
    return opportunities
