
import discord
from discord.ext import commands

import logging

logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s', level=logging.INFO)

async def setup(bot):
    await bot.add_cog(Cheese(bot))

class Cheese(commands.Cog):
    """Cheese cog for testing help command!"""

    def __init__(self, bot):
        self.bot = bot
        self.emoji = ":cheese:"

    async def cog_load(self):
        pass # do async stuff here like start tasks

    @commands.command(brief=":cheese:")
    async def cheese(self, ctx):
        """cheese!"""
        pass
    @commands.command(brief=":cheese:")
    async def cheese2(self, ctx):
        """cheese!"""
        pass
    @commands.command(brief=":cheese:")
    async def cheese3(self, ctx):
        """cheese!"""
        pass
    @commands.command(brief=":cheese:")
    async def cheese4(self, ctx):
        """cheese!"""
        pass
    @commands.command(brief=":cheese:")
    async def cheese5(self, ctx):
        """cheese!"""
        pass
    @commands.command(brief=":cheese:")
    async def cheese6(self, ctx):
        """cheese!"""
        pass
    @commands.command(brief=":cheese:")
    async def cheese7(self, ctx):
        """cheese!"""
        pass
    @commands.command(brief=":cheese:")
    async def cheese8(self, ctx):
        """cheese!"""
        pass
    @commands.command(brief=":cheese:")
    async def cheese9(self, ctx):
        """cheese!"""
        pass
    @commands.command(brief=":cheese:")
    async def cheeseq(self, ctx):
        """cheese!"""
        pass
    @commands.command(brief=":cheese:")
    async def cheesew(self, ctx):
        """cheese!"""
        pass
    @commands.command(brief=":cheese:")
    async def cheesee(self, ctx):
        """cheese!"""
        pass
    @commands.command(brief=":cheese:")
    async def cheeser(self, ctx):
        """cheese!"""
        pass
    @commands.command(brief=":cheese:")
    async def cheeset(self, ctx):
        """cheese!"""
        pass
    @commands.command(brief=":cheese:")
    async def cheesey(self, ctx):
        """cheese!"""
        pass
    @commands.command(brief=":cheese:")
    async def cheeseu(self, ctx):
        """cheese!"""
        pass
    @commands.command(brief=":cheese:")
    async def cheesei(self, ctx):
        """cheese!"""
        pass
    @commands.command(brief=":cheese:")
    async def cheeseo(self, ctx):
        """cheese!"""
        pass
    @commands.command(brief=":cheese:")
    async def cheesep(self, ctx):
        """cheese!"""
        pass
    @commands.command(brief=":cheese:")
    async def cheesea(self, ctx):
        """cheese!"""
        pass
    @commands.command(brief=":cheese:")
    async def cheeses(self, ctx):
        """cheese!"""
        pass
    @commands.command(brief=":cheese:")
    async def cheesed(self, ctx):
        """cheese!"""
        pass
    @commands.command(brief=":cheese:")
    async def cheesef(self, ctx):
        """cheese!"""
        pass
    @commands.command(brief=":cheese:")
    async def cheeseg(self, ctx):
        """cheese!"""
        pass

