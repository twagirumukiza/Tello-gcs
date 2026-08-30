"""Pipeline de vision unique, configurable par mode. Voir chapitre 7 du livre."""
import cv2
import numpy as np

# Plage HSV par défaut (orange vif) — à ajuster selon la cible réelle.
HSV_LOWER = np.array([5, 150, 150])
HSV_UPPER = np.array([15, 255, 255])


class VisionPipeline:
    def __init__(self):
        self.mode = None
        self._face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        self._qr_detector = cv2.QRCodeDetector()

    def set_mode(self, mode: str):
        self.mode = mode

    def process(self, frame):
        if self.mode == "face":
            return self._detect_face(frame)
        if self.mode == "color":
            return self._detect_color(frame)
        if self.mode == "qr":
            return self._detect_qr(frame)
        if self.mode == "line":
            return self._detect_line(frame)
        return None

    def _detect_face(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self._face_cascade.detectMultiScale(gray, 1.3, 5)
        if len(faces) == 0:
            return None
        x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
        return {"cx": x + w // 2, "cy": y + h // 2, "size": w}

    def _detect_color(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, HSV_LOWER, HSV_UPPER)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None
        largest = max(contours, key=cv2.contourArea)
        if cv2.contourArea(largest) < 200:
            return None
        x, y, w, h = cv2.boundingRect(largest)
        return {"cx": x + w // 2, "cy": y + h // 2, "size": w}

    def _detect_qr(self, frame):
        data, points, _ = self._qr_detector.detectAndDecode(frame)
        if not data or points is None:
            return None
        cx = int(points[0][:, 0].mean())
        cy = int(points[0][:, 1].mean())
        return {"cx": cx, "cy": cy, "size": 0, "data": data}

    def _detect_line(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 60, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None
        largest = max(contours, key=cv2.contourArea)
        m = cv2.moments(largest)
        if m["m00"] == 0:
            return None
        return {"cx": int(m["m10"] / m["m00"]), "cy": int(m["m01"] / m["m00"]), "size": 0}
