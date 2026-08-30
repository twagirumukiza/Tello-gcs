"""Flux vidéo décodé dans son propre thread, HUD, enregistrement et capture.

Voir chapitres 6 et 7 du livre (intégration du pipeline de vision).
"""
import os
import time

import cv2
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage


def draw_hud(frame, state: dict):
    battery = state.get("bat", "—")
    height = state.get("h", "—")
    yaw = state.get("yaw", "—")

    cv2.putText(frame, f"BAT {battery}%", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    cv2.putText(frame, f"ALT {height} cm", (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    cv2.putText(frame, f"YAW {yaw}", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    return frame


class VideoWorker(QThread):
    frame_ready = Signal(QImage)
    detection_ready = Signal(object)
    stream_lost = Signal()

    def __init__(self, controller, vision_pipeline=None):
        super().__init__()
        self.controller = controller
        self.vision_pipeline = vision_pipeline
        self._running = True
        self.latest_frame = None
        self.latest_state: dict = {}

    def run(self):
        self.controller.streamon()
        reader = self.controller.get_frame_read()
        empty_count = 0
        while self._running:
            frame = reader.frame
            if frame is None:
                empty_count += 1
                if empty_count > 30:
                    self.stream_lost.emit()
                continue
            empty_count = 0

            detection = None
            if self.vision_pipeline and self.vision_pipeline.mode:
                detection = self.vision_pipeline.process(frame)
                if detection:
                    cv2.circle(frame, (detection["cx"], detection["cy"]), 8, (0, 0, 255), 2)
            self.detection_ready.emit(detection)

            frame = draw_hud(frame, self.latest_state)
            self.latest_frame = frame
            self.frame_ready.emit(self._to_qimage(frame))

    def _to_qimage(self, frame) -> QImage:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        return QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)

    def stop(self):
        self._running = False
        self.controller.streamoff()


class VideoRecorder:
    def __init__(self, path="recordings"):
        self.path = path
        os.makedirs(self.path, exist_ok=True)
        self._writer = None

    def start(self, frame_size):
        filename = f"{self.path}/vol_{int(time.time())}.avi"
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        self._writer = cv2.VideoWriter(filename, fourcc, 25, frame_size)

    def write(self, frame):
        if self._writer:
            self._writer.write(frame)

    def stop(self):
        if self._writer:
            self._writer.release()
            self._writer = None

    def capture_photo(self, frame, path="captures") -> str:
        os.makedirs(path, exist_ok=True)
        filename = f"{path}/photo_{int(time.time())}.jpg"
        cv2.imwrite(filename, frame)
        return filename
