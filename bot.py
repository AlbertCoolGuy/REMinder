import discord
from discord.ext import commands, tasks
from discord import app_commands

import settings
import re
import random
import datetime
import pytz
from typing import Optional


intents = discord.Intents.all()

SØVNRÅD = []
with open('søvnråd.txt', 'r') as f:
    SØVNRÅD = f.readlines()

class REMinderClient(commands.Bot):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(command_prefix="!", intents=intents)
    async def setup_hook(self):
        return
    
client = REMinderClient(intents=intents)


@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    await new_func()

async def new_func():
    await send_søvnråd.start()


@client.tree.command()
@app_commands.user_install()
@app_commands.describe(
    first_value='The first value you want to add something to',
    second_value='The value you want to add to the first value'
)
async def add(interaction: discord.Interaction, first_value: int, second_value: int):
    """Adds two numbers together."""
    await interaction.response.send_message(f'{first_value} + {second_value} = {first_value + second_value}')

@client.tree.command()
@app_commands.user_install()
@app_commands.describe(
    sengetid='Tid du gerne vil gå i seng',
    reminders_enabled='Om påmindelser er slået til'
)
async def sengetid(interaction: discord.Interaction, sengetid: str, reminders_enabled: bool):
    """
    Sætter din sengetid og slår påmindelser til eller fra.
    """
    if re.match("^([0-9]|0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$", sengetid):
        await interaction.response.send_message(f'Din sengetid er nu sat til {sengetid}. Påmindelser er slået {"til" if reminders_enabled else "fra"}.')
        if reminders_enabled:
            interval = (datetime.datetime.strptime(sengetid, "%H:%M") - datetime.timedelta(hours=1)).time()
            send_sengetid.change_interval(time=interval)
            send_sengetid.start()
        else:
            send_sengetid.stop()
    else:
        await interaction.response.send_message('Ugyldig tid. Brug formatet HH:MM.')

@tasks.loop(time=datetime.time(hour=23, minute=0, tzinfo=pytz.timezone('Europe/Copenhagen')))
async def send_sengetid():
    channel = client.get_channel(1314597072011264032)
    await channel.send(f'Klokken er {datetime.datetime.now().strftime("%H:%M")}. Det er tid til at gå i seng. {random.choice(SØVNRÅD)}')

@tasks.loop(time=datetime.time(hour=11, minute=11, tzinfo=pytz.timezone('Europe/Copenhagen')))
async def send_søvnråd():
    channel = client.get_channel(1314597072011264032)
    await channel.send(random.choice(SØVNRÅD))

@client.tree.command()
@app_commands.user_install()
async def søvnråd(interaction: discord.Interaction):
    """Giver dig et tilfældigt søvnråd."""
    await interaction.response.send_message(random.choice(SØVNRÅD))

@client.tree.command(name='sync', description='Owner only')
@app_commands.guilds(discord.Object(id=settings.TEST_GUILD))
@app_commands.user_install()
async def sync(interaction: discord.Interaction, context: Optional[str] = 'guild'):
    if interaction.user.id in settings.OWNERS:
        await interaction.response.defer(ephemeral=True)
        if context == 'guild':
            client.tree.copy_global_to(guild=discord.Object(settings.TEST_GUILD))
            await client.tree.sync(guild=discord.Object(settings.TEST_GUILD))
            print('Kommandoer synkroniseret.')
            await interaction.followup.send("Kommandoer synkroniseret.", ephemeral=True)
        elif context == 'global':
            await client.tree.sync()
            print('Kommandoer synkroniseret.')
            await interaction.followup.send("Kommandoer synkroniseret.", ephemeral=True)
    else:
        await interaction.followup.send('Du skal være ejer for at kunne bruge denne kommando!', ephemeral=True)


client.run(settings.TOKEN)