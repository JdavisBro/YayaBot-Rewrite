import logging
import typing
import os

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
        self.bot.previousReload = None
        self.connection = bot.connection
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

    @commands.group(aliases = ['c'], brief=":gear:")
    @commands.is_owner()
    async def cog(self, ctx):
        """Commands to add, reload and remove cogs."""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    async def check_loaded(self, cog):
        async with self.connection.execute("SELECT count(*) FROM extensions WHERE extension = ?", (cog,)) as cursor:
            inDb = await cursor.fetchone()
        print(inDb)
        inDb = inDb[0] == 1
        loaded = cog in self.bot.extensions.keys()
        return inDb, loaded

    @cog.command(aliases = ['l'], brief=":inbox_tray:")
    async def load(self, ctx, *cogs):
        """Loads a cog."""
        for cog in cogs:
            cog = f"cogs.{cog}"
            inDb, loaded = await self.check_loaded(cog)
            if (loaded and inDb):
                await ctx.send(f"Cog `{cog}` is already loaded.")
                return
            if not loaded:
                try:
                    await self.bot.load_extension(cog)
                except commands.ExtensionNotFound:
                    await ctx.send(f"Cog `{cog}` could not be found.")
                except:
                    await ctx.send(f"Loading cog `{cog}` failed")
                    raise
            if not inDb:
                await self.connection.execute("INSERT INTO extensions(extension) VALUES(?)", (cog,))
                await self.connection.commit()
            await ctx.send(f"Cog `{cog}` {'loaded' if (not loaded) else ''}{' and ' if (not loaded and not inDb) else ''}{'added to database' if (not inDb) else ''}.")

    @cog.command(aliases = ['u'], brief=":outbox_tray:")
    async def unload(self, ctx, *cogs):
        """Unloads a cog."""
        for cog in cogs:
            if cog == 'owner':
                await ctx.send("Cannot unload owner.")
                continue
            cog = f"cogs.{cog}"
            inDb, loaded = await self.check_loaded(cog)
            if not (loaded and inDb):
                await ctx.send(f"Cog `{cog}` is not loaded.")
                return
            if loaded:
                try:
                    await self.bot.unload_extension(cog)
                except:
                    await ctx.send(f"Unloading cog `{cog}` failed")
                    raise
            if inDb:
                await self.connection.execute("DELETE FROM extensions WHERE extension=?", (cog,))
                await self.connection.commit()
            await ctx.send(f"Cog `{cog}` {'unloaded' if loaded else ''}{' and ' if (loaded and inDb) else ''}{'removed from database' if inDb else ''}.")

    @cog.command(aliases = ['r'], brief=":arrows_counterclockwise:")
    async def reload(self,ctx,*cogs:typing.Optional[str]):
        """Reloads cogs."""
        allReloaded = False
        if not cogs:
            if self.bot.previousReload is None:
                await ctx.send("Please specify a cog!")
                return
            else:
                cogs = self.bot.previousReload
        if cogs[0] in ["*","all"]:
            cogs = list(self.bot.extensions.keys())
            allReloaded = True
        elif not cogs[0].startswith("cogs."):
            cogs = [f"cogs.{cog}" for cog in cogs]
        notLoaded = []
        loaded = []
        for cog in cogs:
            try:
                await self.bot.reload_extension(cog)
                loaded.append(cog)
            except commands.ExtensionNotLoaded:
                notLoaded.append(cog)
            except:
                await ctx.send(f"Error while reloading `{cog}`.")
                raise
        await ctx.send(f"{'Cog `'+'`, `'.join(loaded)+'` reloaded.' if loaded else ''}{(' Cog `'+'`, `'.join(notLoaded)+'` was not loaded so not reloaded.') if notLoaded else ''}")
        if allReloaded:
            self.bot.previousReload = ["*"]
        else:
            self.bot.previousReload = loaded

    @cog.command(name="list",aliases=["ls"], brief=":gear:")
    async def cogs_list(self,ctx):
        """Lists loaded and unloaded cogs."""
        loaded_cogs = ['.'.join(cog.split(".")[1:]) for cog in self.bot.loaded_extensions]
        unloaded_cogs = []
        visited = []
        for d, _, files in os.walk("cogs",followlinks=True):
            if os.path.realpath(d) in visited:
                logging.warning("There is infinite recursion in your cogs folder, there is a link to the cog folder or a parent folder of it, this limits the amount of folders we can search for cogs. To fix this remove the links.")
                break
            visited.append(os.path.realpath(d))
            for f in files:
                if d != "cogs":
                    f = d.replace("/",".")[5:] + "." + f
                if f[:-3] not in loaded_cogs and f.endswith(".py"):
                    unloaded_cogs.append("`"+f[:-3]+"`")

        embed = yaya.Embed(ctx.guild.id, bot=self.bot, title="Cogs.", emoji=":gear:")
        embed.add_field(name="Loaded Cogs:", value=", ".join(["`"+c+"`" for c in loaded_cogs])+".", emoji=":wrench:", inline=False)
        embed.add_field(name="Unloaded Cogs:", value=", ".join(unloaded_cogs)+".", emoji=":tools:", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="reload", brief=":arrows_counterclockwise:")
    @commands.is_owner()
    async def reload_alias(self,ctx,*cogs:typing.Optional[str]):
        """Reloads specified cog or previously reloaded cog."""
        command = self.bot.get_command("cog reload")
        await ctx.invoke(command,*cogs)
