import os
import json
import datetime
import yfinance as yf
# Asegúrate de importar la nueva data_pipeline que te di
from ss91_v3.data_pipeline import fetch_ohlcv, get_all_marginal_factors
from ss91_v3.utils import upload_to_github, log

RESULTS_DIR = "results/snapshots"

def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    today = datetime.date.today().isoformat()
    symbol = os.getenv("SYMBOL", "EURUSD=X")
    snapshot_path = os.path.join(RESULTS_DIR, f"{today}.json") # Definido aquí

    try:
        log.info(f"Collector starting for {today}")
        
        # Estas funciones ahora vienen de tu nueva data_pipeline
        df = fetch_ohlcv(symbol, period="1y") 
        payload = get_all_marginal_factors(df)

        with open(snapshot_path, "w", encoding="utf-8") as f:
            # Usamos un serializador de pandas si hay objetos Timestamp
            json.dump(payload, f, indent=2, ensure_ascii=False, default=str)

        upload_to_github(
            f"snapshots/{today}.json",
            json.dumps(payload, indent=2, ensure_ascii=False, default=str),
        )

        # --- msg = ... (ELIMINADO) ---
        # --- send_to_ntfy(...) (ELIMINADO) ---
        
        log.info("Snapshot saved successfully to GitHub.")
        log.info("Collector finished.")
    except Exception as e:
        log.error(f"Collector error: {e}")
        raise

if __name__ == "__main__":
    main()
