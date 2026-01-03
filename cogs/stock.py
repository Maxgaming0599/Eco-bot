# cogs/stocks.py
import discord
from discord.ext import commands
from database import get_stock_price, update_stock_prices, user_has_stock, add_user_stock, remove_user_stock
from utils.charts import generate_price_chart
import random

class Stocks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def stock(self, ctx, name: str):
        buy, sell = await get_stock_price(name)
        chart = generate_price_chart([sell]*10, f"{name} Price")
        file = discord.File(chart, filename="chart.png")

        embed = discord.Embed(title=name, color=0x00FF00)
        embed.set_image(url="attachment://chart.png")
        embed.add_field(name="Buy", value=f"${buy:,.2f}", inline=False)
        embed.add_field(name="Sell", value=f"${sell:,.2f}", inline=False)
        embed.add_field(name="Trend", value="📈 Rising" if buy > sell else "📉 Falling", inline=False)

        await ctx.send(file=file, embed=embed)

    @commands.command()
    async def stocklist(self, ctx):
        embed = discord.Embed(title="Stock Market", color=0x00FF00)
        for name in ["BidCoin", "CryptoX", "GoldToken", "MoonCoin", "SafeCoin", "TechToken", "EnergyCoin", "EcoCoin", "SpaceCoin", "ArtCoin"]:
            buy, sell = await get_stock_price(name)
            embed.add_field(name=name, value=f"Buy: ${buy:,.2f} | Sell: ${sell:,.2f}", inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def buy_stock(self, ctx, name: str, amount: int):
        if not await user_has_stock(ctx.author.id, name):
            await add_user_stock(ctx.author.id, name)
            await ctx.send(f"Bought **{amount}** shares of {name}")
        else:
            await ctx.send("You already own this stock!")

async def setup(bot: commands.Bot):
    await bot.add_cog(Stocks(bot))
