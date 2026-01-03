# cogs/admin.py
import discord
from discord.ext import commands
from database import is_admin, add_admin, set_balance, get_balance, wipe_user, restore_user
from config import OWNER_ID

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        if ctx.author.id == OWNER_ID:
            return True
        if await is_admin(ctx.author.id):
            return True
        return False

    @commands.command()
    async def addadmin(self, ctx, user: discord.User):
        await add_admin(user.id)
        await ctx.send(f"{user.mention} is now an admin.", delete_after=10)

    @commands.command()
    async def setmoney(self, ctx, user: discord.User, amount: int):
        await set_balance(user.id, amount)
        bal = await get_balance(user.id)
        await ctx.send(f"Set {user.mention}'s balance to **{bal}**", delete_after=10)

    @commands.command()
    async def clear(self, ctx, user: discord.User):
        await wipe_user(user.id)
        await ctx.send(f"Wiped {user.mention}'s progress.", delete_after=10)

    @commands.command()
    async def back(self, ctx, user: discord.User):
        await restore_user(user.id)
        await ctx.send(f"Restored {user.mention}'s data.", delete_after=10)

async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))
