# cogs/stocks.py
import discord
from discord.ext import commands
import random
from database import (
    get_stock_price, update_stock_prices, user_has_stock, add_user_stock, 
    remove_user_stock, get_balance, update_balance, update_stock_activity,
    create_stock, get_stock_owner, transfer_stock, get_user_stocks
)
from utils.charts import generate_price_chart

class Stocks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.default_stocks = ["BidCoin", "CryptoX", "GoldToken", "MoonCoin", "SafeCoin", 
                               "TechToken", "EnergyCoin", "EcoCoin", "SpaceCoin", "ArtCoin"]

    @commands.command()
    async def stock(self, ctx, name: str):
        buy, sell = await get_stock_price(name)
        if buy is None:
            return await ctx.send("Stock not found!", ephemeral=True)
        
        # Generate chart
        prices = [buy + random.randint(-5, 5) for _ in range(10)]
        chart = generate_price_chart(prices, f"{name} Price")
        file = discord.File(chart, filename="chart.png")
        
        embed = discord.Embed(title=f"📈 {name}", color=0x00FF00)
        embed.set_image(url="attachment://chart.png")
        embed.add_field(name="Buy Price", value=f"${buy:,.2f}", inline=True)
        embed.add_field(name="Sell Price", value=f"${sell:,.2f}", inline=True)
        
        owner = await get_stock_owner(name)
        if owner:
            owner_user = self.bot.get_user(owner)
            embed.add_field(name="Owner", value=owner_user.mention if owner_user else "Unknown", inline=False)
        
        await ctx.send(file=file, embed=embed)

    @commands.command()
    async def stocklist(self, ctx):
        embed = discord.Embed(title="Stock Market", color=0x00FF00)
        for name in self.default_stocks:
            buy, sell = await get_stock_price(name)
            if buy is None:
                buy, sell = 100, 95
                await update_stock_prices(name, buy, sell)
            embed.add_field(name=name, value=f"Buy: ${buy:,.2f} | Sell: ${sell:,.2f}", inline=False)
        
        # Add user-created stocks
        user_stocks = await self.get_all_user_stocks()
        if user_stocks:
            embed.add_field(name="User-Created Stocks", value="-------------------", inline=False)
            for name, data in user_stocks.items():
                embed.add_field(name=name, value=f"Buy: ${data['buy']:,.2f} | Sell: ${data['sell']:,.2f}", inline=False)
        
        await ctx.send(embed=embed)

    async def get_all_user_stocks(self):
        # Helper to get all user stocks
        async with aiosqlite.connect("data/economy.db") as db:
            async with db.execute("SELECT name, buy_price, sell_price FROM stocks WHERE owner_id IS NOT NULL") as cursor:
                rows = await cursor.fetchall()
                return {row[0]: {"buy": row[1], "sell": row[2]} for row in rows}

    @commands.command()
    async def buystock(self, ctx, name: str, amount: int = 1):
        buy_price, _ = await get_stock_price(name)
        if buy_price is None:
            return await ctx.send("Stock not found!", ephemeral=True)
        
        total_cost = int(buy_price * amount)
        balance = await get_balance(ctx.author.id)
        
        if balance < total_cost:
            return await ctx.send("Not enough funds!", ephemeral=True)
        
        await update_balance(ctx.author.id, -total_cost)
        await add_user_stock(ctx.author.id, name)
        await update_stock_activity(name, buy_volume=amount)
        
        await ctx.send(f"✅ Bought **{amount}** shares of {name} for {total_cost:,}")

    @commands.command()
    async def sellstock(self, ctx, name: str, amount: int = 1):
        if not await user_has_stock(ctx.author.id, name):
            return await ctx.send("You don't own this stock!", ephemeral=True)
        
        _, sell_price = await get_stock_price(name)
        total_earn = int(sell_price * amount)
        
        await update_balance(ctx.author.id, total_earn)
        await remove_user_stock(ctx.author.id, name)
        await update_stock_activity(name, sell_volume=amount)
        
        await ctx.send(f"✅ Sold **{amount}** shares of {name} for {total_earn:,}")

    @commands.command()
    async def createstock(self, ctx, name: str):
        cost = 5000000
        balance = await get_balance(ctx.author.id)
        
        if balance < cost:
            return await ctx.send(f"This costs {cost:,}! You need more.", ephemeral=True)
        
        success = await create_stock(name, ctx.author.id)
        if not success:
            return await ctx.send("Stock name already exists!", ephemeral=True)
        
        await update_balance(ctx.author.id, -cost)
        await ctx.send(f"✅ Created stock **{name}** starting at $100!")

    @commands.command()
    async def ocoin(self, ctx, user: discord.User, stock_name: str):
        owner = await get_stock_owner(stock_name)
        if owner != ctx.author.id:
            return await ctx.send("You don't own this stock!", ephemeral=True)
        
        await transfer_stock(stock_name, user.id)
        await ctx.send(f"✅ Transferred ownership of **{stock_name}** to {user.mention}")

async def setup(bot):
    await bot.add_cog(Stocks(bot))
