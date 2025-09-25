from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
                             QTextEdit, QScrollArea, QFrame, QPushButton, 
                             QGridLayout, QGroupBox, QLineEdit, QDateEdit,
                             QComboBox, QTableWidget, QTableWidgetItem,
                             QHeaderView, QSplitter, QMessageBox, QDialog,
                             QDialogButtonBox, QFormLayout)
from PySide6.QtCore import Qt, QDate, Signal, QSize
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor, QFont, QIcon
from src import resources_rc  # Import des ressources pour les icônes
from src.patient_context import patient_context  # Import du contexte patient
from database import db  # Import de la base de données
from datetime import datetime

class ToothButton(QPushButton):
    """Bouton personnalisé pour représenter une dent"""
    tooth_clicked = Signal(int, str)  # Signal émis quand une dent est cliquée
    
    def __init__(self, tooth_number, tooth_name):
        super().__init__()
        self.tooth_number = tooth_number
        self.tooth_name = tooth_name
        self.status = "normal"  # normal, carie, plombage, couronne, extraction, etc.
        self.notes = ""
        
        self.setFixedSize(40, 50)  # Taille ajustée pour l'icône et le numéro
        self.setToolTip(f"Dent {tooth_number}: {tooth_name}")
        
        # Charger l'icône de la dent
        icon_path = f":/icons/assets/icons/{tooth_number}.ico"
       
        icon = QIcon(icon_path)
        if not icon.isNull():
            self.setIcon(icon)
            self.setIconSize(QSize(40, 40))  # Ajuster la taille de l'icône
        #else:
            #print(f"Warning: Icon not found for tooth {tooth_number} at {icon_path}")
        
        self.update_style()
        self.clicked.connect(self.on_tooth_clicked)
    
    def update_style(self):
        """Met à jour le style du bouton selon le statut de la dent"""
        colors = {
            "normal": "#FFFFFF",
            "carie": "#FF6B6B",
            "plombage": "#4ECDC4",
            "couronne": "#FFD93D",
            "extraction": "#FF4757",
            "implant": "#6C5CE7",
            "bridge": "#00CEC9"
        }
        
        color = colors.get(self.status, "#FFFFFF")
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border: 2px solid #333;
                border-radius: 5px;
                font-weight: bold;
                font-size: 10px;
            }}
            QPushButton:hover {{
                border: 3px solid #007ACC;
            }}
            QPushButton:pressed {{
                background-color: #E0E0E0;
            }}
        """)
    
    def update_tooth_status(self, status, notes=""):
        """Met à jour le statut et les notes de la dent"""
        self.status = status
        self.notes = notes
        self.update_style()
        self.setToolTip(f"Dent {self.tooth_number}: {self.tooth_name}\\nStatut: {status}\\nNotes: {notes}")
    
    def on_tooth_clicked(self):
        """Gère le clic sur la dent"""
        self.tooth_clicked.emit(self.tooth_number, self.tooth_name)

class DentalChart(QWidget):
    """Widget pour afficher le schéma dentaire interactif"""
    tooth_selected = Signal(int, str, str, str)  # tooth_number, tooth_name, status, notes
    
    def __init__(self):
        super().__init__()
        self.teeth_buttons = {}
        self.setup_ui()
    
    def setup_ui(self):
        """Configure l'interface utilisateur du schéma dentaire"""
        layout = QVBoxLayout(self)
        
        # Titre
        title = QLabel("Schéma Dentaire Interactif")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Grille pour les dents
        teeth_widget = QWidget()
        teeth_layout = QVBoxLayout(teeth_widget)
        
        # Dents supérieures (18-11 et 21-28)
        upper_layout = QHBoxLayout()
        
        # Côté droit supérieur (18-11)
        upper_right = QHBoxLayout()
        for i in range(18, 10, -1):
            tooth_name = self.get_tooth_name(i)
            button = ToothButton(i, tooth_name)
            button.tooth_clicked.connect(self.on_tooth_selected)
            self.teeth_buttons[i] = button
            upper_right.addWidget(button)
        
        # Côté gauche supérieur (21-28)
        upper_left = QHBoxLayout()
        for i in range(21, 29):
            tooth_name = self.get_tooth_name(i)
            button = ToothButton(i, tooth_name)
            button.tooth_clicked.connect(self.on_tooth_selected)
            self.teeth_buttons[i] = button
            upper_left.addWidget(button)
        
        upper_layout.addLayout(upper_right)
        upper_layout.addSpacing(20)  # Espace entre les côtés
        upper_layout.addLayout(upper_left)
        
        # Dents inférieures (48-41 et 31-38)
        lower_layout = QHBoxLayout()
        
        # Côté droit inférieur (48-41)
        lower_right = QHBoxLayout()
        for i in range(48, 40, -1):
            tooth_name = self.get_tooth_name(i)
            button = ToothButton(i, tooth_name)
            button.tooth_clicked.connect(self.on_tooth_selected)
            self.teeth_buttons[i] = button
            lower_right.addWidget(button)
        
        # Côté gauche inférieur (31-38)
        lower_left = QHBoxLayout()
        for i in range(31, 39):
            tooth_name = self.get_tooth_name(i)
            button = ToothButton(i, tooth_name)
            button.tooth_clicked.connect(self.on_tooth_selected)
            self.teeth_buttons[i] = button
            lower_left.addWidget(button)
        
        lower_layout.addLayout(lower_right)
        lower_layout.addSpacing(20)  # Espace entre les côtés
        lower_layout.addLayout(lower_left)
        
        teeth_layout.addLayout(upper_layout)
        teeth_layout.addSpacing(10)  # Espace entre mâchoires
        teeth_layout.addLayout(lower_layout)
        
        layout.addWidget(teeth_widget)
        
        # Légende
        legend_widget = self.create_legend()
        layout.addWidget(legend_widget)
    
    def create_legend(self):
        """Crée la légende des couleurs"""
        legend_group = QGroupBox("Légende:")
        legend_layout = QGridLayout(legend_group)
        
        legend_items = [
            ("Normal", "#FFFFFF"),
            ("Carie", "#FF6B6B"),
            ("Plombage", "#4ECDC4"),
            ("Couronne", "#FFD93D"),
            ("Extraction", "#FF4757"),
            ("Implant", "#6C5CE7"),
            ("Bridge", "#00CEC9")
        ]
        
        for i, (label, color) in enumerate(legend_items):
            # Carré de couleur
            color_label = QLabel()
            color_label.setFixedSize(20, 20)
            color_label.setStyleSheet(f"background-color: {color}; border: 1px solid black;")
            
            # Texte
            text_label = QLabel(label)
            
            row = i // 4
            col = (i % 4) * 2
            
            legend_layout.addWidget(color_label, row, col)
            legend_layout.addWidget(text_label, row, col + 1)
        
        return legend_group
    
    def get_tooth_name(self, tooth_number):
        """Retourne le nom de la dent selon son numéro"""
        tooth_names = {
            # Dents supérieures droites
            18: "3e molaire", 17: "2e molaire", 16: "1e molaire", 15: "2e prémolaire",
            14: "1e prémolaire", 13: "Canine", 12: "Incisive latérale", 11: "Incisive centrale",
            # Dents supérieures gauches
            21: "Incisive centrale", 22: "Incisive latérale", 23: "Canine", 24: "1e prémolaire",
            25: "2e prémolaire", 26: "1e molaire", 27: "2e molaire", 28: "3e molaire",
            # Dents inférieures droites
            48: "3e molaire", 47: "2e molaire", 46: "1e molaire", 45: "2e prémolaire",
            44: "1e prémolaire", 43: "Canine", 42: "Incisive latérale", 41: "Incisive centrale",
            # Dents inférieures gauches
            31: "Incisive centrale", 32: "Incisive latérale", 33: "Canine", 34: "1e prémolaire",
            35: "2e prémolaire", 36: "1e molaire", 37: "2e molaire", 38: "3e molaire"
        }
        return tooth_names.get(tooth_number, "Dent inconnue")
    
    def on_tooth_selected(self, tooth_number, tooth_name):
        """Gère la sélection d'une dent"""
        button = self.teeth_buttons[tooth_number]
        self.tooth_selected.emit(tooth_number, tooth_name, button.status, button.notes)
    
    def update_tooth_status(self, tooth_number, status, notes=""):
        """Met à jour le statut d'une dent"""
        if tooth_number in self.teeth_buttons:
            self.teeth_buttons[tooth_number].update_tooth_status(status, notes)

