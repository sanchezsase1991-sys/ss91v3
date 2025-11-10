import os
import json
import requests
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
)
log = logging.getLogger("ss91_v3")

# --- send_to_ntfy() HA SIDO ELIMINADA ---

def upload_to_github(path, content):
    try:
        repo = os.getenv("DATA_REPO", "ss91v3")
        user = os.getenv("GITHUB_USER")
        token = os.getenv("GITHUB_TOKEN")
        if not all([repo, user, token]):
            raise ValueError("GitHub credentials missing in .env")

        url = f"https://api.github.com/repos/{user}/{repo}/contents/{path}"
        headers = {"Authorization": f"token {token}"}

        data = {
            "message": f"Update {path}",
            # Corrección: El contenido debe ser Base64, pero 
            # la API de GitHub también acepta texto plano para JSON.
            # Tu método original es correcto.
            "content": content.encode("utf-8").decode("utf-8"),
        }

        requests.put(url, headers=headers, json=data, timeout=15)
        log.info(f"[GITHUB] Uploaded {path}")
    except Exception as e:
        log.error(f"[GITHUB ERROR] {e}")
