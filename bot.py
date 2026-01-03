# bot.py
import discord
from discord.ext import commands, tasks
from discord.app_commands import AppCommandError
from config import BOT_TOKEN, OWNER_ID
from database import init_db
import os
import aiosqlite
import sys

class EconomyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=';',
            intents=discord.Intents.all(),
            application_id=1234567890123456789  # Replace with your bot's application ID
        )
        self.owner_id = OWNER_ID

    async def setup_hook(self):
        await init_db()
        for file in os.listdir("cogs"):
            if file.endswith(".py"):
                await self.load_extension(f"cogs.{file[:-3]}")
        self.check_price_updates.start()

    async def on_ready(self):
        print(f'Logged in as {self.user}')

    async def on_command_error(self, ctx, error: AppCommandError):
        if isinstance(error, commands.NotOwner):
            return
        await ctx.send(str(error), delete_after=10)

    @tasks.loop(minutes=5)
    async def check_price_updates(self):
        # Implement stock price fluctuations
        pass


bot = EconomyBot()
bot.run(BOT_TOKEN)
