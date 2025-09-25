from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from src.sidebar import Sidebar
from src.header import Header
from src.views.agenda_view import AgendaView
from src.views.examens_view import ExamensView
from src.views.imagerie_view import ImagerieView
from src.views.paiements_view import PaiementsView
from src.views.ordonnance_view import OrdonnanceView
from src.context import context
from database import db



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        #self.setWindowTitle("Agenda Médical - Maram")
        self.setWindowTitle("DentalSoft - Gestion Cabinet Dentaire")
        self.setWindowIcon(QPixmap(":/icons/assets/icons/Logo.ico"))

        self.setGeometry(100, 100, 1200, 800)

        # Set a consistent background color for the main window
        self.setStyleSheet("background-color: #F5F5F5;") # Light gray background

        # Initialiser la base de données
        db.init_database()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.sidebar = Sidebar()
        self.main_layout.addWidget(self.sidebar)

        self.right_section_widget = QWidget()
        self.right_section_layout = QVBoxLayout(self.right_section_widget)
        self.right_section_layout.setContentsMargins(0, 0, 0, 0)
        self.right_section_layout.setSpacing(0)

        self.header = Header()
        self.right_section_layout.addWidget(self.header)

        self.stacked_widget = QStackedWidget()
        self.right_section_layout.addWidget(self.stacked_widget)

        # Add views to stacked widget
        self.agenda_view = AgendaView()
        self.examens_view = ExamensView()
        self.imagerie_view = ImagerieView()
        self.paiements_view = PaiementsView()
        self.ordonnance_view = OrdonnanceView()

        self.stacked_widget.addWidget(self.agenda_view)
        self.stacked_widget.addWidget(self.examens_view)
        self.stacked_widget.addWidget(self.imagerie_view)
        self.stacked_widget.addWidget(self.paiements_view)
        self.stacked_widget.addWidget(self.ordonnance_view)

        # Map button names to views
        self.views = {
            "Agenda": self.agenda_view,
            "Examens": self.examens_view,
            "Imagerie": self.imagerie_view,
            "Paiements": self.paiements_view,
            "Ordonnance": self.ordonnance_view,
        }

        # Connect sidebar buttons to view changes
        self.sidebar.button_clicked.connect(self.switch_view)

        self.main_layout.addWidget(self.right_section_widget)

        # Set initial view
        self.switch_view("Agenda")

    def switch_view(self, view_name):
        if view_name in self.views:
            self.stacked_widget.setCurrentWidget(self.views[view_name])
            # Deselect all other buttons and select the current one
            for button_text, button in zip([b.text() for b in self.sidebar.buttons], self.sidebar.buttons):
                if button_text == view_name:
                    button.setChecked(True)
                else:
                    button.setChecked(False)