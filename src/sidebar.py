import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QToolButton
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize, Signal, Qt

# Import the compiled resources
import src.resources_rc

class Sidebar(QWidget):
    button_clicked = Signal(str) # Signal to emit the name of the clicked button

    def __init__(self):
        super().__init__()
        self.setFixedWidth(100) # Make sidebar narrower to accommodate text under icon
        self.setStyleSheet("background-color: #F0F0F0;")

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 10, 5, 10) # Adjust margins
        self.layout.setSpacing(5) # Adjust spacing between buttons

        self.buttons = [] # Store buttons to access them later
        self.create_buttons()

    def create_buttons(self):
        buttons_data = [
            ("Agenda", ":/icons/assets/icons/calendrier.ico"),
            ("Examens", ":/icons/assets/icons/dent.ico"), # Shorten text for better fit
            ("Imagerie", ":/icons/assets/icons/Imagerie.ico"),
            ("Paiements", ":/icons/assets/icons/paiements.ico"),
            ("Ordonnance", ":/icons/assets/icons/Logo.ico"), # Using Logo.ico for Ordonnance temporarily
        ]

        for text, icon_path in buttons_data:
            button = QToolButton() # Use QToolButton for better icon/text control
            button.setText(text)
            button.setIcon(QIcon(icon_path))
            button.setIconSize(QSize(32, 32))
            button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon) # Icon above text
            button.setCheckable(True)
            button.setFixedSize(90, 70) # Fixed size for better control (width, height)

            button.setStyleSheet(
                "QToolButton {\n"
                "    text-align: center;\n"
                "    padding: 5px;\n"
                "    border: none;\n"
                "    background-color: transparent;\n"
                "    font-size: 12px;\n"
                "}\n"
                "QToolButton:hover {\n"
                "    background-color: #E0E0E0;\n"
                "}\n"
                "QToolButton:checked {\n"
                "    background-color: #D0D0D0;\n"
                "}"
            )
            button.clicked.connect(lambda checked, t=text: self.button_clicked.emit(t)) # Connect signal
            self.layout.addWidget(button)
            self.buttons.append(button)

        self.layout.addStretch()