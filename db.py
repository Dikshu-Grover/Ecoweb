import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("ecoweb.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_conn() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT DEFAULT (datetime('now')),
            url TEXT,
            size REAL,
            co2 REAL,
            score INTEGER,
            rating TEXT,
            images INTEGER,
            scripts INTEGER,
            videos INTEGER,
            links INTEGER,
            opt_size REAL,
            opt_co2 REAL,
            co2_saved REAL,
            saved_percent INTEGER
        )
        """)
        conn.commit()

def insert_analysis(r: dict) -> int:
    with get_conn() as conn:
        cur = conn.execute("""
            INSERT INTO analyses
            (url, size, co2, score, rating, images, scripts, videos, links,
             opt_size, opt_co2, co2_saved, saved_percent)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            r["url"], r["size"], r["co2"], r["score"], r["rating"],
            r["images"], r["scripts"], r["videos"], r["links"],
            r["opt_size"], r["opt_co2"], r["co2_saved"], r["saved_percent"]
        ))
        conn.commit()
        return cur.lastrowid

def get_latest(limit: int = 10):
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT * FROM analyses
            ORDER BY id DESC
            LIMIT ?
        """, (limit,)).fetchall()
        return rows

def get_top_green(limit: int = 10):
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT * FROM analyses
            ORDER BY score DESC, co2 ASC
            LIMIT ?
        """, (limit,)).fetchall()
        return rows

def get_one(row_id: int):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM analyses WHERE id = ?", (row_id,)).fetchone()
        return row
