import os
import json
import datetime
from ss91_v3.utils import log, upload_to_github
from ss91_v3.core import generate_decision # Importará el core del Paso 3

RESULTS_DIR = "results/decisions"

def run_decitor():
    today = datetime.date.today().isoformat()
    os.makedirs(RESULTS_DIR, exist_ok=True)

    try:
        # Esta función la construiremos en el Paso 3
        # Por ahora, asumimos que falla o no existe
        decision_record, decision_raw, opp_text, context_msg = generate_decision()

        local_path = os.path.join(RESULTS_DIR, f"{today}.json")
        with open(local_path, "w", encoding="utf-8") as f:
            json.dump(decision_record, f, indent=2, ensure_ascii=False)

        upload_to_github(
            f"decisions/{today}.json",
            json.dumps(decision_record, indent=2, ensure_ascii=False)
        )

        # --- full_msg = ... (ELIMINADO) ---
        # --- send_to_ntfy(...) (ELIMINADO) ---

        log.info("Decision processed and uploaded to GitHub.")

    except Exception as e:
        log.error(f"Decitor processing error: {e}")
        # (Si el 'generate_decision' aún no existe, fallará aquí)
        # raise # Comentado para que no detenga el script si core.py no existe
        log.warning("Skipping decitor logic (core.py likely not implemented).")


if __name__ == "__main__":
    run_decitor()
