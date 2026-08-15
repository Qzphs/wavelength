import argparse
import json
import os
from typing import Awaitable, Callable

import discord
from discord.ext import commands

FILENAME = "bot.json"

HELP_BOT_TOKEN = "https://support-dev.discord.com/hc/en-us/articles/6470840524311-Why-can-t-I-copy-my-bot-s-token"
HELP_COPY_ID = "https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID"


class _HideoutBot(commands.Bot):

    def __init__(self):
        super().__init__(intents=discord.Intents.all(), command_prefix=[])

        self.channel_id: int = 0
        self.__token: str = ""
        self.whitelist: list[int] = []

        if os.path.exists(FILENAME):
            self.load_from_file()
        else:
            self.reset_from_user_input()

    def load_from_file(self):
        with open(FILENAME) as file:
            config = json.load(file)
        self.channel_id: int = config["channel"]
        self.__token: str = config["token"]
        self.whitelist: list[int] = config["whitelist"]

    def reset_from_user_input(self):
        print(f"{FILENAME} not found - will write a new file instead")
        print()
        print(HELP_BOT_TOKEN)
        self.__token = input("(1/3) enter bot token: ").strip()
        print()
        print(HELP_COPY_ID)
        self.channel_id = int(input("(2/3) enter channel id: ").strip())
        self.whitelist = [int(input("(3/3) enter user id: ").strip())]
        print()

    def save_to_file(self):
        config = {
            "channel": self.channel_id,
            "token": self.__token,
            "whitelist": self.whitelist,
        }
        with open(FILENAME, "w") as file:
            json.dump(config, file)

    def run(self):
        super().run(self.__token)

    async def on_ready(self):
        await self._sync_if_needed()
        self.channel = await self.fetch_channel(self.channel_id)
        await self._on_ready_hook()

    async def _sync_if_needed(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-s", "--sync", action="store_true")
        args = vars(parser.parse_args())
        if args["sync"]:
            await self.tree.sync()

    async def _on_ready_hook(self):
        pass


bot = _HideoutBot()


def event(func: Callable[[], Awaitable[None]]):
    if func.__name__ == "on_ready":
        bot._on_ready_hook = func
    else:
        bot.event(func)


class _HideoutWhitelistError(Exception):
    pass


class _HideoutCommand:
    """
    Provide a uniform interface for responding to users.

    The bot could respond to either a normal message sent in a channel
    or a slash command. The callback function should instantiate a
    subclass and send messages through that instance.
    """

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        if exc_type == _HideoutWhitelistError:
            await self.respond(f"{exc_value}")
            return True
        if exc_type is not None:
            await self.respond(f"{exc_type.__name__}: {exc_value}")

    @property
    def channel(self) -> discord.TextChannel:
        raise NotImplementedError

    @property
    def user(self) -> discord.User:
        raise NotImplementedError

    async def respond(self, text: str):
        raise NotImplementedError

    async def require_whitelisted(self):
        """Check if user is whitelisted, else respond with error."""
        if self.user.id in bot.whitelist:
            return
        raise _HideoutWhitelistError(
            "You can't use commands. (Ask to be added to the whitelist?)"
        )


class Message(_HideoutCommand):
    """Interaction subclass for responding to normal messages."""

    def __init__(self, message: discord.Message):
        self.message = message

    @property
    def channel(self):
        return self.message.channel

    @property
    def user(self):
        return self.message.author

    async def respond(self, text: str):
        await self.message.channel.send(text)


class SlashCommand(_HideoutCommand):
    """Interaction subclass for responding to slash commands."""

    def __init__(self, interaction: discord.Interaction):
        self.interaction = interaction

    @property
    def user(self):
        return self.interaction.user

    async def respond(self, text: str):
        await self.interaction.response.send_message(text)


@bot.tree.command(
    name="whitelist",
    description="Add someone to whitelist.",
)
async def whitelist(interaction: discord.Interaction, user: discord.User):
    async with SlashCommand(interaction) as command:
        await command.require_whitelisted()
        if user.id in bot.whitelist:
            await command.respond(f"{user.display_name} is already whitelisted.")
            return
        bot.whitelist.append(user.id)
        await command.respond(f"Added {user.display_name} to whitelist.")


@bot.tree.command(
    name="unwhitelist",
    description="Remove someone from whitelist",
)
async def whitelist(interaction: discord.Interaction, user: discord.User):
    async with SlashCommand(interaction) as command:
        await command.require_whitelisted()
        if user.id not in bot.whitelist:
            await command.respond(f"{user.display_name} isn't whitelisted.")
            return
        bot.whitelist.remove(user.id)
        await command.respond(f"Removed {user.display_name} from whitelist.")


_quit_hooks: list[Callable[[], None]] = []


def on_quit(callback: Callable[[], None]):
    """Decorator for functions to call when the bot quits."""

    _quit_hooks.append(callback)
    return callback


@bot.tree.command(
    name="quit",
    description="Stop running the bot.",
)
async def quit(interaction: discord.Interaction):
    async with SlashCommand(interaction) as command:
        await command.require_whitelisted()
        for quit_hook in _quit_hooks:
            await quit_hook()
        bot.save_to_file()
        await command.respond(":koala:")
        await bot.close()
