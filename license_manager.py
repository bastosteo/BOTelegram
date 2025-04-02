import requests
import json
import config
import base64
import time

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

# Fonction pour vérifier si une licence a expiré (plus de 60 secondes)
def check_license_expiration(licenses):
    current_time = time.time()
    return [key for key, data in licenses.items() if current_time - data["timestamp"] > 60]

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

# Fonction pour ajouter une nouvelle licence active
def add_license_to_active(license_key, status):
    active_licenses, sha = load_active_licenses()
    
    if license_key in active_licenses:
        print(f"Clé {license_key} déjà active.")
        return
    
    active_licenses[license_key] = {"status": status, "timestamp": time.time()}
    update_active_licenses(active_licenses, sha)

# Fonction de suppression d'une licence
def remove_license(license_key):
    active_licenses, sha = load_active_licenses()
    
    if license_key in active_licenses:
        del active_licenses[license_key]
        update_active_licenses(active_licenses, sha)
        print(f"✅ Licence {license_key} supprimée avec succès.")
    else:
        print(f"❌ Licence {license_key} non trouvée.")

# Fonction pour nettoyer les licences expirées
def cleanup_expired_licenses():
    active_licenses, sha = load_active_licenses()
    expired_licenses = check_license_expiration(active_licenses)
    
    if expired_licenses:
        for license_key in expired_licenses:
            print(f"❌ Licence {license_key} expirée, suppression.")
            del active_licenses[license_key]
        update_active_licenses(active_licenses, sha)

# Fonction pour lancer le nettoyage périodique
def start_license_cleanup():
    while True:
        cleanup_expired_licenses()
        time.sleep(10)  # Vérifie toutes les 10 secondes

if __name__ == "__main__":
    start_license_cleanup()
