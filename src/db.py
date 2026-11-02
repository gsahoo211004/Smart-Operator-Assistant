"""Project root and SQLite bootstrap."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DB_PATH = ROOT / "operator_assistant.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def _load_json(name: str) -> list | dict:
    path = DATA_DIR / name
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def init_db(force: bool = False) -> None:
    if DB_PATH.exists() and not force:
        return

    if force and DB_PATH.exists():
        DB_PATH.unlink()

    conn = get_connection()
    cur = conn.cursor()

    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS telemetry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            machine_id TEXT,
            operator_id TEXT,
            engine_hours REAL,
            fuel_used_l REAL,
            load_cycles INTEGER,
            idling_time_min INTEGER,
            seatbelt_status TEXT,
            safety_alert_triggered INTEGER
        );

        CREATE TABLE IF NOT EXISTS task_history (
            task_id TEXT PRIMARY KEY,
            task_type TEXT,
            weather TEXT,
            operator_skill TEXT,
            machine_age_yrs INTEGER,
            estimated_time_min INTEGER,
            actual_time_min INTEGER
        );

        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT,
            machine_id TEXT,
            operator_id TEXT,
            description TEXT,
            working_conditions TEXT,
            severity TEXT
        );

        CREATE TABLE IF NOT EXISTS training_bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT,
            module_id TEXT,
            operator_id TEXT,
            preferred_date TEXT,
            notes TEXT
        );
        """
    )

    cur.execute("DELETE FROM telemetry")
    for row in _load_json("telemetry.json"):
        cur.execute(
            """
            INSERT INTO telemetry (
                timestamp, machine_id, operator_id, engine_hours, fuel_used_l,
                load_cycles, idling_time_min, seatbelt_status, safety_alert_triggered
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["timestamp"],
                row["machine_id"],
                row["operator_id"],
                row["engine_hours"],
                row["fuel_used_l"],
                row["load_cycles"],
                row["idling_time_min"],
                row["seatbelt_status"],
                1 if row["safety_alert_triggered"] else 0,
            ),
        )

    cur.execute("DELETE FROM task_history")
    for row in _load_json("tasks.json"):
        cur.execute(
            """
            INSERT INTO task_history (
                task_id, task_type, weather, operator_skill, machine_age_yrs,
                estimated_time_min, actual_time_min
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["task_id"],
                row["task_type"],
                row["weather"],
                row["operator_skill"],
                row["machine_age_yrs"],
                row["estimated_time_min"],
                row["actual_time_min"],
            ),
        )

    conn.commit()
    conn.close()
