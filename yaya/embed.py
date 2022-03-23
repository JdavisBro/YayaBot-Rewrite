from datetime import datetime
from typing import Optional, Union

import discord

__all__ = (
    "Embed",
)

class Embed(discord.Embed):
    def __init__(self, guild: Union[int, discord.Guild], bot=None, emoji: Optional[Union[str, discord.Emoji, discord.PartialEmoji]]=None, default_footer: bool=True, footer_text: str=None, **kwargs):
        self.bot = bot
        
        if isinstance(guild, discord.Guild):
            guild = guild.id     
        # check for guild specific settings
        if not ("colour" in kwargs or "color" in kwargs):
            kwargs["colour"] = discord.Colour.blurple() # get guild default instead
        self.emojis = True
        timestamp = True

        if timestamp:
            kwargs["timestamp"] = datetime.utcnow()

        if "title" in kwargs and emoji and self.emojis:
            kwargs["title"] = f"{emoji} {kwargs['title']}"

        super().__init__(**kwargs)

        if default_footer:
            self.set_footer(footer_text=footer_text)

    def set_footer(self, *args, default_footer: bool=True, footer_text: str=None, **kwargs):
        """footer_text only does something with default_footer is used"""
        if default_footer:
            if self.bot:
                footer = self.bot.user.name
                url = self.bot.user.avatar.url
            else:
                footer = "YayaBot"
                url = None
            if footer_text:
                footer += f" - {footer_text}"
            super().set_footer(text=footer, icon_url=url)
        else:
            super().set_footer(*args, **kwargs)

    def add_field(self, name: str, value: str, emoji: Optional[Union[str, discord.Emoji, discord.PartialEmoji]]=None, inline=True):
        if self.emojis and emoji:
            name = f"{str(emoji)} {name}"
        return super().add_field(name=name, value=value, inline=inline)

    def insert_field_at(self, index: int, name: str, value: str, emoji: Optional[Union[str, discord.Emoji, discord.PartialEmoji]]=None, inline=True):
        if self.emojis and emoji:
            name = f"{str(emoji)} {name}"
        return super().insert_field_at(index, name=name, value=value, inline=inline)

    def set_field_at(self, index: int, name: str, value: str, emoji: Optional[Union[str, discord.Emoji, discord.PartialEmoji]]=None, inline=True):
        if self.emojis and emoji:
            name = f"{str(emoji)} {name}"
        return super().set_field_at(index, name=name, value=value, inline=inline)
