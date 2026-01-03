# database.py
import sqlite3
import aiosqlite
from typing import Optional, List, Tuple

DB_PATH = "data/economy.db"


# =========================
# DATABASE INITIALIZATION
# =========================
async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:

        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            balance INTEGER DEFAULT 0,
            job TEXT,
            miner_level INTEGER DEFAULT 1,
            miner_progress INTEGER DEFAULT 0,
            miner_ores TEXT DEFAULT '',
            gems TEXT DEFAULT '',
            workers INTEGER DEFAULT 0,
            stocks TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS stocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            buy_price REAL,
            sell_price REAL,
            owner_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS miner_ores (
            user_id INTEGER,
            ore_type TEXT,
            quantity INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            min_pay INTEGER,
            max_pay INTEGER,
            unlock_cost INTEGER,
            cooldown INTEGER
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            user_id INTEGER PRIMARY KEY
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS auction_house (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seller_id INTEGER,
            item TEXT,
            price REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS black_market_gems (
            gem_name TEXT PRIMARY KEY,
            buy_price REAL,
            sell_price REAL,
            buy_volume INTEGER DEFAULT 0,
            sell_volume INTEGER DEFAULT 0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS user_gems (
            user_id INTEGER,
            gem_name TEXT,
            quantity INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS user_jobs (
            user_id INTEGER PRIMARY KEY,
            job_name TEXT,
            last_worked TIMESTAMP,
            FOREIGN KEY(job_name) REFERENCES jobs(name)
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS admin_limits (
            user_id INTEGER PRIMARY KEY,
            limit_amount INTEGER
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS stock_activity (
            stock_name TEXT,
            buy_volume INTEGER DEFAULT 0,
            sell_volume INTEGER DEFAULT 0,
            last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        await db.commit()


# =========================
# JOB FUNCTIONS
# =========================
async def get_all_jobs() -> List[Tuple]:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT name, min_pay, max_pay, unlock_cost, cooldown FROM jobs"
        ) as cur:
            return await cur.fetchall()


# =========================
# STOCK FUNCTIONS
# =========================
async def get_stock_price(name: str) -> Optional[Tuple[float, float]]:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT buy_price, sell_price FROM stocks WHERE name = ?",
            (name,)
        ) as cur:
            return await cur.fetchone()


async def update_stock_prices(name: str, buy_price: float, sell_price: float) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE stocks SET buy_price = ?, sell_price = ? WHERE name = ?",
            (buy_price, sell_price, name)
        )
        await db.commit()


async def get_stock_volumes(stock_name: str) -> Tuple[int, int]:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT SUM(buy_volume), SUM(sell_volume) FROM stock_activity WHERE stock_name = ?",
            (stock_name,)
        ) as cur:
            row = await cur.fetchone()
            return (row[0] or 0, row[1] or 0)


# =========================
# OPTIONAL HELPERS (SAFE)
# =========================
async def create_stock(name: str, owner_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            await db.execute(
                "INSERT INTO stocks (name, buy_price, sell_price, owner_id) VALUES (?, 100, 100, ?)",
                (name, owner_id)
            )
            await db.commit()
            return True
        except sqlite3.IntegrityError:
            return False
