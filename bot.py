import os
import time
import datetime
import platform

import logging
import discord
from discord.ext import commands

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
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True # 0_0
        self.loaded_extensions = []
        self._restart = False
        super().__init__(command_prefix=self.get_prefix, intents=intents, help_command=yaya.HelpCommand())

    async def get_prefix(self, message):
        return "-"

    async def load_extension(self, name):
        await super().load_extension(name)
        self.loaded_extensions.append(name)
        logging.info(f"{name} loaded.")

    async def sql_init(self):
        pass

    async def load_extensions(self):
        default_extensions = [ # They are tuples for SQL
            ("cogs.owner",)
        ]
        # get extensions from sql
        for ex in default_extensions:
            try:
                await self.load_extension(ex[0])
            except commands.ExtensionNotFound:
                logging.info(f"{ex[0]} couldn't be found.")

    async def setup_hook(self):
        await self.sql_init()
        await self.load_extensions()
        self.startTime = time.time()

    async def on_ready(self):
        logging.info("Connected!")

    async def on_command_error(self, ctx, error):
        raise error

    async def close(self):
        # close sql here
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
