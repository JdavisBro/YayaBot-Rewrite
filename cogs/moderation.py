import logging
import datetime

import discord
from discord.ext import commands

import yaya

logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s', level=logging.INFO)

async def setup(bot):
    await bot.add_cog(Moderation(bot))

class Moderation(commands.Cog):
    """Cog for moderation!"""

    def __init__(self, bot):
        self.bot = bot
        self.connection = bot.connection
        self.emoji = "🔧"

    async def cog_load(self):
        pass # do async stuff here like start tasks

    async def get_purge_messages(self, channel, limit, check=None):
        messages = []
        now = datetime.datetime.utcnow()
        async for message in channel.history(limit=limit):
            if now - message.created_at.replace(tzinfo=None) > datetime.timedelta(days=14):
                break # Older than 14 days
            if not check or check(message):
                messages.append(message)
        return messages

    @commands.group(help="Purge messages.", brief=":x:") # TODO?: alternate purge command that doesn't bulk delete and so can delete messages from 14+ days ago
    #@yaya.checks.is_mod()
    async def purge(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @purge.command(name="number", aliases=["n","num"], brief=":1234:", help="Purges the specified amount of messages from the chat")
    async def purge_number(self, ctx, number: int):
        messages = await self.get_purge_messages(ctx.channel, number+1)
        await ctx.channel.delete_messages(messages, reason=f"Purge by {ctx.author} ({ctx.author.id})")
        await ctx.send(f"✅ Purged {len(messages)-1} messages!", delete_after=2)

    @purge.command(name="match", aliases=["m"], brief=":abcd:", help="Out of the last `limit` messages, deletes those that contain `filtered`.")
    async def purge_match(self, ctx, limit: int, *, filtered):
        await ctx.message.delete() # Delete invoking message
        def check(message):
            return filtered in message.content
        messages = await self.get_purge_messages(ctx.channel, limit, check=check)
        await ctx.channel.delete_messages(messages, reason=f"Purge by {ctx.author} ({ctx.author.id})")
        await ctx.send(f"✅ Purged {len(messages)} messages!", delete_after=2)

    @purge.command(name="commands", aliases=["c","command"], brief=":robot:", help="Out of the last `limit` messages, deletes messages by the bot and messages starting with the bot prefix")
    async def purge_commands(self, ctx, limit: int):
        await ctx.message.delete() # Delete invoking message
        def check(message):
            return message.author == ctx.me or message.content.startswith(ctx.prefix)
        messages = await self.get_purge_messages(ctx.channel, limit, check=check)
        await ctx.channel.delete_messages(messages, reason=f"Purge by {ctx.author} ({ctx.author.id})")
        await ctx.send(f"✅ Purged {len(messages)} messages!", delete_after=2)

    @commands.command(help="Bans the specified `member` for `reason`", brief=":hammer:")
    #@yaya.checks.is_mod()
    @commands.has_guild_permissions(ban_members=True) # temporary so randoms don't ban people in the test server lol.
    async def ban(self, ctx, member: discord.Member, delete_message_days=0, *, reason="No reason specified"):
        if not ctx.guild.me.guild_permissions.ban_members:
            await ctx.send("I don't have permission to ban people.")
            return
        elif ctx.guild.me.top_role <= member.top_role:
            await ctx.send("I don't have permission to ban that member.")
            return
        # TODO: default ban message per guild
        userEmbed = yaya.Embed(ctx.guild, bot=self.bot, emoji=":no_entry_sign:", title=f"You have been banned from {ctx.guild.name}", colour=0xff0000)
        userEmbed.add_field(name="Ban reason: ", value=reason)

        try:
            await member.send(embed=userEmbed)
            desc = None
        except discord.errors.HTTPException:
            desc = "Failed to send a message to the user."

        if delete_message_days < 0:
            delete_message_days = 0
        elif delete_message_days > 7:
            delete_message_days = 7

        await ctx.guild.ban(member, reason=reason, delete_message_days=delete_message_days)

        channelEmbed = yaya.Embed(ctx.guild, bot=self.bot, emoji=":hammer:", title=f"Banned {str(member)}", colour=0x00ff00, description=desc)
        await ctx.send(embed=channelEmbed)

        #await yaya.log(self.bot, ctx.guild, ctx.author, member, "ban", reason, datetime.datetime.now())
