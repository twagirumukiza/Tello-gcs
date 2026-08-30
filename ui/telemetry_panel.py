"""Panneau d'affichage de la télémétrie. Voir chapitre 5 du livre."""
from PySide6.QtWidgets import QGridLayout, QLabel, QWidget


class TelemetryPanel(QWidget):
    FIELDS = {
        "bat": ("Batterie", "%"),
        "h": ("Altitude", "cm"),
        "templ": ("Température", "°C"),
        "vgx": ("Vitesse X", "cm/s"),
    }

    def __init__(self):
        super().__init__()
        self.value_labels = {}
        layout = QGridLayout(self)
        for row, (key, (label, unit)) in enumerate(self.FIELDS.items()):
            layout.addWidget(QLabel(label), row, 0)
            value_label = QLabel("—")
            self.value_labels[key] = (value_label, unit)
            layout.addWidget(value_label, row, 1)

    def update_state(self, state: dict):
        for key, (label, unit) in self.value_labels.items():
            if key in state:
                label.setText(f"{state[key]} {unit}")
