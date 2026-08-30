"""Construction lisible d'une mission par enchaînement. Voir chapitre 9."""
from missions.model import Mission, MissionAction


class MissionBuilder:
    def __init__(self, name: str):
        self.mission = Mission(name=name)

    def takeoff(self):
        self.mission.actions.append(MissionAction("takeoff"))
        return self

    def move(self, direction: str, distance: int):
        self.mission.actions.append(MissionAction("move", {"direction": direction, "distance": distance}))
        return self

    def rotate(self, degrees: int):
        self.mission.actions.append(MissionAction("rotate", {"degrees": degrees}))
        return self

    def wait(self, seconds: float):
        self.mission.actions.append(MissionAction("wait", {"seconds": seconds}))
        return self

    def photo(self):
        self.mission.actions.append(MissionAction("photo"))
        return self

    def land(self):
        self.mission.actions.append(MissionAction("land"))
        return self

    def build(self) -> Mission:
        return self.mission
