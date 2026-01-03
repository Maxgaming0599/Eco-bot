# cogs/gambling.py
import discord
from discord.ext import commands, tasks
import random
from database import get_balance, update_balance

class Gambling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def coinflip(self, ctx, amount: int, choice: str):
        if amount <= 0:
            return await ctx.send("Bet amount must be positive!", ephemeral=True)
        balance = await get_balance(ctx.author.id)
        if balance < amount:
            return await ctx.send("You don't have enough funds!", ephemeral=True)

        result = random.choice(["Heads", "Tails"])
        if choice.lower() == result.lower():
            await update_balance(ctx.author.id, amount)
            await ctx.send(f"You won! **{amount}** added.")
        else:
            await update_balance(ctx.author.id, -amount)
            await ctx.send(f"You lost! **{amount}** removed.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Gambling(bot))
