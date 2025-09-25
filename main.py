import sys
import os
from PySide6.QtWidgets import QApplication
from database import db
from src.main_window import MainWindow
from src.path_manager import path_manager
from src.splash import show_splash

if __name__ == "__main__":
    # Initialiser l'application
    app = QApplication(sys.argv)
    show_splash(app)
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())