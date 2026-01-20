import argparse

import discord
from discord.ext import commands

from game import random_number, random_word


parser = argparse.ArgumentParser()
parser.add_argument("-s", "--sync", action="store_true")
args = vars(parser.parse_args())


bot = commands.Bot(intents=discord.Intents.all(), command_prefix=[])

channel_whitelist: list[discord.TextChannel] = []


@bot.event
async def on_ready():
    try:
        with open("channel.txt") as file:
            channel_whitelist.append(bot.get_channel(int(file.read())))
    except (FileNotFoundError, ValueError):
        pass
    if args["sync"]:

        # TODO remove once this is no longer needed
        for guild in bot.guilds:
            bot.tree.clear_commands(guild=guild, type=None)
            await bot.tree.sync(guild=guild)

        await bot.tree.sync()


@bot.tree.command(
    name="reroll",
    description="Send a random word and a (spoilered) number from 0 to 100.",
)
async def reroll(interaction: discord.Interaction):
    if channel_whitelist and interaction.channel not in channel_whitelist:
        return
    await interaction.response.send_message(
        f"word: {random_word()}, number: ||`{random_number():>3}`||"
    )


@bot.tree.command(
    name="quit",
    description="Stop running the bot.",
)
async def quit(interaction: discord.Interaction):
    if channel_whitelist and interaction.channel not in channel_whitelist:
        return
    await interaction.response.send_message(":zany_face:")
    await bot.close()


with open("token.txt") as file:
    TOKEN = file.read().strip()

bot.run(TOKEN)
