from PySide6.QtWidgets import QSplashScreen
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QTimer
import os

def show_splash(app):
    
    # Chemin absolu vers le dossier du projet
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    splash_path = os.path.join(base_dir, "assets", "icons", "splash_logo.png")
    # Charger l'image du splash
    splash_pix = QPixmap(splash_path)
    if splash_pix.isNull():
        return None

    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)

    splash.setWindowFlag(Qt.FramelessWindowHint)
    splash.show()

    # Rafraîchir l'affichage
    app.processEvents()

    # Durée d'affichage en millisecondes (3000 ms = 3 secondes)
    QTimer.singleShot(3000, splash.close)