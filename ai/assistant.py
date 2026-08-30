"""Convertit une instruction en langage naturel en mission JSON validée.

Voir chapitre 11 du livre. Exemples écrits et testés avec le modèle
claude-sonnet-4-6 (API Anthropic, janvier 2026) — si ce nom de modèle n'est
plus reconnu, remplace MODEL_NAME par le modèle courant recommandé dans la
documentation Anthropic, le reste du code n'a pas besoin de changer.
"""
import json

from anthropic import Anthropic

client = Anthropic()

MODEL_NAME = "claude-sonnet-4-6"

SYSTEM_PROMPT = """Tu convertis une instruction de pilotage de drone en mission JSON.
Réponds UNIQUEMENT avec un objet JSON de la forme :
{"name": "...", "actions": [{"type": "...", "params": {...}}]}

Types d'actions valides : takeoff, land, move (params: direction, distance en cm),
rotate (params: degrees), wait (params: seconds), photo.
Directions valides pour move : forward, back, left, right.
N'invente aucun autre type d'action. Distance maximale par déplacement : 300 cm."""


class MissionParsingError(Exception):
    pass


def build_mission_from_text(instruction: str) -> dict:
    response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": instruction}],
    )
    text = response.content[0].text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise MissionParsingError(f"Réponse IA non-JSON : {text[:200]!r}") from exc


def prepare_mission_from_instruction(instruction: str):
    from ai.validation import validate_mission_dict
    from missions.model import Mission

    data = build_mission_from_text(instruction)
    validate_mission_dict(data)  # lève une exception si la mission est dangereuse
    return Mission.from_json(json.dumps(data))


def explain_flight_log(log_lines: list[str]) -> str:
    response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=500,
        messages=[
            {
                "role": "user",
                "content": (
                    "Explique en deux phrases ce qui s'est passé pendant ce vol, "
                    "pour un pilote débutant :\n" + "\n".join(log_lines)
                ),
            }
        ],
    )
    return response.content[0].text
