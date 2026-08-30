"""Garde-fous appliqués à toute mission générée par l'assistant IA.

Voir chapitre 11 du livre.
"""

ALLOWED_TYPES = {"takeoff", "land", "move", "rotate", "wait", "photo"}
ALLOWED_DIRECTIONS = {"forward", "back", "left", "right"}
MAX_DISTANCE_CM = 300
MAX_ACTIONS = 30


class MissionValidationError(Exception):
    pass


def validate_mission_dict(data: dict):
    actions = data.get("actions", [])
    if len(actions) > MAX_ACTIONS:
        raise MissionValidationError(f"Mission trop longue ({len(actions)} actions)")

    for action in actions:
        action_type = action.get("type")
        if action_type not in ALLOWED_TYPES:
            raise MissionValidationError(f"Type d'action inconnu : {action_type}")

        if action_type == "move":
            direction = action["params"].get("direction")
            distance = action["params"].get("distance", 0)
            if direction not in ALLOWED_DIRECTIONS:
                raise MissionValidationError(f"Direction invalide : {direction}")
            if not (0 < distance <= MAX_DISTANCE_CM):
                raise MissionValidationError(f"Distance hors limites : {distance} cm")

        if action_type == "rotate":
            degrees = action["params"].get("degrees", 0)
            if abs(degrees) > 360:
                raise MissionValidationError(f"Rotation hors limites : {degrees}°")
