import aiohttp
import discord
from discord import app_commands
from dotenv import load_dotenv
from os import getenv

load_dotenv()

class PanelBot(discord.Client):
    def __init__(self, *, intents: discord.Intents = discord.Intents.default()):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.bh_key = getenv("BISECT_TOKEN")
        self.server_id = getenv("SERVER_ID")  # Ensure you have this in your .env file

    async def setup_hook(self):
        print("Syncing commands...")
        await self.tree.sync()

    async def bh_api_request(self, endpoint: str, method: str = "GET", data: dict|None = None):
        base_url = f"https://games.bisecthosting.com/api/client/servers/{self.server_id}"
        headers = {
            "Authorization": f"Bearer {self.bh_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        url = f"{base_url}/{endpoint}" if endpoint else base_url
        print(url)
        print(data)
        async with aiohttp.ClientSession() as session:
            if method.upper() == "GET":
                async with session.get(url, headers=headers) as response:
                    return await response.json(), response.status
            elif method.upper() == "POST":
                async with session.post(url, headers=headers, json=data) as response:
                    return await response.json(), response.status
            elif method.upper() == "DELETE":
                async with session.delete(url, headers=headers) as response:
                    return await response.json(), response.status
            else:
                raise ValueError("Unsupported HTTP method.")

client = PanelBot()

@client.event
async def on_ready():
    print(f"{client.user} has logged in!")

@client.tree.command(name="restart", description="Restart the server")
async def restart_server(interaction: discord.Interaction):
    await interaction.response.send_message("Restarting the server...")
    response, status = await client.bh_api_request("power", method="POST", data={"signal": "restart"})
    print(response)
    if status == 204:
        await interaction.followup.send("Server restarted!")
    else:
        await interaction.followup.send("Failed to restart the server.")

client.run(getenv("DISCORD_TOKEN"))