class NewExamDialog(QDialog):
    """Dialogue pour créer un nouvel examen"""
    
    def __init__(self, patient_id, parent=None):
        super().__init__(parent)
        self.patient_id = patient_id
        self.setWindowTitle("Nouvel Examen")
        self.setModal(True)
        self.setup_ui()
    
    def setup_ui(self):
        """Configure l'interface du dialogue"""
        layout = QVBoxLayout(self)
        
        # Formulaire
        form_layout = QFormLayout()
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Contrôle", "Soin", "Urgence", "Consultation"])
        form_layout.addRow("Type d'examen:", self.type_combo)
        
        self.dent_edit = QLineEdit()
        self.dent_edit.setPlaceholderText("Ex: 16, 23, Toutes...")
        form_layout.addRow("Dent concernée:", self.dent_edit)
        
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        form_layout.addRow("Description:", self.description_edit)
        
        layout.addLayout(form_layout)
        
        # Boutons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def accept(self):
        """Valide et sauvegarde le nouvel examen"""
        type_examen = self.type_combo.currentText()
        dent_concernee = self.dent_edit.text() or "Toutes"
        description = self.description_edit.toPlainText()
        
        if not description.strip():
            QMessageBox.warning(self, "Attention", "Veuillez saisir une description.")
            return
        
        # Sauvegarder dans la base de données
        try:
            db.ajouter_historique_examen(
                self.patient_id,
                type_examen,
                dent_concernee,
                description
            )
            super().accept()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la sauvegarde: {e}")

