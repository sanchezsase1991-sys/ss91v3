"""
Simple backtest stub: iterate historical snapshots and compute decisions.
Use for initial validation before full vectorbt/backtrader integration.
"""
import pandas as pd
from ss91_v3.data_pipeline import fetch_ohlcv, get_all_marginal_factors
from ss91_v3.core import SS91Core

def run_backtest(symbol='EURUSD=X'):
    df = fetch_ohlcv(symbol, period='1y')
    core = SS91Core()
    results = []
    for date in df.index[60:]:
        factors = get_all_marginal_factors(date.strftime('%Y-%m-%d'), df)
        price = float(df.loc[date,'Close'])
        atr = float(df.loc[date,'ATRr_14'])
        atr_ma = float(df.loc[date,'ATR_MA_20'])
        dec = core.decide(factors, price, atr, atr_ma)
        dec['date'] = str(date.date())
        results.append(dec)
    return pd.DataFrame(results)
