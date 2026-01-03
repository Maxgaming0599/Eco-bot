# utils/helpers.py
import discord
from config import CURRENCY_NAME, CURRENCY_SYMBOL

def format_currency(amount: int) -> str:
    return f"{CURRENCY_SYMBOL} {amount:,}"

def check_admin(user_id: int) -> bool:
    # This will be used in slash commands
    import asyncio
    from database import is_admin
    return asyncio.run(is_admin(user_id))
