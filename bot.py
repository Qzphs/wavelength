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


@hideout.event
async def on_message(message: discord.Message):
    if message.author not in hideout.whitelist:
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


@hideout.function
async def reroll(interaction: discord.Interaction):
    player = interaction.user.nick or interaction.user.name
    game.new_round(player)
    await interaction.response.send_message(
        f"word: {game.rounds[-1].word}, number: ||`{game.rounds[-1].number:>3}`||"
    )


@hideout.command(
    name="reroll",
    description="Send a random word and a (spoilered) number from 0 to 100.",
)
async def reroll_command(interaction: discord.Interaction):
    await reroll(interaction)


@hideout.function
async def scores(interaction: discord.Interaction):
    if game.scores():
        scores_message = "\n".join(
            f"- {player}: {score}" for player, score in game.scores().items()
        )
    else:
        scores_message = "(no scores yet)"
    await interaction.response.send_message(str(scores_message))


@hideout.command(
    name="scores",
    description="Send the current score of each player.",
)
async def scores_command(interaction: discord.Interaction):
    await scores(interaction)


@hideout.function
async def rounds(interaction: discord.Interaction):
    if game.rounds:
        rounds_message = "\n".join(
            f"- {round.word}, {round.number} {round.scores}" for round in game.rounds
        )
    else:
        rounds_message = "(no rounds yet)"
    await interaction.response.send_message(str(rounds_message))


@hideout.command(
    name="rounds",
    description="Send information about each individual round.",
)
async def rounds_command(interaction: discord.Interaction):
    await rounds(interaction)


@hideout.on_quit
async def on_quit():
    words.save("words.txt")


hideout.bot.run()
