import sqlite3
import logging
from config import DATABASE_FILE

logger = logging.getLogger(__name__)

def get_db_connection():
    """Create and return a database connection."""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
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
        
        # Create table to store chat IDs where the bot is a member
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS chats (
            chat_id INTEGER PRIMARY KEY,
            chat_title TEXT,
            chat_type TEXT,
            join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create table to store sent messages for tracking
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
        
        # Create table to log received webhooks
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS webhook_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            news_id TEXT,
            content TEXT,
            received_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        logger.info("Database initialized successfully")
    except sqlite3.Error as e:
        logger.error(f"Database initialization error: {e}")
        raise
    finally:
        conn.close()

def add_chat(chat_id, chat_title, chat_type):
    """Add a new chat to the database."""
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
    """Get all chats from the database."""
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

def log_webhook(news_id, content):
    """Log a received webhook."""
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
    """Log a sent message."""
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
