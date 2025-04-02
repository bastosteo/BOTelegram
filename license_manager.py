import requests
import json
import config
import base64
import time
import threading
import sys
import signal

# URL du fichier active_licenses.json sur GitHub
GITHUB_REPO = "bastosteo/BOTelegram"
FILE_PATH = "active_licenses.json"
GITHUB_TOKEN = "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"

# URL pour accéder au fichier via l'API GitHub
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{FILE_PATH}"

# Fonction pour récupérer les licences actives depuis GitHub
def load_active_licenses():
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(GITHUB_API_URL, headers=headers)

    if response.status_code == 200:
        file_content = response.json()
        decoded_content = base64.b64decode(file_content["content"]).decode("utf-8")
        return json.loads(decoded_content).get("licenses", {}), file_content["sha"]  # Retourne aussi le SHA du fichier
    else:
        print(f"❌ Erreur lors du téléchargement du fichier : {response.status_code}")
        return {}, None

# Fonction pour mettre à jour les licences actives sur GitHub
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
        print(f"❌ Erreur lors de la mise à jour du fichier : {response.status_code}")
        print(response.json())

# Fonction pour libérer une licence
def remove_license(license_key):
    active_licenses, sha = load_active_licenses()
    
    if license_key in active_licenses:
        del active_licenses[license_key]
        update_active_licenses(active_licenses, sha)
        print(f"✅ Licence {license_key} libérée.")
    else:
        print(f"❌ Licence {license_key} non trouvée.")

# Fonction pour ajouter une licence active avec expiration automatique
def add_license_with_timer(license_key, status):
    active_licenses, sha = load_active_licenses()
    
    if license_key in active_licenses:
        print(f"Clé {license_key} déjà active.")
        return
    
    active_licenses[license_key] = {"status": status, "timestamp": time.time()}
    update_active_licenses(active_licenses, sha)
    
    # Démarrer un timer pour supprimer la licence après 1 minute
    threading.Timer(60, remove_license, [license_key]).start()
    print(f"🕒 Licence {license_key} sera libérée dans 1 minute...")

# Gestion de la fermeture brutale du script
def handle_exit(signum, frame):
    print("🚨 Fermeture détectée, la licence sera libérée dans 1 minute...")
    time.sleep(60)
    remove_license("license_key")  # Remplace par la vraie clé du bot
    sys.exit(0)

# Capture des signaux pour les fermetures inattendues
signal.signal(signal.SIGTERM, handle_exit)
signal.signal(signal.SIGINT, handle_exit)

if __name__ == "__main__":
    bot_license_key = "my_bot_license"  # À modifier avec la clé réelle
    add_license_with_timer(bot_license_key, "active")
    
    while True:
        time.sleep(1)