class ExamensView(QWidget):
    """Vue principale pour les examens dentaires"""
    
    def __init__(self):
        super().__init__()
        self.selected_tooth_number = None
        self.setup_ui()
        
        # Connecter au contexte patient
        patient_context.patient_changed.connect(self.on_patient_changed)
        self.load_patient_data()  # Charger les données initiales
    
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Partie gauche - Schéma dentaire
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Schéma dentaire
        self.dental_chart = DentalChart()
        self.dental_chart.tooth_selected.connect(self.on_tooth_selected)
        left_layout.addWidget(self.dental_chart)
        
        # Section de modification de la dent sélectionnée
        tooth_modification_group = QGroupBox("Modification de la Dent Sélectionnée")
        tooth_modification_layout = QVBoxLayout(tooth_modification_group)
        
        # Aucune dent sélectionnée
        self.no_tooth_label = QLabel("Aucune dent sélectionnée")
        self.no_tooth_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_tooth_label.setStyleSheet("color: #666; font-style: italic;")
        tooth_modification_layout.addWidget(self.no_tooth_label)
        
        # Statut
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Statut:"))
        self.status_combo = QComboBox()
        self.status_combo.addItems(["normal", "carie", "plombage", "couronne", "extraction", "implant", "bridge"])
        self.status_combo.currentTextChanged.connect(self.update_selected_tooth)
        status_layout.addWidget(self.status_combo)
        tooth_modification_layout.addLayout(status_layout)
        
        # Notes
        tooth_modification_layout.addWidget(QLabel("Notes:"))
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(80)
        self.notes_edit.textChanged.connect(self.update_selected_tooth)
        tooth_modification_layout.addWidget(self.notes_edit)
        
        left_layout.addWidget(tooth_modification_group)
        
        # Partie droite - Informations patient et historique
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Informations patient
        patient_info_group = self.create_patient_info_section()
        right_layout.addWidget(patient_info_group)
        
        # Historique des examens
        exam_history_group = self.create_exam_history_section()
        right_layout.addWidget(exam_history_group)
        
        # Utiliser un splitter pour permettre le redimensionnement
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([600, 400])  # Tailles initiales
        
        main_layout.addWidget(splitter)
    
    def create_patient_info_section(self):
        """Crée la section d'informations patient"""
        group = QGroupBox("Informations Patient")
        layout = QVBoxLayout(group)
        
        # Grille pour les informations
        info_layout = QGridLayout()
        
        # Nom
        info_layout.addWidget(QLabel("Nom:"), 0, 0)
        self.patient_name = QLineEdit("")  # VIDE au lieu de données par défaut
        self.patient_name.setReadOnly(True)
        info_layout.addWidget(self.patient_name, 0, 1)
        
        # Âge
        info_layout.addWidget(QLabel("Âge:"), 1, 0)
        self.patient_age = QLineEdit("")  # VIDE au lieu de données par défaut
        self.patient_age.setReadOnly(True)
        info_layout.addWidget(self.patient_age, 1, 1)
        
        # Téléphone
        info_layout.addWidget(QLabel("Téléphone:"), 2, 0)
        self.patient_phone = QLineEdit("")  # VIDE au lieu de données par défaut
        self.patient_phone.setReadOnly(True)
        info_layout.addWidget(self.patient_phone, 2, 1)
        
        # Dernière visite
        info_layout.addWidget(QLabel("Dernière visite:"), 3, 0)
        self.last_visit = QLineEdit("")  # VIDE au lieu de données par défaut
        self.last_visit.setReadOnly(True)
        info_layout.addWidget(self.last_visit, 3, 1)
        
        layout.addLayout(info_layout)
        
        # Remarques générales
        layout.addWidget(QLabel("Remarques générales:"))
        self.general_notes = QTextEdit()
        self.general_notes.setMaximumHeight(100)
        self.general_notes.textChanged.connect(self.save_patient_remarks)  # Sauvegarde automatique
        layout.addWidget(self.general_notes)
        
        return group
    
    def create_exam_history_section(self):
        """Crée la section d'historique des examens"""
        group = QGroupBox("Historique des Examens")
        layout = QVBoxLayout(group)
        
        # Tableau des examens
        self.exam_table = QTableWidget()
        self.exam_table.setColumnCount(4)
        self.exam_table.setHorizontalHeaderLabels(["Date", "Type", "Dent", "Description"])
        
        # Ajuster les colonnes
        header = self.exam_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.exam_table)
        
        # Boutons d'action
        buttons_layout = QHBoxLayout()
        
        add_exam_btn = QPushButton("Nouvel Examen")
        add_exam_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        add_exam_btn.clicked.connect(self.on_nouvel_examen)  # CONNEXION AJOUTÉE
        buttons_layout.addWidget(add_exam_btn)
        
        edit_exam_btn = QPushButton("Modifier")
        edit_exam_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        edit_exam_btn.clicked.connect(self.on_modifier_examen)  # CONNEXION AJOUTÉE
        buttons_layout.addWidget(edit_exam_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        return group
    
    def on_tooth_selected(self, tooth_number, tooth_name, status, notes):
        """Gère la sélection d'une dent"""
        self.selected_tooth_number = tooth_number
        
        # Masquer le label "Aucune dent sélectionnée"
        self.no_tooth_label.hide()
        
        # Mettre à jour les contrôles
        self.status_combo.setCurrentText(status)
        self.notes_edit.setPlainText(notes)
        
        # Activer les contrôles
        self.status_combo.setEnabled(True)
        self.notes_edit.setEnabled(True)
        
        #print(f"Dent sélectionnée: {tooth_number} ({tooth_name}) - Statut: {status}")
    
    def update_selected_tooth(self):
        """Met à jour la dent sélectionnée avec les nouvelles informations"""
        if self.selected_tooth_number is not None:
            status = self.status_combo.currentText()
            notes = self.notes_edit.toPlainText()
            self.dental_chart.update_tooth_status(self.selected_tooth_number, status, notes)
            
            # NOUVEAU : Sauvegarde automatique
            self.save_dental_changes()
    
    def on_patient_changed(self, patient_id, patient_name):
        """Appelé quand le patient change"""
        self.load_patient_data()
    
    def load_patient_data(self):
        """Charge TOUTES les données du patient sélectionné"""
        if patient_context.is_patient_selected():
            try:
                # Récupérer les données de base du patient
                patient_data = db.get_patient_by_id(patient_context.selected_patient_id)
                
                if patient_data:
                    # 7 valeurs : id, nom, prenom, telephone, email, date_naissance, adresse
                    patient_id, nom, prenom, telephone, email, date_naissance, adresse = patient_data
                    
                    # Remplir les champs d'informations
                    self.patient_name.setText(f"{nom}, {prenom}")
                    self.patient_phone.setText(telephone or "Non renseigné")
                    
                    # Calculer l'âge
                    if date_naissance:
                        try:
                            birth_date = datetime.strptime(date_naissance, '%Y-%m-%d')
                            age = datetime.now().year - birth_date.year
                            self.patient_age.setText(f"{age} ans")
                        except:
                            self.patient_age.setText("Non renseigné")
                    else:
                        self.patient_age.setText("Non renseigné")
                    
                    # NOUVEAU : Charger les remarques générales
                    remarques = db.get_patient_remarks(patient_id)
                    self.general_notes.setPlainText(remarques or "")
                    
                    # NOUVEAU : Charger la dernière visite
                    last_visit = db.get_last_visit_date(patient_id)
                    self.last_visit.setText(last_visit or "Aucune visite")
                    
                    # NOUVEAU : Charger l'historique des examens
                    self.load_exam_history(patient_id)
                    
                    # NOUVEAU : Charger le schéma dentaire
                    self.load_dental_chart(patient_id)
                    
                    #print(f"Données complètes chargées pour le patient: {nom}, {prenom}")
                    
            except Exception as e:
                #print(f"Erreur lors du chargement des données patient: {e}")
                self.clear_patient_data()
        else:
            self.clear_patient_data()
    
    def load_exam_history(self, patient_id):
        """Charge l'historique des examens du patient"""
        try:
            examens = db.get_patient_exam_history(patient_id)
            
            self.exam_table.setRowCount(len(examens))
            
            for row, examen in enumerate(examens):
                date_examen, type_examen, dent_concernee, description = examen
                
                # Convertir la date au format français
                try:
                    date_obj = datetime.strptime(date_examen, '%Y-%m-%d')
                    date_fr = date_obj.strftime('%d/%m/%Y')
                except:
                    date_fr = date_examen
                
                self.exam_table.setItem(row, 0, QTableWidgetItem(date_fr))
                self.exam_table.setItem(row, 1, QTableWidgetItem(type_examen or ""))
                self.exam_table.setItem(row, 2, QTableWidgetItem(str(dent_concernee) if dent_concernee else "Toutes"))
                self.exam_table.setItem(row, 3, QTableWidgetItem(description or ""))
                
        except Exception as e:
           #print(f"Erreur lors du chargement des examens: {e}")
            self.exam_table.setRowCount(0)

    def load_dental_chart(self, patient_id):
        """Charge l'état du schéma dentaire du patient"""
        try:
            examens_dentaires = db.obtenir_examens_dentaires_patient(patient_id)
            
            # Remettre toutes les dents à "normal" d'abord
            for numero_dent, button in self.dental_chart.teeth_buttons.items():
                button.update_tooth_status("normal", "")
            
            # Mettre à jour chaque dent selon les données sauvegardées
            for numero_dent, data in examens_dentaires.items():
                statut = data['statut']
                notes = data['notes'] or ""
                self.dental_chart.update_tooth_status(numero_dent, statut, notes)
                
            #print(f"Schéma dentaire chargé: {len(examens_dentaires)} dents avec statut")
            
        except Exception as e:
            #print(f"Erreur lors du chargement du schéma dentaire: {e}")
            QMessageBox.warning(self, "Erreur", f"Erreur lors du chargement du schéma dentaire: {e}")

    def save_dental_changes(self):
        """Sauvegarde les modifications du schéma dentaire"""
        if not patient_context.is_patient_selected():
            return
        
        try:
            patient_id = patient_context.selected_patient_id
            
            # Sauvegarder seulement la dent sélectionnée si elle a été modifiée
            if self.selected_tooth_number:
                button = self.dental_chart.teeth_buttons[self.selected_tooth_number]
                if button.status != "normal" or button.notes:
                    # Sauvegarder cette dent
                    db.sauvegarder_examen_dentaire(
                        patient_id, 
                        self.selected_tooth_number, 
                        button.status, 
                        button.notes,
                        datetime.now().strftime('%Y-%m-%d')
                    )
                    #print(f"Dent {self.selected_tooth_number} sauvegardée: {button.status}")
            
        except Exception as e:
            #print(f"Erreur lors de la sauvegarde du schéma dentaire: {e}")
            QMessageBox.warning(self, "Erreur", f"Erreur lors de la sauvegarde du schéma dentaire: {e}")

            

    def save_patient_remarks(self):
        """Sauvegarde les remarques générales du patient"""
        if not patient_context.is_patient_selected():
            return
        
        try:
            patient_id = patient_context.selected_patient_id
            remarques = self.general_notes.toPlainText()
            
            #if db.update_patient_remarks(patient_id, remarques):
                #print("Remarques générales sauvegardées")
            #else:
                #print("Erreur lors de la sauvegarde des remarques")
                
        except Exception as e:
            #print(f"Erreur lors de la sauvegarde des remarques: {e}")
            QMessageBox.warning(self, "Erreur", f"Erreur lors de la sauvegarde des remarques: {e}")


    def on_nouvel_examen(self):
        """Gère le clic sur le bouton Nouvel Examen"""
        if not patient_context.is_patient_selected():
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un patient d'abord.")
            return
        
        # Ouvrir un dialogue pour créer un nouvel examen
        dialog = NewExamDialog(patient_context.selected_patient_id, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Recharger l'historique des examens
            self.load_exam_history(patient_context.selected_patient_id)
            QMessageBox.information(self, "Succès", "Nouvel examen ajouté avec succès!")

    def on_modifier_examen(self):
        """Gère le clic sur le bouton Modifier"""
        current_row = self.exam_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un examen à modifier.")
            return
        
        # Récupérer les données de l'examen sélectionné
        date_item = self.exam_table.item(current_row, 0)
        type_item = self.exam_table.item(current_row, 1)
        
        if date_item and type_item:
            QMessageBox.information(self, "Modifier Examen", 
                                  f"Modification de l'examen du {date_item.text()}\\n"
                                  f"Type: {type_item.text()}\\n\\n"
                                  f"Fonctionnalité en cours de développement...")

    def clear_patient_data(self):
        """Vide tous les champs patient"""
        self.patient_name.setText("")
        self.patient_age.setText("")
        self.patient_phone.setText("")
        self.last_visit.setText("")
        self.general_notes.setPlainText("")
        self.exam_table.setRowCount(0)
        
        # Remettre toutes les dents à "normal"
        for numero_dent, button in self.dental_chart.teeth_buttons.items():
            button.update_tooth_status("normal", "")
        
        # Désélectionner la dent
        self.selected_tooth_number = None
        self.no_tooth_label.show()
        self.status_combo.setEnabled(False)
        self.notes_edit.setEnabled(False)
        self.notes_edit.setPlainText("")