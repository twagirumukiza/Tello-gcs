"""Schéma SQLite de l'historique des vols. Voir chapitre 12 du livre."""
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS flights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    max_battery_used INTEGER,
    mission_name TEXT
);

CREATE TABLE IF NOT EXISTS flight_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    flight_id INTEGER REFERENCES flights(id),
    timestamp TEXT NOT NULL,
    level TEXT NOT NULL,
    message TEXT NOT NULL
);
"""


def get_connection(path="tello_gcs.db"):
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA)
    return conn
