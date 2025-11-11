import os
import json
import requests
import logging
import base64  # <-- 1. IMPORTANTE: Importar la librería Base64

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
)
log = logging.getLogger("ss91_v3")


def upload_to_github(path, content):
    """
    Sube contenido al repositorio de GitHub, manejando la codificación
    Base64 y forzando que los errores se reporten.
    """
    try:
        repo = os.getenv("DATA_REPO", "ss91v3")
        user = os.getenv("GITHUB_USER")
        token = os.getenv("GITHUB_TOKEN")
        
        if not all([repo, user, token]):
            raise ValueError("GitHub credentials missing in .env")

        url = f"https://api.github.com/repos/{user}/{repo}/contents/{path}"
        
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }

        # --- 2. CORRECCIÓN CRÍTICA (Codificación Base64) ---
        # El contenido (string) debe ser convertido a bytes,
        # luego codificado en Base64, y luego devuelto a string.
        content_bytes = content.encode("utf-8")
        content_base64 = base64.b64encode(content_bytes).decode("utf-8")
        # --------------------------------------------------

        data = {
            "message": f"Update {path}",
            "content": content_base64  # <-- 3. Usar el contenido codificado
        }

        response = requests.put(url, headers=headers, json=data, timeout=15)
        
        # 4. FORZAR ERROR (Esto lo mantenemos)
        # Si la API devuelve 403, 404, etc., esto fallará ruidosamente.
        response.raise_for_status() 
        
        log.info(f"[GITHUB] Uploaded {path}")

    except Exception as e:
        log.error(f"[GITHUB ERROR] Fallo al subir {path}: {e}")
        # 5. RE-LANZAR ERROR (Esto lo mantenemos)
        # Asegura que el workflow de GitHub falle si la subida no funciona.
        raise
