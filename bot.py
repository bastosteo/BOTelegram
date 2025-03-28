from telethon import TelegramClient, events
import requests
import re
import asyncio
import config  # On importe les paramètres utilisateur
import json

# Fonction pour récupérer les clés valides depuis GitHub
def load_licenses():
    url = "https://raw.githubusercontent.com/bastosteo/BOTelegram/main/licenses.json"  # URL brute du fichier JSON
    response = requests.get(url)  # Effectue la requête GET pour récupérer le fichier
    if response.status_code == 200:
        data = response.json()  # Parse le JSON si la requête est réussie
        return data["licenses"]
    else:
        print(f"Erreur lors du téléchargement du fichier : {response.status_code}")
        return []

# Fonction pour vérifier et mettre à jour l'état d'une clé
def update_license_status(key, reserved):
    licenses = load_licenses()  # Charge les clés depuis GitHub
    for license in licenses:
        if license["key"] == key:
            license["is_reserved"] = reserved
            break
    # Sauvegarde les nouvelles données dans le fichier
    with open("licenses.json", "w") as file:
        json.dump({"licenses": licenses}, file, indent=4)

# Vérifier si la clé de licence est valide et non réservée
def is_license_valid_and_available(license_key):
    licenses = load_licenses()  # Charge les clés depuis GitHub
    for license in licenses:
        if license["key"] == license_key:
            if license["is_reserved"]:
                send_alert(f"Alerte : La clé {license_key} est déjà utilisée par une autre personne.")
                return False  # La clé est déjà réservée, envoie une alerte
            else:
                return True  # La clé est valide et disponible
    return False  # La clé n'existe pas

# Vérifier si la clé de licence est valide et réserver la clé
def reserve_license(license_key):
    if is_license_valid_and_available(license_key):
        # Réserve la clé (la rend indisponible)
        update_license_status(license_key, reserved=True)
        return True
    else:
        return False

# Vérification de la clé de licence
if reserve_license(config.license_key):  # Vérifie et réserve la clé définie dans config.py
    print("Licence valide et réservée. Démarrage du bot...")
    # Démarre le bot ici (ajoute ton code de démarrage de bot)
else:
    print("Clé de licence invalide ou déjà réservée. Arrêt du bot.")
    exit()  # Arrêter le bot si la clé n'est pas valide ou déjà réservée



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

with client:
    client.loop.run_until_complete(main())
