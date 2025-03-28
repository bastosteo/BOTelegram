from telethon import TelegramClient, events
import requests
import re
import asyncio
import config  # On importe les paramètres utilisateur
import json
import base64

# === PARAMÈTRES GITHUB ===
GITHUB_REPO = "bastosteo/BOTelegram"
FILE_PATH = "active_licenses.json"
GITHUB_TOKEN = config.GITHUB_TOKEN
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{FILE_PATH}"

# === FONCTIONS POUR LA GESTION DES LICENCES ===
# Charge les licences actives depuis GitHub
def load_active_licenses():
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(GITHUB_API_URL, headers=headers)

    if response.status_code == 200:
        file_content = response.json()
        decoded_content = base64.b64decode(file_content["content"]).decode("utf-8")
        return json.loads(decoded_content)["licenses"], file_content["sha"]
    else:
        print(f"❌ Erreur de chargement des licences : {response.status_code}")
        return {}, None

# Ajoute une clé à active_licenses.json sur GitHub
def add_license_to_active(license_key):
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    active_licenses, sha = load_active_licenses()

    if license_key in active_licenses:
        print(⚠️ Clé déjà utilisée. Arrêt du bot.")
        exit()  # Empêche le démarrage du bot

    # Marquer la clé comme active
    active_licenses[license_key] = "active"
    updated_content = json.dumps({"licenses": active_licenses}, indent=4)

    # Envoi de la mise à jour via GitHub API
    data = {
        "message": "Ajout d'une licence active",
        "content": base64.b64encode(updated_content.encode()).decode(),
        "sha": sha
    }
    response = requests.put(GITHUB_API_URL, headers=headers, json=data)

    if response.status_code == 200:
        print(f"✅ Clé {license_key} activée.")
    else:
        print(f"❌ Erreur lors de l'ajout de la clé : {response.status_code}")
        exit()

# Supprime une clé de active_licenses.json sur GitHub
def remove_license_from_active(license_key):
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    active_licenses, sha = load_active_licenses()

    if license_key in active_licenses:
        del active_licenses[license_key]  # Supprime la clé
        updated_content = json.dumps({"licenses": active_licenses}, indent=4)

        # Envoi de la mise à jour via GitHub API
        data = {
            "message": "Suppression d'une licence active",
            "content": base64.b64encode(updated_content.encode()).decode(),
            "sha": sha
        }
        response = requests.put(GITHUB_API_URL, headers=headers, json=data)

        if response.status_code == 200:
            print(f"🔓 Clé {license_key} libérée.")
        else:
            print(f"❌ Erreur lors de la suppression de la clé : {response.status_code}")

# Ajoute la clé avant de démarrer
add_license_to_active(config.license_key)

# === DÉMARRAGE DU BOT TELEGRAM ===
client = TelegramClient('session_name', config.API_ID, config.API_HASH)

# Regex pour détecter une adresse crypto
crypto_address_pattern = r'\b0x[a-fA-F0-9]{40}\b'

@client.on(events.NewMessage(chats=config.CHANNEL_ID))
async def handler(event):
    if event.sender_id == config.TARGET_USER_ID:  # Filtre les messages de la personne ciblée
        message = event.raw_text
        addresses = re.findall(crypto_address_pattern, message)

        if addresses:
            for address in addresses:
                print(f'⚡ Adresse crypto détectée : {address}')
                await execute_buy(address)

async def execute_buy(address):   
    await asyncio.sleep(2)

    message = config.MESSAGE_TEMPLATE.format(address=address)
    await client.send_message(config.GMGN_BSC_ID, message)
    print(f"🚀 Commande envoyée à GMGN BSC BOT : {message}")

async def main():
    await client.start(config.PHONE_NUMBER)
    print(f'🤖 Bot connecté et à l\'écoute du canal {config.CHANNEL_ID}, surveille {config.TARGET_USER_ID}')
    await client.run_until_disconnected()

# Suppression de la licence en cas d'arrêt du bot
try:
    with client:
        client.loop.run_until_complete(main())
except KeyboardInterrupt:
    print("❌ Arrêt du bot. Suppression de la licence.")
    remove_license_from_active(config.license_key)
