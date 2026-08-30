"""Point d'entrée du Tello Ground Control Station.

Assemble les modules construits chapitre après chapitre dans le livre
« Programmer un drone Tello ». Voir le README pour la correspondance
entre chaque fichier et le chapitre qui l'introduit.
"""
import sys

from PySide6.QtWidgets import QApplication

from config import Config
from monitoring.alerts import AlertManager
from safety.monitor import SafetyMonitor
from storage.database import get_connection
from storage.recorder import FlightRecorder
from tello_link.controller import TelloController
from ui.main_window import MainWindow


def main():
    config = Config.load()

    app = QApplication(sys.argv)

    controller = TelloController()
    controller.start_watchdog()

    conn = get_connection()
    recorder = FlightRecorder(conn)
    alerts = AlertManager(recorder)

    safety = SafetyMonitor(controller, min_battery=config.min_battery, max_height_cm=config.max_height_cm)

    window = MainWindow(controller)
    window.show()
    window.connect_to_drone()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
