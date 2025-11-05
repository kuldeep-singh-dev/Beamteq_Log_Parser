# db/database.py

import sqlite3
from pathlib import Path
from typing import List

class Database:
    def __init__(self, db_path):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.cur = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        with open("db/schema.sql", "r", encoding="utf-8") as f:
            sql = f.read()
            self.cur.executescript(sql)
        self.conn.commit()

    def insert(self, table: str, data: dict):
        """Insert dictionary data into a given table."""
        keys = ", ".join(data.keys())
        values = tuple(data.values())
        placeholders = ", ".join(["?"] * len(values))
        sql = f"INSERT INTO {table} ({keys}) VALUES ({placeholders})"
        self.cur.execute(sql, values)
        self.conn.commit()
        return self.cur.lastrowid
    
    def bulk_insert(self, table: str, rows: List[dict]):
        """Insert many rows at once – much faster."""
        if not rows:
            return
        keys = ", ".join(rows[0].keys())
        placeholders = ", ".join(["?"] * len(rows[0]))
        sql = f"INSERT INTO {table} ({keys}) VALUES ({placeholders})"
        values = [tuple(r.values()) for r in rows]
        self.cur.executemany(sql, values)
        self.conn.commit()

    def fetchall(self, query: str, params: tuple = ()):
        """Run SELECT queries and fetch all results."""
        self.cur.execute(query, params)
        return self.cur.fetchall()

    def close(self):
        self.conn.close()
