"""Format d'entrée de pilotage unique, indépendant de sa source (clavier,
manette, ou plus tard interface tactile). Voir chapitre 4 du livre.
"""
from dataclasses import dataclass


@dataclass
class ControllerInput:
    forward: float = 0.0
    strafe: float = 0.0
    vertical: float = 0.0
    yaw: float = 0.0

    def as_rc(self, max_speed=60) -> tuple[int, int, int, int]:
        return (
            int(self.strafe * max_speed),
            int(self.forward * max_speed),
            int(self.vertical * max_speed),
            int(self.yaw * max_speed),
        )
