# cogs/mining.py
import discord
from discord.ext import commands, tasks
import random
from database import (
    get_miner_level, set_miner_level, update_ore_inventory,
    get_ore_inventory, get_balance, update_balance
)
from utils.embeds import balance_embed

MINING_COOLDOWN = 300  # 5 minutes

ORE_TYPES = {
    "Gold Ore": {"buy": 43428, "sell": 37890},
    "Silver Ore": {"buy": 6789, "sell": 4500},
    "Iron Ore": {"buy": 5556, "sell": 3980},
    "Coal": {"buy": 500, "sell": 350},
    "Diamond": {"buy": 72000, "sell": 68000},
    "Platinum Ore": {"buy": 52000, "sell": 45000},
    "Silver Shard": {"buy": 3000, "sell": 2700}
}

GEM_CHANCE = 0.1
GEMS = ["Ruby", "Sapphire", "Emerald", "Topaz", "Amethyst", "Diamond Gem", "Opal", "Jade", "Onyx", "Pearl"]

class Mining(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mining_cooldown = commands.CooldownMapping.from_cooldown(1, MINING_COOLDOWN, commands.BucketType.user)

    @commands.command()
    @commands.cooldown(1, MINING_COOLDOWN, commands.BucketType.user)
    async def mine(self, ctx):
        user_id = ctx.author.id
        level = await get_miner_level(user_id)

        ore_roll = random.random()
        ore_chance = sum(1 / (i + 1) for i in range(level)) ** -1
        ore_type = "Gold Ore"

        if ore_roll < 0.1:
            ore_type = "Diamond"
        elif ore_roll < 0.3:
            ore_type = "Platinum Ore"
        elif ore_roll < 0.5:
            ore_type = "Silver Ore"
        elif ore_roll < 0.7:
            ore_type = "Iron Ore"
        else:
            ore_type = "Gold Ore"

        quantity = random.randint(1, level * 2)

        await update_ore_inventory(user_id, ore_type, quantity)

        gem_chance = random.random()
        if gem_chance < GEM_CHANCE:
            gem = random.choice(GEMS)
            await ctx.send(f"✨ You found a rare **{gem}** while mining!", delete_after=30)

        await ctx.send(f"You mined **{quantity}x {ore_type}**!", delete_after=30)

    @commands.command()
    async def orelist(self, ctx):
        embed = discord.Embed(title="Ore Prices", color=0x1E90FF)
        for ore, data in ORE_TYPES.items():
            embed.add_field(name=ore, value=f"Buy: {data['buy']:,} | Sell: {data['sell']:,}", inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def miner(self, ctx):
        embed = discord.Embed(title="Your Miner", color=0x1E90FF)
        embed.add_field(name="Level", value=await get_miner_level(ctx.author.id), inline=False)
        inv = await get_ore_inventory(ctx.author.id)
        embed.add_field(name="Inventory", value="\n".join([f"{ore}: {qty}" for ore, qty in inv.items()]) or "Empty", inline=False)
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Mining(bot))
