import discord
from gradio_client import Client, handle_file
import httpx
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
gradio_client = Client("abidlabs/gradio-playground-bot")

def download_image(attachment):
    response = httpx.get(attachment.url, verify=False)
    image_path = f"./images/{attachment.filename}"
    os.makedirs("./images", exist_ok=True)
    with open(image_path, "wb") as f:
        f.write(response.content)
    return image_path

@client.event
async def on_ready():
    print(f'Bot conectado como {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if client.user in message.mentions:
        clean_message = message.content.replace(f"<@{client.user.id}>", "").strip()

        files = []
        if message.attachments:
            for attachment in message.attachments:
                if any(attachment.filename.lower().endswith(ext) for ext in ['png', 'jpg', 'jpeg', 'gif', 'webp']):
                    image_path = download_image(attachment)
                    files.append(handle_file(image_path))
                    break
        
        for response in gradio_client.submit(
            message={"text": clean_message, "files": files},
        ):
            await message.channel.send(response[-1])

client.run(TOKEN)
