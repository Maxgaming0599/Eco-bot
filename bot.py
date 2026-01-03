# bot.py
import discord
from discord.ext import commands, tasks
from config import BOT_TOKEN, OWNER_ID
from database import init_db, get_all_jobs, get_stock_volumes, update_stock_prices, get_stock_price
import aiosqlite
import random
import asyncio

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
        
        # Start background tasks
        if not self.stock_fluctuation.is_running():
            self.stock_fluctuation.start()
        if not self.gem_price_update.is_running():
            self.gem_price_update.start()

    async def on_ready(self):
        print(f'Logged in as {self.user}')

    @tasks.loop(minutes=5)
    async def stock_fluctuation(self):
        # Dynamic stock price updates
        async with aiosqlite.connect("data/economy.db") as db:
            async with db.execute("SELECT name FROM stocks") as cursor:
                stocks = [row[0] async for row in cursor]
        
        for stock in stocks:
            buy, sell = await get_stock_price(stock)
            if buy is None:
                continue
            
            # Get volume data
            buy_vol, sell_vol = await get_stock_volumes(stock)
            buy_vol = buy_vol or 0
            sell_vol = sell_vol or 0
            
            # Calculate price change based on volume
            volume_diff = buy_vol - sell_vol
            price_change = volume_diff * 0.01  # 1% per unit difference
            
            # Add random fluctuation
            random_change = random.uniform(-0.5, 0.5)
            
            new_buy = max(1, buy * (1 + price_change + random_change))
            new_sell = new_buy * 0.95
            
            await update_stock_prices(stock, new_buy, new_sell)
            
            # Reset volumes
            async with aiosqlite.connect("data/economy.db") as db:
                await db.execute("DELETE FROM stock_activity WHERE stock_name = ?", (stock,))
                await db.commit()

    @tasks.loop(minutes=10)
    async def gem_price_update(self):
        # Update black market gem prices
        gems = ["Ruby", "Sapphire", "Emerald", "Topaz", "Amethyst", "Diamond Gem", "Opal", "Jade", "Onyx", "Pearl"]
        for gem in gems:
            buy, sell = await get_gem_price(gem)
            if buy is None:
                continue
            
            # Random fluctuation based on market conditions
            change = random.uniform(-0.05, 0.05)
            new_buy = max(1000, buy * (1 + change))
            new_sell = new_buy * 0.9
            
            await update_gem_price(gem, new_buy, new_sell)

bot = EconomyBot()
bot.run(BOT_TOKEN)
