import os
import json
import requests
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
)
log = logging.getLogger("ss91_v3")


def send_to_ntfy(title, message):
    try:
        topic = os.getenv("NTFY_TOPIC")
        if not topic:
            raise ValueError("NTFY_TOPIC not defined in environment.")
        url = f"https://ntfy.sh/{topic}"
        payload = {"title": title, "message": message}
        response = requests.post(url, json=payload, timeout=10)
        log.info(f"ntfy: {response.status_code} {response.text[:80]}")
    except Exception as e:
        log.error(f"ntfy send error: {e}")


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
            "content": content.encode("utf-8").decode("utf-8"),
        }

        requests.put(url, headers=headers, json=data, timeout=15)
        log.info(f"[GITHUB] Uploaded {path}")
    except Exception as e:
        log.error(f"[GITHUB ERROR] {e}")
