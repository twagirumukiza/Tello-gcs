"""Récupération continue de l'état du drone et filtrage. Voir chapitre 5."""
import time
from collections import deque

from PySide6.QtCore import QThread, Signal


class TelemetryWorker(QThread):
    updated = Signal(dict)

    def __init__(self, controller, interval=0.2):
        super().__init__()
        self.controller = controller
        self.interval = interval
        self._running = True

    def run(self):
        while self._running:
            if self.controller.is_connected:
                state = self.controller.get_current_state()
                self.updated.emit(state)
            time.sleep(self.interval)

    def stop(self):
        self._running = False


class MovingAverage:
    def __init__(self, size=5):
        self.values = deque(maxlen=size)

    def update(self, value: float) -> float:
        self.values.append(value)
        return sum(self.values) / len(self.values)


class TelemetryFilter:
    """Lisse les valeurs bruitées (hauteur, vitesses). La batterie et le yaw
    ne sont volontairement pas filtrés : ce sont des valeurs déjà stables
    côté Tello, un lissage y ajouterait juste de la latence perçue."""

    def __init__(self):
        self._filters = {
            "h": MovingAverage(),
            "vgx": MovingAverage(),
            "vgy": MovingAverage(),
            "vgz": MovingAverage(),
        }

    def apply(self, state: dict) -> dict:
        filtered = dict(state)
        for key, filt in self._filters.items():
            if key in state:
                filtered[key] = filt.update(state[key])
        return filtered
