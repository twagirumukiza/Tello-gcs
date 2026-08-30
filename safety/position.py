"""Estimation de position par intégration des déplacements commandés.

Cette position est une ESTIMATION, pas une mesure : le Tello n'a pas de GPS
ni de capteurs latéraux, la dérive s'accumule à chaque commande.
Voir chapitre 10 du livre.
"""
import math

from missions.builder import MissionBuilder
from missions.model import Mission


class PositionEstimator:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.heading = 0.0  # degrés, 0 = orientation de départ

    def register_move(self, direction: str, distance_cm: float):
        rad = math.radians(self.heading)
        dx, dy = {
            "forward": (math.sin(rad), math.cos(rad)),
            "back": (-math.sin(rad), -math.cos(rad)),
            "left": (-math.cos(rad), math.sin(rad)),
            "right": (math.cos(rad), -math.sin(rad)),
        }.get(direction, (0, 0))
        self.x += dx * distance_cm
        self.y += dy * distance_cm

    def register_rotation(self, degrees: float):
        self.heading = (self.heading + degrees) % 360

    def reset(self):
        self.x = self.y = self.heading = 0.0

    def vector_to_origin(self) -> tuple[float, float]:
        distance = math.hypot(self.x, self.y)
        angle_to_origin = math.degrees(math.atan2(-self.x, -self.y))
        turn_needed = (angle_to_origin - self.heading) % 360
        return distance, turn_needed


def build_return_mission(estimator: PositionEstimator) -> Mission:
    distance, turn = estimator.vector_to_origin()
    return (
        MissionBuilder("Retour position estimée")
        .rotate(int(turn))
        .move("forward", int(distance))
        .land()
        .build()
    )
