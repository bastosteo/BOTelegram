import requests
import json
import base64
import time
import threading
import sys
import signal

GITHUB_REPO = "bastosteo/BOTelegram"
FILE_PATH = "active_licenses.json"
GITHUB_TOKEN = "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"  # Même token qu’au-dessus

GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{FILE_PATH}"

def load_active_licenses():
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(GITHUB_API_URL, headers=headers)

    if response.status_code == 200:
        file_content = response.json()
        decoded_content = base64.b64decode(file_content["content"]).decode("utf-8")
        return json.loads(decoded_content).get("licenses", {}), file_content["sha"]
    else:
        print(f"❌ Erreur GitHub {response.status_code} : impossible de lire les licences.")
        return {}, None

def update_active_licenses(licenses, sha):
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    updated_content = json.dumps({"licenses": licenses}, indent=4)

    data = {
        "message": "Mise à jour des licences",
        "content": base64.b64encode(updated_content.encode()).decode(),
        "sha": sha
    }

    response = requests.put(GITHUB_API_URL, headers=headers, json=data)

    if response.status_code == 200:
        print("✅ Fichier active_licenses.json mis à jour avec succès !")
    else:
        print(f"❌ Erreur lors de la mise à jour : {response.status_code}")
        print(response.json())

def remove_license(license_key):
    active_licenses, sha = load_active_licenses()

    if license_key in active_licenses:
        del active_licenses[license_key]
        update_active_licenses(active_licenses, sha)
        print(f"✅ Licence {license_key} libérée.")
    else:
        print(f"❌ Licence {license_key} non trouvée.")

def add_license_with_timer(license_key, status):
    active_licenses, sha = load_active_licenses()

    if license_key in active_licenses:
        print(f"🔒 Licence {license_key} déjà active.")
        return

    active_licenses[license_key] = {"status": status, "timestamp": time.time()}
    update_active_licenses(active_licenses, sha)

    threading.Timer(60, remove_license, [license_key]).start()
    print(f"🕒 Licence {license_key} sera libérée dans 1 minute...")

def handle_exit(signum, frame):
    print("🚨 Fermeture détectée. Libération dans 1 min...")
    time.sleep(60)
    remove_license("X9A7B3C2D1")  # Clé de ton bot
    sys.exit(0)

signal.signal(signal.SIGTERM, handle_exit)
signal.signal(signal.SIGINT, handle_exit)

if __name__ == "__main__":
    bot_license_key = "X9A7B3C2D1"
    add_license_with_timer(bot_license_key, "active")
    while True:
        time.sleep(1)
