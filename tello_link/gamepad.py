"""Pilotage à la manette, avec dead zone. Voir chapitre 4 du livre."""
import pygame

from tello_link.input import ControllerInput

DEAD_ZONE = 0.10


def apply_dead_zone(value: float, threshold: float = DEAD_ZONE) -> float:
    return 0.0 if abs(value) < threshold else value


def read_gamepad(joystick) -> ControllerInput:
    pygame.event.pump()
    return ControllerInput(
        forward=apply_dead_zone(-joystick.get_axis(1)),
        strafe=apply_dead_zone(joystick.get_axis(0)),
        vertical=apply_dead_zone(-joystick.get_axis(3)),
        yaw=apply_dead_zone(joystick.get_axis(2)),
    )
