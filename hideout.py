"""
Hideout v0.1

Support for private discord bot used with friends.
"""

__all__ = ["bot", "command", "event", "Function", "function", "on_quit", "whitelist"]


import argparse
import functools
import json
from typing import Awaitable, Callable

import discord
from discord.ext import commands


class Config:

    def __init__(self):
        with open("bot.json") as file:
            config = json.load(file)
        self.channel_id: int = config["channel"]
        self.__token: str = config["token"]
        self.whitelist: list[int] = config["whitelist"]

    @property
    def token(self):
        token = self.__token
        self.__token = ""
        return token


config = Config()
whitelist: list[discord.User] = []


class Bot(commands.Bot):

    def __init__(self):
        super().__init__(intents=discord.Intents.all(), command_prefix=[])

    async def on_ready(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-s", "--sync", action="store_true")
        args = vars(parser.parse_args())
        if args["sync"]:
            await self.tree.sync()

        for user_id in config.whitelist:
            whitelist.append(await self.fetch_user(user_id))

        self.channel = await self.fetch_channel(config.channel_id)
        await self.on_ready_hook()

    async def on_ready_hook(self):
        pass

    def run(self):
        super().run(config.token)


bot = Bot()
command = bot.tree.command


def event(func: Callable[[], Awaitable[None]]):
    if func.__name__ == "on_ready":
        bot.on_ready_hook = func
    else:
        bot.event(func)


Function = Callable[..., Awaitable[None]]


def function(callback: Function):
    """
    Decorator for hideout functions.

    Hideout functions are intended to be called by actual Discord
    commands. (This is a workaround to issues with wrapping commands
    directly when they have parameters.)

    Hideout functions can only be used by whitelisted users. This
    decorator also catches any errors raised by the function and sends
    the error message to the user.
    """

    @functools.wraps(callback)
    async def wrapper(interaction: discord.Interaction, *args, **kwargs):
        try:
            if interaction.user not in whitelist:
                await interaction.response.send_message(
                    "You can't use commands. (Ask to be added to the whitelist?)"
                )
                return
            await callback(interaction, *args, **kwargs)
        except Exception as error:
            await interaction.response.send_message(
                f"{error.__class__.__name__}: {error}"
            )

    return wrapper


_quit_hooks: list[Function] = []


def on_quit(callback: Function):
    """Decorator for functions to call when the bot quits."""

    _quit_hooks.append(callback)
    return callback


@function
async def quit(interaction: discord.Interaction):
    for quit_hook in _quit_hooks:
        await quit_hook()
    await interaction.response.send_message(":koala:")
    await bot.close()


@bot.tree.command(
    name="quit",
    description="Stop running the bot.",
)
async def quit_discord(interaction: discord.Interaction):
    await quit(interaction)
