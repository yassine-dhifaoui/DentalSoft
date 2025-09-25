from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
                             QScrollArea, QFrame, QPushButton, QGridLayout, 
                             QGroupBox, QListWidget, QListWidgetItem, QSplitter,
                             QComboBox, QDateEdit, QTextEdit, QFileDialog,
                             QMessageBox, QProgressBar, QTabWidget, QFormLayout,
                             QDialog, QDialogButtonBox, QLineEdit)
from PySide6.QtCore import Qt, QDate, QSize, Signal
from PySide6.QtGui import QPixmap, QIcon, QFont
import os
import shutil
from database import db
from src.patient_context import patient_context
from src.path_manager import path_manager

class AjouterImageDialog(QDialog):
    """Dialog pour ajouter une nouvelle image"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajouter une Image")
        self.setModal(True)
        self.resize(400, 300)
        self.chemin_fichier = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Titre
        title = QLabel("Ajouter une Nouvelle Image")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #333; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Formulaire
        form_layout = QFormLayout()
        
        # Sélection du patient
        self.patient_combo = QComboBox()
        self.charger_patients()
        form_layout.addRow("Patient *:", self.patient_combo)
        
        # Type d'image
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "Radiographie Panoramique",
            "Radiographie Rétro-alvéolaire", 
            "Scanner 3D",
            "Photo Intra-orale",
            "Photo Extra-orale",
            "Empreinte Numérique",
            "Autre"
        ])
        form_layout.addRow("Type *:", self.type_combo)
        
        # Nom de l'image
        self.nom_edit = QLineEdit()
        self.nom_edit.setPlaceholderText("Nom descriptif de l'image...")
        form_layout.addRow("Nom *:", self.nom_edit)
        
        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        self.description_edit.setPlaceholderText("Description détaillée de l'image...")
        form_layout.addRow("Description:", self.description_edit)
        
        # Bouton pour sélectionner le fichier
        self.btn_fichier = QPushButton("Sélectionner le fichier image...")
        self.btn_fichier.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.btn_fichier.clicked.connect(self.selectionner_fichier)
        form_layout.addRow("Fichier *:", self.btn_fichier)
        
        # Label pour afficher le fichier sélectionné
        self.label_fichier = QLabel("Aucun fichier sélectionné")
        self.label_fichier.setStyleSheet("color: gray; font-style: italic;")
        form_layout.addRow("", self.label_fichier)
        
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
        """Charge la liste des patients"""
        try:
            patients = db.obtenir_patients()
            self.patient_combo.clear()
            
            for patient in patients:
                self.patient_combo.addItem(patient['nom_complet'], patient['id'])
                
            # Sélectionner le patient actuel si disponible
            if patient_context.selected_patient_id:
                for i in range(self.patient_combo.count()):
                    if self.patient_combo.itemData(i) == patient_context.selected_patient_id:
                        self.patient_combo.setCurrentIndex(i)
                        break
                        
        except Exception as e:
            #print(f"Erreur lors du chargement des patients: {e}")
            QMessageBox.warning(self, "Erreur", f"Erreur lors du chargement des patients: {e}")
    
    def selectionner_fichier(self):
        """Ouvre le dialog de sélection de fichier"""
        initial_dir = path_manager.get_app_data_folder()
        fichier, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner une image",
            initial_dir,
            "Images (*.png *.jpg *.jpeg *.bmp *.tiff *.dcm);;Tous les fichiers (*)"
        )
        
        if fichier:
            self.chemin_fichier = fichier
            nom_fichier = os.path.basename(fichier)
            self.label_fichier.setText(f"Fichier: {nom_fichier}")
            self.label_fichier.setStyleSheet("color: green;")
            
            # Remplir automatiquement le nom si vide
            if not self.nom_edit.text():
                nom_sans_ext = os.path.splitext(nom_fichier)[0]
                self.nom_edit.setText(nom_sans_ext)
    
    def valider_et_accepter(self):
        """Valide les données avant d'accepter"""
        if not self.chemin_fichier:
            QMessageBox.warning(self, "Validation", "Veuillez sélectionner un fichier image.")
            return
        
        if not self.nom_edit.text().strip():
            QMessageBox.warning(self, "Validation", "Veuillez saisir un nom pour l'image.")
            return
            
        if not self.patient_combo.currentData():
            QMessageBox.warning(self, "Validation", "Veuillez sélectionner un patient.")
            return
        
        self.accept()
    
    def get_image_data(self):
        """Retourne les données de l'image"""
        return {
            'patient_id': self.patient_combo.currentData(),
            'nom': self.nom_edit.text().strip(),
            'type': self.type_combo.currentText(),
            'description': self.description_edit.toPlainText().strip(),
            'chemin_source': self.chemin_fichier
        }

