#!/usr/bin/env python3
import os, json, logging
from datetime import datetime
from ss91_v3.data_pipeline import get_all_marginal_factors, send_to_ntfy, upload_to_github

logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(name)s — %(levelname)s — %(message)s")
log = logging.getLogger("collector")

RESULTS_DIR = os.path.join(os.getcwd(), "results", "snapshots")
os.makedirs(RESULTS_DIR, exist_ok=True)
SYMBOL = os.getenv("SYMBOL", "EURUSD=X")

def main():
    today = datetime.utcnow().strftime("%Y-%m-%d")
    filename = f"{today}.json"
    local_path = os.path.join(RESULTS_DIR, filename)
    log.info("Collector starting for %s", today)
    try:
        payload = get_all_marginal_factors(symbol=SYMBOL)
        # save local
        with open(local_path, "w") as f:
            json.dump(payload, f, indent=2)
        log.info("Snapshot saved local: %s", local_path)
        # upload to GitHub (path inside repo)
        repo_path = f"snapshots/{filename}"
        upload_to_github(repo_path, json.dumps(payload, indent=2))
        # send summary to ntfy (trim)
        summary = {
            "symbol": payload.get("symbol"),
            "price": payload.get("fibo",{}).get("current_price"),
            "fibo_nearest": payload.get("fibo",{}).get("nearest_level")
        }
        send_to_ntfy(f"SS91-V3 Snapshot {today}", json.dumps(summary))
        log.info("Snapshot pushed and notified.")
    except Exception as e:
        log.error("Collector failed: %s", e)
        send_to_ntfy("SS91-V3 Collector ERROR", str(e))
    finally:
        log.info("Collector finished.")

if __name__ == "__main__":
    main()
