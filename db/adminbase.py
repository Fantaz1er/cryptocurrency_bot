# -*- coding: utf-8 -*-
import sqlite3
import sys

from pathlib import Path
from typing import Union, Optional

__all__ = [
    "db_add_new_administrator", "db_check_is_admin", "db_get_last_admin_activity", "db_change_last_activity",
    "db_get_admins_list", "db_change_admin_rang"
]
ADMIN_ID = Union[str, int]


def init() -> sqlite3.Connection:
    connect = sqlite3.connect('./db/admins.db', check_same_thread=False)
    connect.execute("pragma journal_mode=wal;")
    return connect


def create_database():
    conn = init()
    cur = conn.cursor()
    cur.execute(
        '''CREATE TABLE `admins` (
            `id` INTEGER NOT NULL UNIQUE,
            `admin_id` INTEGER NOT NULL UNIQUE,
            `rang` INTEGER default 1,
            `lastActivity` INTEGER,
            PRIMARY KEY(`id` AUTOINCREMENT)
        );'''
    )
    conn.commit()
    conn.close()


db = Path('./db/admins.db')
try:
    db.resolve(strict=True)
except FileNotFoundError:
    try:
        create_database()
    except Exception as _:
        sys.exit(1)
finally:
    del db


def db_add_new_administrator(user_id: ADMIN_ID):
    conn = init()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO admins(admin_id) VALUES (?)", (user_id,))
    except sqlite3.IntegrityError:
        pass
    finally:
        conn.commit()
        conn.close()


def db_check_is_admin(admin_id: ADMIN_ID) -> Union[int, bool]:
    """Check user on admin status. If user in admin table return him rang else return False"""
    conn = init()
    cursor = conn.cursor()
    res = cursor.execute("SELECT rang FROM `admins` WHERE admin_id=?", (admin_id,)).fetchone()
    conn.close()
    return res[0] if res else False


def db_get_admins_list() -> Optional[list]:
    conn = init()
    cursor = conn.cursor()
    res = cursor.execute("SELECT admin_id FROM `admins`").fetchall()
    conn.close()
    return res if res else None


def db_get_last_admin_activity(admin_id: ADMIN_ID) -> Optional[int]:
    conn = init()
    cursor = conn.cursor()
    res = cursor.execute("SELECT lastActivity FORM `admins` WHERE admin_id=?", (admin_id,))
    conn.close()
    return res if res else None


def db_change_last_activity(admin_id: ADMIN_ID, value: Optional[int]) -> None:
    conn = init()
    cursor = conn.cursor()
    cursor.execute("UPDATE `admins` SET lastActivity=? WHERE admin_id=?", (value, admin_id,))
    conn.commit()
    conn.close()


def db_change_admin_rang(admin_id: ADMIN_ID, rang: Optional[int] = None) -> None:
    current_rang = db_check_is_admin(admin_id)
    if not current_rang:
        return
    if rang is None:
        rang = current_rang + 1
    conn = init()
    cursor = conn.cursor()
    cursor.execute("UPDATE `admins` SET rang=? WHERE admin_id=?", (rang, admin_id,))
    conn.commit()
    conn.close()
