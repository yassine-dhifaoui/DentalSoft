from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
                             QScrollArea, QFrame, QPushButton, QGridLayout, 
                             QGroupBox, QLineEdit, QDateEdit, QComboBox, 
                             QTableWidget, QTableWidgetItem, QHeaderView, 
                             QSplitter, QCalendarWidget, QTimeEdit, QTextEdit,
                             QDialog, QDialogButtonBox, QMessageBox, QFormLayout)
from PySide6.QtCore import Qt, QDate, QTime, Signal
from PySide6.QtGui import QFont
from database import db
from src.context import context

class AjouterRendezVousDialog(QDialog):
    """Dialog pour ajouter un nouveau rendez-vous"""
    
    def __init__(self, date_selectionnee=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nouveau Rendez-vous")
        self.setModal(True)
        self.resize(400, 350)
        
        self.date_selectionnee = date_selectionnee or QDate.currentDate()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Titre
        title = QLabel("Ajouter un Nouveau Rendez-vous")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #333; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Formulaire
        form_layout = QFormLayout()
        
        # Sélection du patient
        self.patient_combo = QComboBox()
        self.charger_patients()
        form_layout.addRow("Patient *:", self.patient_combo)
        
        # Date du rendez-vous
        self.date_edit = QDateEdit()
        self.date_edit.setDate(self.date_selectionnee)
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setStyleSheet("QDateEdit { padding: 5px; }")
        form_layout.addRow("Date *:", self.date_edit)
        
        # Heure du rendez-vous
        self.heure_edit = QTimeEdit()
        self.heure_edit.setTime(QTime(9, 0))  # 9h00 par défaut
        self.heure_edit.setStyleSheet("QTimeEdit { padding: 5px; }")
        form_layout.addRow("Heure *:", self.heure_edit)
        
        # Type de rendez-vous
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Contrôle", "Soin", "Urgence", "Consultation", "Détartrage", "Radiographie", "Chirurgie"])
        self.type_combo.setStyleSheet("QComboBox { padding: 5px; }")
        form_layout.addRow("Type *:", self.type_combo)
        
        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        self.description_edit.setPlaceholderText("Description du rendez-vous...")
        form_layout.addRow("Description:", self.description_edit)
        
        layout.addLayout(form_layout)
        
        # Note sur les champs obligatoires
        note = QLabel("* Champs obligatoires")
        note.setStyleSheet("color: #666; font-style: italic; margin-top: 10px;")
        layout.addWidget(note)
        
        # Boutons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.button(QDialogButtonBox.StandardButton.Ok).setText("Ajouter")
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setText("Annuler")
        button_box.accepted.connect(self.valider_et_accepter)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def charger_patients(self):
        """Charge la liste des patients dans le combo box"""
        try:
            patients = db.obtenir_patients()
            self.patient_combo.clear()
            
            for patient in patients:
                self.patient_combo.addItem(patient['nom_complet'], patient['id'])
                
        except Exception as e:
            #print(f"Erreur lors du chargement des patients: {e}")
            QMessageBox.warning(self, "Erreur", "Impossible de charger la liste des patients")
    
    def valider_et_accepter(self):
        """Valide les données avant d'accepter"""
        if not self.patient_combo.currentData():
            QMessageBox.warning(self, "Validation", "Veuillez sélectionner un patient")
            return
            
        if not self.date_edit.date().isValid():
            QMessageBox.warning(self, "Validation", "Veuillez sélectionner une date valide")
            return
            
        if not self.heure_edit.time().isValid():
            QMessageBox.warning(self, "Validation", "Veuillez sélectionner une heure valide")
            return
        
        self.accept()
    
    def get_rendez_vous_data(self):
        """Retourne les données du rendez-vous"""
        return {
            'patient_id': self.patient_combo.currentData(),
            'date': self.date_edit.date().toString('yyyy-MM-dd'),
            'heure': self.heure_edit.time().toString('HH:mm'),
            'type': self.type_combo.currentText(),
            'description': self.description_edit.toPlainText().strip()
        }

class ModifierRendezVousDialog(QDialog):
    """Dialog pour modifier un rendez-vous existant"""
    
    def __init__(self, rdv_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Modifier Rendez-vous")
        self.setModal(True)
        self.resize(400, 350)
        
        self.rdv_data = rdv_data
        self.setup_ui()
        self.charger_donnees()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Titre
        title = QLabel("Modifier le Rendez-vous")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #333; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Formulaire
        form_layout = QFormLayout()
        
        # Sélection du patient
        self.patient_combo = QComboBox()
        self.charger_patients()
        form_layout.addRow("Patient *:", self.patient_combo)
        
        # Date du rendez-vous
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setStyleSheet("QDateEdit { padding: 5px; }")
        form_layout.addRow("Date *:", self.date_edit)
        
        # Heure du rendez-vous
        self.heure_edit = QTimeEdit()
        self.heure_edit.setStyleSheet("QTimeEdit { padding: 5px; }")
        form_layout.addRow("Heure *:", self.heure_edit)
        
        # Type de rendez-vous
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Contrôle", "Soin", "Urgence", "Consultation", "Détartrage", "Radiographie", "Chirurgie"])
        self.type_combo.setStyleSheet("QComboBox { padding: 5px; }")
        form_layout.addRow("Type *:", self.type_combo)
        
        # Statut
        self.statut_combo = QComboBox()
        self.statut_combo.addItems(["planifie", "termine", "annule", "reporte"])
        self.statut_combo.setStyleSheet("QComboBox { padding: 5px; }")
        form_layout.addRow("Statut:", self.statut_combo)
        
        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        self.description_edit.setPlaceholderText("Description du rendez-vous...")
        form_layout.addRow("Description:", self.description_edit)
        
        layout.addLayout(form_layout)
        
        # Note sur les champs obligatoires
        note = QLabel("* Champs obligatoires")
        note.setStyleSheet("color: #666; font-style: italic; margin-top: 10px;")
        layout.addWidget(note)
        
        # Boutons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.button(QDialogButtonBox.StandardButton.Ok).setText("Modifier")
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setText("Annuler")
        button_box.accepted.connect(self.valider_et_accepter)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def charger_patients(self):
        """Charge la liste des patients dans le combo box"""
        try:
            patients = db.obtenir_patients()
            self.patient_combo.clear()
            
            for patient in patients:
                self.patient_combo.addItem(patient['nom_complet'], patient['id'])
                
        except Exception as e:
            #print(f"Erreur lors du chargement des patients: {e}")
            QMessageBox.warning(self, "Erreur", f"Erreur lors du chargement des patients: {e}")
    
    def charger_donnees(self):
        """Charge les données du rendez-vous dans le formulaire"""
        try:
            # Sélectionner le patient
            for i in range(self.patient_combo.count()):
                if self.patient_combo.itemData(i) == self.rdv_data.get('patient_id'):
                    self.patient_combo.setCurrentIndex(i)
                    break
            
            # Date
            date_str = self.rdv_data.get('date_rdv', '')
            if date_str:
                date = QDate.fromString(date_str, 'yyyy-MM-dd')
                self.date_edit.setDate(date)
            
            # Heure
            heure_str = self.rdv_data.get('heure_rdv', '')
            if heure_str:
                heure = QTime.fromString(heure_str, 'HH:mm')
                self.heure_edit.setTime(heure)
            
            # Type
            type_rdv = self.rdv_data.get('type_rdv', '')
            index = self.type_combo.findText(type_rdv)
            if index >= 0:
                self.type_combo.setCurrentIndex(index)
            
            # Statut
            statut = self.rdv_data.get('statut', 'planifie')
            index = self.statut_combo.findText(statut)
            if index >= 0:
                self.statut_combo.setCurrentIndex(index)
            
            # Description
            self.description_edit.setPlainText(self.rdv_data.get('description', ''))
            
        except Exception as e:
            #print(f"Erreur lors du chargement des données: {e}")
            QMessageBox.warning(self, "Erreur", f"Erreur lors du chargement des données: {e}")
    
    def valider_et_accepter(self):
        """Valide les données avant d'accepter"""
        if not self.patient_combo.currentData():
            QMessageBox.warning(self, "Validation", "Veuillez sélectionner un patient")
            return
            
        if not self.date_edit.date().isValid():
            QMessageBox.warning(self, "Validation", "Veuillez sélectionner une date valide")
            return
            
        if not self.heure_edit.time().isValid():
            QMessageBox.warning(self, "Validation", "Veuillez sélectionner une heure valide")
            return
        
        self.accept()
    
    def get_rendez_vous_data(self):
        """Retourne les données modifiées du rendez-vous"""
        return {
            'id': self.rdv_data.get('id'),
            'patient_id': self.patient_combo.currentData(),
            'date': self.date_edit.date().toString('yyyy-MM-dd'),
            'heure': self.heure_edit.time().toString('HH:mm'),
            'type': self.type_combo.currentText(),
            'statut': self.statut_combo.currentText(),
            'description': self.description_edit.toPlainText().strip()
        }

class AgendaView(QWidget):
    def __init__(self):
        super().__init__()
        self.date_courante = QDate.currentDate()
        self.setup_ui()
        self.charger_rendez_vous()
        
        # Connecter au contexte global pour les changements de patient
        context.patient_changed.connect(self.on_patient_changed)
    
    def setup_ui(self):
        # Layout principal horizontal
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Splitter pour diviser l'interface
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Partie gauche: Calendrier et contrôles
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Titre et navigation de date
        title_layout = QHBoxLayout()
        
        # Bouton jour précédent
        self.prev_day_btn = QPushButton("◀ Jour Précédent")
        self.prev_day_btn.clicked.connect(self.jour_precedent)
        title_layout.addWidget(self.prev_day_btn)
        
        # Titre avec date courante
        self.btn_aujourd_hui = QPushButton("Aujourd'hui")
        self.btn_aujourd_hui.clicked.connect(self.aller_aujourd_hui)
        title_layout.addWidget(self.btn_aujourd_hui)
        
        # Bouton jour suivant
        self.next_day_btn = QPushButton("Jour Suivant ▶")
        self.next_day_btn.clicked.connect(self.jour_suivant)
        title_layout.addWidget(self.next_day_btn)
        
        left_layout.addLayout(title_layout)
        
        # Calendrier
        self.calendar = QCalendarWidget()
        self.calendar.setSelectedDate(self.date_courante)
        self.calendar.clicked.connect(self.date_selectionnee)
        self.calendar.setStyleSheet("""
            QCalendarWidget {
                background-color: white;
                border: 1px solid #D0D0D0;
                border-radius: 5px;
            }
            QCalendarWidget QToolButton {
                height: 30px;
                width: 60px;
                color: #333;
                font-size: 12px;
                background-color: #F0F0F0;
                border: 1px solid #C0C0C0;
                border-radius: 3px;
            }
            QCalendarWidget QToolButton:hover {
                background-color: #E0E0E0;
            }
            QCalendarWidget QMenu {
                background-color: white;
                border: 1px solid #C0C0C0;
            }
            QCalendarWidget QSpinBox {
                background-color: white;
                border: 1px solid #C0C0C0;
                border-radius: 3px;
                padding: 2px;
            }
            QCalendarWidget QAbstractItemView:enabled {
                background-color: white;
                selection-background-color: #007BFF;
                selection-color: white;
            }
        """)
        left_layout.addWidget(self.calendar)
        
        # Bouton nouveau rendez-vous
        self.nouveau_rdv_btn = QPushButton("+ Nouveau Rendez-vous")
        self.nouveau_rdv_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.nouveau_rdv_btn.clicked.connect(self.nouveau_rendez_vous)
        left_layout.addWidget(self.nouveau_rdv_btn)
        
        # Liste des patients
        patients_group = self.create_patients_list_section()
        left_layout.addWidget(patients_group)
        
        # Partie droite: Planning du jour
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Titre du planning
        planning_title = QLabel("Planning du Jour")
        planning_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #333; margin-bottom: 10px;")
        right_layout.addWidget(planning_title)
        
        # Tableau des rendez-vous
        self.rdv_table = QTableWidget()
        self.rdv_table.setColumnCount(5)
        self.rdv_table.setHorizontalHeaderLabels(["Heure", "Patient", "Type", "Description", "Statut"])
        
        # Configuration du tableau
        header = self.rdv_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)  # Heure
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Patient
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)  # Type
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Description
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)  # Statut
        
        # Largeurs fixes pour certaines colonnes
        self.rdv_table.setColumnWidth(0, 80)   # Heure - plus petite
        self.rdv_table.setColumnWidth(2, 100)  # Type
        self.rdv_table.setColumnWidth(4, 100)  # Statut
        
        self.rdv_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #D0D0D0;
                background-color: white;
                gridline-color: #E0E0E0;
                border-radius: 3px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #E0E0E0;
            }
            QTableWidget::item:selected {
                background-color: #C0D0E0;
                color: black;
            }
            QHeaderView::section {
                background-color: #F0F0F0;
                padding: 8px;
                border: 1px solid #D0D0D0;
                font-weight: bold;
            }
        """)
        
        self.rdv_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        right_layout.addWidget(self.rdv_table)
        
        # Boutons d'action
        actions_layout = QHBoxLayout()
        
        self.modifier_btn = QPushButton("Modifier")
        self.modifier_btn.setStyleSheet("""
            QPushButton {
                background-color: #007BFF;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:disabled {
                background-color: #C0C0C0;
            }
        """)
        self.modifier_btn.clicked.connect(self.modifier_rendez_vous)
        self.modifier_btn.setEnabled(False)
        actions_layout.addWidget(self.modifier_btn)
        
        self.supprimer_btn = QPushButton("Supprimer")
        self.supprimer_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:disabled {
                background-color: #C0C0C0;
            }
        """)
        self.supprimer_btn.clicked.connect(self.supprimer_rendez_vous)
        self.supprimer_btn.setEnabled(False)
        actions_layout.addWidget(self.supprimer_btn)
        
        actions_layout.addStretch()
        right_layout.addLayout(actions_layout)
        
        # Connecter la sélection du tableau
        self.rdv_table.itemSelectionChanged.connect(self.on_selection_changed)
        
        # Ajouter les widgets au splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([350, 650])  # Proportion initiale
        
        main_layout.addWidget(splitter)
    
    def create_patients_list_section(self):
        """Crée la section de la liste des patients"""
        group = QGroupBox("Liste Patients")
        layout = QVBoxLayout(group)
        
        # Champ de recherche
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher un patient...")
        self.search_input.textChanged.connect(self.filtrer_patients)
        layout.addWidget(self.search_input)
        
        # Tableau des patients
        self.patients_table = QTableWidget()
        self.patients_table.setColumnCount(2)
        self.patients_table.setHorizontalHeaderLabels(["Nom", "Téléphone"])
        
        # Configuration du tableau
        header = self.patients_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.patients_table.setColumnWidth(1, 120)
        
        self.patients_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #D0D0D0;
                background-color: white;
                gridline-color: #E0E0E0;
                border-radius: 3px;
            }
            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid #E0E0E0;
            }
            QTableWidget::item:selected {
                background-color: #C0D0E0;
                color: black;
            }
            QHeaderView::section {
                background-color: #F0F0F0;
                padding: 5px;
                border: 1px solid #D0D0D0;
                font-weight: bold;
                font-size: 12px;
            }
        """)
        
        self.patients_table.setMaximumHeight(200)
        layout.addWidget(self.patients_table)
        
        # Charger les patients
        self.charger_patients()
        
        return group
    
    def charger_patients(self):
        """Charge la liste des patients"""
        try:
            patients = db.obtenir_patients()
            self.patients_table.setRowCount(len(patients))
            
            for row, patient in enumerate(patients):
                # Nom complet
                nom_item = QTableWidgetItem(patient['nom_complet'])
                self.patients_table.setItem(row, 0, nom_item)
                
                # Téléphone
                tel_item = QTableWidgetItem(patient['telephone'] or "")
                self.patients_table.setItem(row, 1, tel_item)
                
        except Exception as e:
            #print(f"Erreur lors du chargement des patients: {e}")
            QMessageBox.warning(self, "Erreur", f"Erreur lors du chargement des patients: {e}")
    
    def filtrer_patients(self, texte):
        """Filtre les patients selon le texte de recherche"""
        for row in range(self.patients_table.rowCount()):
            nom_item = self.patients_table.item(row, 0)
            if nom_item:
                visible = texte.lower() in nom_item.text().lower()
                self.patients_table.setRowHidden(row, not visible)
    
    def mettre_a_jour_titre(self):
        """Met à jour le titre avec la date courante"""
        date_str = self.date_courante.toString("dddd d MMMM yyyy")
        # Note: titre supprimé de l'interface mais méthode gardée pour compatibilité
        pass
    
    def jour_precedent(self):
        """Navigue vers le jour précédent"""
        self.date_courante = self.date_courante.addDays(-1)
        self.calendar.setSelectedDate(self.date_courante)
        self.mettre_a_jour_titre()
        self.charger_rendez_vous()

    def aller_aujourd_hui(self):
        """Retourne à la date d'aujourd'hui"""
        self.date_courante = QDate.currentDate()
        self.calendar.setSelectedDate(self.date_courante)
        self.mettre_a_jour_titre()
        self.charger_rendez_vous()
    
    def jour_suivant(self):
        """Navigue vers le jour suivant"""
        self.date_courante = self.date_courante.addDays(1)
        self.calendar.setSelectedDate(self.date_courante)
        self.mettre_a_jour_titre()
        self.charger_rendez_vous()
    
    def date_selectionnee(self, date):
        """Gère la sélection d'une date dans le calendrier"""
        self.date_courante = date
        self.mettre_a_jour_titre()
        self.charger_rendez_vous()
    
    def charger_rendez_vous(self):
        """Charge les rendez-vous du jour sélectionné - VERSION CORRIGÉE"""
        try:
            date_str = self.date_courante.toString('yyyy-MM-dd')
            #print(f"🔍 Chargement des RDV pour la date: {date_str}")  # Debug
            
            # Récupérer les rendez-vous de la date
            rendez_vous = db.obtenir_rendez_vous_date(date_str)
            #print(f"🔍 Nombre de RDV trouvés: {len(rendez_vous)}")  # Debug
            
            # Filtrer par patient si un patient est sélectionné
            if context.selected_patient_id:
                rendez_vous_filtres = [rdv for rdv in rendez_vous if rdv.get('patient_id') == context.selected_patient_id]
                #print(f"🔍 RDV filtrés pour patient {context.selected_patient_id}: {len(rendez_vous_filtres)}")
                rendez_vous = rendez_vous_filtres
            
            # Vider le tableau et définir le nombre de lignes
            self.rdv_table.setRowCount(len(rendez_vous))
            
            # Remplir le tableau avec les données
            for row, rdv in enumerate(rendez_vous):
                #print(f"🔍 RDV {row}: {rdv}")  # Debug
                
                # Heure
                heure_item = QTableWidgetItem(rdv.get('heure_rdv', ''))
                self.rdv_table.setItem(row, 0, heure_item)
                
                # Patient - Construire le nom complet
                if rdv.get('nom') and rdv.get('prenom'):
                    patient_nom = f"{rdv.get('nom')}, {rdv.get('prenom')}"
                else:
                    patient_nom = rdv.get('patient_nom', 'Patient inconnu')
                
                patient_item = QTableWidgetItem(patient_nom)
                self.rdv_table.setItem(row, 1, patient_item)
                
                # Type
                type_item = QTableWidgetItem(rdv.get('type_rdv', ''))
                self.rdv_table.setItem(row, 2, type_item)
                
                # Description
                desc_item = QTableWidgetItem(rdv.get('description', ''))
                self.rdv_table.setItem(row, 3, desc_item)
                
                # Statut avec couleur
                statut = rdv.get('statut', 'planifie')
                statut_item = QTableWidgetItem(statut)
                
                # Couleur selon le statut
                if statut == 'termine':
                    statut_item.setBackground(Qt.GlobalColor.green)
                elif statut == 'annule':
                    statut_item.setBackground(Qt.GlobalColor.red)
                else:
                    statut_item.setBackground(Qt.GlobalColor.yellow)
                
                self.rdv_table.setItem(row, 4, statut_item)
                
                # Stocker l'ID du rendez-vous et toutes les données pour les actions
                heure_item.setData(Qt.ItemDataRole.UserRole, rdv)
            
            #print(f"✅ Tableau mis à jour avec {len(rendez_vous)} rendez-vous")  # Debug
                
        except Exception as e:
            #print(f"❌ Erreur lors du chargement des rendez-vous: {e}")
            import traceback
            traceback.print_exc()
            # En cas d'erreur, vider le tableau
            self.rdv_table.setRowCount(0)
    
    def nouveau_rendez_vous(self):
        """Ouvre le dialogue pour ajouter un nouveau rendez-vous"""
        dialog = AjouterRendezVousDialog(self.date_courante, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_rendez_vous_data()
            
            try:
                rdv_id = db.ajouter_rendez_vous(
                    data['patient_id'],
                    data['date'],
                    data['heure'],
                    data['type'],
                    data['description']
                )
                
                if rdv_id:
                    QMessageBox.information(self, "Succès", "Rendez-vous ajouté avec succès!")
                    self.charger_rendez_vous()
                else:
                    QMessageBox.warning(self, "Erreur", "Erreur lors de l'ajout du rendez-vous")
                    
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur: {e}")
    
    def on_selection_changed(self):
        """Gère le changement de sélection dans le tableau"""
        has_selection = len(self.rdv_table.selectedItems()) > 0
        self.modifier_btn.setEnabled(has_selection)
        self.supprimer_btn.setEnabled(has_selection)
    
    def modifier_rendez_vous(self):
        """Modifie le rendez-vous sélectionné"""
        current_row = self.rdv_table.currentRow()
        if current_row >= 0:
            rdv_id_item = self.rdv_table.item(current_row, 0)
            if rdv_id_item:
                rdv_data = rdv_id_item.data(Qt.ItemDataRole.UserRole)
                
                if rdv_data:
                    dialog = ModifierRendezVousDialog(rdv_data, self)
                    if dialog.exec() == QDialog.DialogCode.Accepted:
                        modified_data = dialog.get_rendez_vous_data()
                        
                        try:
                            success = db.modifier_rendez_vous(
                                modified_data['id'],
                                modified_data['patient_id'],
                                modified_data['date'],
                                modified_data['heure'],
                                modified_data['type'],
                                modified_data['description'],
                                modified_data['statut']
                            )
                            
                            if success:
                                QMessageBox.information(self, "Succès", "Rendez-vous modifié avec succès!")
                                self.charger_rendez_vous()
                            else:
                                QMessageBox.warning(self, "Erreur", "Erreur lors de la modification")
                                
                        except Exception as e:
                            QMessageBox.critical(self, "Erreur", f"Erreur: {e}")
                else:
                    QMessageBox.warning(self, "Erreur", "Impossible de récupérer les données du rendez-vous")
    
    def supprimer_rendez_vous(self):
        """Supprime le rendez-vous sélectionné"""
        current_row = self.rdv_table.currentRow()
        if current_row >= 0:
            rdv_id_item = self.rdv_table.item(current_row, 0)
            if rdv_id_item:
                rdv_data = rdv_id_item.data(Qt.ItemDataRole.UserRole)
                
                if rdv_data and rdv_data.get('id'):
                    reply = QMessageBox.question(
                        self, 
                        "Confirmer la suppression",
                        f"Êtes-vous sûr de vouloir supprimer le rendez-vous de {rdv_data.get('heure_rdv', '')} ?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    
                    if reply == QMessageBox.StandardButton.Yes:
                        try:
                            success = db.supprimer_rendez_vous(rdv_data['id'])
                            if success:
                                QMessageBox.information(self, "Succès", "Rendez-vous supprimé avec succès!")
                                self.charger_rendez_vous()
                            else:
                                QMessageBox.warning(self, "Erreur", "Erreur lors de la suppression")
                        except Exception as e:
                            QMessageBox.critical(self, "Erreur", f"Erreur: {e}")
                else:
                    QMessageBox.warning(self, "Erreur", "Impossible de récupérer l'ID du rendez-vous")
    
    def on_patient_changed(self, patient_id):
        """Gère le changement de patient sélectionné"""
        #print(f"🔍 Patient changé: {patient_id}")  # Debug
        # Recharger les rendez-vous pour le nouveau patient
        self.charger_rendez_vous()