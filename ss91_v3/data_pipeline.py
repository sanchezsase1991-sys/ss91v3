import yfinance as yf
import pandas as pd
import pandas_ta as ta
import numpy as np
import json
import os
import requests
from ss91_v3.utils import log
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from pytrends.request import TrendReq

# =============================================================================
# 1. CÁLCULO DE FACTORES TÉCNICOS (Usando pandas_ta)
# =============================================================================
def fetch_ohlcv(symbol, period="1y", interval="1d"):
    """
    Obtiene datos de yfinance Y calcula todos los indicadores técnicos.
    """
    log.info("Obteniendo datos de mercado de yfinance...")
    df = yf.download(symbol, period=period, interval=interval, progress=False)
    if df.empty:
        raise ValueError("No se pudieron obtener datos de yfinance.")
    
    df = df.reset_index()
    df.columns = [c.lower() for c in df.columns]

    # --- Añadimos todos los indicadores técnicos reales ---
    log.info("Calculando factores técnicos con pandas_ta...")
    df.ta.rsi(length=14, append=True)
    df.ta.ema(length=20, append=True)
    df.ta.atr(length=14, append=True)
    
    # Añadimos más indicadores (ejemplos)
    df.ta.aroon(length=14, append=True) # Aroon Oscillator
    df.ta.trix(length=14, append=True)  # Trix
    df.ta.dpo(length=14, append=True)   # Detrended Price Oscillator
    df.ta.macd(append=True)             # MACD
    
    # Limpiamos NaNs (muy importante)
    df = df.ffill().bfill()
    log.info("Datos técnicos calculados.")
    return df