class ImageViewer(QLabel):
    """Widget personnalisé pour afficher et manipuler les images médicales - VERSION CORRIGÉE"""
    
    def __init__(self):
        super().__init__()
        self.setMinimumSize(400, 400)
        self.setStyleSheet("""
            QLabel {
                border: 2px solid #D0D0D0;
                background-color: #F8F8F8;
                border-radius: 5px;
            }
        """)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText("Image non trouvée")
        self.setWordWrap(True)
        
        self.current_pixmap = None
        self.scale_factor = 1.0
        self.original_size = None
    
    def load_image(self, image_path):
        """Charge et affiche une image - VERSION CORRIGÉE"""
        #print(f"🔍 Chargement de l'image: {image_path}")  # Debug
        
        if os.path.exists(image_path):
            self.current_pixmap = QPixmap(image_path)
            if not self.current_pixmap.isNull():
                self.original_size = self.current_pixmap.size()
                self.scale_factor = 1.0
                self.update_display()
                #print(f"✅ Image chargée avec succès: {self.original_size}")  # Debug
            else:
                self.setText("Erreur lors du chargement de l'image")
                #print("❌ Erreur: Pixmap null")  # Debug
        else:
            self.setText("Image non trouvée")
            #print(f"❌ Fichier non trouvé: {image_path}")  # Debug
    
    def update_display(self):
        """Met à jour l'affichage de l'image avec le facteur de zoom - VERSION CORRIGÉE"""
        if self.current_pixmap and not self.current_pixmap.isNull():
            # Calculer la nouvelle taille
            new_size = self.original_size * self.scale_factor
            
            # Redimensionner l'image
            scaled_pixmap = self.current_pixmap.scaled(
                new_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            self.setPixmap(scaled_pixmap)
            self.resize(scaled_pixmap.size()) 

    def zoom_in(self):
        """Zoom avant - VERSION CORRIGÉE"""
        if self.current_pixmap and not self.current_pixmap.isNull():
            self.scale_factor *= 1.25
            self.update_display()
            #print(f"🔍 Zoom avant: {self.scale_factor:.2f}")  # Debug
    
    def zoom_out(self):
        """Zoom arrière - VERSION CORRIGÉE"""
        if self.current_pixmap and not self.current_pixmap.isNull():
            self.scale_factor /= 1.25
            if self.scale_factor < 0.1:  # Limite minimale
                self.scale_factor = 0.1
            self.update_display()
            #print(f"🔍 Zoom arrière: {self.scale_factor:.2f}")  # Debug
    
    def reset_zoom(self):
        """Remet le zoom à 100% - VERSION CORRIGÉE"""
        if self.current_pixmap and not self.current_pixmap.isNull():
            self.scale_factor = 1.0
            self.update_display()
            #print(f"🔍 Zoom reset: 100%")  # Debug
    
    def get_zoom_percentage(self):
        """Retourne le pourcentage de zoom actuel"""
        return int(self.scale_factor * 100)

class ImageListWidget(QListWidget):
    """Widget personnalisé pour la liste des images - VERSION CORRIGÉE"""
    image_selected = Signal(str, dict)  # path, metadata
    
    def __init__(self):
        super().__init__()
        self.setIconSize(QSize(80, 80))
        self.setViewMode(QListWidget.ViewMode.ListMode)
        self.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.setStyleSheet("""
            QListWidget {
                border: 1px solid #D0D0D0;
                background-color: white;
                border-radius: 3px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #E0E0E0;
            }
            QListWidget::item:selected {
                background-color: #C0D0E0;
                color: black;
            }
            QListWidget::item:hover {
                background-color: #E8F4FD;
            }
        """)
        
        self.itemClicked.connect(self.on_item_clicked)
    
    def charger_images_patient(self, patient_id):
        """Charge les images d'un patient depuis la base de données - VERSION CORRIGÉE"""
        self.clear()
        #print(f"🔍 Chargement des images pour patient ID: {patient_id}")  # Debug
        
        if patient_id is None:
            #print("❌ Aucun patient sélectionné")  # Debug
            return
        
        try:
            images = db.obtenir_images_patient(patient_id)
            #print(f"🔍 Nombre d'images trouvées: {len(images)}")  # Debug
            
            for image_data in images:
                self.add_image_item(image_data)
                
        except Exception as e:
            #print(f"❌ Erreur lors du chargement des images: {e}")
            QMessageBox.warning(self, "Erreur", f"Erreur lors du chargement des images: {e}")
    
    def add_image_item(self, image_data):
        """Ajoute un élément image à la liste - VERSION CORRIGÉE"""
        item = QListWidgetItem()
        
        # Créer l'icône à partir de l'image
        chemin_image = image_data.get("chemin_fichier", "")
        if chemin_image and os.path.exists(chemin_image):
            try:
                pixmap = QPixmap(chemin_image)
                if not pixmap.isNull():
                    # Redimensionner pour l'icône
                    icon_pixmap = pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    icon = QIcon(icon_pixmap)
                    item.setIcon(icon)
            except Exception as e:
                #print(f"❌ Erreur lors de la création de l'icône: {e}")
                QMessageBox.warning(self, "Erreur", f"Erreur lors de la création de l'icône: {e}")
        
        # Texte de l'élément
        nom = image_data.get('nom_fichier', 'Image sans nom')
        type_img = image_data.get('type_image', 'Type inconnu')
        date_creation = image_data.get('date_creation', '')
        date_affichage = date_creation[:10] if date_creation else 'Date inconnue'
        
        item.setText(f"{nom}\n{type_img} - {date_affichage}")
        
        # Stocker les métadonnées directement dans l'élément
        item.setData(Qt.ItemDataRole.UserRole, image_data)
        
        self.addItem(item)
        #print(f"✅ Image ajoutée à la liste: {nom}")  # Debug
    
    def on_item_clicked(self, item):
        """Gère le clic sur un élément de la liste - VERSION CORRIGÉE"""
        image_data = item.data(Qt.ItemDataRole.UserRole)
        if image_data:
            chemin_image = image_data.get("chemin_fichier", "")
            #print(f"🔍 Image sélectionnée: {chemin_image}")  # Debug
            self.image_selected.emit(chemin_image, image_data)

class ImagerieView(QWidget):
    def __init__(self):
        super().__init__()
        self.patient_actuel = None
        self.image_actuelle = None
        self.setup_ui()
        
        # Connecter au contexte patient global
        patient_context.patient_changed.connect(self.on_patient_changed)
        
        # Charger le patient initial si disponible
        if patient_context.selected_patient_id:
            self.on_patient_changed(patient_context.selected_patient_id, patient_context.selected_patient_name)
    
    def setup_ui(self):
        # Layout principal horizontal
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Splitter pour diviser l'interface
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Partie gauche: Filtres et liste des images
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Titre
        titre = QLabel("Imagerie Médicale")
        titre.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px; color: #333;")
        left_layout.addWidget(titre)
        
        # Section des filtres
        filtres_section = self.create_filters_section()
        left_layout.addWidget(filtres_section)
        
        # Section des images disponibles
        images_section = self.create_images_list_section()
        left_layout.addWidget(images_section)
        
        # Section des actions
        actions_section = self.create_actions_section()
        left_layout.addWidget(actions_section)
        
        # Partie droite: Visualiseur et informations
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Section du visualiseur
        viewer_section = self.create_viewer_section()
        right_layout.addWidget(viewer_section)
        
        # Section des informations de l'image
        info_section = self.create_image_info_section()
        right_layout.addWidget(info_section)
        
        # Ajouter les widgets au splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([400, 600])  # Proportion initiale
        
        main_layout.addWidget(splitter)
    
    def create_filters_section(self):
        """Crée la section des filtres - VERSION CORRIGÉE"""
        group = QGroupBox("Filtres")
        layout = QVBoxLayout(group)
        
        # Sélection du patient
        patient_layout = QHBoxLayout()
        patient_layout.addWidget(QLabel("Patient:"))
        self.patient_combo = QComboBox()
        self.charger_patients()
        self.patient_combo.currentIndexChanged.connect(self.patient_change)
        patient_layout.addWidget(self.patient_combo)
        layout.addLayout(patient_layout)
        
        # Type d'image
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Tous", "Radiographie Panoramique", "Radiographie Rétro-alvéolaire", 
                                 "Scanner 3D", "Photo Intra-orale", "Photo Extra-orale", "Empreinte Numérique", "Autre"])
        type_layout.addWidget(self.type_combo)
        layout.addLayout(type_layout)
        
        # Date depuis
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Depuis:"))
        self.date_combo = QComboBox()
        self.date_combo.addItems(["Toutes", "Aujourd'hui", "Cette semaine", "Ce mois", "Cette année"])
        date_layout.addWidget(self.date_combo)
        layout.addLayout(date_layout)
        
        # Bouton appliquer filtres - CORRIGÉ
        self.btn_appliquer = QPushButton("Appliquer Filtres")
        self.btn_appliquer.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.btn_appliquer.clicked.connect(self.appliquer_filtres)
        layout.addWidget(self.btn_appliquer)
        
        return group
    
    def create_images_list_section(self):
        """Crée la section de la liste des images"""
        group = QGroupBox("Images Disponibles")
        layout = QVBoxLayout(group)
        
        # Liste des images
        self.image_list = ImageListWidget()
        self.image_list.image_selected.connect(self.on_image_selected)
        layout.addWidget(self.image_list)
        
        return group
    
    def create_actions_section(self):
        """Crée la section des actions - VERSION CORRIGÉE"""
        group = QGroupBox("Actions")
        layout = QVBoxLayout(group)
        
        # Bouton ajouter
        self.btn_ajouter = QPushButton("Ajouter Image")
        self.btn_ajouter.setStyleSheet("""
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
        self.btn_ajouter.clicked.connect(self.ajouter_image)
        layout.addWidget(self.btn_ajouter)
        
        # Bouton supprimer - CORRIGÉ
        self.btn_supprimer = QPushButton("Supprimer")
        self.btn_supprimer.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
            QPushButton:disabled {
                background-color: #C0C0C0;
            }
        """)
        self.btn_supprimer.clicked.connect(self.supprimer_image)
        self.btn_supprimer.setEnabled(False)
        layout.addWidget(self.btn_supprimer)
        
        # Bouton exporter - CORRIGÉ
        self.btn_exporter = QPushButton("Exporter")
        self.btn_exporter.setStyleSheet("""
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
            QPushButton:disabled {
                background-color: #C0C0C0;
            }
        """)
        self.btn_exporter.clicked.connect(self.exporter_image)
        self.btn_exporter.setEnabled(False)
        layout.addWidget(self.btn_exporter)
        
        return group
    
    def create_viewer_section(self):
        """Crée la section du visualiseur - VERSION CORRIGÉE"""
        group = QGroupBox("Visualiseur")
        layout = QVBoxLayout(group)
        
        # Contrôles de zoom - CORRIGÉS
        zoom_layout = QHBoxLayout()
        
        self.btn_zoom_out = QPushButton("Zoom -")
        self.btn_zoom_out.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        self.btn_zoom_out.clicked.connect(self.zoom_out)
        zoom_layout.addWidget(self.btn_zoom_out)
        
        # Bouton 100% - CORRIGÉ
        self.btn_100_percent = QPushButton("100%")
        self.btn_100_percent.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.btn_100_percent.clicked.connect(self.reset_zoom)
        zoom_layout.addWidget(self.btn_100_percent)
        
        self.btn_zoom_in = QPushButton("Zoom +")
        self.btn_zoom_in.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        self.btn_zoom_in.clicked.connect(self.zoom_in)
        zoom_layout.addWidget(self.btn_zoom_in)
        
        layout.addLayout(zoom_layout)
        
        # Visualiseur d'image - CORRIGÉ
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(False)
        scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        
        self.image_viewer = ImageViewer()
        scroll_area.setWidget(self.image_viewer)
        
        layout.addWidget(scroll_area)
        
        return group
    
    def create_image_info_section(self):
        """Crée la section des informations de l'image"""
        group = QGroupBox("Informations de l'Image")
        layout = QVBoxLayout(group)
        
        # Onglets pour organiser les informations
        tabs = QTabWidget()
        
        # Onglet Général
        general_tab = QWidget()
        general_layout = QFormLayout(general_tab)
        
        self.meta_nom = QLabel("-")
        self.meta_type = QLabel("-")
        self.meta_date = QLabel("-")
        self.meta_patient = QLabel("-")
        
        general_layout.addRow("Nom:", self.meta_nom)
        general_layout.addRow("Type:", self.meta_type)
        general_layout.addRow("Date:", self.meta_date)
        general_layout.addRow("Patient:", self.meta_patient)
        
        tabs.addTab(general_tab, "Général")
        
        # Onglet Description
        desc_tab = QWidget()
        desc_layout = QVBoxLayout(desc_tab)
        
        desc_layout.addWidget(QLabel("Description:"))
        self.meta_description = QTextEdit()
        self.meta_description.setReadOnly(True)
        self.meta_description.setMaximumHeight(100)
        desc_layout.addWidget(self.meta_description)
        
        tabs.addTab(desc_tab, "Description")
        
        layout.addWidget(tabs)
        
        return group
    
    def charger_patients(self):
        """Charge la liste des patients - VERSION CORRIGÉE"""
        try:
            patients = db.obtenir_patients()
            self.patient_combo.clear()
            self.patient_combo.addItem("Sélectionner un patient...", None)
            
            for patient in patients:
                self.patient_combo.addItem(patient['nom_complet'], patient['id'])
                
        except Exception as e:
            #print(f"❌ Erreur lors du chargement des patients: {e}")
            QMessageBox.warning(self, "Erreur", f"Erreur lors du chargement des patients: {e}")
    
    def patient_change(self):
        """Gère le changement de patient sélectionné - VERSION CORRIGÉE"""
        self.patient_actuel = self.patient_combo.currentData()
        #print(f"🔍 Patient changé: {self.patient_actuel}")  # Debug
        
        # Vider l'affichage actuel
        self.image_viewer.setText("Aucune image sélectionnée")
        self.clear_image_info()
        self.image_actuelle = None
        self.btn_supprimer.setEnabled(False)
        self.btn_exporter.setEnabled(False)
        
        # Charger les images du nouveau patient
        self.image_list.charger_images_patient(self.patient_actuel)


    def appliquer_filtres(self):
        """Applique les filtres sélectionnés avec filtrage réel - VERSION CORRIGÉE"""
        
        # Récupérer les valeurs des filtres
        patient_id = self.patient_combo.currentData()
        type_filtre = self.type_combo.currentText()
        
        if not patient_id:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un patient d'abord.")
            return
        
        try:
            # Charger toutes les images du patient d'abord
            images = db.obtenir_images_patient(patient_id)
            
            # Filtrer par type si spécifié
            if type_filtre and type_filtre != "Tous":
                images = [img for img in images if img.get('type_image') == type_filtre]
            
            # Mettre à jour la liste avec les images filtrées
            self.image_list.clear()
            for image_data in images:
                self.image_list.add_image_item(image_data)
            
            QMessageBox.information(self, "Filtres", f"Filtres appliqués avec succès!\n{len(images)} image(s) trouvée(s).")
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du filtrage: {str(e)}")

    
    def on_image_selected(self, image_path, metadata):
        """Gère la sélection d'une image - VERSION CORRIGÉE"""
        
        # Stocker l'image actuelle
        self.image_actuelle = metadata
        
        # Charger l'image dans le visualiseur
        self.image_viewer.load_image(image_path)
        
        # Mettre à jour les métadonnées
        self.update_image_info(metadata)
        
        # Activer les boutons d'action
        self.btn_supprimer.setEnabled(True)
        self.btn_exporter.setEnabled(True)
    
    def update_image_info(self, metadata):
        """Met à jour les informations de l'image"""
        self.meta_nom.setText(metadata.get("nom_fichier", "-"))
        self.meta_type.setText(metadata.get("type_image", "-"))
        
        date_creation = metadata.get("date_creation", "")
        date_affichage = date_creation[:10] if date_creation else "-"
        self.meta_date.setText(date_affichage)
        
        # Obtenir le nom du patient
        try:
            patient_id = metadata.get("patient_id")
            if patient_id:
                patient = db.get_patient_by_id(patient_id)
                if patient and len(patient) >= 3:
                    self.meta_patient.setText(f"{patient[1]}, {patient[2]}")
                else:
                    self.meta_patient.setText("-")
            else:
                self.meta_patient.setText("-")
        except Exception as e:
            self.meta_patient.setText("-")
        
        self.meta_description.setPlainText(metadata.get("description", ""))
    
    def clear_image_info(self):
        """Vide les informations de l'image"""
        self.meta_nom.setText("-")
        self.meta_type.setText("-")
        self.meta_date.setText("-")
        self.meta_patient.setText("-")
        self.meta_description.setPlainText("")
    
    def zoom_in(self):
        """Zoom avant - VERSION CORRIGÉE"""
        self.image_viewer.zoom_in()
        # Mettre à jour l'affichage du pourcentage
        self.btn_100_percent.setText(f"{self.image_viewer.get_zoom_percentage()}%")
    
    def zoom_out(self):
        """Zoom arrière - VERSION CORRIGÉE"""
        self.image_viewer.zoom_out()
        # Mettre à jour l'affichage du pourcentage
        self.btn_100_percent.setText(f"{self.image_viewer.get_zoom_percentage()}%")
    
    def reset_zoom(self):
        """Remet le zoom à 100% - VERSION CORRIGÉE"""
        self.image_viewer.reset_zoom()
        self.btn_100_percent.setText("100%")
    
    def ajouter_image(self):
        """Ajoute une nouvelle image - VERSION CORRIGÉE"""
        dialog = AjouterImageDialog(self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            image_data = dialog.get_image_data()
            
            try:
                # Créer le dossier de destination s'il n'existe pas
                #dest_dir = "data/images"
                dest_dir = path_manager.get_images_folder()
                os.makedirs(dest_dir, exist_ok=True)
                
                # Générer un nom de fichier unique
                timestamp = QDate.currentDate().toString("yyyyMMdd")
                extension = os.path.splitext(image_data['chemin_source'])[1]
                nom_fichier = f"{image_data['patient_id']}_{timestamp}_{image_data['nom']}{extension}"
                nom_fichier = nom_fichier.replace(" ", "_")  # Remplacer les espaces
                
                chemin_dest = os.path.join(dest_dir, nom_fichier)
                
                # Copier le fichier vers le dossier de données
                shutil.copy2(image_data['chemin_source'], chemin_dest)
                
                # Ajouter à la base de données
                image_id = db.ajouter_image(
                    image_data['patient_id'],
                    nom_fichier,
                    image_data['type'],
                    chemin_dest,
                    image_data['description']
                )
                
                if image_id:
                    QMessageBox.information(self, "Succès", "Image ajoutée avec succès!")
                    # Recharger les images si c'est le patient actuel
                    if self.patient_actuel == image_data['patient_id']:
                        self.image_list.charger_images_patient(self.patient_actuel)
                else:
                    QMessageBox.warning(self, "Erreur", "Erreur lors de l'ajout de l'image en base de données.")
                    
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de l'ajout de l'image: {str(e)}")
                #print(f"❌ Erreur lors de l'ajout: {e}")
    
    def supprimer_image(self):
        """Supprime l'image sélectionnée - VERSION CORRIGÉE"""
        if not self.image_actuelle:
            QMessageBox.warning(self, "Erreur", "Aucune image sélectionnée.")
            return
        
        # Demander confirmation
        nom_image = self.image_actuelle.get("nom_fichier", "cette image")
        reply = QMessageBox.question(
            self,
            "Confirmer la suppression",
            f"Êtes-vous sûr de vouloir supprimer '{nom_image}' ?\n\nCette action est irréversible.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                image_id = self.image_actuelle.get("id")
                if image_id:
                    # Supprimer de la base de données
                    success = db.supprimer_image(image_id)
                    
                    if success:
                        # Supprimer le fichier physique
                        chemin_fichier = self.image_actuelle.get("chemin_fichier")
                        if chemin_fichier and os.path.exists(chemin_fichier):
                            try:
                                os.remove(chemin_fichier)
                            except Exception as e:
                        
                                QMessageBox.information(self, "Succès", "Image supprimée avec succès!")
                        
                        # Recharger la liste et vider l'affichage
                        self.image_list.charger_images_patient(self.patient_actuel)
                        self.image_viewer.setText("Aucune image sélectionnée")
                        self.clear_image_info()
                        self.image_actuelle = None
                        self.btn_supprimer.setEnabled(False)
                        self.btn_exporter.setEnabled(False)
                    else:
                        QMessageBox.warning(self, "Erreur", "Erreur lors de la suppression de l'image.")
                else:
                    QMessageBox.warning(self, "Erreur", "ID de l'image non trouvé.")
                    
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de la suppression: {str(e)}")
    
    def exporter_image(self):
        """Exporte l'image sélectionnée - VERSION CORRIGÉE"""
        if not self.image_actuelle:
            QMessageBox.warning(self, "Erreur", "Aucune image sélectionnée.")
            return
        
        # Obtenir le chemin source
        chemin_source = self.image_actuelle.get("chemin_fichier")
        if not chemin_source or not os.path.exists(chemin_source):
            QMessageBox.warning(self, "Erreur", "Fichier image non trouvé.")
            return
        
        # Proposer un nom de fichier par défaut
        nom_original = self.image_actuelle.get("nom_fichier", "image")
        extension = os.path.splitext(nom_original)[1]
        nom_propose = f"{nom_original}"
        default_path = os.path.join(path_manager.get_exports_folder(), nom_propose)
        # Dialogue de sauvegarde
        chemin_dest, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter l'image",
            default_path,
            f"Images (*{extension});;Tous les fichiers (*)"
        )
        
        if chemin_dest:
            try:
                shutil.copy2(chemin_source, chemin_dest)
                QMessageBox.information(self, "Succès", f"Image exportée vers:\n{chemin_dest}")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de l'exportation: {str(e)}")
    
    def on_patient_changed(self, patient_id, patient_name):
        """Gère le changement de patient depuis le contexte global - NOUVEAU"""
        if patient_id:
            # Recharger la liste des patients
            self.charger_patients()
            # Mettre à jour le combo box
            for i in range(self.patient_combo.count()):
                if self.patient_combo.itemData(i) == patient_id:
                    self.patient_combo.setCurrentIndex(i)
                    break
        
        # Charger les images du nouveau patient
        self.patient_actuel = patient_id
        self.image_list.charger_images_patient(patient_id)
        
        # Vider l'affichage actuel
        self.image_viewer.setText("Aucune image sélectionnée")
        self.clear_image_info()
        self.image_actuelle = None
        self.btn_supprimer.setEnabled(False)
        self.btn_exporter.setEnabled(False)