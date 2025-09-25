# -*- coding: utf-8 -*-
"""
Header du logiciel médical avec système de sélection patient et appel rapide
"""

from PySide6.QtWidgets import (QWidget, QHBoxLayout, QPushButton, QLabel, 
                             QComboBox, QDialog, QVBoxLayout, QLineEdit, 
                             QDialogButtonBox, QMessageBox, QListWidget, 
                             QListWidgetItem, QSplitter, QFormLayout, 
                             QDateEdit, QTextEdit)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from src.patient_context import patient_context
from database import db

class PatientSelectorDialog(QDialog):
    """Dialogue avancé pour sélectionner un patient avec recherche en temps réel"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sélectionner un Patient")
        self.setModal(True)
        self.resize(500, 400)
        self.selected_patient_id = None
        self.selected_patient_name = ""
        self.all_patients = []
        
        self.setup_ui()
        self.load_patients()
        
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Titre
        title = QLabel("Sélection du Patient")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Champ de recherche
        search_label = QLabel("Rechercher un patient :")
        layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Tapez le nom, prénom ou téléphone...")
        self.search_input.textChanged.connect(self.filter_patients)
        layout.addWidget(self.search_input)
        
        # Liste des patients
        patients_label = QLabel("Patients disponibles :")
        layout.addWidget(patients_label)
        
        self.patients_list = QListWidget()
        self.patients_list.itemDoubleClicked.connect(self.on_patient_double_click)
        self.patients_list.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.patients_list)
        
        # Informations du patient sélectionné
        self.info_label = QLabel("Aucun patient sélectionné")
        self.info_label.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.info_label)
        
        # Boutons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        # Connecter les signaux
        self.search_input.setFocus()
    
    def load_patients(self):
        """Charge tous les patients depuis la base de données"""
        try:
            self.all_patients = db.get_patients()
            self.display_patients(self.all_patients)
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Erreur lors du chargement des patients: {str(e)}")
            self.all_patients = []
    
    def display_patients(self, patients):
        """Affiche la liste des patients"""
        self.patients_list.clear()
        
        for patient in patients:
            patient_id, nom, prenom, telephone, email, date_naissance, adresse = patient
            
            # Créer le texte d'affichage
            display_text = f"{nom}, {prenom}"
            if telephone:
                display_text += f" - {telephone}"
            
            # Créer l'item
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, {
                'id': patient_id,
                'nom': nom,
                'prenom': prenom,
                'telephone': telephone,
                'email': email,
                'date_naissance': date_naissance,
                'adresse': adresse,
                'nom_complet': f"{nom}, {prenom}"
            })
            
            self.patients_list.addItem(item)
    
    def filter_patients(self, search_text):
        """Filtre les patients selon le texte de recherche"""
        if not search_text:
            self.display_patients(self.all_patients)
            return
        
        search_text = search_text.lower()
        filtered_patients = []
        
        for patient in self.all_patients:
            patient_id, nom, prenom, telephone, email, date_naissance, adresse = patient
            
            # Recherche dans nom, prénom et téléphone
            if (search_text in nom.lower() or 
                search_text in prenom.lower() or 
                (telephone and search_text in telephone)):
                filtered_patients.append(patient)
        
        self.display_patients(filtered_patients)
    
    def on_selection_changed(self):
        """Gère le changement de sélection"""
        current_item = self.patients_list.currentItem()
        if current_item:
            patient_data = current_item.data(Qt.ItemDataRole.UserRole)
            self.selected_patient_id = patient_data['id']
            self.selected_patient_name = patient_data['nom_complet']
            
            # Afficher les informations du patient
            info_text = f"""
            <b>Patient sélectionné :</b><br>
            <b>Nom :</b> {patient_data['nom_complet']}<br>
            <b>Téléphone :</b> {patient_data['telephone'] or 'Non renseigné'}<br>
            <b>Email :</b> {patient_data['email'] or 'Non renseigné'}
            """
            self.info_label.setText(info_text)
        else:
            self.selected_patient_id = None
            self.selected_patient_name = ""
            self.info_label.setText("Aucun patient sélectionné")
    
    def on_patient_double_click(self, item):
        """Gère le double-clic sur un patient"""
        self.accept()
    
    def get_selected_patient(self):
        """Retourne le patient sélectionné"""
        return self.selected_patient_id, self.selected_patient_name

class AddPatientDialog(QDialog):
    """Dialogue pour ajouter un nouveau patient"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajouter un Nouveau Patient")
        self.setModal(True)
        self.resize(400, 500)
        self.patient_added = False
        self.new_patient_id = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Titre
        title = QLabel("Nouveau Patient")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Formulaire
        form_layout = QFormLayout()
        
        # Nom (obligatoire)
        self.nom_edit = QLineEdit()
        self.nom_edit.setPlaceholderText("Nom du patient (obligatoire)")
        form_layout.addRow("Nom *:", self.nom_edit)
        
        # Prénom (obligatoire)
        self.prenom_edit = QLineEdit()
        self.prenom_edit.setPlaceholderText("Prénom du patient (obligatoire)")
        form_layout.addRow("Prénom *:", self.prenom_edit)
        
        # Téléphone
        self.telephone_edit = QLineEdit()
        self.telephone_edit.setPlaceholderText("Ex: +216 12 345 678")
        form_layout.addRow("Téléphone:", self.telephone_edit)
        
        # Email
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("email@exemple.com")
        form_layout.addRow("Email:", self.email_edit)
        
        # Date de naissance
        self.date_naissance_edit = QDateEdit()
        self.date_naissance_edit.setDate(QDate.currentDate().addYears(-30))
        self.date_naissance_edit.setCalendarPopup(True)
        self.date_naissance_edit.setDisplayFormat("dd/MM/yyyy")
        form_layout.addRow("Date de naissance:", self.date_naissance_edit)
        
        # Adresse
        self.adresse_edit = QTextEdit()
        self.adresse_edit.setMaximumHeight(80)
        self.adresse_edit.setPlaceholderText("Adresse complète du patient")
        form_layout.addRow("Adresse:", self.adresse_edit)
        
        # Remarques générales
        self.remarques_edit = QTextEdit()
        self.remarques_edit.setMaximumHeight(80)
        self.remarques_edit.setPlaceholderText("Allergies, remarques médicales...")
        form_layout.addRow("Remarques:", self.remarques_edit)
        
        layout.addLayout(form_layout)
        
        # Note obligatoire
        note = QLabel("* Champs obligatoires")
        note.setStyleSheet("color: red; font-style: italic;")
        layout.addWidget(note)
        
        # Boutons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        # Focus sur le nom
        self.nom_edit.setFocus()
    
    def validate_and_accept(self):
        """Valide les données et ajoute le patient"""
        # Vérifier les champs obligatoires
        if not self.nom_edit.text().strip():
            QMessageBox.warning(self, "Erreur", "Le nom est obligatoire.")
            self.nom_edit.setFocus()
            return
        
        if not self.prenom_edit.text().strip():
            QMessageBox.warning(self, "Erreur", "Le prénom est obligatoire.")
            self.prenom_edit.setFocus()
            return
        
        # Préparer les données
        patient_data = {
            'nom': self.nom_edit.text().strip(),
            'prenom': self.prenom_edit.text().strip(),
            'telephone': self.telephone_edit.text().strip() or None,
            'email': self.email_edit.text().strip() or None,
            'date_naissance': self.date_naissance_edit.date().toString('yyyy-MM-dd'),
            'adresse': self.adresse_edit.toPlainText().strip() or None,
            'remarques': self.remarques_edit.toPlainText().strip() or None
        }
        
        try:
            # Ajouter le patient à la base de données
            #self.new_patient_id = db.ajouter_patient(patient_data)
            self.new_patient_id = db.ajouter_patient(
                patient_data['nom'],
                patient_data['prenom'], 
                patient_data['date_naissance'],
                patient_data['telephone'],
                patient_data['email'],
                patient_data['adresse'],
                patient_data['remarques']
            )

            
            if self.new_patient_id:
                self.patient_added = True
                QMessageBox.information(
                    self,
                    "Succès",
                    f"Patient ajouté avec succès !\n\n"
                    f"Nom: {patient_data['nom']}, {patient_data['prenom']}\n"
                    f"ID: {self.new_patient_id}"
                )
                self.accept()
            else:
                QMessageBox.critical(self, "Erreur", "Erreur lors de l'ajout du patient.")
        
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'ajout du patient:\n{str(e)}")
    
    def get_new_patient_info(self):
        """Retourne les informations du nouveau patient"""
        if self.patient_added and self.new_patient_id:
            return self.new_patient_id, f"{self.nom_edit.text()}, {self.prenom_edit.text()}"
        return None, None

