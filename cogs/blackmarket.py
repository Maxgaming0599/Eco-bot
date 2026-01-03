# cogs/blackmarket.py
import discord
from discord.ext import commands
import random
from database import (
    get_gem_price, update_gem_price, update_gem_volume,
    get_user_gems, update_user_gems, get_balance, update_balance
)

class BlackMarket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.gems = ["Ruby", "Sapphire", "Emerald", "Topaz", "Amethyst", "Diamond Gem", "Opal", "Jade", "Onyx", "Pearl"]
        self.base_prices = {gem: random.randint(10000, 50000) for gem in self.gems}

    @commands.group(invoke_without_command=True)
    async def blackmarket(self, ctx):
        embed = discord.Embed(title="🖤 Black Market", description="Rare gems and items", color=0x8B0000)
        for gem in self.gems:
            buy, sell = await get_gem_price(gem)
            if buy is None:
                buy = self.base_prices[gem]
                sell = buy * 0.9
                await update_gem_price(gem, buy, sell)
            embed.add_field(name=gem, value=f"Buy: {buy:,.0f} | Sell: {sell:,.0f}", inline=False)
        await ctx.send(embed=embed)

    @blackmarket.command()
    async def buy(self, ctx, gem: str, amount: int = 1):
        if gem not in self.gems:
            return await ctx.send("Invalid gem!", ephemeral=True)
        
        buy_price, _ = await get_gem_price(gem)
        total_cost = int(buy_price * amount)
        
        balance = await get_balance(ctx.author.id)
        if balance < total_cost:
            return await ctx.send("Not enough funds!", ephemeral=True)
        
        await update_balance(ctx.author.id, -total_cost)
        await update_user_gems(ctx.author.id, gem, amount)
        await update_gem_volume(gem, "buy", amount)
        
        # Dynamic price increase
        new_buy = buy_price * (1 + (amount * 0.01))
        new_sell = new_buy * 0.9
        await update_gem_price(gem, new_buy, new_sell)
        
        await ctx.send(f"✅ Bought **{amount}x {gem}** for {total_cost:,}")

    @blackmarket.command()
    async def sell(self, ctx, gem: str, amount: int = 1):
        if gem not in self.gems:
            return await ctx.send("Invalid gem!", ephemeral=True)
        
        user_gems = await get_user_gems(ctx.author.id)
        if user_gems.get(gem, 0) < amount:
            return await ctx.send("You don't have enough gems!", ephemeral=True)
        
        _, sell_price = await get_gem_price(gem)
        total_earn = int(sell_price * amount)
        
        await update_user_gems(ctx.author.id, gem, -amount)
        await update_balance(ctx.author.id, total_earn)
        await update_gem_volume(gem, "sell", amount)
        
        # Dynamic price decrease
        _, current_sell = await get_gem_price(gem)
        new_sell = current_sell * (1 - (amount * 0.01))
        new_buy = new_sell / 0.9
        await update_gem_price(gem, new_buy, new_sell)
        
        await ctx.send(f"✅ Sold **{amount}x {gem}** for {total_earn:,}")

async def setup(bot):
    await bot.add_cog(BlackMarket(bot))
