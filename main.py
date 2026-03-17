import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
from discord import app_commands

class Client(commands.Bot):

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.reactions = True
        super().__init__(command_prefix="!", intents=intents)

    async def on_ready(self):
        print(f'Logged on as {self.user}!')

        try:
            guild = discord.Object(id=1288157001402159175)
            synced = await self.tree.sync(guild=guild)
            print(f'Synced {len(synced)} commands to guild {guild.id}')

        except Exception as e:
            print(f'Error syncing commands: {e}')

    async def on_message(self, message):
        if message.author.bot:
            return

        if message.content.startswith('hello'):
            await message.channel.send(f'Hi there {message.author}')

        await self.process_commands(message)

    async def on_reaction_add(self, reaction, user):
        if user.bot:
            return
        await reaction.message.channel.send('You reacted')


intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.guilds = True
intents.members = True

client = Client()

GUILD_ID = discord.Object(id=1288157001402159175)

# ===============================
# COLOR ROLE MESSAGE
# ===============================

@client.tree.command(name="colourroles", description="Create a message", guild=GUILD_ID)
async def colour_roles(interaction: discord.Interaction):

    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You must be an admin", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)

    description = (
        "React to this message to get your color roles\n\n"
        "🟥 Red\n"
        "🟦 Blue\n"
        "🟩 Green\n"
        "🟨 Yellow\n"
        "🟧 Orange\n"
    )

    embed = discord.Embed(
        title="Pick your color",
        description=description,
        color=discord.Color.blurple()
    )

    message = await interaction.channel.send(embed=embed)

    emojis = ['🟥','🟦','🟩','🟨','🟧']

    for emoji in emojis:
        await message.add_reaction(emoji)

    client.colour_role_message_id = message.id

    await interaction.followup.send("Colour role created", ephemeral=True)


# ===============================
# SIMPLE COMMANDS
# ===============================

@client.tree.command(name="hello", description="Say hello!", guild=GUILD_ID)
async def sayHello(interaction: discord.Interaction):
    await interaction.response.send_message("Hi there!")

# In ra chữ 
@client.tree.command(name="printer", description="print text", guild=GUILD_ID)
async def printer(interaction: discord.Interaction, printer: str):
    await interaction.response.send_message(printer)


# ===============================
# EMBED DEMO
# ===============================

@client.tree.command(name="embed", description="embed demo", guild=GUILD_ID)
async def embed_demo(interaction: discord.Interaction):

    embed = discord.Embed(
        title="Bot Info",
        description="Example embed message",
        color=discord.Color.blurple()
    )

    embed.set_thumbnail(url=interaction.user.display_avatar.url)

    embed.add_field(name="User", value=interaction.user.mention)
    embed.add_field(name="Server", value=interaction.guild.name)

    embed.set_footer(text="Discord Bot")

    await interaction.response.send_message(embed=embed)


# ===============================
# BUTTON VIEW
# ===============================

class View(discord.ui.View):

    @discord.ui.button(label="1st button", style=discord.ButtonStyle.red, emoji="🎧")
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("You clicked the 1st button!")

    @discord.ui.button(label="2nd button", style=discord.ButtonStyle.green, emoji="🎧")
    async def two_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("You clicked the 2nd button!")

    @discord.ui.button(label="3rd button", style=discord.ButtonStyle.blurple, emoji="🎧")
    async def three_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("You clicked the 3rd button!")


@client.tree.command(name="button", description="Displaying a button", guild=GUILD_ID)
async def myButton(interaction: discord.Interaction):
    await interaction.response.send_message(view=View())


# ===============================
# SELECT MENU
# ===============================

class Menu(discord.ui.Select):

    def __init__(self):

        options = [
            discord.SelectOption(label="Option 1", description="This is opt 1", emoji="🎧"),
            discord.SelectOption(label="Option 2", description="This is opt 2", emoji="🎧"),
            discord.SelectOption(label="Option 3", description="This is opt 3", emoji="🎧")
        ]

        super().__init__(
            placeholder="Please choose an option:",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):

        if self.values[0] == "Option 1":
            await interaction.response.send_message("You picked opt 1")

        elif self.values[0] == "Option 2":
            await interaction.response.send_message("You picked opt 2")

        elif self.values[0] == "Option 3":
            await interaction.response.send_message("You picked opt 3")


class MenuView(discord.ui.View):

    def __init__(self):
        super().__init__()
        self.add_item(Menu())

@client.tree.command(name="menu", description="Displaying a drop down menu", guild=GUILD_ID)
async def myMenu(interaction: discord.Interaction):
    await interaction.response.send_message(view=MenuView())

# ===============================
# PHÁT RA ÂM THANH MỖI KHI NGƯỜI DÙNG THAM GIA VÀO VOICE
# ===============================

import asyncio
import time

voice_lock = asyncio.Lock()
last_play = 0
cooldown = 5   # số giây chờ giữa các lần phát

@client.event
async def on_voice_state_update(member, before, after):
    global last_play

    if member.bot:
        return

    if before.channel is None and after.channel is not None:

        async with voice_lock:

            now = time.time()

            # chống spam join
            if now - last_play < cooldown:
                return

            last_play = now

            channel = after.channel
            vc = channel.guild.voice_client

            if vc is None:
                vc = await channel.connect()

            if not vc.is_playing():
                vc.play(discord.FFmpegPCMAudio(
                    "nanana.mp3",
                    executable="D:/ffmpeg-8.0.1-essentials_build/bin/ffmpeg.exe"
                ))

            while vc.is_playing():
                await asyncio.sleep(1)

            await vc.disconnect()



load_dotenv()
TOKEN = os.getenv("TOKEN")
client.run(TOKEN)