"""
Hideout v0.3

Support for private discord bot used with friends.

https://github.com/Qzphs/hideout
"""

__all__ = [
    "bot",
    "command",
    "event",
    "Message",
    "on_quit",
    "SlashCommand",
    "whitelist",
]


from hideout.bot import bot, event, Message, on_quit, SlashCommand

command = bot.tree.command
whitelist = bot.whitelist
