import os
import time

import logging
import discord
from discord.ext import commands

import yaya

logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s', level=logging.INFO)

TOKEN = None

def no_token():
    print("Token could not be found, it must be the first line of `TOKEN.txt`.")
    exit()

def get_token():
    if os.path.exists("TOKEN.txt"):
        with open("TOKEN.txt","r") as f:
            TOKEN = f.readline().strip()
    else:
        no_token()

    if not TOKEN:
        no_token()

    return TOKEN

class YayaBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True # 0_0
        self.loaded_extensions = []
        self._restart = False
        print(yaya.HelpCommand)
        super().__init__(command_prefix=self.get_prefix,intents=intents,help_command=yaya.HelpCommand())

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

while True:
    TOKEN = get_token()
    bot = YayaBot()
    bot.run(TOKEN)
    if bot._restart:
        logging.info("Restarting in 3 seconds...")
        time.sleep(3)
    else:
        logging.info("Closing!")
        break
