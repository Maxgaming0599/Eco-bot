# database.py
import sqlite3
import aiosqlite
from typing import Optional, List, Tuple, Union

DB_PATH = "data/economy.db"


async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        # Users Table
        await db.execute('''
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
        ''')

        # Stocks Table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS stocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                buy_price REAL,
                sell_price REAL,
                owner_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Miner Ores
        await db.execute('''
            CREATE TABLE IF NOT EXISTS miner_ores (
                user_id INTEGER,
                ore_type TEXT,
                quantity INTEGER,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        ''')

        # Jobs Table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                min_pay INTEGER,
                max_pay INTEGER,
                unlock_cost INTEGER,
                cooldown INTEGER
            )
        ''')

        # Admin List
        await db.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                user_id INTEGER PRIMARY KEY
            )
        ''')

        # Auction House
        await db.execute('''
            CREATE TABLE IF NOT EXISTS auction_house (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                seller_id INTEGER,
                item TEXT,
                price REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Black Market Gems
        await db.execute('''
            CREATE TABLE IF NOT EXISTS black_market_gems (
                gem_name TEXT PRIMARY KEY,
                buy_price REAL,
                sell_price REAL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        await db.commit()


async def get_user(user_id: int) -> aiosqlite.Row:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchone()


async def create_user(user_id: int) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        await db.commit()


async def update_balance(user_id: int, amount: int) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
        await db.commit()


async def get_balance(user_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)) as cursor:
            res = await cursor.fetchone()
            return res[0] if res else 0


async def set_balance(user_id: int, amount: int) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET balance = ? WHERE user_id = ?", (amount, user_id))
        await db.commit()


async def get_stock_price(name: str) -> Optional[Tuple[float, float]]:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT buy_price, sell_price FROM stocks WHERE name = ?", (name,)) as cursor:
            return await cursor.fetchone()


async def update_stock_prices(name: str, buy: float, sell: float) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE stocks SET buy_price = ?, sell_price = ? WHERE name = ?", (buy, sell, name))
        await db.commit()


async def user_has_stock(user_id: int, stock_name: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT stocks FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row and row[0]:
                stocks = row[0].split(",")
                return stock_name in stocks
            return False


async def add_user_stock(user_id: int, stock_name: str) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT stocks FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            current = row[0] if row and row[0] else ""
            if stock_name not in current.split(",") if current else True:
                new_stocks = f"{current},{stock_name}" if current else stock_name
                await db.execute("UPDATE users SET stocks = ? WHERE user_id = ?", (new_stocks, user_id))
                await db.commit()


async def remove_user_stock(user_id: int, stock_name: str) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT stocks FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row and row[0]:
                stocks = [s for s in row[0].split(",") if s != stock_name]
                new_stocks = ",".join(stocks)
                await db.execute("UPDATE users SET stocks = ? WHERE user_id = ?", (new_stocks, user_id))
                await db.commit()


async def get_ore_inventory(user_id: int) -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT ore_type, quantity FROM miner_ores WHERE user_id = ?", (user_id,)) as cursor:
            rows = await cursor.fetchall()
            return {row[0]: row[1] for row in rows}


async def update_ore_inventory(user_id: int, ore: str, quantity: int) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT quantity FROM miner_ores WHERE user_id = ? AND ore_type = ?", (user_id, ore)) as cursor:
            row = await cursor.fetchone()
        if row:
            await db.execute("UPDATE miner_ores SET quantity = quantity + ? WHERE user_id = ? AND ore_type = ?", (quantity, user_id, ore))
        else:
            await db.execute("INSERT INTO miner_ores (user_id, ore_type, quantity) VALUES (?, ?, ?)", (user_id, ore, quantity))
        await db.commit()


async def get_miner_level(user_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT miner_level FROM users WHERE user_id = ?", (user_id,)) as cursor:
            res = await cursor.fetchone()
            return res[0] if res else 1


async def set_miner_level(user_id: int, level: int) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET miner_level = ? WHERE user_id = ?", (level, user_id))
        await db.commit()


async def add_admin(user_id: int) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR IGNORE INTO admins (user_id) VALUES (?)", (user_id,))
        await db.commit()


async def is_admin(user_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT 1 FROM admins WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchone() is not None


async def get_all_users() -> List[int]:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT user_id FROM users") as cursor:
            return [row[0] async for row in cursor]


async def wipe_user(user_id: int) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        await db.execute("DELETE FROM miner_ores WHERE user_id = ?", (user_id,))
        await db.commit()


async def restore_user(user_id: int) -> None:
    # Implement backup/restore logic if needed
    pass

# database.py (Add to existing file)

# Add to init_db()
async def init_db() -> None:
    # ... existing tables ...
    
    # Black Market Gems
    await db.execute('''
        CREATE TABLE IF NOT EXISTS black_market_gems (
            gem_name TEXT PRIMARY KEY,
            buy_price REAL,
            sell_price REAL,
            buy_volume INTEGER DEFAULT 0,
            sell_volume INTEGER DEFAULT 0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # User Gem Inventory
    await db.execute('''
        CREATE TABLE IF NOT EXISTS user_gems (
            user_id INTEGER,
            gem_name TEXT,
            quantity INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    ''')

    # User Jobs
    await db.execute('''
        CREATE TABLE IF NOT EXISTS user_jobs (
            user_id INTEGER PRIMARY KEY,
            job_name TEXT,
            last_worked TIMESTAMP,
            FOREIGN KEY(job_name) REFERENCES jobs(name)
        )
    ''')

    # Admin Limits
    await db.execute('''
        CREATE TABLE IF NOT EXISTS admin_limits (
            user_id INTEGER PRIMARY KEY,
            limit_amount INTEGER
        )
    ''')

    # Stock Activity Tracking
    await db.execute('''
        CREATE TABLE IF NOT EXISTS stock_activity (
            stock_name TEXT,
            buy_volume INTEGER DEFAULT 0,
            sell_volume INTEGER DEFAULT 0,
            last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    await db.commit()


# Black Market Functions
async def get_gem_price(gem_name: str) -> tuple:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT buy_price, sell_price FROM black_market_gems WHERE gem_name = ?", (gem_name,)) as cursor:
            return await cursor.fetchone()


async def update_gem_price(gem_name: str, buy: float, sell: float) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT OR REPLACE INTO black_market_gems (gem_name, buy_price, sell_price, last_updated)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ''', (gem_name, buy, sell))
        await db.commit()


async def update_gem_volume(gem_name: str, volume_type: str, amount: int) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        column = f"{volume_type}_volume"
        await db.execute(f'''
            UPDATE black_market_gems 
            SET {column} = {column} + ? 
            WHERE gem_name = ?
        ''', (amount, gem_name))
        await db.commit()


async def get_user_gems(user_id: int) -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT gem_name, quantity FROM user_gems WHERE user_id = ?", (user_id,)) as cursor:
            rows = await cursor.fetchall()
            return {row[0]: row[1] for row in rows}


async def update_user_gems(user_id: int, gem: str, quantity: int) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT quantity FROM user_gems WHERE user_id = ? AND gem_name = ?", (user_id, gem)) as cursor:
            row = await cursor.fetchone()
        if row:
            await db.execute("UPDATE user_gems SET quantity = quantity + ? WHERE user_id = ? AND gem_name = ?", (quantity, user_id, gem))
        else:
            await db.execute("INSERT INTO user_gems (user_id, gem_name, quantity) VALUES (?, ?, ?)", (user_id, gem, quantity))
        await db.commit()


# Job Functions
async def get_user_job(user_id: int) -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT job_name, last_worked FROM user_jobs WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchone()


async def set_user_job(user_id: int, job_name: str) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR REPLACE INTO user_jobs (user_id, job_name) VALUES (?, ?)", (user_id, job_name))
        await db.commit()


async def update_last_worked(user_id: int) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE user_jobs SET last_worked = CURRENT_TIMESTAMP WHERE user_id = ?", (user_id,))
        await db.commit()


async def get_all_jobs() -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT name, min_pay, max_pay, unlock_cost FROM jobs") as cursor:
            return await cursor.fetchall()


async def get_job_details(job_name: str) -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT min_pay, max_pay, unlock_cost, cooldown FROM jobs WHERE name = ?", (job_name,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return {"min_pay": row[0], "max_pay": row[1], "unlock_cost": row[2], "cooldown": row[3]}
            return None


async def add_job(name: str, min_pay: int, max_pay: int, unlock_cost: int, cooldown: int = 3600) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR REPLACE INTO jobs (name, min_pay, max_pay, unlock_cost, cooldown) VALUES (?, ?, ?, ?, ?)",
                         (name, min_pay, max_pay, unlock_cost, cooldown))
        await db.commit()


async def remove_job(name: str) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM jobs WHERE name = ?", (name,))
        await db.commit()


# Admin Limit Functions
async def get_user_limit(user_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT limit_amount FROM admin_limits WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0


async def set_user_limit(user_id: int, amount: int) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR REPLACE INTO admin_limits (user_id, limit_amount) VALUES (?, ?)", (user_id, amount))
        await db.commit()


# Stock Activity Functions
async def update_stock_activity(stock_name: str, buy_volume: int = 0, sell_volume: int = 0) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT INTO stock_activity (stock_name, buy_volume, sell_volume)
            VALUES (?, ?, ?)
        ''', (stock_name, buy_volume, sell_volume))
        await db.commit()


async def get_stock_volumes(stock_name: str) -> tuple:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT SUM(buy_volume), SUM(sell_volume) FROM stock_activity WHERE stock_name = ?", (stock_name,)) as cursor:
            return await cursor.fetchone()


async def get_user_stocks(user_id: int) -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT stocks FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row and row[0]:
                stocks = row[0].split(",")
                return {stock: 1 for stock in stocks}
            return {}


async def create_stock(name: str, owner_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            await db.execute("INSERT INTO stocks (name, buy_price, sell_price, owner_id) VALUES (?, 100, 100, ?)", (name, owner_id))
            await db.commit()
            return True
        except sqlite3.IntegrityError:
            return False


async def transfer_stock(stock_name: str, new_owner_id: int) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE stocks SET owner_id = ? WHERE name = ?", (new_owner_id, stock_name))
        await db.commit()


async def get_stock_owner(stock_name: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT owner_id FROM stocks WHERE name = ?", (stock_name,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None
 
