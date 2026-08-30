"""Transforme une détection de VisionPipeline en commande RC. Voir chapitre 8."""

FRAME_WIDTH = 960
FRAME_HEIGHT = 720
CENTER_X, CENTER_Y = FRAME_WIDTH // 2, FRAME_HEIGHT // 2
TARGET_SIZE = 120


class FollowController:
    def __init__(self, gain=0.3, max_speed=40):
        self.gain = gain
        self.max_speed = max_speed
        self.lost_count = 0
        self.max_lost = 20

    def compute(self, detection):
        if detection is None:
            self.lost_count += 1
            if self.lost_count > self.max_lost:
                return (0, 0, 0, 0)  # cible perdue : on arrête proprement
            return None  # dernière commande conservée le temps de retrouver la cible

        self.lost_count = 0
        error_x = detection["cx"] - CENTER_X
        error_y = detection["cy"] - CENTER_Y

        yaw = self._clamp(error_x * self.gain / 10)
        vertical = self._clamp(-error_y * self.gain / 10)
        return (0, 0, vertical, yaw)

    def compute_with_distance(self, detection):
        base = self.compute(detection)
        if base is None or detection is None:
            return base
        size_error = TARGET_SIZE - detection["size"]
        forward = self._clamp(size_error * self.gain / 10)
        lr, _, vertical, yaw = base
        return (lr, forward, vertical, yaw)

    def _clamp(self, value):
        return max(-self.max_speed, min(self.max_speed, int(value)))
