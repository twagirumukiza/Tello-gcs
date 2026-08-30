"""Enregistrement automatique d'un vol en base. Voir chapitre 12 du livre.

Version corrigée : max_battery_used est réellement calculé via
record_battery(), appelée à chaque mise à jour de télémétrie.
"""
from datetime import datetime


class FlightRecorder:
    def __init__(self, conn):
        self.conn = conn
        self.flight_id = None
        self._battery_start = None

    def start_flight(self, mission_name=None, battery_start=None):
        self._battery_start = battery_start
        cursor = self.conn.execute(
            "INSERT INTO flights (started_at, mission_name, max_battery_used) VALUES (?, ?, 0)",
            (datetime.now().isoformat(), mission_name),
        )
        self.conn.commit()
        self.flight_id = cursor.lastrowid

    def record_battery(self, current_battery: int):
        """À appeler à chaque mise à jour de télémétrie (chapitre 5) pour
        tenir à jour la consommation maximale observée pendant le vol."""
        if self.flight_id is None or self._battery_start is None:
            return
        used = max(0, self._battery_start - current_battery)
        self.conn.execute(
            "UPDATE flights SET max_battery_used = MAX(max_battery_used, ?) WHERE id = ?",
            (used, self.flight_id),
        )
        self.conn.commit()

    def log_event(self, level: str, message: str):
        if self.flight_id is None:
            return
        self.conn.execute(
            "INSERT INTO flight_events (flight_id, timestamp, level, message) VALUES (?, ?, ?, ?)",
            (self.flight_id, datetime.now().isoformat(), level, message),
        )
        self.conn.commit()

    def end_flight(self):
        self.conn.execute(
            "UPDATE flights SET ended_at = ? WHERE id = ?",
            (datetime.now().isoformat(), self.flight_id),
        )
        self.conn.commit()
        self.flight_id = None
