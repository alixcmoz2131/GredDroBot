# -*- coding: utf-8 -*-
"""
لایه‌ی دیتابیس (SQLite). همه‌ی چیزهایی که باید واقعی و پایدار باشن
(موجودی، تعداد زیرمجموعه، وضعیت برداشت‌ها، کانال‌های عضویت اجباری) اینجا ذخیره می‌شن.
"""

import sqlite3
from datetime import datetime, timezone

import config


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            balance REAL DEFAULT 0,
            referred_by INTEGER,
            referral_count INTEGER DEFAULT 0,
            awaiting_wallet INTEGER DEFAULT 0,
            joined_at TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS withdrawals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL,
            wallet_address TEXT,
            status TEXT DEFAULT 'pending',
            created_at TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS force_channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_ref TEXT UNIQUE
        )
        """
    )
    # --- مهاجرت ایمن: اگه از نسخه‌ی قدیمی‌تر (بدون UNIQUE) کانال‌های تکراری
    # تو دیتابیس مونده باشن، اینجا پاکشون می‌کنیم تا ایندکس یکتا با خطا مواجه نشه.
    conn.execute(
        "DELETE FROM force_channels WHERE id NOT IN "
        "(SELECT MIN(id) FROM force_channels GROUP BY chat_ref)"
    )
    conn.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_force_channels_chat_ref ON force_channels(chat_ref)"
    )
    conn.commit()
    conn.close()


# ---------- کاربرها ----------
def get_user(user_id: int):
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    return row


def get_or_create_user(user_id: int, username: str):
    """برمی‌گردونه (row, created) - created یعنی همین الان برای اولین‌بار ساخته شد."""
    row = get_user(user_id)
    if row is not None:
        return row, False

    conn = get_conn()
    conn.execute(
        "INSERT INTO users (user_id, username, balance, referral_count, joined_at) "
        "VALUES (?, ?, ?, 0, ?)",
        (user_id, username, config.STARTING_BALANCE, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    conn.close()
    return get_user(user_id), True


def add_balance(user_id: int, delta: float):
    conn = get_conn()
    conn.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (delta, user_id))
    conn.commit()
    conn.close()


def increment_referral_count(user_id: int):
    conn = get_conn()
    conn.execute(
        "UPDATE users SET referral_count = referral_count + 1 WHERE user_id = ?",
        (user_id,),
    )
    conn.commit()
    conn.close()


def set_awaiting_wallet(user_id: int, value: bool):
    conn = get_conn()
    conn.execute(
        "UPDATE users SET awaiting_wallet = ? WHERE user_id = ?",
        (1 if value else 0, user_id),
    )
    conn.commit()
    conn.close()


def get_all_user_ids():
    conn = get_conn()
    rows = conn.execute("SELECT user_id FROM users").fetchall()
    conn.close()
    return [r["user_id"] for r in rows]


def get_user_count() -> int:
    conn = get_conn()
    row = conn.execute("SELECT COUNT(*) AS c FROM users").fetchone()
    conn.close()
    return row["c"]


def get_top_referrers(limit: int = 3):
    conn = get_conn()
    rows = conn.execute(
        "SELECT user_id, username, referral_count FROM users "
        "WHERE referral_count > 0 ORDER BY referral_count DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return rows


# ---------- برداشت‌ها ----------
def create_withdrawal(user_id: int, amount: float, wallet_address: str) -> int:
    conn = get_conn()
    cur = conn.execute(
        "INSERT INTO withdrawals (user_id, amount, wallet_address, status, created_at) "
        "VALUES (?, ?, ?, 'pending', ?)",
        (user_id, amount, wallet_address, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    wid = cur.lastrowid
    conn.close()
    return wid


def get_withdrawal(wid: int):
    conn = get_conn()
    row = conn.execute("SELECT * FROM withdrawals WHERE id = ?", (wid,)).fetchone()
    conn.close()
    return row


def update_withdrawal_status(wid: int, status: str):
    conn = get_conn()
    conn.execute("UPDATE withdrawals SET status = ? WHERE id = ?", (status, wid))
    conn.commit()
    conn.close()


def get_pending_withdrawal(user_id: int):
    """اگه این کاربر یه درخواست برداشت داشته باشه که هنوز ادمین روش تصمیم نگرفته، برمی‌گردونه."""
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM withdrawals WHERE user_id = ? AND status = 'pending' "
        "ORDER BY id DESC LIMIT 1",
        (user_id,),
    ).fetchone()
    conn.close()
    return row


# ---------- کانال‌های عضویت اجباری ----------
def add_force_channel(chat_ref: str) -> bool:
    """
    اضافه می‌کنه؛ اگه از قبل (حتی با حروف بزرگ/کوچک متفاوت) وجود داشته باشه،
    دوباره اضافه نمی‌کنه. خروجی True یعنی واقعاً تازه اضافه شد، False یعنی از قبل بود.
    """
    normalized = chat_ref.strip().lower()
    conn = get_conn()
    cur = conn.execute(
        "INSERT OR IGNORE INTO force_channels (chat_ref) VALUES (?)", (normalized,)
    )
    conn.commit()
    inserted = cur.rowcount > 0
    conn.close()
    return inserted


def get_force_channels():
    conn = get_conn()
    rows = conn.execute("SELECT chat_ref FROM force_channels").fetchall()
    conn.close()
    return [r["chat_ref"] for r in rows]


def get_force_channels_full():
    """برای پنل مدیریت - هر ردیف با id (برای حذف) و chat_ref."""
    conn = get_conn()
    rows = conn.execute("SELECT id, chat_ref FROM force_channels").fetchall()
    conn.close()
    return rows


def remove_force_channel(channel_id: int):
    conn = get_conn()
    conn.execute("DELETE FROM force_channels WHERE id = ?", (channel_id,))
    conn.commit()
    conn.close()

