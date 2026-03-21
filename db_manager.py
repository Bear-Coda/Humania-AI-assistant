import sqlite3
from datetime import datetime

DB_PATH = "app_data.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Users Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (username TEXT PRIMARY KEY, password TEXT)''')
    # Chats Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS chats 
                      (chat_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       username TEXT, title TEXT, created_at TEXT)''')
    # Messages Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS messages 
                      (chat_id INTEGER, role TEXT, content TEXT)''')
    conn.commit()
    conn.close()

def validate_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    res = cursor.fetchone()
    conn.close()
    return res is not None

def create_user(username, password):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except: return False
    finally: conn.close()

def start_new_chat(username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute("INSERT INTO chats (username, title, created_at) VALUES (?, ?, ?)", 
                   (username, "New Discussion...", now))
    chat_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return chat_id

def update_chat_title(chat_id, first_msg):
    title = (first_msg[:25] + '...') if len(first_msg) > 25 else first_msg
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE chats SET title=? WHERE chat_id=?", (title, chat_id))
    conn.commit()
    conn.close()

def save_message(chat_id, role, content):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (chat_id, role, content) VALUES (?, ?, ?)", (chat_id, role, content))
    conn.commit()
    conn.close()

def get_user_chats(username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT chat_id, title, created_at FROM chats WHERE username=? ORDER BY chat_id DESC", (username,))
    res = cursor.fetchall()
    conn.close()
    return res

def get_chat_messages(chat_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT role, content FROM messages WHERE chat_id=?", (chat_id,))
    res = cursor.fetchall()
    conn.close()
    return res

def delete_chats(chat_ids):
    """Deletes specific chats and their messages"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Delete messages first (Foreign key safety)
    cursor.execute(f"DELETE FROM messages WHERE chat_id IN ({','.join(['?']*len(chat_ids))})", chat_ids)
    # Delete the chats
    cursor.execute(f"DELETE FROM chats WHERE chat_id IN ({','.join(['?']*len(chat_ids))})", chat_ids)
    conn.commit()
    conn.close()

def delete_all_user_chats(username):
    """Wipes everything for a specific user"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM messages WHERE chat_id IN (SELECT chat_id FROM chats WHERE username=?)", (username,))
    cursor.execute("DELETE FROM chats WHERE username=?", (username,))
    conn.commit()
    conn.close()