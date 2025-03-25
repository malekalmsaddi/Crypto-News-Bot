import sqlite3
import logging
from config import DATABASE_FILE

logger = logging.getLogger(__name__)

def get_db_connection():
    """Create and return a database connection with thread safety."""
    try:
        conn = sqlite3.connect(DATABASE_FILE, check_same_thread=False)  # ✅ Allow async/threaded access
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}")
        raise

def init_db():
    """Initialize the database by creating tables if they don't exist."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Chats table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS chats (
            chat_id INTEGER PRIMARY KEY,
            chat_title TEXT,
            chat_type TEXT,
            join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Messages table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            news_id TEXT,
            chat_id INTEGER,
            message_id INTEGER,
            sent_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (chat_id) REFERENCES chats (chat_id)
        )
        ''')

        # Webhook logs table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS webhook_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            news_id TEXT,
            content TEXT,
            received_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Market Prices table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS market_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coin TEXT UNIQUE,
            price REAL,
            change REAL,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Market Summary table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS market_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total_market_cap REAL,
            total_volume REAL,
            btc_dominance REAL,
            eth_dominance REAL,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        conn.commit()
        logger.info("Database initialized successfully")
    except sqlite3.Error as e:
        logger.error(f"Database initialization error: {e}")
        raise
    finally:
        conn.close()

# --------- Chats Functions ---------
def add_chat(chat_id, chat_title, chat_type):
    """Add or update a chat in the database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO chats (chat_id, chat_title, chat_type) VALUES (?, ?, ?)",
            (chat_id, chat_title, chat_type)
        )
        conn.commit()
        logger.info(f"Added chat: {chat_id} ({chat_title})")
        return True
    except sqlite3.Error as e:
        logger.error(f"Error adding chat: {e}")
        return False
    finally:
        conn.close()

def remove_chat(chat_id):
    """Remove a chat from the database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chats WHERE chat_id = ?", (chat_id,))
        conn.commit()
        logger.info(f"Removed chat: {chat_id}")
        return True
    except sqlite3.Error as e:
        logger.error(f"Error removing chat: {e}")
        return False
    finally:
        conn.close()

def get_all_chats():
    """Fetch all chats from the database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM chats")
        chats = cursor.fetchall()
        return chats
    except sqlite3.Error as e:
        logger.error(f"Error getting chats: {e}")
        return []
    finally:
        conn.close()

# --------- Webhook / Messages Logging ---------
def log_webhook(news_id, content):
    """Log webhook data into the database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO webhook_logs (news_id, content) VALUES (?, ?)",
            (news_id, content)
        )
        conn.commit()
        logger.info(f"Logged webhook: {news_id}")
        return True
    except sqlite3.Error as e:
        logger.error(f"Error logging webhook: {e}")
        return False
    finally:
        conn.close()

def log_message(news_id, chat_id, message_id):
    """Log a sent message into the database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO messages (news_id, chat_id, message_id) VALUES (?, ?, ?)",
            (news_id, chat_id, message_id)
        )
        conn.commit()
        return True
    except sqlite3.Error as e:
        logger.error(f"Error logging message: {e}")
        return False
    finally:
        conn.close()

# --------- Market Data Update Functions ---------
def update_market_price(coin, price, change):
    """Insert or update a coin price."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO market_prices (coin, price, change, last_updated)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(coin) DO UPDATE SET
                price=excluded.price,
                change=excluded.change,
                last_updated=CURRENT_TIMESTAMP
        ''', (coin, price, change))
        conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Error updating market price: {e}")
    finally:
        conn.close()

def update_market_summary(total_market_cap, total_volume, btc_dominance, eth_dominance):
    """Insert the latest market summary (keep latest only)."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM market_summary')  # Keep latest only
        cursor.execute('''
            INSERT INTO market_summary (total_market_cap, total_volume, btc_dominance, eth_dominance)
            VALUES (?, ?, ?, ?)
        ''', (total_market_cap, total_volume, btc_dominance, eth_dominance))
        conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Error updating market summary: {e}")
    finally:
        conn.close()

# --------- Market Data Fetch Functions ---------
def get_market_prices():
    """Fetch the latest prices from the database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT coin, price, change FROM market_prices')
        prices = cursor.fetchall()
        return {row['coin']: {"price": row['price'], "change": row['change']} for row in prices}
    except sqlite3.Error as e:
        logger.error(f"Error fetching market prices: {e}")
        return {}
    finally:
        conn.close()

def get_market_summary():
    """Fetch the latest market summary from the database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT total_market_cap, total_volume, btc_dominance, eth_dominance FROM market_summary ORDER BY id DESC LIMIT 1')
        row = cursor.fetchone()
        if row:
            return {
                "total_market_cap": row["total_market_cap"],
                "total_volume": row["total_volume"],
                "btc_dominance": row["btc_dominance"],
                "eth_dominance": row["eth_dominance"]
            }
        return None
    except sqlite3.Error as e:
        logger.error(f"Error fetching market summary: {e}")
        return None
    finally:
        conn.close()