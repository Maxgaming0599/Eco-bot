# cogs/economy.py
import discord
from discord import app_commands
from discord.ext import commands
from database import get_balance, update_balance, get_user, create_user
from utils.embeds import balance_embed

class Economy(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="balance", description="Check your balance")
    async def balance(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        await create_user(user_id)
        balance = await get_balance(user_id)
        await interaction.response.send_message(embed=balance_embed(interaction.user, balance))

    @app_commands.command(name="pay", description="Pay another user")
    @app_commands.describe(user: "User to pay", amount: "Amount to pay")
    async def pay(self, interaction: discord.Interaction, user: discord.User, amount: int):
        sender_id = interaction.user.id
        await create_user(sender_id)
        await create_user(user.id)

        balance = await get_balance(sender_id)
        if amount <= 0:
            return await interaction.response.send_message("Amount must be positive!", ephemeral=True)
        if balance < amount:
            return await interaction.response.send_message("You don't have enough funds!", ephemeral=True)

        await update_balance(sender_id, -amount)
        await update_balance(user.id, amount)
        await interaction.response.send_message(f"Sent **{amount}** {CURRENCY_SYMBOL} to {user.mention}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Economy(bot))