# =============================================================================
# 2. CÁLCULO DE FACTORES EXTERNOS (Sentimiento, Interés, Macro)
# =============================================================================
def get_all_marginal_factors(df):
    """
    Función principal que recolecta todos los factores
    técnicos, de sentimiento, interés y macro.
    """
    log.info("Iniciando recolección de factores marginales...")
    
    # --- A. Factores de Sentimiento (Reddit + VADER) ---
    def _get_sentiment_factors(api_keys):
        log.info("Obteniendo factor de sentimiento (Reddit)...")
        try:
            # 1. Autenticación con Reddit
            auth = requests.auth.HTTPBasicAuth(
                api_keys['REDDIT_CLIENT_ID'], 
                api_keys['REDDIT_SECRET']
            )
            token = requests.post('https://www.reddit.com/api/v1/access_token', 
                                  auth=auth,
                                  data={'grant_type': 'client_credentials'},
                                  headers={'User-Agent': 'ss91_script'}).json().get('access_token')
            
            headers = {'Authorization': f'bearer {token}', 'User-Agent': 'ss91_script'}
            
            # 2. Obtener posts de subreddits clave
            subs = ['Forex', 'wallstreetbets', 'economics']
            scores = []
            analyzer = SentimentIntensityAnalyzer()
            
            for sub in subs:
                posts = requests.get(f"https://oauth.reddit.com/r/{sub}/new?limit=50", headers=headers).json()
                for p in posts.get('data', {}).get('children', []):
                    text = p['data'].get('title', '')
                    # 3. Analizar CADA título con VADER
                    # 'compound' es un score normalizado de -1.0 (neg) a 1.0 (pos)
                    score = analyzer.polarity_scores(text)['compound']
                    scores.append(score)
            
            if not scores:
                return {"reddit_vader_avg": 0.5} # Neutral si no hay datos

            # 4. Promediar y normalizar de [-1, 1] a [0, 1]
            avg_score = sum(scores) / len(scores)
            normalized_score = (avg_score + 1) / 2.0
            return {"reddit_vader_avg": round(normalized_score, 6)}
        
        except Exception as e:
            log.error(f"Error en factor de sentimiento: {e}")
            return {"reddit_vader_avg": 0.5} # Devuelve neutral en caso de error

    # --- B. Factores de Interés (Google Trends) ---
    def _get_interest_factors():
        log.info("Obteniendo factor de interés (Google Trends)...")
        try:
            pytrends = TrendReq(hl='en-US', tz=360)
            pytrends.build_payload(kw_list=['EURUSD', 'recession', 'forex trading'], timeframe='now 1-d')
            df_trends = pytrends.interest_over_time()
            
            if df_trends.empty:
                return {"gtrends_eurusd": 0, "gtrends_recession": 0}
            
            # Obtener el último valor de interés (0-100) y normalizarlo (0-1)
            interest = df_trends.iloc[-1]
            return {
                "gtrends_eurusd": round(interest.get('EURUSD', 0) / 100.0, 6),
                "gtrends_recession": round(interest.get('recession', 0) / 100.0, 6)
            }
        except Exception as e:
            log.error(f"Error en factor de interés: {e}")
            return {"gtrends_eurusd": 0, "gtrends_recession": 0}

    # --- C. Factores Macro (FRED) ---
    def _get_macro_factors(api_keys):
        log.info("Obteniendo factor macro (FRED)...")
        try:
            fred_key = api_keys['FRED_API_KEY']
            # Ejemplo: Deuda de Tarjetas de Crédito (TERMCBCCALLNS)
            url = f"https://api.stlouisfed.org/fred/series/observations?series_id=TERMCBCCALLNS&api_key={fred_key}&file_type=json"
            data = requests.get(url).json()
            latest_debt = float(data['observations'][-1]['value'])
            
            # Normalización (ejemplo: 1.1T es un valor alto histórico)
            normalized_debt = max(0.0, min(1.0, latest_debt / 1.1e12))
            return {"fred_debt_norm": round(normalized_debt, 6)}
        except Exception as e:
            log.error(f"Error en factor macro: {e}")
            return {"fred_debt_norm": 0.5} # Neutral en caso de error

    # --- D. Orquestación y Construcción del Payload Final ---
    try:
        api_keys = {
            "REDDIT_CLIENT_ID": os.getenv("REDDIT_CLIENT_ID"),
            "REDDIT_SECRET": os.getenv("REDDIT_SECRET"),
            "FRED_API_KEY": os.getenv("FRED_API_KEY")
        }
        
        # 1. Obtener todos los factores de fuentes externas
        sentiment_factors = _get_sentiment_factors(api_keys)
        interest_factors = _get_interest_factors()
        macro_factors = _get_macro_factors(api_keys)
        
        # 2. Combinar todos los factores externos
        marginal_factors = {**sentiment_factors, **interest_factors, **macro_factors}

        # 3. Obtener los últimos factores técnicos del DataFrame
        # .iloc[-1] toma la última fila (los datos de hoy)
        latest_technicals = df.iloc[-1].to_dict()
               
        # Añadimos los 5 últimos precios de cierre para el comando "forecast"
        latest_technicals["recent_prices"] = df["close"].iloc[-5:].tolist()

        # 4. Calcular Fibonacci (de tu código original)
        fibo = compute_fibonacci_levels(df)

        # 5. Construir el Payload (el snapshot.json)
        payload = {
            "snapshot_time_utc": str(pd.Timestamp.utcnow()),
            "symbol": "EURUSD=X",
            "ohlc_latest": latest_technicals, # Todos los indicadores técnicos están aquí
            "fibonacci": fibo,
            "marginal_factors": marginal_factors # Todos los factores externos están aquí
        }
        return payload
    
    except Exception as e:
        log.error(f"Error al generar factores marginales: {e}")
        raise

# =============================================================================
# 3. CÁLCULO DE FIBONACCI (Sin cambios, de tu código)
# =============================================================================
def compute_fibonacci_levels(df):
    high = df["high"].max()
    low = df["low"].min()
    current = df["close"].iloc[-1]
    levels = {
        "0.0%": high,
        "23.6%": high - (high - low) * 0.236,
        "38.2%": high - (high - low) * 0.382,
        "50.0%": high - (high - low) * 0.5,
        "61.8%": high - (high - low) * 0.618,
        "78.6%": high - (high - low) * 0.786,
        "100%": low,
    }
    nearest_level = min(levels.items(), key=lambda x: abs(x[1] - current))
    ratio = (current - low) / (high - low)
    return {
        "fibo_levels": levels,
        "nearest_level": nearest_level[0],
        "nearest_value": nearest_level[1],
        "position_ratio": ratio,
        "current_price": current,
        "high_1y": high,
        "low_1y": low,
    }
