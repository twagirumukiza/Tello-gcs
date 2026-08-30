"""Modèle de mission sérialisable en JSON. Voir chapitre 9 du livre."""
import json
from dataclasses import asdict, dataclass, field


@dataclass
class MissionAction:
    type: str  # "move", "rotate", "wait", "takeoff", "land", "photo"
    params: dict = field(default_factory=dict)


@dataclass
class Mission:
    name: str
    actions: list[MissionAction] = field(default_factory=list)

    def to_json(self) -> str:
        return json.dumps(
            {"name": self.name, "actions": [asdict(a) for a in self.actions]}, indent=2
        )

    @staticmethod
    def from_json(text: str) -> "Mission":
        data = json.loads(text)
        actions = [MissionAction(**a) for a in data["actions"]]
        return Mission(name=data["name"], actions=actions)

    def save(self, path: str):
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.to_json())

    @staticmethod
    def load(path: str) -> "Mission":
        with open(path, encoding="utf-8") as f:
            return Mission.from_json(f.read())
