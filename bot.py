from telethon import TelegramClient, events
import requests
import re
import asyncio
import config  # On importe les paramètres utilisateur
import json

# Fonction pour charger les clés valides depuis le fichier JSON
def load_licenses():
    with open("licenses.json", "r") as file:
        data = json.load(file)
        return data["licenses"]

# Vérifier si la clé du client est valide
def is_license_valid(license_key):
    valid_licenses = load_licenses()
    return license_key in valid_licenses

# Vérification de la clé de licence
if is_license_valid(config.license_key):
    print("Licence valide. Démarrage du bot...")
    # Démarre le bot ici
else:
    print("Clé de licence invalide. Arrêt du bot.")
    exit()  # Arrêter le bot



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
