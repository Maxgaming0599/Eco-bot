# cogs/auction.py
import discord
from discord.ext import commands
from database import get_balance, update_balance
import aiosqlite

class AuctionHouse(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ah(self, ctx, action: str, *, args: str):
        pass

async def setup(bot: commands.Bot):
    await bot.add_cog(AuctionHouse(bot))
