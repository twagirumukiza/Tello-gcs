from missions.engine import MissionEngine
from missions.model import Mission, MissionAction


class FakeTelloController:
    """Contrôleur factice, sans matériel, pour tester le moteur de missions."""

    emergency = False

    def __init__(self):
        self.calls = []

    def takeoff(self):
        self.calls.append(("takeoff", ()))

    def land(self):
        self.calls.append(("land", ()))

    def move(self, direction, distance):
        self.calls.append(("move", (direction, distance)))

    def rotate_clockwise(self, degrees):
        self.calls.append(("rotate_clockwise", (degrees,)))


def test_mission_executes_actions_in_order():
    controller = FakeTelloController()
    mission = Mission("Test", [
        MissionAction("takeoff"),
        MissionAction("move", {"direction": "forward", "distance": 50}),
        MissionAction("land"),
    ])
    engine = MissionEngine(controller)
    engine.run(mission)
    assert [call[0] for call in controller.calls] == ["takeoff", "move", "land"]


def test_mission_stops_on_emergency():
    controller = FakeTelloController()
    controller.emergency = True
    mission = Mission("Test", [MissionAction("takeoff"), MissionAction("land")])
    engine = MissionEngine(controller)
    engine.run(mission)
    assert controller.calls == []


def test_unknown_action_type_stops_mission():
    controller = FakeTelloController()
    mission = Mission("Test", [MissionAction("dance")])
    engine = MissionEngine(controller)
    engine.run(mission)
    assert "Mission arrêtée" in engine.log[0]


def test_photo_without_callback_stops_mission():
    controller = FakeTelloController()
    mission = Mission("Test", [MissionAction("photo")])
    engine = MissionEngine(controller)
    engine.run(mission)
    assert "Mission arrêtée" in engine.log[0]


def test_photo_with_callback_is_called():
    controller = FakeTelloController()
    calls = []
    engine = MissionEngine(controller, photo_callback=lambda: calls.append(1))
    mission = Mission("Test", [MissionAction("photo")])
    engine.run(mission)
    assert calls == [1]
