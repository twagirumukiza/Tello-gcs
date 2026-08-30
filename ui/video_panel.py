"""Widget d'affichage du flux vidéo. Voir chapitre 6 du livre."""
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel


class VideoPanel(QLabel):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(640, 480)
        self.setStyleSheet("background-color: black;")

    def show_frame(self, image):
        self.setPixmap(QPixmap.fromImage(image).scaled(self.size(), aspectRatioMode=1))
