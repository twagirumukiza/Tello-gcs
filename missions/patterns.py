"""Générateurs de parcours prédéfinis. Voir chapitre 9 du livre."""
from missions.builder import MissionBuilder
from missions.model import Mission


def square(side_cm=100) -> Mission:
    builder = MissionBuilder("Carré").takeoff()
    for _ in range(4):
        builder.move("forward", side_cm).rotate(90)
    return builder.land().build()


def triangle(side_cm=100) -> Mission:
    builder = MissionBuilder("Triangle").takeoff()
    for _ in range(3):
        builder.move("forward", side_cm).rotate(120)
    return builder.land().build()


def spiral(steps=6, start_cm=30, increment_cm=15, turn_degrees=60) -> Mission:
    builder = MissionBuilder("Spirale").takeoff()
    distance = start_cm
    for _ in range(steps):
        builder.move("forward", distance).rotate(turn_degrees)
        distance += increment_cm
    return builder.land().build()
