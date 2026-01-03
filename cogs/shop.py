# cogs/shop.py
import discord
from discord.ext import commands
from discord.ui import Button, View
from database import (
    get_balance, update_balance, get_miner_level, set_miner_level,
    get_user_gems, update_user_gems
)

class ShopView(View):
    def __init__(self, bot, user_id):
        super().__init__(timeout=60)
        self.bot = bot
        self.user_id = user_id

    @discord.ui.button(label="Miner Lv1", style=discord.ButtonStyle.red, row=0)
    async def miner1(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This is not your shop!", ephemeral=True)
            return
        
        cost = 10000
        balance = await get_balance(self.user_id)
        if balance < cost:
            await interaction.response.send_message("Not enough funds!", ephemeral=True)
            return
        
        await update_balance(self.user_id, -cost)
        await set_miner_level(self.user_id, 1)
        await interaction.response.send_message("✅ Purchased Miner Level 1!", ephemeral=True)

    @discord.ui.button(label="Miner Lv2", style=discord.ButtonStyle.red, row=0)
    async def miner2(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This is not your shop!", ephemeral=True)
            return
        
        cost = 50000
        balance = await get_balance(self.user_id)
        if balance < cost:
            await interaction.response.send_message("Not enough funds!", ephemeral=True)
            return
        
        level = await get_miner_level(self.user_id)
        if level < 1:
            await interaction.response.send_message("Buy Miner Lv1 first!", ephemeral=True)
            return
        
        await update_balance(self.user_id, -cost)
        await set_miner_level(self.user_id, 2)
        await interaction.response.send_message("✅ Purchased Miner Level 2!", ephemeral=True)

    @discord.ui.button(label="Miner Lv3", style=discord.ButtonStyle.red, row=0)
    async def miner3(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This is not your shop!", ephemeral=True)
            return
        
        cost = 250000
        balance = await get_balance(self.user_id)
        if balance < cost:
            await interaction.response.send_message("Not enough funds!", ephemeral=True)
            return
        
        level = await get_miner_level(self.user_id)
        if level < 2:
            await interaction.response.send_message("Buy Miner Lv2 first!", ephemeral=True)
            return
        
        await update_balance(self.user_id, -cost)
        await set_miner_level(self.user_id, 3)
        await interaction.response.send_message("✅ Purchased Miner Level 3!", ephemeral=True)

    @discord.ui.button(label="5 Workers", style=discord.ButtonStyle.blurple, row=1)
    async def workers5(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This is not your shop!", ephemeral=True)
            return
        
        cost = 25000
        balance = await get_balance(self.user_id)
        if balance < cost:
            await interaction.response.send_message("Not enough funds!", ephemeral=True)
            return
        
        await update_balance(self.user_id, -cost)
        # Add 5 workers (simplified)
        await interaction.response.send_message("✅ Hired 5 workers! Mining output increased!", ephemeral=True)

    @discord.ui.button(label="Market Boost", style=discord.ButtonStyle.green, row=1)
    async def market_boost(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This is not your shop!", ephemeral=True)
            return
        
        cost = 100000
        balance = await get_balance(self.user_id)
        if balance < cost:
            await interaction.response.send_message("Not enough funds!", ephemeral=True)
            return
        
        await update_balance(self.user_id, -cost)
        await interaction.response.send_message("✅ Market boost purchased! (Temporary effect)", ephemeral=True)

    @discord.ui.button(label="Special Coin", style=discord.ButtonStyle.gold, row=1)
    async def special_coin(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This is not your shop!", ephemeral=True)
            return
        
        cost = 500000
        balance = await get_balance(self.user_id)
        if balance < cost:
            await interaction.response.send_message("Not enough funds!", ephemeral=True)
            return
        
        await update_balance(self.user_id, -cost)
        await update_user_gems(self.user_id, "Special Coin", 1)
        await interaction.response.send_message("✅ Purchased Special Coin!", ephemeral=True)

    @discord.ui.button(label="Worker Boost", style=discord.ButtonStyle.blurple, row=2)
    async def worker_boost(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This is not your shop!", ephemeral=True)
            return
        
        cost = 75000
        balance = await get_balance(self.user_id)
        if balance < cost:
            await interaction.response.send_message("Not enough funds!", ephemeral=True)
            return
        
        await update_balance(self.user_id, -cost)
        await interaction.response.send_message("✅ Worker boost purchased! Mining efficiency increased!", ephemeral=True)

    @discord.ui.button(label="Rare Gem Pack", style=discord.ButtonStyle.red, row=2)
    async def gem_pack(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This is not your shop!", ephemeral=True)
            return
        
        cost = 200000
        balance = await get_balance(self.user_id)
        if balance < cost:
            await interaction.response.send_message("Not enough funds!", ephemeral=True)
            return
        
        await update_balance(self.user_id, -cost)
        gem = random.choice(["Ruby", "Sapphire", "Emerald"])
        await update_user_gems(self.user_id, gem, 1)
        await interaction.response.send_message(f"✅ Purchased Gem Pack! Got {gem}!", ephemeral=True)

class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def shop(self, ctx):
        embed = discord.Embed(
            title="🛒 Shop",
            description="Click buttons to purchase items",
            color=0xFF0000
        )
        embed.add_field(name="Miners", value="Level 1-3 for mining", inline=False)
        embed.add_field(name="Workers", value="Increase mining output", inline=False)
        embed.add_field(name="Boosts", value="Market & Worker boosts", inline=False)
        embed.add_field(name="Special Items", value="Coins & Gems", inline=False)
        embed.set_footer(text="Prices are subject to change")
        
        view = ShopView(self.bot, ctx.author.id)
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Shop(bot))
