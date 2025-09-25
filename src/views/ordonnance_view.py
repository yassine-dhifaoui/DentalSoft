from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
                             QScrollArea, QFrame, QPushButton, QGridLayout, 
                             QGroupBox, QLineEdit, QDateEdit, QComboBox, 
                             QTableWidget, QTableWidgetItem, QHeaderView, 
                             QSplitter, QTextEdit, QSpinBox, QFormLayout,
                             QDialog, QDialogButtonBox, QMessageBox, QFileDialog,
                             QTabWidget, QCheckBox)
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QFont, QPixmap, QPainter, QPen
from PySide6.QtPrintSupport import QPrinter, QPrintDialog
import os
import json
import shutil
from datetime import datetime
from database import db
from src.patient_context import patient_context
from src.path_manager import path_manager

# Import pour la génération PDF
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

class ConfigurationCabinetDialog(QDialog):
    """Dialogue pour configurer les informations du cabinet"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuration du Cabinet")
        self.setModal(True)
        self.resize(500, 600)
        self.config_data = self.charger_configuration()
        self.setup_ui()
        self.charger_donnees()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Titre
        titre = QLabel("Configuration des Informations du Cabinet")
        titre.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px; color: #2c3e50;")
        layout.addWidget(titre)
        
        # Onglets
        tabs = QTabWidget()
        
        # Onglet Informations générales
        tab_info = QWidget()
        self.setup_tab_informations(tab_info)
        tabs.addTab(tab_info, "Informations Générales")
        
        # Onglet Logo
        tab_logo = QWidget()
        self.setup_tab_logo(tab_logo)
        tabs.addTab(tab_logo, "Logo du Cabinet")
        
        layout.addWidget(tabs)
        
        # Boutons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.sauvegarder_configuration)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def setup_tab_informations(self, tab):
        layout = QFormLayout(tab)
        
        # Nom du cabinet
        self.nom_cabinet_edit = QLineEdit()
        self.nom_cabinet_edit.setPlaceholderText("Ex: Cabinet Dentaire Médecin")
        layout.addRow("Nom du Cabinet:", self.nom_cabinet_edit)
        
        # Nom du médecin
        self.nom_medecin_edit = QLineEdit()
        self.nom_medecin_edit.setPlaceholderText("Ex: Dr. Médecin")
        layout.addRow("Nom du Médecin:", self.nom_medecin_edit)
        
        # Spécialité
        self.specialite_edit = QLineEdit()
        self.specialite_edit.setPlaceholderText("Ex: Chirurgien-Dentiste")
        layout.addRow("Spécialité:", self.specialite_edit)
        
        # Adresse
        self.adresse_edit = QTextEdit()
        self.adresse_edit.setMaximumHeight(80)
        self.adresse_edit.setPlaceholderText("Adresse complète du cabinet")
        layout.addRow("Adresse:", self.adresse_edit)
        
        # Ville
        self.ville_edit = QLineEdit()
        self.ville_edit.setPlaceholderText("Ex: Tunis")
        layout.addRow("Ville:", self.ville_edit)
        
        # Code postal
        self.code_postal_edit = QLineEdit()
        self.code_postal_edit.setPlaceholderText("Ex: 1000")
        layout.addRow("Code Postal:", self.code_postal_edit)
        
        # Téléphone 1
        self.telephone1_edit = QLineEdit()
        self.telephone1_edit.setPlaceholderText("Ex: +216 71 123 456")
        layout.addRow("Téléphone 1:", self.telephone1_edit)
        
        # Téléphone 2
        self.telephone2_edit = QLineEdit()
        self.telephone2_edit.setPlaceholderText("Ex: +216 98 765 432")
        layout.addRow("Téléphone 2:", self.telephone2_edit)
        
        # Email
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("Ex: contact@cabinet-médecin.tn")
        layout.addRow("Email:", self.email_edit)
        
        # Site web
        self.site_web_edit = QLineEdit()
        self.site_web_edit.setPlaceholderText("Ex: www.cabinet-médecin.tn")
        layout.addRow("Site Web:", self.site_web_edit)
        
        # Numéro d'ordre
        self.numero_ordre_edit = QLineEdit()
        self.numero_ordre_edit.setPlaceholderText("Ex: 12345")
        layout.addRow("N° Ordre:", self.numero_ordre_edit)
    
    def setup_tab_logo(self, tab):
        layout = QVBoxLayout(tab)
        
        # Instructions
        instructions = QLabel(
            "Sélectionnez le logo de votre cabinet qui apparaîtra sur les ordonnances.\n"
            "Formats acceptés: PNG, JPG, JPEG\n"
            "Taille recommandée: 200x200 pixels maximum"
        )
        instructions.setStyleSheet("color: #7f8c8d; margin: 10px;")
        layout.addWidget(instructions)
        
        # Aperçu du logo actuel
        self.logo_label = QLabel()
        self.logo_label.setFixedSize(150, 150)
        self.logo_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #bdc3c7;
                border-radius: 10px;
                background-color: #ecf0f1;
            }
        """)
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_label.setText("Aucun logo\nsélectionné")
        layout.addWidget(self.logo_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Boutons pour le logo
        boutons_layout = QHBoxLayout()
        
        self.btn_choisir_logo = QPushButton("Choisir un Logo")
        self.btn_choisir_logo.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.btn_choisir_logo.clicked.connect(self.choisir_logo)
        boutons_layout.addWidget(self.btn_choisir_logo)
        
        self.btn_supprimer_logo = QPushButton("Supprimer Logo")
        self.btn_supprimer_logo.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.btn_supprimer_logo.clicked.connect(self.supprimer_logo)
        boutons_layout.addWidget(self.btn_supprimer_logo)
        
        layout.addLayout(boutons_layout)
        
        # Utiliser logo par défaut
        self.utiliser_logo_defaut_check = QCheckBox("Utiliser le logo par défaut (dent)")
        self.utiliser_logo_defaut_check.stateChanged.connect(self.toggle_logo_defaut)
        layout.addWidget(self.utiliser_logo_defaut_check)
        
        layout.addStretch()
        
        self.chemin_logo = ""
    
    def choisir_logo(self):
        """Permet de choisir un fichier logo"""
        fichier, _ = QFileDialog.getOpenFileName(
            self,
            "Choisir le logo du cabinet",
            "",
            "Images (*.png *.jpg *.jpeg)"
        )
        
        if fichier:
            # Utiliser le dossier DentalSoft via PathManager
            dossier_logos = os.path.join(path_manager.get_app_data_folder(), "logos")
            os.makedirs(dossier_logos, exist_ok=True)
            
            # Copier le fichier dans le dossier du projet
            nom_fichier = "logo_cabinet" + os.path.splitext(fichier)[1]
            chemin_destination = os.path.join(dossier_logos, nom_fichier)
            
            try:
                shutil.copy2(fichier, chemin_destination)
                self.chemin_logo = chemin_destination
                self.afficher_logo()
                self.utiliser_logo_defaut_check.setChecked(False)
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de la copie du logo:\n{str(e)}")
    
    def supprimer_logo(self):
        """Supprime le logo sélectionné"""
        self.chemin_logo = ""
        self.logo_label.clear()
        self.logo_label.setText("Aucun logo\nsélectionné")
        self.utiliser_logo_defaut_check.setChecked(False)
    
    def toggle_logo_defaut(self, state):
        """Active/désactive le logo par défaut"""
        if state == Qt.CheckState.Checked.value:
            # Utiliser le logo par défaut (dent)
            self.chemin_logo = "defaut"
            self.logo_label.setText("Logo par défaut\n(dent)")
        else:
            if self.chemin_logo == "defaut":
                self.supprimer_logo()
    
    def afficher_logo(self):
        """Affiche l'aperçu du logo"""
        if self.chemin_logo and self.chemin_logo != "defaut" and os.path.exists(self.chemin_logo):
            pixmap = QPixmap(self.chemin_logo)
            if not pixmap.isNull():
                # Redimensionner pour l'aperçu
                pixmap = pixmap.scaled(140, 140, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.logo_label.setPixmap(pixmap)
    
    def charger_configuration(self):
        """Charge la configuration depuis le fichier JSON dans le dossier DentalSoft"""
        config_file = os.path.join(path_manager.get_app_data_folder(), "config_cabinet.json")
        
        config_defaut = {
            "nom_cabinet": "Cabinet Dentaire",
            "nom_medecin": "Dr. Médecin",
            "specialite": "Chirurgien-Dentiste",
            "adresse": "",
            "ville": "",
            "code_postal": "",
            "telephone1": "",
            "telephone2": "",
            "email": "",
            "site_web": "",
            "numero_ordre": "",
            "chemin_logo": ""
        }
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Fusionner avec la config par défaut pour les nouvelles clés
                    config_defaut.update(config)
            return config_defaut
        except Exception:
            return config_defaut
    
    def charger_donnees(self):
        """Charge les données dans les champs"""
        self.nom_cabinet_edit.setText(self.config_data.get("nom_cabinet", ""))
        self.nom_medecin_edit.setText(self.config_data.get("nom_medecin", ""))
        self.specialite_edit.setText(self.config_data.get("specialite", ""))
        self.adresse_edit.setPlainText(self.config_data.get("adresse", ""))
        self.ville_edit.setText(self.config_data.get("ville", ""))
        self.code_postal_edit.setText(self.config_data.get("code_postal", ""))
        self.telephone1_edit.setText(self.config_data.get("telephone1", ""))
        self.telephone2_edit.setText(self.config_data.get("telephone2", ""))
        self.email_edit.setText(self.config_data.get("email", ""))
        self.site_web_edit.setText(self.config_data.get("site_web", ""))
        self.numero_ordre_edit.setText(self.config_data.get("numero_ordre", ""))
        
        # Logo
        self.chemin_logo = self.config_data.get("chemin_logo", "")
        if self.chemin_logo == "defaut":
            self.utiliser_logo_defaut_check.setChecked(True)
            self.logo_label.setText("Logo par défaut\n(dent)")
        elif self.chemin_logo:
            self.afficher_logo()
    
    def sauvegarder_configuration(self):
        """Sauvegarde la configuration dans le dossier DentalSoft"""
        config = {
            "nom_cabinet": self.nom_cabinet_edit.text(),
            "nom_medecin": self.nom_medecin_edit.text(),
            "specialite": self.specialite_edit.text(),
            "adresse": self.adresse_edit.toPlainText(),
            "ville": self.ville_edit.text(),
            "code_postal": self.code_postal_edit.text(),
            "telephone1": self.telephone1_edit.text(),
            "telephone2": self.telephone2_edit.text(),
            "email": self.email_edit.text(),
            "site_web": self.site_web_edit.text(),
            "numero_ordre": self.numero_ordre_edit.text(),
            "chemin_logo": self.chemin_logo
        }
        
        config_file = os.path.join(path_manager.get_app_data_folder(), "config_cabinet.json")
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            QMessageBox.information(self, "Succès", "Configuration sauvegardée avec succès!")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la sauvegarde:\n{str(e)}")

class MedicamentWidget(QWidget):
    """Widget pour un médicament dans l'ordonnance - CHAMPS SÉPARÉS"""
    supprimer_clicked = Signal(object)
    
    def __init__(self, medicament_data=None):
        super().__init__()
        self.setup_ui()
        
        if medicament_data:
            self.charger_medicament(medicament_data)
    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Nom du médicament
        self.nom_edit = QLineEdit()
        self.nom_edit.setPlaceholderText("Nom du médicament")
        layout.addWidget(QLabel("Médicament:"))
        layout.addWidget(self.nom_edit)
        
        # Dosage avec unité automatique
        self.dosage_edit = QLineEdit()
        self.dosage_edit.setPlaceholderText("ex: 500")
        self.dosage_edit.editingFinished.connect(self.on_dosage_finished)
        layout.addWidget(QLabel("Dosage:"))
        layout.addWidget(self.dosage_edit)
        
        # Forme
        self.forme_combo = QComboBox()
        self.forme_combo.addItems(["cp", "gélule", "ml", "g", "sachet", "ampoule", "autre"])
        layout.addWidget(QLabel("Forme:"))
        layout.addWidget(self.forme_combo)
        
        # Quantité par prise
        self.quantite_spin = QSpinBox()
        self.quantite_spin.setMinimum(1)
        self.quantite_spin.setMaximum(10)
        self.quantite_spin.setValue(1)
        layout.addWidget(QLabel("Qté:"))
        layout.addWidget(self.quantite_spin)
        
        # Fréquence par jour
        self.frequence_spin = QSpinBox()
        self.frequence_spin.setMinimum(1)
        self.frequence_spin.setMaximum(6)
        self.frequence_spin.setValue(2)
        layout.addWidget(QLabel("x/jour:"))
        layout.addWidget(self.frequence_spin)
        
        # Durée avec unité automatique
        self.duree_edit = QLineEdit()
        self.duree_edit.setPlaceholderText("ex: 7")
        self.duree_edit.editingFinished.connect(self.on_duree_finished)
        layout.addWidget(QLabel("Durée:"))
        layout.addWidget(self.duree_edit)
        
        # Bouton supprimer
        self.btn_supprimer = QPushButton("✕")
        self.btn_supprimer.setFixedSize(30, 30)
        self.btn_supprimer.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        self.btn_supprimer.clicked.connect(lambda: self.supprimer_clicked.emit(self))
        layout.addWidget(self.btn_supprimer)

    def on_dosage_finished(self):
        """Appelée quand l'utilisateur termine la saisie du dosage"""
        text = self.dosage_edit.text()
        if text and text.isdigit() and not text.endswith('mg'):
            self.dosage_edit.setText(text + "mg")

    def on_duree_finished(self):
        """Appelée quand l'utilisateur termine la saisie de la durée"""
        text = self.duree_edit.text()
        if text and text.isdigit() and not text.endswith('j'):
            self.duree_edit.setText(text + "j")
    
    def charger_medicament(self, data):
        """Charge les données d'un médicament"""
        self.nom_edit.setText(data.get('nom', ''))
        self.dosage_edit.setText(data.get('dosage', ''))
        self.forme_combo.setCurrentText(data.get('forme', 'cp'))
        self.quantite_spin.setValue(data.get('quantite', 1))
        self.frequence_spin.setValue(data.get('frequence', 2))
        self.duree_edit.setText(data.get('duree', ''))
    
    def get_medicament_data(self):
        """Retourne les données du médicament"""
        return {
            'nom': self.nom_edit.text(),
            'dosage': self.dosage_edit.text(),
            'forme': self.forme_combo.currentText(),
            'quantite': self.quantite_spin.value(),
            'frequence': self.frequence_spin.value(),
            'duree': self.duree_edit.text()
        }
    
    def get_posologie_formatee(self):
        """Retourne la posologie formatée pour l'ordonnance"""
        data = self.get_medicament_data()
        return f"{data['quantite']}{data['forme']} x {data['frequence']} par jour – pendant {data['duree']}"

class OrdonnanceView(QWidget):
    def __init__(self):
        super().__init__()
        self.medicaments_widgets = []
        self.patient_actuel = None
        self.config_cabinet = self.charger_configuration_cabinet()
        self.setup_ui()
        self.charger_patients()
        
        # Connexion au signal de changement de patient global
        patient_context.patient_changed.connect(self.on_patient_changed)
        patient_context.patient_added.connect(self.charger_patients)
    
    def on_patient_changed(self, patient_id):
        """Gère le changement de patient global"""
        if patient_id:
            # Recharger la liste des patients
            self.charger_patients()
            # Trouver l'index du patient dans la combo
            for i in range(self.patient_combo.count()):
                if self.patient_combo.itemData(i) == patient_id:
                    self.patient_combo.setCurrentIndex(i)
                    break
    
    def charger_configuration_cabinet(self):
        """Charge la configuration du cabinet depuis le dossier DentalSoft"""
        config_file = os.path.join(path_manager.get_app_data_folder(), "config_cabinet.json")
        
        config_defaut = {
            "nom_cabinet": "Cabinet Dentaire",
            "nom_medecin": "Dr. Médecin",
            "specialite": "Chirurgien-Dentiste",
            "adresse": "",
            "ville": "Tunis",
            "code_postal": "",
            "telephone1": "",
            "telephone2": "",
            "email": "",
            "site_web": "",
            "numero_ordre": "",
            "chemin_logo": ""
        }
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    config_defaut.update(config)
            return config_defaut
        except Exception:
            return config_defaut
    
    def setup_ui(self):
        # Layout principal horizontal
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Splitter pour diviser l'interface
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Partie gauche: Création d'ordonnance
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Titre avec bouton configuration
        titre_layout = QHBoxLayout()
        titre = QLabel("Création d'Ordonnance")
        titre.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px; color: #333;")
        titre_layout.addWidget(titre)
        
        # Bouton configuration
        self.btn_config = QPushButton("⚙️ Configuration Cabinet")
        self.btn_config.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        self.btn_config.clicked.connect(self.ouvrir_configuration)
        titre_layout.addWidget(self.btn_config)
        titre_layout.addStretch()
        
        left_layout.addLayout(titre_layout)
        
        # Section informations
        info_section = self.create_info_section()
        left_layout.addWidget(info_section)
        
        # Section médicaments
        medicaments_section = self.create_medicaments_section()
        left_layout.addWidget(medicaments_section)
        
        # Section recommandations
        recommandations_section = self.create_recommandations_section()
        left_layout.addWidget(recommandations_section)
        
        # Section actions
        actions_section = self.create_actions_section()
        left_layout.addWidget(actions_section)
        
        # Partie droite: Aperçu de l'ordonnance
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Aperçu
        apercu_section = self.create_apercu_section()
        right_layout.addWidget(apercu_section)
        
        # Ajouter les widgets au splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([500, 500])
        
        main_layout.addWidget(splitter)
    
    def ouvrir_configuration(self):
        """Ouvre le dialogue de configuration du cabinet"""
        dialog = ConfigurationCabinetDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Recharger la configuration
            self.config_cabinet = self.charger_configuration_cabinet()
            # Actualiser l'aperçu
            self.actualiser_apercu()
    
    def create_info_section(self):
        """Crée la section des informations"""
        group = QGroupBox("Informations")
        layout = QFormLayout(group)
        
        # Sélection du patient
        self.patient_combo = QComboBox()
        self.patient_combo.currentIndexChanged.connect(self.patient_change)
        layout.addRow("Patient:", self.patient_combo)
        
        # Âge du patient
        self.age_label = QLabel("-")
        layout.addRow("Âge:", self.age_label)
        
        # Date de l'ordonnance
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        layout.addRow("Date:", self.date_edit)
        
        return group
    
    def create_medicaments_section(self):
        """Crée la section des médicaments prescrits"""
        group = QGroupBox("Médicaments Prescrits")
        layout = QVBoxLayout(group)
        
        # Bouton pour ajouter un médicament
        self.btn_ajouter_medicament = QPushButton("+ Ajouter un Médicament")
        self.btn_ajouter_medicament.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.btn_ajouter_medicament.clicked.connect(self.ajouter_medicament)
        layout.addWidget(self.btn_ajouter_medicament)
        
        # Zone de défilement pour les médicaments
        self.medicaments_scroll = QScrollArea()
        self.medicaments_scroll.setWidgetResizable(True)
        self.medicaments_scroll.setMaximumHeight(400)
        
        self.medicaments_container = QWidget()
        self.medicaments_layout = QVBoxLayout(self.medicaments_container)
        self.medicaments_layout.addStretch()
        
        self.medicaments_scroll.setWidget(self.medicaments_container)
        layout.addWidget(self.medicaments_scroll)
        
        # Ajouter un médicament par défaut
        self.ajouter_medicament()
        
        return group
    
    def create_recommandations_section(self):
        """Crée la section des recommandations"""
        group = QGroupBox("Recommandations et Instructions")
        layout = QVBoxLayout(group)
        
        self.recommandations_edit = QTextEdit()
        self.recommandations_edit.setPlainText(
            "- Prendre les médicaments selon la posologie indiquée\n"
            "- En cas d'effets secondaires, contacter immédiatement le médecin\n"
            "- Conserver les médicaments dans un endroit sec et frais"
        )
        self.recommandations_edit.setMaximumHeight(80)
        layout.addWidget(self.recommandations_edit)
        
        return group
    
    def create_actions_section(self):
        """Crée la section des actions"""
        group = QGroupBox("Actions")
        layout = QGridLayout(group)
        
        # Bouton actualiser aperçu
        self.btn_actualiser = QPushButton("Actualiser Aperçu")
        self.btn_actualiser.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.btn_actualiser.clicked.connect(self.actualiser_apercu)
        layout.addWidget(self.btn_actualiser, 0, 0)
        
        # Bouton générer PDF
        self.btn_generer_pdf = QPushButton("Générer PDF")
        self.btn_generer_pdf.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        self.btn_generer_pdf.clicked.connect(self.generer_pdf)
        layout.addWidget(self.btn_generer_pdf, 0, 1)
        
        # Bouton imprimer
        self.btn_imprimer = QPushButton("Imprimer")
        self.btn_imprimer.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7B1FA2;
            }
        """)
        self.btn_imprimer.clicked.connect(self.imprimer)
        layout.addWidget(self.btn_imprimer, 1, 0)
        
        # Bouton envoyer par email
        self.btn_email = QPushButton("Envoyer par Email")
        self.btn_email.setStyleSheet("""
            QPushButton {
                background-color: #607D8B;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #455A64;
            }
        """)
        self.btn_email.clicked.connect(self.envoyer_email)
        layout.addWidget(self.btn_email, 1, 1)
        
        return group
    
    def create_apercu_section(self):
        """Crée la section d'aperçu de l'ordonnance"""
        group = QGroupBox("Aperçu de l'Ordonnance")
        layout = QVBoxLayout(group)
        
        # Zone d'aperçu
        self.apercu_text = QTextEdit()
        self.apercu_text.setReadOnly(True)
        self.apercu_text.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #ccc;
                font-family: 'Times New Roman', serif;
                font-size: 12px;
                line-height: 1.5;
            }
        """)
        layout.addWidget(self.apercu_text)
        
        # Actualiser l'aperçu initial
        self.actualiser_apercu()
        
        return group
    
    def charger_patients(self):
        """Charge la liste des patients"""
        patients = db.obtenir_patients()
        self.patient_combo.clear()
        self.patient_combo.addItem("Sélectionner un patient...", None)
        
        for patient in patients:
            self.patient_combo.addItem(patient['nom_complet'], patient['id'])
    
    def patient_change(self):
        """Gère le changement de patient sélectionné"""
        patient_id = self.patient_combo.currentData()
        
        if patient_id:
            patient = db.obtenir_patient(patient_id)
            if patient and patient['date_naissance']:
                # Calculer l'âge
                from datetime import datetime
                naissance = datetime.strptime(patient['date_naissance'], '%Y-%m-%d')
                age = datetime.now().year - naissance.year
                if datetime.now().month < naissance.month or (datetime.now().month == naissance.month and datetime.now().day < naissance.day):
                    age -= 1
                self.age_label.setText(f"{age} ans")
            else:
                self.age_label.setText("-")
        else:
            self.age_label.setText("-")
        
        self.patient_actuel = patient_id
        self.actualiser_apercu()
    
    def ajouter_medicament(self):
        """Ajoute un nouveau widget médicament"""
        medicament_widget = MedicamentWidget()
        medicament_widget.supprimer_clicked.connect(self.supprimer_medicament)
        
        # Insérer avant le stretch
        self.medicaments_layout.insertWidget(len(self.medicaments_widgets), medicament_widget)
        self.medicaments_widgets.append(medicament_widget)
    
    def supprimer_medicament(self, widget):
        """Supprime un widget médicament"""
        if len(self.medicaments_widgets) > 1:
            self.medicaments_widgets.remove(widget)
            widget.deleteLater()
    
    def actualiser_apercu(self):
        """Met à jour l'aperçu de l'ordonnance selon le format exact du modèle"""
        # En-tête simple et propre
        html = f"""
        <div style="text-align: left; margin-bottom: 40px;">
            <h1 style="color: #2c3e50; margin: 0; font-size: 24px; font-weight: bold;">{self.config_cabinet['nom_medecin']}</h1>
            <h2 style="color: #34495e; margin: 5px 0; font-size: 18px;">{self.config_cabinet['specialite']}</h2>
            <h3 style="color: #7f8c8d; margin: 5px 0; font-size: 16px; font-style: italic;">{self.config_cabinet['nom_cabinet']}</h3>
        </div>
        """
        
        # Date et ville en haut à droite
        date = self.date_edit.date().toString('dd/MM/yyyy')
        ville = self.config_cabinet.get('ville', 'Monastir')
        html += f"""
        <div style="text-align: right; margin-bottom: 30px;">
            <p style="margin: 0; font-weight: bold; font-size: 14px;">{ville}, le {date}</p>
        </div>
        """
        
        # Informations patient
        patient_nom = self.patient_combo.currentText()
        if patient_nom != "Sélectionner un patient...":
            age = self.age_label.text()
            html += f"""
            <div style="margin-bottom: 10px;">
                <p style="margin: 0; font-size: 16px; font-weight: bold;">Nom & Prénom: {patient_nom}</p>
                <p style="margin: 5px 0 0 0; font-size: 14px;">Âge: {age}</p>
            </div>
            """
        
        # Prescription avec format exact du modèle
        html += "<h3 style='color: #2c3e50; font-size: 18px; margin: 30px 0 20px 0; font-weight: bold;'>Prescription:</h3>"
        
        # Médicaments avec format EXACT du modèle
        for i, widget in enumerate(self.medicaments_widgets, 1):
            data = widget.get_medicament_data()
            if data['nom']:
                # Format exact: Nom (dosage) puis posologie avec flèche
                nom_complet = data['nom']
                if data['dosage']:
                    nom_complet += f" ({data['dosage']})"
                
                posologie = widget.get_posologie_formatee()
                
                html += f"""
                <div style="margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 16px; font-weight: bold; color: #2c3e50;">{nom_complet}</p>
                    <p style="margin: 5px 0 0 20px; font-size: 14px; color: #555;">
                        ➤ {posologie}
                    </p>
                </div>
                """
        
        # Recommandations
        recommandations = self.recommandations_edit.toPlainText()
        if recommandations:
            html += "<h3 style='color: #2c3e50; font-size: 18px; margin: 40px 0 20px 0; font-weight: bold;'>Recommandations:</h3>"
            for ligne in recommandations.split('\n'):
                if ligne.strip():
                    html += f"<p style='margin: 5px 0; font-size: 14px;'>{ligne}</p>"
        

        # Signature
        html += f"""
        <div style="margin-top: 50px; text-align: right;">
            <p style="margin: 0; font-weight: bold; font-size: 14px;">Signature du médecin</p>
            <p style="margin: 0; font-weight: bold; font-size: 14px;">{self.config_cabinet['nom_medecin']}</p>
        </div>
        """

        html += "</div>"

        # Coordonnées du cabinet en bas
        html += "<div style='margin-top: 100px; text-align: left; border-top: 1px solid #e0e0e0; padding-top: 20px;'>"

        # Informations de contact
        contact_info = []
        if self.config_cabinet.get('telephone1'):
            contact_info.append(f"Tél: {self.config_cabinet['telephone1']}")
        if self.config_cabinet.get('telephone2'):
            contact_info.append(f"Mobile: {self.config_cabinet['telephone2']}")
        if self.config_cabinet.get('email'):
            contact_info.append(f"Email: {self.config_cabinet['email']}")


        if contact_info:
            for info in contact_info:
                html += f"<p style='margin: 5px 0; font-size: 12px; color: #7f8c8d;'>{info}</p>"

        # Adresse
        adresse = self.config_cabinet.get('adresse', '')
        code_postal = self.config_cabinet.get('code_postal', '')
        ville = self.config_cabinet.get('ville', '')

        adresse_complete = f"{adresse}, {code_postal} {ville}".strip(", ")
        html += f"<p style='margin: 5px 0; font-size: 12px; color: #7f8c8d;'>{adresse_complete}</p>"

        self.apercu_text.setHtml(html)
    
    def generer_pdf(self):
        """Génère un PDF de l'ordonnance avec mise en page professionnelle"""
        if not self.patient_actuel:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un patient.")
            return
        
        if not REPORTLAB_AVAILABLE:
            QMessageBox.warning(self, "Erreur", "La bibliothèque ReportLab n'est pas installée.\nVeuillez l'installer avec: pip install reportlab")
            return
        
        # Utiliser le dossier ordonnances du PathManager
        patient_nom = self.patient_combo.currentText().replace(", ", "_")
        date_str = self.date_edit.date().toString('yyyy-MM-dd')
        nom_fichier = f"Ordonnance_{patient_nom}_{date_str}.pdf"
        
        fichier_defaut = os.path.join(path_manager.get_ordonnances_folder(), nom_fichier)
        
        fichier, _ = QFileDialog.getSaveFileName(
            self,
            "Sauvegarder l'ordonnance",
            fichier_defaut,
            "Fichiers PDF (*.pdf)"
        )
        
        if not fichier:
            return
        
        try:
            self._generer_pdf_reportlab_professionnel(fichier)
            
            # Sauvegarder en base de données
            medicaments_json = json.dumps([w.get_medicament_data() for w in self.medicaments_widgets])
            ordonnance_id = db.ajouter_ordonnance(
                self.patient_actuel,
                medicaments_json,
                self.recommandations_edit.toPlainText(),
                fichier,
                self.date_edit.date().toString('yyyy-MM-dd')
            )
            
            if ordonnance_id:
                QMessageBox.information(self, "Succès", f"Ordonnance générée et sauvegardée:\n{fichier}")
            else:
                QMessageBox.warning(self, "Avertissement", f"PDF généré mais erreur de sauvegarde en base:\n{fichier}")
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la génération du PDF:\n{str(e)}")
    
    def _generer_pdf_reportlab_professionnel(self, fichier):
        """Génère le PDF avec mise en page EXACTE du modèle d'ordonnance"""
        doc = SimpleDocTemplate(
            fichier, 
            pagesize=A4, 
            topMargin=1*cm, 
            bottomMargin=1*cm,
            leftMargin=0.5*cm,
            rightMargin=0.5*cm
        )
        styles = getSampleStyleSheet()
        story = []
        
        # Styles personnalisés pour correspondre au modèle
        title_style = ParagraphStyle(
            'DoctorName',
            parent=styles['Heading1'],
            fontSize=22,
            spaceAfter=5,
            alignment=0,  # GAUCHE
            textColor=colors.HexColor('#2c3e50'),
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'Specialty',
            parent=styles['Heading2'],
            fontSize=18,
            spaceAfter=5,
            alignment=0,  # GAUCHE
            textColor=colors.HexColor('#34495e'),
            fontName='Helvetica'
        )
        
        cabinet_style = ParagraphStyle(
            'Cabinet',
            parent=styles['Heading3'],
            fontSize=16,
            spaceAfter=30,
            alignment=0,  # GAUCHE
            textColor=colors.HexColor('#7f8c8d'),
            fontName='Helvetica-Oblique'
        )
        
        # En-tête avec logo (si disponible)
        logo_path = None
        if self.config_cabinet.get('chemin_logo'):
            if self.config_cabinet['chemin_logo'] == "defaut":
                # Chercher le logo par défaut
                logo_defaut = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "icons", "logo_cabinet_defaut.png")
                if os.path.exists(logo_defaut):
                    logo_path = logo_defaut
            elif os.path.exists(self.config_cabinet['chemin_logo']):
                logo_path = self.config_cabinet['chemin_logo']
        
        if logo_path:
            try:
                # Table avec logo et informations
                logo_img = Image(logo_path, width=2*cm, height=2*cm)
                
                # Informations du médecin
                info_text = f"""
                <b>{self.config_cabinet['nom_medecin']}</b><br/>
                {self.config_cabinet['specialite']}<br/>
                <i>{self.config_cabinet['nom_cabinet']}</i>
                """
                info_para = Paragraph(info_text, title_style)
                
                header_table = Table([[logo_img, info_para]], colWidths=[3*cm, 18*cm])
                header_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                    ('ALIGN', (1, 0), (1, 0), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                story.append(header_table)
            except Exception:
                # Si erreur avec le logo, afficher sans logo
                story.append(Paragraph(self.config_cabinet['nom_medecin'], title_style))
                story.append(Paragraph(self.config_cabinet['specialite'], subtitle_style))
                story.append(Paragraph(self.config_cabinet['nom_cabinet'], cabinet_style))
        else:
            # Sans logo - format simple et élégant
            story.append(Paragraph(self.config_cabinet['nom_medecin'], title_style))
            story.append(Paragraph(self.config_cabinet['specialite'], subtitle_style))
            story.append(Paragraph(self.config_cabinet['nom_cabinet'], cabinet_style))
        
        story.append(Spacer(1, 20))
        
        # Date et ville en haut à droite
        date = self.date_edit.date().toString('dd/MM/yyyy')
        ville = self.config_cabinet.get('ville', 'Monastir')
        
        date_style = ParagraphStyle(
            'DateStyle',
            parent=styles['Normal'],
            fontSize=14,
            alignment=2,  # Aligné à droite
            fontName='Helvetica-Bold'
        )
        
        story.append(Paragraph(f"{ville}, le {date}", date_style))
        story.append(Spacer(1, 30))
        
        # Informations patient
        patient_nom = self.patient_combo.currentText()
        age = self.age_label.text()
        
        patient_style = ParagraphStyle(
            'PatientStyle',
            parent=styles['Normal'],
            fontSize=16,
            spaceAfter=10,
            fontName='Helvetica-Bold'
        )
        
        story.append(Paragraph(f"Nom & Prénom: {patient_nom}", patient_style))
        story.append(Paragraph(f"Âge: {age}", patient_style))
        story.append(Spacer(1, 30))
        
        # Prescription
        prescription_style = ParagraphStyle(
            'PrescriptionTitle',
            parent=styles['Heading2'],
            fontSize=18,
            spaceAfter=20,
            textColor=colors.HexColor('#2c3e50'),
            fontName='Helvetica-Bold'
        )
        
        story.append(Paragraph("Prescription:", prescription_style))
        
        # Médicaments avec format EXACT du modèle
        medicament_nom_style = ParagraphStyle(
            'MedicamentNom',
            parent=styles['Normal'],
            fontSize=16,
            spaceAfter=5,
            textColor=colors.HexColor('#2c3e50'),
            fontName='Helvetica-Bold'
        )
        
        posologie_style = ParagraphStyle(
            'PosologieStyle',
            parent=styles['Normal'],
            fontSize=14,
            spaceAfter=20,
            leftIndent=20,
            textColor=colors.HexColor('#555555'),
            fontName='Helvetica'
        )
        
        for widget in self.medicaments_widgets:
            data = widget.get_medicament_data()
            if data['nom']:
                # Nom du médicament avec dosage
                nom_complet = data['nom']
                if data['dosage']:
                    nom_complet += f" ({data['dosage']})"
                
                story.append(Paragraph(nom_complet, medicament_nom_style))
                
                # Posologie avec flèche
                posologie = widget.get_posologie_formatee()
                story.append(Paragraph(f"➤ {posologie}", posologie_style))
        
        # Recommandations
        recommandations = self.recommandations_edit.toPlainText()
        if recommandations:
            story.append(Spacer(1, 30))
            story.append(Paragraph("Recommandations:", prescription_style))
            
            recommandation_style = ParagraphStyle(
                'RecommandationStyle',
                parent=styles['Normal'],
                fontSize=14,
                spaceAfter=5,
                fontName='Helvetica'
            )
            
            for ligne in recommandations.split('\n'):
                if ligne.strip():
                    story.append(Paragraph(ligne, recommandation_style))
        
        # Signature
        story.append(Spacer(1, 70))
        
        signature_style = ParagraphStyle(
            'SignatureStyle',
            parent=styles['Normal'],
            fontSize=14,
            alignment=2,  # Aligné à droite
            fontName='Helvetica-Bold'
        )
        
        story.append(Paragraph("Signature du médecin", signature_style))
        story.append(Spacer(1, 10))
        story.append(Paragraph(self.config_cabinet['nom_medecin'], signature_style))


        # Ligne séparatrice
        story.append(Spacer(1, 70))
        from reportlab.platypus import HRFlowable
        story.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
        
        # Coordonnées du cabinet en bas
        story.append(Spacer(1, 10))
        
        contact_info = []
        if self.config_cabinet.get('telephone1'):
            contact_info.append(f"Tél: {self.config_cabinet['telephone1']}")
        if self.config_cabinet.get('telephone2'):
            contact_info.append(f"Mobile: {self.config_cabinet['telephone2']}")
        if self.config_cabinet.get('email'):
            contact_info.append(f"Email: {self.config_cabinet['email']}")
        
        contact_style = ParagraphStyle(
            'ContactStyle',
            parent=styles['Normal'],
            fontSize=12,
            alignment=0,  # Aligné à gauche
            textColor=colors.HexColor('#7f8c8d'),
            fontName='Helvetica'
        )

        if contact_info:
            for info in contact_info:
                story.append(Paragraph(info, contact_style))
        
        adresse = self.config_cabinet.get('adresse', '')
        code_postal = self.config_cabinet.get('code_postal', '')
        ville = self.config_cabinet.get('ville', '')
        adresse_complete = f"{adresse}, {code_postal} {ville}".strip(", ")

        if adresse_complete:
            story.append(Paragraph(f"Adresse: {adresse_complete}", contact_style))

        # Construire le PDF
        doc.build(story)
    
    def imprimer(self):
        """Imprime l'ordonnance"""
        printer = QPrinter()
        dialog = QPrintDialog(printer, self)
        
        if dialog.exec() == QPrintDialog.DialogCode.Accepted:
            self.apercu_text.print(printer)
    
    def envoyer_email(self):
        """Envoie l'ordonnance par email"""
        QMessageBox.information(
            self, 
            "Fonctionnalité à venir", 
            "La fonctionnalité d'envoi par email sera implémentée dans une prochaine version."
        )