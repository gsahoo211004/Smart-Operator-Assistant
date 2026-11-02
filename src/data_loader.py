"""Load seed data into pandas and SQLite."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.db import DATA_DIR, get_connection, init_db

ROOT = Path(__file__).resolve().parents[1]


def ensure_data() -> None:
    init_db()


def load_telemetry() -> pd.DataFrame:
    ensure_data()
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM telemetry ORDER BY timestamp", conn)
    conn.close()
    df["safety_alert_triggered"] = df["safety_alert_triggered"].astype(bool)
    return df


def load_task_history() -> pd.DataFrame:
    ensure_data()
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM task_history", conn)
    conn.close()
    return df


def load_today_tasks() -> pd.DataFrame:
    path = DATA_DIR / "today_tasks.json"
    with path.open(encoding="utf-8") as f:
        rows = json.load(f)
    return pd.DataFrame(rows)


def load_training_modules() -> pd.DataFrame:
    path = DATA_DIR / "training_modules.json"
    with path.open(encoding="utf-8") as f:
        rows = json.load(f)
    return pd.DataFrame(rows)


def insert_incident(
    machine_id: str,
    operator_id: str,
    description: str,
    working_conditions: str,
    severity: str,
) -> None:
    ensure_data()
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO incidents (created_at, machine_id, operator_id, description, working_conditions, severity)
        VALUES (datetime('now'), ?, ?, ?, ?, ?)
        """,
        (machine_id, operator_id, description, working_conditions, severity),
    )
    conn.commit()
    conn.close()


def load_incidents() -> pd.DataFrame:
    ensure_data()
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM incidents ORDER BY id DESC",
        conn,
    )
    conn.close()
    return df


def insert_training_booking(
    module_id: str,
    operator_id: str,
    preferred_date: str,
    notes: str,
) -> None:
    ensure_data()
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO training_bookings (created_at, module_id, operator_id, preferred_date, notes)
        VALUES (datetime('now'), ?, ?, ?, ?)
        """,
        (module_id, operator_id, preferred_date, notes),
    )
    conn.commit()
    conn.close()


def load_training_bookings() -> pd.DataFrame:
    ensure_data()
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM training_bookings ORDER BY id DESC",
        conn,
    )
    conn.close()
    return df
