import discord
from discord.ext import commands
from discord import app_commands

import settings

intents = discord.Intents.all()

class MyClient(commands.Bot):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(command_prefix="!", intents=intents)
    async def setup_hook(self):
        return
    
client = MyClient(intents=intents)


@client.event
async def on_ready(): 
    await client.change_presence(status=discord.Status.online, activity=discord.Activity(name=settings.BotStatus)) 
    await client.tree.sync(guild=discord.Object(id=settings.TEST_GUILD))
    print("Bot is ready!")


@client.tree.command()
@app_commands.user_install()
@app_commands.describe(
    first_value='The first value you want to add something to',
    second_value='The value you want to add to the first value',
)
async def add(interaction: discord.Interaction, first_value: int, second_value: int):
    """Adds two numbers together."""
    await interaction.response.send_message(f'{first_value} + {second_value} = {first_value + second_value}')


@client.tree.command(name='sync', description='Owner only')
@app_commands.guilds(discord.Object(id=settings.TEST_GUILD))
@app_commands.user_install()
async def sync(interaction: discord.Interaction):
    if interaction.user.id in settings.OWNERS:
        await client.tree.sync()
        print('Command tree synced.')
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("Command tree synced.")
    else:
        await interaction.response.send_message('You must be the owner to use this command!')


client.run(settings.TOKEN)