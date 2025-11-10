#!/usr/bin/env python3
import os, json, logging
from datetime import datetime
from dotenv import load_dotenv
from sherloock import Sherloock
from ss91_v3.data_pipeline import fetch_ohlcv, detect_fx_opportunities, send_to_ntfy, upload_to_github

load_dotenv()
NTFY_TOPIC = os.getenv("NTFY_TOPIC", "ss91_alertas")

logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(name)s — %(levelname)s — %(message)s")
log = logging.getLogger("decitor")

RESULTS_DIR = os.path.join(os.getcwd(), "results", "decisions")
os.makedirs(RESULTS_DIR, exist_ok=True)

def fibo_context_from_df(df):
    high_1y = df["close"].rolling(window=252, min_periods=1).max().iloc[-1]
    low_1y = df["close"].rolling(window=252, min_periods=1).min().iloc[-1]
    diff = high_1y - low_1y if (high_1y - low_1y)!=0 else 1.0
    current = df["close"].iloc[-1]
    ratio = (current - low_1y)/diff
    phase = ("zona techo" if ratio>0.85 else
             "zona media" if ratio>0.5 else
             "acumulación" if ratio>0.2 else
             "suelo/inicio")
    return {"ratio": float(ratio), "phase": phase, "price": float(current), "high": float(high_1y), "low": float(low_1y)}

def main():
    today = datetime.utcnow().strftime("%Y-%m-%d")
    log.info("Decitor running for %s", today)
    try:
        # Get 1y DF
        df = fetch_ohlcv(os.getenv("SYMBOL","EURUSD=X"), period="1y")
    except Exception as e:
        log.error("fetch_ohlcv failed: %s", e)
        send_to_ntfy("SS91-V3 Error", f"fetch_ohlcv failed: {e}")
        return

    try:
        fibo = fibo_context_from_df(df)
        log.info("Fibo context: %s", fibo)

        # instantiate Sherloock
        sher = Sherloock(max_fibers=4)
        sample_values = [float(v) for v in df["close"].tail(5)]
        prompt = f"forecast {json.dumps(sample_values)} with_limit avg + 3"
        decision_raw = sher.reason(prompt)

        # detect fx opportunities (related assets)
        opportunities = detect_fx_opportunities()

        # build consolidated message
        context_msg = (
            f"Contexto: {fibo['phase']} ({fibo['ratio']*100:.2f}% del rango anual)\n"
            f"Precio actual: {fibo['price']:.4f} | Máx: {fibo['high']:.4f} | Mín: {fibo['low']:.4f}\n"
        )
        opp_text = ""
        if opportunities:
            opp_text = "\nOportunidades detectadas:\n"
            for o in opportunities:
                opp_text += f"- {o['symbol']} ({o.get('relation','')}) RSI {o['rsi']} → {o['momentum']}\n"

        decision_record = {
            "date": today,
            "symbol": os.getenv("SYMBOL","EURUSD=X"),
            "fibo_context": fibo,
            "sample_values": sample_values,
            "decision_raw": decision_raw,
            "opportunities": opportunities,
            "timestamp": datetime.utcnow().isoformat()
        }

        # ensure results/decisions directory exists
os.makedirs(RESULTS_DIR, exist_ok=True)

local_path = os.path.join(RESULTS_DIR, f"{today}.json")
try:
    with open(local_path, "w", encoding="utf-8") as f:
        json.dump(decision_record, f, indent=2, ensure_ascii=False)
    log.info(f"Decision JSON saved locally at {local_path}")
except Exception as e:
    log.error(f"Error saving decision locally: {e}")

        # upload json to github
        upload_to_github(f"decisions/{today}.json", json.dumps(decision_record, indent=2))

        # consolidate message and send once
        full_msg = f"🧠 SS91-V3 Decision {today}\n\n{context_msg}\nDecision: {decision_raw}\n{opp_text}"
        send_to_ntfy(f"SS91-V3 Diario {today}", full_msg)

        log.info("Decision processed and notified.")

    except Exception as e:
        log.error("Decitor processing error: %s", e)
        send_to_ntfy("SS91-V3 Error", f"Decitor failed: {e}")

if __name__ == "__main__":
    main()
