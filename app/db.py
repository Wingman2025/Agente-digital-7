import os
import psycopg2
import asyncio
from typing import List, Tuple
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def ensure_conversations_table():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id SERIAL PRIMARY KEY,
            session_id TEXT NOT NULL,
            sender TEXT NOT NULL,
            message TEXT NOT NULL,
            ts TIMESTAMP DEFAULT NOW()
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

async def fetch_history(session_id: str) -> List[Tuple[str, str]]:
    def _fetch():
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute(
            "SELECT sender, message FROM conversations WHERE session_id=%s ORDER BY ts",
            (session_id,)
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows
    return await asyncio.to_thread(_fetch)

async def insert_message(session_id: str, sender: str, message: str):
    def _insert():
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO conversations (session_id, sender, message) VALUES (%s,%s,%s)",
            (session_id, sender, message)
        )
        conn.commit()
        cur.close()
        conn.close()
    await asyncio.to_thread(_insert)
