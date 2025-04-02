import requests
import json
import config
import base64
import time  # Pour gérer les horodatages

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
        return json.loads(decoded_content)["licenses"], file_content["sha"]  # Retourne aussi le SHA du fichier
    else:
        print(f"❌ Erreur lors du téléchargement du fichier : {response.status_code}")
        return {}, None

# Fonction pour vérifier si une licence a expiré (plus de 3 heures)
def check_license_expiration(licenses):
    current_time = time.time()
    expired_licenses = []

    for license_key, data in licenses.items():
        license_time = data["timestamp"]  # On suppose que chaque licence a un champ "timestamp"
        if current_time - license_time > 10:  # 10800 secondes = 3 heures
            expired_licenses.append(license_key)
    
    return expired_licenses

# Fonction pour mettre à jour les licences actives sur GitHub
def update_active_licenses(licenses):
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    existing_licenses, sha = load_active_licenses()

    # Vérification des licences expirées
    expired_licenses = check_license_expiration(existing_licenses)
    
    # Suppression des licences expirées
    for expired_license in expired_licenses:
        print(f"❌ Licence {expired_license} expirée, suppression.")
        del existing_licenses[expired_license]

    # Ajout des nouvelles licences ou mise à jour des anciennes
    existing_licenses.update(licenses)

    updated_content = json.dumps({"licenses": existing_licenses}, indent=4)

    # Préparation des données pour GitHub
    data = {
        "message": "Mise à jour des licences",
        "content": base64.b64encode(updated_content.encode()).decode(),
        "sha": sha
    }

    # Envoi de la requête PUT pour mettre à jour le fichier
    response = requests.put(GITHUB_API_URL, headers=headers, json=data)

    if response.status_code == 200:
        print("✅ Fichier active_licenses.json mis à jour avec succès !")
    else:
        print(f"❌ Erreur lors de la mise à jour du fichier : {response.status_code}")
        print(response.json())

# Fonction pour ajouter une nouvelle licence active avec un horodatage
def add_license_to_active(license_key, status):
    # Récupère les licences actives existantes
    active_licenses, sha = load_active_licenses()

    # Si la licence est déjà présente dans les licences actives
    if license_key in active_licenses:
        print(f"Clé {license_key} déjà active.")
        return
    
    # Ajoute un timestamp à la licence
    active_licenses[license_key] = {"status": status, "timestamp": time.time()}

    # Met à jour les licences actives sur GitHub
    update_active_licenses(active_licenses)

# Fonction de suppression de la licence
def remove_license(license_key):
    active_licenses, sha = load_active_licenses()
    
    if license_key in active_licenses:
        del active_licenses[license_key]
        update_active_licenses(active_licenses)
        print(f"✅ Licence {license_key} supprimée avec succès.")
    else:
        print(f"❌ Licence {license_key} non trouvée.")
