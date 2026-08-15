import random

import discord

from game.game import Game
from game.round import InvalidActionError
from game.words import words
import hideout

game = Game()


def _parse_number(text: str):
    text = text.strip().removeprefix("||").removesuffix("||").strip()
    if not text.isdigit():
        return None
    number = int(text)
    if not 0 <= number <= 100:
        return None
    return number


async def reroll(command: hideout.Message | hideout.SlashCommand):
    await command.require_whitelisted()
    player = command.user.name
    game.new_round(player)
    await command.respond(
        f"word: {game.rounds[-1].word}, number: ||`{game.rounds[-1].number:>3}`||"
    )


async def reroll_2d(command: hideout.Message | hideout.SlashCommand):
    await command.require_whitelisted()
    await command.respond(
        f"words: {words.random()}, {words.random()}, "
        f"number: ||`{random.randint(1, 16):>2}`||"
    )


async def scores(command: hideout.Message | hideout.SlashCommand):
    await command.require_whitelisted()
    if game.scores():
        scores_message = "\n".join(
            f"- {player}: {score}" for player, score in game.scores().items()
        )
    else:
        scores_message = "(no scores yet)"
    await command.respond(str(scores_message))


async def rounds(command: hideout.Message | hideout.SlashCommand):
    await command.require_whitelisted()
    if game.rounds:
        rounds_message = "\n".join(
            f"- {round.word}, {round.number} {round.scores()}" for round in game.rounds
        )
    else:
        rounds_message = "(no rounds yet)"
    await command.respond(str(rounds_message))


@hideout.event
async def on_message(message: discord.Message):
    if message.author not in hideout.whitelist:
        return

    if message.content.startswith(".r2"):
        async with hideout.Message(message) as command:
            await reroll_2d(command)
        return

    if message.content.startswith(".r"):
        async with hideout.Message(message) as command:
            await reroll(command)
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


@hideout.command(
    name="reroll",
    description="Send a random word and a (spoilered) number from 0 to 100.",
)
async def reroll_command(interaction: discord.Interaction):
    async with hideout.SlashCommand(interaction) as command:
        await reroll(command)


@hideout.command(
    name="reroll2d",
    description="Send two random words and a (spoilered) number from 1 to 16.",
)
async def reroll_2d_command(interaction: discord.Interaction):
    async with hideout.SlashCommand(interaction) as command:
        await reroll_2d(command)


# Alias for reroll2d
@hideout.command(
    name="r2roll",
    description="Send two random words and a (spoilered) number from 1 to 16.",
)
async def r2roll_command(interaction: discord.Interaction):
    async with hideout.SlashCommand(interaction) as command:
        await reroll_2d(command)


@hideout.command(
    name="scores",
    description="Send the current score of each player.",
)
async def scores_command(interaction: discord.Interaction):
    async with hideout.SlashCommand(interaction) as command:
        await scores(command)


@hideout.command(
    name="rounds",
    description="Send information about each individual round.",
)
async def rounds_command(interaction: discord.Interaction):
    async with hideout.SlashCommand(interaction) as command:
        await rounds(command)


@hideout.on_quit
async def on_quit():
    words.save("words.txt")


hideout.bot.run()