class Header(QWidget):
    """Header principal du logiciel avec sélection patient et appel rapide"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.connect_signals()
        self.update_patient_display()
    
    def setup_ui(self):
        """Configure l'interface utilisateur du header"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(15)
        
        # Bouton sélectionner patient
        self.btn_select_patient = QPushButton("Sélectionner Patient")
        self.btn_select_patient.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        self.btn_select_patient.clicked.connect(self.select_patient)
        layout.addWidget(self.btn_select_patient)
        
        # NOUVEAU: Bouton ajouter patient
        self.btn_add_patient = QPushButton("+ Ajouter Patient")
        self.btn_add_patient.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #2E7D32;
            }
        """)
        self.btn_add_patient.clicked.connect(self.add_patient)
        layout.addWidget(self.btn_add_patient)
        
        # Bouton appel rapide
        self.btn_quick_call = QPushButton("Appel rapide 📞")
        self.btn_quick_call.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
            QPushButton:pressed {
                background-color: #E65100;
            }
        """)
        self.btn_quick_call.clicked.connect(self.quick_call)
        layout.addWidget(self.btn_quick_call)
        
        # Spacer pour pousser le label à droite
        layout.addStretch()
        
        # Label patient sélectionné
        self.patient_label = QLabel("Patient sélectionné: Aucun")
        self.patient_label.setStyleSheet("""
            QLabel {
                background-color: #f5f5f5;
                color: #333;
                padding: 8px 15px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.patient_label)
    
    def connect_signals(self):
        """Connecte les signaux du contexte patient"""
        patient_context.patient_changed.connect(self.on_patient_changed)
    
    def select_patient(self):
        """Ouvre le dialogue de sélection de patient"""
        dialog = PatientSelectorDialog(self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            patient_id, patient_name = dialog.get_selected_patient()
            
            if patient_id:
                # Mettre à jour le contexte global
                patient_context.set_patient(patient_id, patient_name)
                
                QMessageBox.information(
                    self,
                    "Patient sélectionné",
                    f"Patient sélectionné: {patient_name}\n\n"
                    "Ce patient est maintenant actif dans toutes les vues du logiciel."
                )
            else:
                # Effacer la sélection
                patient_context.clear_patient()


    def add_patient(self):
        """Ouvre le dialogue d'ajout de patient"""
        dialog = AddPatientDialog(self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            patient_id, patient_name = dialog.get_new_patient_info()
            
            if patient_id:
                # Proposer de sélectionner le nouveau patient
                reply = QMessageBox.question(
                    self,
                    "Patient ajouté",
                    f"Patient ajouté avec succès !\n\n"
                    f"{patient_name}\n\n"
                    "Voulez-vous le sélectionner maintenant ?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    # Sélectionner automatiquement le nouveau patient
                    patient_context.set_patient(patient_id, patient_name)

    def quick_call(self):
        """Gère l'appel rapide selon le patient sélectionné"""
        if patient_context.is_patient_selected():
            # Patient sélectionné - afficher ses informations
            patient_data = patient_context.get_patient_info()
            
            if patient_data and patient_data.get('telephone'):
                message = f"""
                <h3>📞 Appel Rapide</h3>
                <p><b>Patient :</b> {patient_context.selected_patient_name}</p>
                <p><b>Téléphone :</b> {patient_data['telephone']}</p>
                <p><b>Email :</b> {patient_data.get('email', 'Non renseigné')}</p>
                """
            else:
                message = f"""
                <h3>📞 Appel Rapide</h3>
                <p><b>Patient :</b> {patient_context.selected_patient_name}</p>
                <p><b>Téléphone :</b> Non renseigné</p>
                <p>Veuillez mettre à jour les informations du patient.</p>
                """
        else:
            # Aucun patient sélectionné - afficher les numéros d'urgence
            message = """
            <h3>📞 Numéros d'Urgence</h3>
            <p><b>Support Technique :</b></p>
            <p>Yassine Dhifaoui (Ingénieur TechMed)</p>
            <p>📱 +216 94 94 13 62</p>
            <p>📱 +33 6 69 40 16 26</p>
            <br>
            <p><b>Urgences Médicales :</b></p>
            <p>🚨 Police : 197</p>
            <p>🏥 Urgences : 71 744 215</p>
            <br>
            <p><i>Sélectionnez un patient pour voir ses coordonnées.</i></p>
            """
        
        # Afficher le message
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Appel Rapide")
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.exec()
    
    def on_patient_changed(self, patient_id, patient_name):
        """Gère le changement de patient dans le contexte global"""
        self.update_patient_display()
    
    def update_patient_display(self):
        """Met à jour l'affichage du patient sélectionné"""
        if patient_context.is_patient_selected():
            self.patient_label.setText(f"Patient sélectionné: {patient_context.selected_patient_name}")
            self.patient_label.setStyleSheet("""
                QLabel {
                    background-color: #e8f5e8;
                    color: #2e7d32;
                    padding: 8px 15px;
                    border: 1px solid #4caf50;
                    border-radius: 5px;
                    font-weight: bold;
                    font-size: 12px;
                }
            """)
        else:
            self.patient_label.setText("Patient sélectionné: Aucun")
            self.patient_label.setStyleSheet("""
                QLabel {
                    background-color: #f5f5f5;
                    color: #333;
                    padding: 8px 15px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    font-weight: bold;
                    font-size: 12px;
                }
            """)