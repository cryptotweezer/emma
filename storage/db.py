import sqlite3
import os
from typing import Optional

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
DB_PATH = os.path.join(DB_DIR, 'emma.db')


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = _get_conn()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                market_id TEXT NOT NULL,
                question TEXT NOT NULL,
                side TEXT NOT NULL,
                amount_sim REAL NOT NULL,
                entry_price REAL NOT NULL,
                metaculus_prob REAL,
                manifold_prob REAL,
                edge REAL NOT NULL,
                kelly_fraction REAL NOT NULL,
                status TEXT DEFAULT 'open',
                exit_price REAL,
                pnl_sim REAL,
                resolved_at TEXT
            );

            CREATE TABLE IF NOT EXISTS daily_snapshots (
                date TEXT PRIMARY KEY,
                balance_sim REAL,
                daily_pnl REAL,
                total_trades INTEGER DEFAULT 0,
                win_trades INTEGER DEFAULT 0,
                loss_trades INTEGER DEFAULT 0,
                win_rate REAL DEFAULT 0.0,
                open_positions INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS signal_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                market_id TEXT,
                question TEXT NOT NULL,
                metaculus_prob REAL,
                manifold_prob REAL,
                polymarket_price REAL,
                edge REAL,
                action TEXT NOT NULL,
                skip_reason TEXT
            );
        """)
        conn.commit()
    finally:
        conn.close()


def save_trade(trade_dict: dict) -> int:
    conn = _get_conn()
    try:
        cur = conn.execute(
            """INSERT INTO trades
               (timestamp, market_id, question, side, amount_sim,
                entry_price, metaculus_prob, manifold_prob, edge,
                kelly_fraction)
               VALUES (:timestamp, :market_id, :question, :side, :amount,
                       :entry_price, :metaculus_prob, :manifold_prob,
                       :edge, :kelly_fraction)""",
            trade_dict
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def save_signal(signal_dict: dict):
    conn = _get_conn()
    try:
        conn.execute(
            """INSERT INTO signal_log
               (timestamp, market_id, question, metaculus_prob,
                manifold_prob, polymarket_price, edge, action, skip_reason)
               VALUES (:timestamp, :market_id, :question, :metaculus_prob,
                       :manifold_prob, :polymarket_price, :edge,
                       :action, :skip_reason)""",
            signal_dict
        )
        conn.commit()
    finally:
        conn.close()


def get_open_trades() -> list:
    conn = _get_conn()
    try:
        rows = conn.execute(
            "SELECT * FROM trades WHERE status = 'open' ORDER BY timestamp"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_daily_stats(date_str: str) -> dict:
    conn = _get_conn()
    try:
        row = conn.execute(
            "SELECT * FROM daily_snapshots WHERE date = ?", (date_str,)
        ).fetchone()
        if row:
            return dict(row)
        return {
            'date': date_str,
            'balance_sim': None,
            'daily_pnl': 0.0,
            'total_trades': 0,
            'win_trades': 0,
            'loss_trades': 0,
            'win_rate': 0.0,
            'open_positions': 0,
        }
    finally:
        conn.close()


def get_total_pnl() -> float:
    conn = _get_conn()
    try:
        row = conn.execute(
            "SELECT SUM(pnl_sim) FROM trades WHERE status = 'closed'"
        ).fetchone()
        return row[0] or 0.0
    finally:
        conn.close()


def get_win_rate() -> float:
    conn = _get_conn()
    try:
        row = conn.execute(
            """SELECT
                   COUNT(*) as total,
                   SUM(CASE WHEN pnl_sim > 0 THEN 1 ELSE 0 END) as wins
               FROM trades WHERE status = 'closed'"""
        ).fetchone()
        total = row['total'] or 0
        wins = row['wins'] or 0
        return wins / total if total > 0 else 0.0
    finally:
        conn.close()
