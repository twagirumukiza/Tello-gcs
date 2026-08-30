"""Configuration externalisée. Voir chapitre 13 du livre."""
import os
from dataclasses import dataclass


@dataclass
class Config:
    anthropic_api_key: str
    min_battery: int = 15
    max_height_cm: int = 300
    max_mission_actions: int = 30

    @staticmethod
    def load() -> "Config":
        return Config(
            anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
            min_battery=int(os.environ.get("TELLO_MIN_BATTERY", 15)),
            max_height_cm=int(os.environ.get("TELLO_MAX_HEIGHT", 300)),
        )
