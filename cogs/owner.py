import logging

import discord
from discord.ext import commands

import yaya

logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s', level=logging.INFO)

async def setup(bot):
    await bot.add_cog(Owner(bot))

class Owner(commands.Cog):
    """Cog with utilities for the bot owner!"""

    def __init__(self, bot):
        self.bot = bot
        self.emoji = "👑"

    async def cog_load(self):
        pass # do async stuff here like start tasks

    @commands.command(brief=":sleeping:")
    @commands.is_owner()
    async def shutdown(self, ctx):
        """Shuts the bot down!"""
        await ctx.send("👋 Goodbye")
        await self.bot.close()

    @commands.command(brief=":arrows_counterclockwise:")
    @commands.is_owner()
    async def restart(self, ctx):
        """Restarts the bot! Currently does not reload bot.py"""
        await ctx.send("🏃‍♂️ Be right back!")
        await self.bot.restart()

    @commands.command(brief=":muscle:")
    async def embed_test(self, ctx):
        embed = yaya.Embed(ctx.guild.id, bot=self.bot, title="Test.", emoji=":gear:")
        embed.add_field(name="Status:", value="*beatboxing wildly*", emoji=":wrench:")
        embed.add_field(name="Boxes:", value="eaten", emoji=":tools:")
        await ctx.send(embed=embed)
