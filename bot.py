from telethon import TelegramClient, events
import requests
import re
import asyncio
import config  # On importe les paramètres utilisateur
import requests
import sys

API_URL = "https://ton-serveur-render.com/validate"  # URL de ton serveur Render

def check_license():
    try:
        response = requests.post(API_URL, json={"key": LICENSE_KEY})
        response.raise_for_status()
        print("✅ Licence valide. Démarrage du bot...")
    except requests.exceptions.RequestException:
        print("❌ Clé de licence invalide. Fermeture du bot.")
        sys.exit(1)

if __name__ == "__main__":
    check_license()
    # Démarrage du bot ici...

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
