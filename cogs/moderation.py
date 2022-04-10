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
        now = discord.utils.utcnow()
        async for message in channel.history(limit=limit):
            if now - message.created_at > datetime.timedelta(days=14):
                break # Older than 14 days
            if not check or check(message):
                messages.append(message)
        return messages

    @commands.group(help="Purge messages.", brief=":x:") # TODO?: alternate purge command that doesn't bulk delete and so can delete messages from 14+ days ago
    #@yaya.checks.is_mod()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @purge.command(name="number", aliases=["n","num"], brief=":1234:", help="Purges the specified amount of messages from the chat")
    async def purge_number(self, ctx, number: int):
        messages = await self.get_purge_messages(ctx.channel, number+1)
        await ctx.channel.delete_messages(messages, reason=f"Purge by {ctx.author} ({ctx.author.id})")
        await ctx.send(f"✅ Purged {len(messages)-1} messages!", delete_after=2)
        await yaya.log_message(
            self.bot, ctx.guild, "purge", moderator=ctx.author,
            extra=f":notepad_spiral: Purged: {number} messages\n:fire: Messages Deleted: {len(messages)-1}\n",
            extraEmojiless=f"Purged: {number} messages\nMessages Deleted: {len(messages)-1}\n"
        )

    @purge.command(name="match", aliases=["m"], brief=":abcd:", help="Out of the last `limit` messages, deletes those that contain `filtered`.")
    async def purge_match(self, ctx, limit: int, *, filtered):
        await ctx.message.delete() # Delete invoking message
        def check(message):
            return filtered in message.content
        messages = await self.get_purge_messages(ctx.channel, limit, check=check)
        await ctx.channel.delete_messages(messages, reason=f"Purge by {ctx.author} ({ctx.author.id})")
        await ctx.send(f"✅ Purged {len(messages)} messages!", delete_after=2)
        await yaya.log_message(
            self.bot, ctx.guild, "purge", moderator=ctx.author,
            extra=f":notepad_spiral: Purged: Matches `{filtered}`\n:fire: Messages Deleted: {len(messages)}\n",
            extraEmojiless=f"Purged: Matches `{filtered}`\nMessages Deleted: {len(messages)}\n"
        )

    @purge.command(name="commands", aliases=["c","command"], brief=":robot:", help="Out of the last `limit` messages, deletes messages by the bot and messages starting with the bot prefix")
    async def purge_commands(self, ctx, limit: int):
        await ctx.message.delete() # Delete invoking message
        def check(message):
            return message.author == ctx.me or message.content.startswith(ctx.prefix)
        messages = await self.get_purge_messages(ctx.channel, limit, check=check)
        await ctx.channel.delete_messages(messages, reason=f"Purge by {ctx.author} ({ctx.author.id})")
        await ctx.send(f"✅ Purged {len(messages)} messages!", delete_after=2)
        await yaya.log_message(
            self.bot, ctx.guild, "purge", moderator=ctx.author,
            extra=f":notepad_spiral: Purged: Bot Commands\n:fire: Messages Deleted: {len(messages)}\n",
            extraEmojiless=f"Purged: Bot Commands\nMessages Deleted: {len(messages)}\n"
        )

    @commands.command(help="Bans the specified `member` for `reason` and deletes `delete message days` worth of messages (between 0 and 7)", brief=":hammer:")
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

        await yaya.log(self.bot, ctx.guild, ctx.author, member, "ban", reason, datetime.datetime.now())

    @commands.command(help="Unbans the user `userid`", brief=":key:")
    #@yaya.checks.is_mod()
    @commands.has_guild_permissions(ban_members=True)
    async def unban(self, ctx, userid: int, reason="No reason specified"):
        if not ctx.guild.me.guild_permissions.ban_members:
            await ctx.send("I don't have permission to unban people.")

        try:
            user = await ctx.guild.fetch_ban(discord.Object(userid))
            user = user.user
        except discord.NotFound:
            notBannedEmbed = yaya.Embed(ctx.guild, bot=self.bot, emoji=":x:", title="This user is not banned.")
            await ctx.send(embed=notBannedEmbed)
            return

        await ctx.guild.unban(user, reason=reason)

        channelEmbed = yaya.Embed(ctx.guild, bot=self.bot, emoji=":white_check_mark:", title=f"Unbanned {str(user)}", colour=0x00ff00)
        await ctx.send(embed=channelEmbed)

        await yaya.log(self.bot, ctx.guild, ctx.author, user, "unban", reason, datetime.datetime.now())

    @commands.command(help="Kicks the specified `member` for `reason`", brief=":boot:")
    #@yaya.checks.is_mod()
    @commands.has_guild_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="No reason specified"):
        if not ctx.guild.me.guild_permissions.kick_members:
            await ctx.send("I don't have permission to kick people.")
            return
        elif ctx.guild.me.top_role <= member.top_role:
            await ctx.send("I don't have permission to kick that person.")
            return

        userEmbed = yaya.Embed(ctx.guild, bot=self.bot, emoji=":boot:", title=f"You have been kicked from {ctx.guild.name}", colour=0xff0000)
        userEmbed.add_field(name="Kick reason:", value=reason)

        try:
            await member.send(embed=userEmbed)
            desc = None
        except discord.errors.HTTPException:
            desc = "Failed to send a message to the user."

        await ctx.guild.kick(member, reason=reason)

        channelEmbed = yaya.Embed(ctx.guild, bot=self.bot, emoji=":boot:", title=f"Kicked {str(member)}", colour=0x00ff00, description=desc)
        await ctx.send(embed=channelEmbed)

        await yaya.log(self.bot, ctx.guild, ctx.author, member, "kick", reason, datetime.datetime.now())

    @commands.command(help="Softbans (bans then unbans to delete messages) the specified `member` for `reason`", brief=":wastebasket:")
    #@yaya.checks.is_mod()
    @commands.has_guild_permissions(ban_members=True)
    async def softban(self, ctx, member: discord.Member, *, reason="No reason specified"):
        if not ctx.guild.me.guild_permissions.ban_members:
            await ctx.send("I don't have permission to ban people.")
            return
        elif ctx.guild.me.top_role <= member.top_role:
            await ctx.send("I don't have permission to ban that person.")
            return

        userEmbed = yaya.Embed(ctx.guild, bot=self.bot, emoji=":boot:", title=f"You have been softbanned (kicked) from {ctx.guild.name}", colour=0xff0000)
        userEmbed.add_field(name="Softban reason:", value=reason)

        try:
            await member.send(embed=userEmbed)
            desc = None
        except discord.errors.HTTPException:
            desc = "Failed to send a message to the user."

        await ctx.guild.ban(member, reason=reason)
        await ctx.guild.unban(member, reason="Softban unban.")

        channelEmbed = yaya.Embed(ctx.guild, bot=self.bot, emoji=":boot:", title=f"Softbanned {str(member)}", colour=0x00ff00, description=desc)
        await ctx.send(embed=channelEmbed)

        await yaya.log(self.bot, ctx.guild, ctx.author, member, "softban", reason, datetime.datetime.now())

    @commands.command(help="Get modlogs for a specific `member`, and goes to `page number`.s", brief=":file_folder:")
    #@yaya.checks.is_mod()
    async def modlogs(self, ctx, member: discord.Member, page_number: int=1):
        async with ctx.channel.typing():
            async with await self.connection.execute("SELECT * FROM caselog WHERE user=? AND guild=?", (member.id, ctx.guild.id)) as cursor:
                logs = await cursor.fetchall()

            if not logs:
                await ctx.send("❎ That user does not have any modlogs!")

            def new_embed():
                return yaya.Embed(ctx.guild, self.bot, emoji=":open_file_folder:", title=f"{str(member)}'s Modlogs")

            embeds = []
            embed = new_embed()

            for log in logs:
                mod = await self.bot.fetch_user(log[7])
                start = yaya.time.DiscordTimestamp(log[5])
                if log[6] != -1:
                    end = yaya.time.DiscordTimestamp(log[6])
                else:
                    end = False
                if len(embed.fields) >= 6:
                    embeds.append(embed)
                    embed = new_embed()
                embed.add_field(
                    emoji=":notepad_spiral:", name=f"***Case {str(log[1])}***", inline=False,
                    value=(
                        ((":page_facing_up:" if embed.emojis else '') + f"**Type:** {log[3]}\n") +
                        ((":pencil2:" if embed.emojis else '') + f"**Reason:** {log[4]}\n") +
                        ((":cop:" if embed.emojis else '') + f"**Moderator:** {str(mod)}\n") +
                        ((":clock3:" if embed.emojis else '') + f"**Time:** {start.relative} ({start.date_time_full})\n") +
                        ((":stopwatch:" if embed.emojis else '') + f"**Ends:** {end.relative} ({end.date_time_full}" if end else '')
                    ).rstrip()
                )

            embeds.append(embed)
        
        if len(embeds) > 1:
            await yaya.send_paged(ctx, embeds, ctx.author, page_number-1, expire=120)
        else:
            await ctx.send(embed=embed)

    @commands.command(help="Gets info on a specific `caseid`", brief=":briefcase:")
    #@yaya.checks.is_mod()
    async def case(self, ctx, caseid: int):
        if caseid < 1:
            await ctx.send("That is not a valid case id.")

        case: yaya.ModLog = await yaya.get_log(self.bot, ctx.guild, caseid)

        if not case:
            await ctx.send("There isn't a case with that id.")
            return
        
        embed = yaya.Embed(ctx.guild, self.bot, emoji=":notepad_spiral:", title=f"Case {str(caseid)}")
        
        if isinstance(case.user, discord.Object):
            case.user = await self.bot.fetch_user(case.user.id)
        if isinstance(case.moderator, discord.Object):
            case.moderator = await self.bot.fetch_user(case.moderator.id)
        startTimestamp = yaya.time.DiscordTimestamp(case.start)
        
        embed.add_field(name="User:", value=str(case.user), emoji=":child:")
        embed.add_field(name="Type:", value=case.type, emoji=":page_facing_up:")
        embed.add_field(name="Time:", value=f"{startTimestamp.relative} ({startTimestamp.date_time_full})", emoji=":clock3:", inline=False)
        if case.end:
            endTimestamp = yaya.time.DiscordTimestamp(case.end)
            embed.add_field(name="Ends:", value=f"{endTimestamp.relative} ({endTimestamp.date_time_full})", emoji=":stopwatch:", inline=False)
        embed.add_field(name="Reason:", value=case.reason, emoji=":pencil2:")
        embed.add_field(name="Moderator:", value=str(case.moderator), emoji=":cop:")
        embed.set_thumbnail(url=case.user.avatar.url)

        await ctx.send(embed=embed)
