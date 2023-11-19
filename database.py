import sqlite3
import sys

from pathlib import Path
from typing import Union

__all__ = [
    "db_delete_user", "db_get_user_state", "db_edit_user_state", "db_create_new_user",
    "db_get_last_value", "db_edit_last_value"
]


def init() -> sqlite3.Connection:
    connect = sqlite3.connect('users.db', check_same_thread=False)
    connect.execute("pragma journal_mode=wal;")
    return connect


def create_database():
    conn = init()
    cur = conn.cursor()
    cur.execute(
        '''CREATE TABLE `users` (
            `id` INTEGER NOT NULL UNIQUE,
            `user_id` INTEGER NOT NULL UNIQUE,
            `lastValue` REAL,
            `isRun` INTEGER,
            PRIMARY KEY(`id` AUTOINCREMENT)
        );'''
    )
    conn.commit()
    conn.close()


db = Path('users.db')
try:
    db.resolve(strict=True)
except FileNotFoundError:
    try:
        create_database()
    except Exception as _:
        sys.exit(1)
    del db


def db_create_new_user(user_id: Union[str, int], is_run: Union[bool, int] = False):
    conn = init()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users(user_id, isRun) VALUES (?, ?)",
                       (user_id, int(is_run)))
    except sqlite3.IntegrityError:
        pass
    finally:
        conn.commit()
        conn.close()


def db_get_user_state(user_id: Union[str, int]) -> bool:
    conn = init()
    cursor = conn.cursor()
    res = cursor.execute(f"SELECT isRun FROM users WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    return res[0] if res else None


def db_get_last_value(user_id: Union[str, int]) -> float:
    conn = init()
    cursor = conn.cursor()
    res = cursor.execute(f"SELECT lastValue FROM users WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    return res[0] if res else None


def db_edit_user_state(user_id: Union[str, int], state: Union[bool, int]):
    conn = init()
    cursor = conn.cursor()
    cursor.execute(f"UPDATE users SET isRun=? WHERE user_id = ?", (state, user_id))
    conn.commit()
    conn.close()


def db_edit_last_value(user_id: Union[str, int], value: float):
    conn = init()
    cursor = conn.cursor()
    cursor.execute(f"UPDATE users SET lastValue=? WHERE user_id = ?", (value, user_id))
    conn.commit()
    conn.close()


def db_delete_user(user_id: int):
    conn = init()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()
