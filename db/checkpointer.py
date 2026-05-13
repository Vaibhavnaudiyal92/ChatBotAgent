import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver

conn = sqlite3.connect(database='chatbot.db', check_same_thread=False)
# Checkpointer
checkpointer = SqliteSaver(conn=conn)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id TEXT,
    filename TEXT,
    content TEXT
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS thread_titles (
    thread_id TEXT PRIMARY KEY,
    title TEXT
)
""")


conn.commit()