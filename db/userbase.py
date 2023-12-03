# -*- coding: utf-8 -*-
import sqlite3
import sys

from pathlib import Path
from typing import Union

__all__ = [
    "db_delete_user", "db_get_user_state", "db_edit_user_state", "db_create_new_user",
    "db_get_last_value", "db_edit_last_value", "db_get_last_activity", "db_edit_last_activity",
    "db_get_language_code", "db_edit_language_code", "db_get_all_users"
]

USER_CHAT_ID = Union[str, int]


def init() -> sqlite3.Connection:
    connect = sqlite3.connect('./db/users.db', check_same_thread=False)
    connect.execute("pragma journal_mode=wal;")
    return connect


def create_database():
    conn = init()
    cur = conn.cursor()
    cur.execute(
        '''CREATE TABLE `users` (
            `id` INTEGER NOT NULL UNIQUE,
            `user_id` INTEGER NOT NULL UNIQUE,
            `chat_id` INTEGER NOT NULL UNIQUE,
            `lastValue` REAL,
            `isRun` INTEGER default 0,
            `lastActivity` INTEGER,
            `language` STRING default "en",
            PRIMARY KEY(`id` AUTOINCREMENT)
        );'''
    )
    conn.commit()
    conn.close()


db = Path('./db/users.db')
try:
    db.resolve(strict=True)
except FileNotFoundError:
    try:
        create_database()
    except Exception as _:
        sys.exit(1)
finally:
    del db


def db_create_new_user(
    user_id: USER_CHAT_ID, chat_id: USER_CHAT_ID, last_activity: int, is_run: Union[bool, int] = False
):
    conn = init()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users(user_id, chat_id, isRun, lastActivity) VALUES (?, ?, ?, ?)",
                       (user_id, chat_id, int(is_run), last_activity))
    except sqlite3.IntegrityError:
        pass
    finally:
        conn.commit()
        conn.close()


def db_get_user_state(chat_id: USER_CHAT_ID) -> bool:
    conn = init()
    cursor = conn.cursor()
    res = cursor.execute("SELECT isRun FROM users WHERE chat_id=?", (chat_id,)).fetchone()
    conn.close()
    return res[0] if res else None


def db_get_last_value(chat_id: USER_CHAT_ID) -> float:
    conn = init()
    cursor = conn.cursor()
    res = cursor.execute("SELECT lastValue FROM users WHERE chat_id=?", (chat_id,)).fetchone()
    conn.close()
    return res[0] if res else None


def db_get_last_activity():
    conn = init()
    cursor = conn.cursor()
    res = cursor.execute("SELECT lastActivity, user_id FROM users").fetchall()
    conn.close()
    return res


def db_get_all_users():
    conn = init()
    cursor = conn.cursor()
    res = cursor.execute("SELECT isRun, user_id FROM users").fetchall()
    conn.close()
    return res


def db_get_language_code(user_id: USER_CHAT_ID) -> str:
    conn = init()
    cursor = conn.cursor()
    res = cursor.execute("SELECT language FROM users WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    return res[0] if res else None


def db_edit_user_state(chat_id: USER_CHAT_ID, state: Union[bool, int]):
    conn = init()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET isRun=? WHERE chat_id = ?", (state, chat_id))
    conn.commit()
    conn.close()


def db_edit_last_value(chat_id: USER_CHAT_ID, value: float):
    conn = init()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET lastValue=? WHERE chat_id = ?", (value, chat_id))
    conn.commit()
    conn.close()


def db_edit_last_activity(chat_id: USER_CHAT_ID, time: int):
    conn = init()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET lastActivity=? WHERE chat_id = ?", (time, chat_id))
    conn.commit()
    conn.close()


def db_edit_language_code(user_id: USER_CHAT_ID, language_code: Union[str, int]):
    if type(language_code) is int:
        language_code = 'ru' if language_code else 'en'
    conn = init()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET language=? WHERE user_id=?", (language_code, user_id))
    conn.commit()
    conn.close()


def db_delete_user(user_id: int):
    conn = init()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()
