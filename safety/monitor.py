"""Garde-fous de sécurité, indépendants de l'interface et des missions.

Voir chapitre 10 du livre. Version corrigée : la comparaison d'altitude se
fait bien en centimètres des deux côtés (get_height() renvoie des cm).
"""
import threading
import time


class SafetyMonitor:
    def __init__(self, controller, min_battery=15, max_height_cm=300):
        self.controller = controller
        self.min_battery = min_battery
        self.max_height_cm = max_height_cm
        self.on_alert = None  # callback(message: str) branché par l'interface

    def start(self, interval=1.0):
        threading.Thread(target=self._loop, args=(interval,), daemon=True).start()

    def _loop(self, interval):
        while True:
            if self.controller.is_connected and not self.controller.emergency:
                self._check_battery()
                self._check_height()
            time.sleep(interval)

    def _check_battery(self):
        battery = self.controller.get_battery()
        if battery < self.min_battery:
            self._trigger(f"Batterie critique ({battery}%) — atterrissage forcé")
            self.controller.emergency_stop()

    def _check_height(self):
        height = self.controller.get_height()  # en cm, comme max_height_cm
        if height > self.max_height_cm:
            self._trigger(f"Altitude maximale dépassée ({height} cm)")
            self.controller.move("down", 30)

    def _trigger(self, message):
        if self.on_alert:
            self.on_alert(message)

    def can_takeoff(self) -> tuple[bool, str]:
        if not self.controller.is_connected:
            return False, "Drone non connecté"
        battery = self.controller.get_battery()
        if battery < 30:
            return False, f"Batterie insuffisante pour décoller ({battery}%)"
        return True, ""
