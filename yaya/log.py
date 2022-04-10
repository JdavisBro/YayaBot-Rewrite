import time
import datetime
from typing import Union, Optional

import discord
from discord.ext import commands

from . import embed as yayaembed
from . import timehelpers

__all__ = (
    "log_message",
    "log",
    "get_log",
    "ModLog"
)

logText = {
    "ban": {
        "emoji": ":hammer:",
        "text": "User Banned: "
    },
    "unban": {
        "emoji": ":x:",
        "text": "User Unbanned: "
    },
    "softban": {
        "emoji": ":boot:",
        "text": "User Softbanned: "
    },
    "kick": {
        "emoji": ":boot:",
        "text": "User Kicked: "
    },
    "mute": {
        "emoji": ":mute:",
        "text": "User Muted: "
    },
    "gravel": {
        "emoji": ":mute:",
        "text": "User Gravelled: "
    },
    "warn": {
        "emoji": ":exclamation:",
        "text": "User Warned: "
    },
    "unmute": {
        "emoji": ":sound:",
        "text": "User Unmuted: "
    },
    "ungravel": {
        "emoji": ":sound:",
        "text": "User Ungravelled: "
    },
    "purge": {
        "emoji": ":wastebasket:",
        "text": "Purged Messages"
    }
}

async def log_message(bot: commands.Bot, guild: discord.Guild, type: str, user: Optional[discord.Member]=None, id: Optional[int]=None, moderator: Optional[discord.Member]=None, reason: Optional[str]=None, extra: Optional[str]=None, extraEmojiless: Optional[str]=None, end: Union[datetime.datetime, datetime.timedelta, int]=-1):
    logchannel = bot.get_channel(817534444415221820) # get actual log channel here in future
    if not logchannel:
        return
    embed = yayaembed.Embed(guild, bot, emoji=logText[type]["emoji"], title=logText[type]["text"]+(str(user) if user else ''))
    embed.description = ""
    if id:
        embed.description += f":notepad_spiral: Case ID: {id}\n" if embed.emojis else f"Case ID: {id}\n"
    if moderator:
        embed.description += f":cop: Moderator: {str(moderator)}\n" if embed.emojis else f"Moderator: {str(moderator)}\n"
    if reason:
        embed.description += f":scroll: Reason: {reason}\n" if embed.emojis else f"Reason: {reason}\n"
    if extra:
        assert extraEmojiless
        embed.description += extra if embed.emojis else extraEmojiless
    if end != -1:
        endTimestamp = timehelpers.DiscordTimestamp(end)
        embed.description += f"\n{':stopwatch: ' if embed.emojis else ''}Ends: {endTimestamp.relative} ({endTimestamp.date_time_full})"
    embed.description = embed.description.rstrip()
    if user:
        embed.set_thumbnail(url=user.avatar.url)
    await logchannel.send(embed=embed)


async def log(bot: commands.Bot, guild: discord.Guild, moderator: discord.Member, user: Union[discord.Member, discord.User], type: str, reason: str, start: Union[datetime.datetime, datetime.timedelta, int], end: Union[datetime.datetime, datetime.timedelta, int]=-1):
    id = 1
    async with bot.connection.execute("SELECT id FROM caselog WHERE guild=? ORDER BY id DESC LIMIT 1", (guild.id,)) as cursor:
        caseN = await cursor.fetchone()
        if caseN:
            id += caseN[0]
        if end != -1: # For cases that should expire, any shorter cases of the same type should be updated.
            cursor.execute("SELET id FROM caselog WHERE guild=? AND user=? AND type=? AND end >=? AND end <=?", (guild.id, user.id, type, time.time(), expires))
            oldCases = cursor.fetchall()
            for case in oldCases:
                await cursor.execute("UPDATE caselog SET expire=? WHERE id=? AND guild=?", (time.time(), case[0], guild.id))
        await cursor.execute("INSERT INTO caselog(guild, id, user, type, reason, start, end, moderator) VALUES (?,?,?,?,?,?,?,?)", (guild.id, id, user.id, type, reason, start.timestamp(), end.timestamp() if end != -1 else -1, moderator.id))
    await bot.connection.commit()
    await log_message(bot, guild, type, user, id, moderator, reason, end=end)

async def get_log(bot: commands.Bot, guild: discord.Guild, id: int):
    async with bot.connection.execute("SELECT * FROM caselog WHERE guild=? AND id=?", (guild.id, id)) as cursor:
        logdata = await cursor.fetchone()
    return ModLog(bot, guild, id, logdata[7], logdata[2], logdata[3], logdata[4], logdata[5], logdata[6])

class ModLog():
    def __init__(self, bot, guild, id, moderator, user, type, reason, start, end=None):
        self.guild: Union[discord.Guild, discord.Object] = guild if isinstance(guild,discord.Guild) else bot.get_guild(guild) or discord.Object(guild)
        self.id: int = id
        self.moderator: Union[discord.Member, discord.User, discord.Object] = self.guild.get_member(moderator) or bot.get_user(moderator) or discord.Object(member)
        self.user: Union[discord.Member, discord.User, discord.Object] = self.guild.get_member(user) or bot.get_user(user) or discord.Object(user)
        self.type: str = type
        self.reason: str = reason
        self.start: datetime.datetime = datetime.datetime.fromtimestamp(start)
        self.end: Optional[datetime.datetime] = None if end == -1 else datetime.datetime.fromtimestamp(end)

    def __repr__(self):
        return f"<ModLog guild.id={self.guild.id} moderator.id={self.moderator.id} user.id={self.user.id} type={repr(self.type)} reason={repr(self.reason)} start={self.start.timestamp()} end={self.end.timestamp() if self.end else 'None'}>"