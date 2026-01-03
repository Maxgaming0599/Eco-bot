# utils/embeds.py
import discord
from config import CURRENCY_NAME, CURRENCY_SYMBOL

def balance_embed(user: discord.User, balance: int) -> discord.Embed:
    embed = discord.Embed(
        title=f"{user.display_name}'s Balance",
        description=f"{CURRENCY_SYMBOL} **{balance:,}** {CURRENCY_NAME}",
        color=0x00FF00
    )
    embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
    return embed
