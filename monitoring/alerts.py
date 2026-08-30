"""Gestionnaire d'alertes centralisé, avec niveau de criticité.

Voir chapitre 12 du livre.
"""
from enum import Enum


class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertManager:
    def __init__(self, recorder):
        self.recorder = recorder
        self.listeners = []  # callables(level, message) branchés par l'interface

    def raise_alert(self, level: AlertLevel, message: str):
        self.recorder.log_event(level.value, message)
        for listener in self.listeners:
            listener(level, message)

    def subscribe(self, listener):
        self.listeners.append(listener)
