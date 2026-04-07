import sqlite3
import datetime

conn = sqlite3.connect("chat.db", check_same_thread=False)
c = conn.cursor()

def init_db():
    c.execute("""
    CREATE TABLE IF NOT EXISTS chats (
        chat_id TEXT PRIMARY KEY,
        title TEXT,
        created_at TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        chat_id TEXT,
        sender TEXT,
        message TEXT
    )
    """)
    conn.commit()

def create_new_chat(chat_id: str, title: str):
    created_at = datetime.datetime.now().isoformat()
    c.execute("INSERT INTO chats VALUES (?, ?, ?)", (chat_id, title, created_at))
    conn.commit()

def save_message(chat_id: str, sender: str, message: str):
    c.execute("INSERT INTO messages VALUES (?, ?, ?)", (chat_id, sender, message))
    conn.commit()