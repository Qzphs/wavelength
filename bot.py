import argparse

import discord
from discord.ext import commands

from game import Game, InvalidActionError


parser = argparse.ArgumentParser()
parser.add_argument("-s", "--sync", action="store_true")
args = vars(parser.parse_args())


game = Game()

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
        await bot.tree.sync()


@bot.event
async def on_message(message: discord.Message):
    if channel_whitelist and message.channel not in channel_whitelist:
        return
    number = _parse_number(message.content)
    if number is None:
        return
    player = message.author.nick or message.author.name
    try:
        game.guess(player, number)
    except InvalidActionError:
        return
    await message.add_reaction("❤")


def _parse_number(text: str):
    text = text.strip().removeprefix("||").removesuffix("||").strip()
    if not text.isdigit():
        return None
    number = int(text)
    if not 0 <= number <= 100:
        return None
    return number


@bot.tree.command(
    name="reroll",
    description="Send a random word and a (spoilered) number from 0 to 100.",
)
async def reroll(interaction: discord.Interaction):
    if channel_whitelist and interaction.channel not in channel_whitelist:
        return
    player = interaction.user.nick or interaction.user.name
    game.new_round(player)
    await interaction.response.send_message(
        f"word: {game.rounds[-1].word}, number: ||`{game.rounds[-1].number:>3}`||"
    )


@bot.tree.command(
    name="scores",
    description="Send the current score of each player.",
)
async def scores(interaction: discord.Interaction):
    if channel_whitelist and interaction.channel not in channel_whitelist:
        return
    if game.scores():
        scores_message = "\n".join(
            f"- {player}: {score}" for player, score in game.scores().items()
        )
    else:
        scores_message = "(no scores yet)"
    await interaction.response.send_message(str(scores_message))


@bot.tree.command(
    name="rounds",
    description="Send information about each individual round.",
)
async def rounds(interaction: discord.Interaction):
    if channel_whitelist and interaction.channel not in channel_whitelist:
        return
    if game.rounds:
        rounds_message = "\n".join(
            f"- {round.word}, {round.number} {round.scores}" for round in game.rounds
        )
    else:
        rounds_message = "(no rounds yet)"
    await interaction.response.send_message(str(rounds_message))


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
