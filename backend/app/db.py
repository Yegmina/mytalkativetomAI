from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).resolve().parent.parent / "data.sqlite"


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS profile (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                coins INTEGER NOT NULL,
                level INTEGER NOT NULL,
                xp INTEGER NOT NULL,
                hunger REAL NOT NULL,
                energy REAL NOT NULL,
                hygiene REAL NOT NULL,
                fun REAL NOT NULL,
                mood REAL NOT NULL,
                last_updated TEXT NOT NULL,
                owned_items TEXT NOT NULL,
                equipped_items TEXT NOT NULL
            )
            """
        )
        conn.commit()


def row_to_profile(row: sqlite3.Row) -> dict[str, Any]:
    profile = dict(row)
    profile["owned_items"] = json.loads(profile["owned_items"])
    profile["equipped_items"] = json.loads(profile["equipped_items"])
    return profile


def default_profile() -> dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    return {
        "id": 1,
        "name": "Tom",
        "coins": 120,
        "level": 1,
        "xp": 0,
        "hunger": 75.0,
        "energy": 75.0,
        "hygiene": 80.0,
        "fun": 70.0,
        "mood": 75.0,
        "last_updated": now,
        "owned_items": [],
        "equipped_items": {},
    }


def get_or_create_profile(conn: sqlite3.Connection) -> dict[str, Any]:
    row = conn.execute("SELECT * FROM profile WHERE id = 1").fetchone()
    if row:
        return row_to_profile(row)
    profile = default_profile()
    upsert_profile(conn, profile)
    return profile


def upsert_profile(conn: sqlite3.Connection, profile: dict[str, Any]) -> None:
    conn.execute(
        """
        INSERT OR REPLACE INTO profile (
            id, name, coins, level, xp, hunger, energy, hygiene, fun, mood,
            last_updated, owned_items, equipped_items
        ) VALUES (
            :id, :name, :coins, :level, :xp, :hunger, :energy, :hygiene, :fun, :mood,
            :last_updated, :owned_items, :equipped_items
        )
        """,
        {
            **profile,
            "owned_items": json.dumps(profile["owned_items"]),
            "equipped_items": json.dumps(profile["equipped_items"]),
        },
    )
    conn.commit()
