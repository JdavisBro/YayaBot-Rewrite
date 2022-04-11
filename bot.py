import os
import time
import datetime
import platform

import logging
import discord
from discord.ext import commands
import aiosqlite

import yaya

logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s', level=logging.INFO)

def no_token():
    logging.error("Token could not be found, it must be the first line of `TOKEN.txt`.")
    exit()

def get_token():
    if os.path.exists("TOKEN.txt"):
        with open("TOKEN.txt","r") as f:
            token = f.readline().strip()
    else:
        no_token()

    if not token:
        no_token()

    return token

class YayaBot(commands.Bot):
    connection: aiosqlite.Connection

    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True # 0_0
        self._restart = False
        super().__init__(command_prefix=self.get_prefix, intents=intents, help_command=yaya.HelpCommand())

    async def get_prefix(self, message):
        return "-"

    async def load_extension(self, name):
        await super().load_extension(name)
        logging.info(f"COG: {name} loaded.")

    async def reload_extension(self, name):
        await super().reload_extension(name)
        logging.info(f"COG: {name} reloaded.")

    async def unload_extension(self, name):
        await super().unload_extension(name)
        logging.info(f"COG: {name} unloaded.")

    async def sql_init(self):
        self.connection = await aiosqlite.connect("database.db")
        await self.connection.execute("CREATE TABLE IF NOT EXISTS extensions (extension TEXT PRIMARY KEY)")
        await self.connection.execute("CREATE TABLE IF NOT EXISTS caselog (guild INTEGETER, id INTEGER, user INTEGER, type TEXT, reason TEXT, start FLOAT, end FLOAT, moderator INTEGER)")
        await self.connection.commit()

    async def load_extensions(self):
        default_extensions = [ # They are tuples for SQL
            ("cogs.owner",),
            ("cogs.moderation",)
        ]
        async with self.connection.execute("SELECT * FROM extensions") as cursor:
            extensions = await cursor.fetchall()
            if not extensions:
                await cursor.executemany("INSERT INTO extensions(extension) VALUES (?)", default_extensions)
                extensions = default_extensions
        await self.connection.commit()
        for ex in extensions:
            try:
                await self.load_extension(ex[0])
            except commands.ExtensionNotFound:
                logging.info(f"{ex[0]} couldn't be found.")

    async def setup_hook(self):
        await self.sql_init()
        await self.load_extensions()

    async def on_ready(self):
        self.startTime = time.time()
        appinfo = await bot.application_info()
        self.owner = appinfo.owner
        logging.info("Connected!")

    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, 'on_error'):
            return
        error = getattr(error, 'original', error)

        if isinstance(error, commands.CommandNotFound): # Perhaps make these toggleable by guild settings
            await ctx.message.add_reaction("❓")
        elif isinstance(error, commands.CheckFailure):
            await ctx.message.add_reaction("🚫")

        elif isinstance(error, commands.BadUnionArgument):
            typeText = {discord.Member: "User",discord.User: "User",discord.Role: "Role",discord.TextChannel: "Channel"}
            types = []
            userInput = ""
            for i, v in enumerate(error.converters):
                if not userInput:
                    userInput = getattr(error.errors[i],"argument","")
                if v in typeText:
                    types.append(typeText[v])
            await ctx.send(f"{', '.join(types)} `{userInput}` could not be found.")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send(f"User `{error.argument}` could not be found")
        elif isinstance(error, commands.RoleNotFound):
            await ctx.send(f"Role `{error.argument}` could not be found")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("The value for agument `"+str(error)[str(error).rfind('r "')+3:-2]+"` is incorrect, you may have put letters in a number.")

        elif isinstance(error, commands.MissingRequiredArgument):
            commandUsageLine = f"{ctx.prefix}{ctx.command.qualified_name} {ctx.command.signature}"
            paramLocation = commandUsageLine.index("<" + error.param.name + ">")
            paramLength = len(error.param.name) + 2
            await ctx.send(f"```{commandUsageLine}\n{' '*paramLocation}{'^'*paramLength}\n{str(error)}```")

        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to run that command.")
        elif isinstance(error, discord.errors.Forbidden):
            await ctx.send("Something went wrong, I may be missing a permission.")

        elif isinstance(error, commands.ExpectedClosingQuoteError):
            await ctx.send("Your command aguments are inputted incorrectly. You are missing a closing `\"`")

        else:
            await ctx.send("Something has gone wrong somewhere!" if bot.owner != ctx.author else "An Error Occured! " + str(error))
            raise error

    async def close(self):
        await self.connection.close()
        await super().close()

    async def restart(self):
        self._restart = True
        await self.close()

@commands.command(aliases=["info","bot"], brief=":green_book: " )
async def about(ctx):
    """Sends some information about the bot!"""
    currentTime = time.time()
    uptime = int(round(currentTime - bot.startTime))
    uptime = str(datetime.timedelta(seconds=uptime))
    appinfo = await bot.application_info()

    embed = yaya.Embed(ctx.guild.id, bot=bot, description="Yayabot!")
    embed.set_author(name="YayaBot (Rewrite)", url="https://github.com/JdavisBro/YayaBot-Rewrite/", icon_url=bot.user.avatar.url)

    embed.add_field(name="Instance Owner:", value=appinfo.owner, emoji=":slight_smile:", inline=True)
    embed.add_field(name="_ _", value="_ _", inline=True)
    embed.add_field(name="Python Version:", value=f"[{platform.python_version()}](https://www.python.org)", emoji=":snake:", inline=True)

    embed.add_field(name="Bot Uptime:", value=f"{uptime}", emoji=":stopwatch:", inline=True)
    embed.add_field(name="_ _", value="_ _", inline=True)
    embed.add_field(name="Discord.py Version:", value=f"[{discord.__version__}](https://github.com/Rapptz/discord.py)", emoji=":desktop:", inline=True)

    await ctx.send(embed=embed)

while True:
    token = get_token()
    bot = YayaBot()
    bot.add_command(about)
    bot.run(token)
    if bot._restart:
        logging.info("Restarting in 3 seconds...")
        time.sleep(3)
    else:
        logging.info("Closing!")
        break