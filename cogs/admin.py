# cogs/admin.py
import discord
from discord.ext import commands
from database import (
    is_admin, add_admin, remove_admin, set_balance, get_balance, 
    wipe_user, restore_user, update_balance, get_user_limit, set_user_limit,
    get_ore_inventory, update_ore_inventory, user_has_stock, add_user_stock
)
from config import OWNER_ID
import aiosqlite

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
    async def removeadmin(self, ctx, user: discord.User):
        await remove_admin(user.id)
        await ctx.send(f"{user.mention} is no longer an admin.", delete_after=10)

    @commands.command()
    async def addmoney(self, ctx, user: discord.User, amount: int):
        await update_balance(user.id, amount)
        bal = await get_balance(user.id)
        await ctx.send(f"Added {amount:,} to {user.mention}. New balance: {bal:,}", delete_after=10)

    @commands.command()
    async def removemoney(self, ctx, user: discord.User, amount: int):
        await update_balance(user.id, -amount)
        bal = await get_balance(user.id)
        await ctx.send(f"Removed {amount:,} from {user.mention}. New balance: {bal:,}", delete_after=10)

    @commands.command()
    async def setmoney(self, ctx, user: discord.User, amount: int):
        await set_balance(user.id, amount)
        await ctx.send(f"Set {user.mention}'s balance to {amount:,}", delete_after=10)

    @commands.command()
    async def setlimit(self, ctx, user: discord.User, amount: int):
        await set_user_limit(user.id, amount)
        await ctx.send(f"Set limit for {user.mention} to {amount:,}", delete_after=10)

    @commands.command()
    async def giveore(self, ctx, user: discord.User, ore: str, amount: int = 1):
        await update_ore_inventory(user.id, ore, amount)
        await ctx.send(f"Gave {amount}x {ore} to {user.mention}", delete_after=10)

    @commands.command()
    async def givestock(self, ctx, user: discord.User, stock: str):
        await add_user_stock(user.id, stock)
        await ctx.send(f"Gave {stock} to {user.mention}", delete_after=10)

    @commands.command()
    async def stockprice(self, ctx, stock: str, buy: float, sell: float):
        async with aiosqlite.connect("data/economy.db") as db:
            await db.execute("UPDATE stocks SET buy_price = ?, sell_price = ? WHERE name = ?", (buy, sell, stock))
            await db.commit()
        await ctx.send(f"Updated {stock} prices to Buy: {buy}, Sell: {sell}", delete_after=10)

    @commands.command()
    async def ban(self, ctx, user: discord.User, duration: int, *, reason: str):
        # Simple ban logic - you can expand this
        await ctx.send(f"Banned {user.mention} for {duration} minutes. Reason: {reason}", delete_after=10)

    @commands.command()
    async def unban(self, ctx, user: discord.User):
        await ctx.send(f"Unbanned {user.mention}", delete_after=10)

    @commands.command()
    async def clear(self, ctx, user: discord.User):
        await wipe_user(user.id)
        await ctx.send(f"Wiped all data for {user.mention}", delete_after=10)

    @commands.command()
    async def back(self, ctx, user: discord.User):
        await restore_user(user.id)
        await ctx.send(f"Restored data for {user.mention}", delete_after=10)

async def setup(bot):
    await bot.add_cog(Admin(bot))
