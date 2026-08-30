import pytest

from ai.validation import MissionValidationError, validate_mission_dict


def test_rejects_excessive_distance():
    data = {"actions": [{"type": "move", "params": {"direction": "forward", "distance": 999}}]}
    with pytest.raises(MissionValidationError):
        validate_mission_dict(data)


def test_accepts_valid_mission():
    data = {"actions": [{"type": "move", "params": {"direction": "forward", "distance": 100}}]}
    validate_mission_dict(data)  # ne doit pas lever d'exception


def test_photo_action_is_allowed():
    data = {"actions": [{"type": "photo", "params": {}}]}
    validate_mission_dict(data)  # ne doit pas lever d'exception


def test_rejects_unknown_type():
    data = {"actions": [{"type": "dance", "params": {}}]}
    with pytest.raises(MissionValidationError):
        validate_mission_dict(data)
