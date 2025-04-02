import requests
import json
import config
import base64

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

# Fonction pour mettre à jour les licences actives sur GitHub
def update_active_licenses(licenses):
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    existing_licenses, sha = load_active_licenses()
    
    # Mise à jour des licences
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
