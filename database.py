import sqlite3
from pathlib import Path
from datetime import datetime, timezone

DB_FILE = Path(__file__).with_name("products.db")

def get_connection():
    connection = sqlite3.connect(DB_FILE)
    connection.row_factory = sqlite3.Row
    return connection

def create_table():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL CHECK(price >= 0),
                stock INTEGER NOT NULL CHECK(stock >= 0),
                description TEXT NOT NULL
            )
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS visitor_log (
                ip_address TEXT PRIMARY KEY,
                country TEXT NOT NULL,
                request_count INTEGER NOT NULL DEFAULT 1,
                first_seen TEXT NOT NULL,
                last_seen TEXT NOT NULL
            )
        """)

def record_visit(ip_address, country):
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with get_connection() as connection:
        existing = connection.execute(
            "SELECT ip_address FROM visitor_log WHERE ip_address = ?",
            (ip_address,)
        ).fetchone()

        if existing:
            connection.execute("""
                UPDATE visitor_log
                SET request_count = request_count + 1, last_seen = ?
                WHERE ip_address = ?
            """, (now, ip_address))
        else:
            connection.execute("""
                INSERT INTO visitor_log
                    (ip_address, country, request_count, first_seen, last_seen)
                VALUES (?, ?, 1, ?, ?)
            """, (ip_address, country, now, now))

def get_visitors():
    with get_connection() as connection:
        return connection.execute("""
            SELECT ip_address, country, request_count, first_seen, last_seen
            FROM visitor_log
            ORDER BY last_seen DESC
        """).fetchall()
