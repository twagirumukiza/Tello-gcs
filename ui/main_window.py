"""Fenêtre principale du poste de contrôle.

Ce fichier assemble, dans l'ordre où le livre les construit, les morceaux
introduits aux chapitres 3 (squelette), 4 (pilotage manuel), 5 (télémétrie),
6 (vidéo), 8 (suivi automatique) et 11 (assistant IA).

Remarque sur le chapitre 8 : le suivi automatique y accède à
``self.controller._tello.send_rc_control`` directement plutôt que par
``self.controller.send_rc_control``, contrairement à la règle d'encapsulation
posée au chapitre 2. C'est un écart connu, volontairement laissé tel quel
(voir la relecture technique du livre) : à corriger de la même façon que le
chapitre 4 si tu réutilises ce module.
"""
from PySide6.QtCore import Qt, QThread, QTimer, Signal
from PySide6.QtWidgets import QGridLayout, QLabel, QMainWindow, QStatusBar, QWidget

from ai.assistant import MissionParsingError, prepare_mission_from_instruction
from ai.validation import MissionValidationError
from tello_link.controller import TelloController
from tello_link.input import ControllerInput
from tello_link.telemetry import TelemetryFilter, TelemetryWorker
from ui.telemetry_panel import TelemetryPanel
from ui.video_panel import VideoPanel

# --- Chapitre 4 : pilotage clavier -------------------------------------

KEY_MAP = {
    Qt.Key_Z: "forward", Qt.Key_S: "backward",
    Qt.Key_Q: "left", Qt.Key_D: "right",
    Qt.Key_A: "yaw_left", Qt.Key_E: "yaw_right",
    Qt.Key_Space: "up", Qt.Key_Shift: "down",
}

AXIS_MAP = {
    "forward": ("forward", 1.0), "backward": ("forward", -1.0),
    "left": ("strafe", -1.0), "right": ("strafe", 1.0),
    "up": ("vertical", 1.0), "down": ("vertical", -1.0),
    "yaw_left": ("yaw", -1.0), "yaw_right": ("yaw", 1.0),
}


class ConnectWorker(QThread):
    """Chapitre 3 : la connexion se fait dans un thread dédié pour ne
    jamais geler l'interface pendant la négociation Wi-Fi."""

    connected = Signal(bool, str)

    def __init__(self, controller):
        super().__init__()
        self.controller = controller

    def run(self):
        try:
            self.controller.connect()
            self.connected.emit(True, "")
        except ConnectionError as exc:
            self.connected.emit(False, str(exc))


class MainWindow(QMainWindow):
    def __init__(self, controller: TelloController):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Tello Ground Control Station")
        self.resize(1100, 720)

        self.pilot_input = ControllerInput()
        self.held_actions: set[str] = set()
        self.follow_mode_active = False
        self.vision_pipeline = None  # branché depuis main.py si le chapitre 7/8 est utilisé
        self.follow_controller = None

        self._build_layout()
        self._build_status_bar()
        self._start_control_loop()

    # --- Chapitre 3 : squelette -----------------------------------------

    def _build_layout(self):
        central = QWidget()
        grid = QGridLayout(central)

        self.video_area = VideoPanel()
        self.telemetry_panel = TelemetryPanel()
        self.controls_panel = QLabel("Commandes")
        self.mission_panel = QLabel("Missions")

        grid.addWidget(self.video_area, 0, 0, 2, 1)
        grid.addWidget(self.telemetry_panel, 0, 1)
        grid.addWidget(self.controls_panel, 1, 1)
        grid.addWidget(self.mission_panel, 2, 0, 1, 2)

        self.setCentralWidget(central)

    def _build_status_bar(self):
        self.setStatusBar(QStatusBar())
        self.connection_label = QLabel("Déconnecté")
        self.statusBar().addPermanentWidget(self.connection_label)

    def connect_to_drone(self):
        self.connection_label.setText("Connexion en cours…")
        self.worker = ConnectWorker(self.controller)
        self.worker.connected.connect(self._on_connected)
        self.worker.start()

    def _on_connected(self, success: bool, error: str):
        self.connection_label.setText("Connecté" if success else f"Erreur : {error}")
        self._set_connection_indicator(success)

    def _set_connection_indicator(self, connected: bool):
        color = "#1D9E75" if connected else "#E24B4A"
        self.connection_label.setStyleSheet(f"color: {color}; font-weight: bold;")

    # --- Chapitre 4 : pilotage manuel ------------------------------------

    def keyPressEvent(self, event):
        action = KEY_MAP.get(event.key())
        if action:
            self.held_actions.add(action)
            self._recompute_pilot_input()

    def keyReleaseEvent(self, event):
        action = KEY_MAP.get(event.key())
        if action:
            self.held_actions.discard(action)
            self._recompute_pilot_input()

    def _recompute_pilot_input(self):
        """Reconstruit l'entrée à partir de TOUTES les touches actuellement
        maintenues — relâcher une touche ne doit annuler que son propre axe."""
        new_input = ControllerInput()
        for action in self.held_actions:
            axis, sign = AXIS_MAP[action]
            setattr(new_input, axis, sign)
        self.pilot_input = new_input

    def _start_control_loop(self):
        self.control_timer = QTimer()
        self.control_timer.timeout.connect(self._send_rc)
        self.control_timer.start(50)  # 20 Hz

    def _send_rc(self):
        if self.controller.is_connected and not self.follow_mode_active:
            lr, fb, ud, yaw = self.pilot_input.as_rc()
            self.controller.send_rc_control(lr, fb, ud, yaw)

    # --- Chapitre 5 : télémétrie ------------------------------------------

    def start_telemetry(self):
        self.telemetry_filter = TelemetryFilter()
        self.telemetry_worker = TelemetryWorker(self.controller)
        self.telemetry_worker.updated.connect(self._on_telemetry)
        self.telemetry_worker.start()

    def _on_telemetry(self, state: dict):
        filtered = self.telemetry_filter.apply(state)
        self.telemetry_panel.update_state(filtered)
        self.check_battery(state)

    def check_battery(self, state: dict):
        if state.get("bat", 100) < 15:
            self.connection_label.setText("⚠ Batterie faible — atterrissage recommandé")

    # --- Chapitre 6/7/8 : vidéo, vision, suivi automatique ------------------

    def on_video_frame(self, image):
        self.video_area.show_frame(image)

    def toggle_follow_mode(self, enabled: bool):
        self.follow_mode_active = enabled
        if self.vision_pipeline:
            self.vision_pipeline.set_mode("face" if enabled else None)

    def on_detection(self, detection):
        """Chapitre 8. Accès direct à _tello laissé tel quel — voir la note
        en tête de fichier."""
        if not self.follow_mode_active or self.follow_controller is None:
            return
        rc = self.follow_controller.compute_with_distance(detection)
        if rc is not None and not self.controller.emergency:
            self.controller._tello.send_rc_control(*rc)

    # --- Chapitre 11 : assistant IA -----------------------------------------

    def on_ai_instruction_submitted(self, text: str):
        try:
            mission = prepare_mission_from_instruction(text)
            self.mission_panel.setText(f"Mission proposée : {mission.name} ({len(mission.actions)} actions)")
        except (MissionValidationError, MissionParsingError) as exc:
            self.connection_label.setText(f"Mission refusée : {exc}")
