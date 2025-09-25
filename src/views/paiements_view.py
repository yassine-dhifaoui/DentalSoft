from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
                             QScrollArea, QFrame, QPushButton, QGridLayout, 
                             QGroupBox, QLineEdit, QDateEdit, QComboBox, 
                             QTableWidget, QTableWidgetItem, QHeaderView, 
                             QSplitter, QTextEdit, QSpinBox, QFormLayout,
                             QDialog, QDialogButtonBox, QMessageBox, QFileDialog,
                             QTabWidget, QCalendarWidget, QDoubleSpinBox)
from PySide6.QtCore import Qt, QDate, Signal, QDateTime
from PySide6.QtGui import QFont, QColor, QIcon, QPainter, QPen, QBrush
from PySide6.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog
from PySide6.QtCharts import QChart, QChartView, QPieSeries, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis

import os
import json
from datetime import datetime, timedelta
from database import db
from src.patient_context import patient_context
from src.path_manager import path_manager


try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen.canvas import Canvas
    from reportlab.lib.utils import ImageReader
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

class FactureDialog(QDialog):
    """Dialogue pour créer ou modifier une facture"""
    
    def __init__(self, parent=None, patient_id=None, facture_id=None):
        super().__init__(parent)
        self.patient_id = patient_id
        self.facture_id = facture_id
        self.lignes_facture = []
        self.actes_dentaires = db.obtenir_actes_dentaires()
        
        self.setup_ui()
        
        if facture_id:
            self.charger_facture(facture_id)
        else:
            self.setWindowTitle("Nouvelle Facture")
    
    def setup_ui(self):
        self.setWindowTitle("Facture")
        self.resize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # Informations générales
        info_group = QGroupBox("Informations Générales")
        info_layout = QFormLayout(info_group)
        
        # Patient
        self.patient_combo = QComboBox()
        self.charger_patients()
        if self.patient_id:
            index = self.patient_combo.findData(self.patient_id)
            if index >= 0:
                self.patient_combo.setCurrentIndex(index)
        info_layout.addRow("Patient:", self.patient_combo)
        
        # Date de facture
        self.date_facture = QDateEdit()
        self.date_facture.setDate(QDate.currentDate())
        self.date_facture.setCalendarPopup(True)
        info_layout.addRow("Date:", self.date_facture)
        
        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        info_layout.addRow("Description:", self.description_edit)
        
        layout.addWidget(info_group)
        
        # Lignes de facture
        lignes_group = QGroupBox("Détails de la Facture")
        lignes_layout = QVBoxLayout(lignes_group)
        
        # Tableau des lignes
        self.lignes_table = QTableWidget(0, 5)
        self.lignes_table.setHorizontalHeaderLabels(["Acte", "Description", "Quantité", "Prix unitaire", "Total"])
        self.lignes_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.lignes_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        lignes_layout.addWidget(self.lignes_table)
        
        # Boutons d'action pour les lignes
        btn_layout = QHBoxLayout()
        
        self.btn_ajouter_ligne = QPushButton("Ajouter Acte")
        self.btn_ajouter_ligne.clicked.connect(self.ajouter_ligne)
        btn_layout.addWidget(self.btn_ajouter_ligne)
        
        self.btn_supprimer_ligne = QPushButton("Supprimer Acte")
        self.btn_supprimer_ligne.clicked.connect(self.supprimer_ligne)
        btn_layout.addWidget(self.btn_supprimer_ligne)
        
        lignes_layout.addLayout(btn_layout)
        
        # Total
        total_layout = QHBoxLayout()
        total_layout.addStretch()
        self.label_total = QLabel("Total: 0.00 DT")
        self.label_total.setStyleSheet("font-size: 16px; font-weight: bold;")
        total_layout.addWidget(self.label_total)
        
        lignes_layout.addLayout(total_layout)
        
        layout.addWidget(lignes_group)
        
        # Boutons de dialogue
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def charger_patients(self):
        """Charge la liste des patients dans le combobox"""
        self.patient_combo.clear()
        patients = db.obtenir_patients()
        
        for patient in patients:
            self.patient_combo.addItem(f"{patient['nom']}, {patient['prenom']}", patient['id'])
    
    def charger_facture(self, facture_id):
        """Charge les données d'une facture existante"""
        # TODO: Implémenter le chargement d'une facture existante
        pass
    
    def ajouter_ligne(self):
        """Ajoute une nouvelle ligne à la facture"""
        dialog = LigneFactureDialog(self, self.actes_dentaires)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            ligne = dialog.get_ligne()
            self.lignes_facture.append(ligne)
            self.rafraichir_tableau()
    
    def supprimer_ligne(self):
        """Supprime la ligne sélectionnée"""
        selected_rows = self.lignes_table.selectedIndexes()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        if 0 <= row < len(self.lignes_facture):
            del self.lignes_facture[row]
            self.rafraichir_tableau()
    
    def rafraichir_tableau(self):
        """Met à jour le tableau des lignes et le total"""
        self.lignes_table.setRowCount(0)
        total = 0
        
        for ligne in self.lignes_facture:
            row = self.lignes_table.rowCount()
            self.lignes_table.insertRow(row)
            
            # Acte
            acte_item = QTableWidgetItem(ligne.get("code", ""))
            self.lignes_table.setItem(row, 0, acte_item)
            
            # Description
            desc_item = QTableWidgetItem(ligne.get("libelle", ""))
            self.lignes_table.setItem(row, 1, desc_item)
            
            # Quantité
            qte_item = QTableWidgetItem(str(ligne.get("quantite", 1)))
            self.lignes_table.setItem(row, 2, qte_item)
            
            # Prix unitaire
            prix_item = QTableWidgetItem(f"{ligne.get('prix_unitaire', 0):.2f} DT")
            self.lignes_table.setItem(row, 3, prix_item)
            
            # Total ligne
            montant = ligne.get("quantite", 1) * ligne.get("prix_unitaire", 0)
            total_item = QTableWidgetItem(f"{montant:.2f} DT")
            self.lignes_table.setItem(row, 4, total_item)
            
            total += montant
        
        self.label_total.setText(f"Total: {total:.2f} DT")
    
    def accept(self):
        """Valide la facture"""
        if not self.lignes_facture:
            QMessageBox.warning(self, "Erreur", "Veuillez ajouter au moins une ligne à la facture.")
            return
        
        patient_id = self.patient_combo.currentData()
        if not patient_id:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un patient.")
            return
        
        date_facture = self.date_facture.date().toString("yyyy-MM-dd")
        description = self.description_edit.toPlainText()
        
        # Calculer le total
        total = sum(ligne.get("quantite", 1) * ligne.get("prix_unitaire", 0) for ligne in self.lignes_facture)
        
        # Créer la facture
        facture_id = db.ajouter_facture(
            patient_id=patient_id,
            date_facture=date_facture,
            montant_total=total,
            details=description,
            lignes_facture=self.lignes_facture
        )
        
        if facture_id:
            QMessageBox.information(self, "Succès", "La facture a été créée avec succès.")
            super().accept()
        else:
            QMessageBox.critical(self, "Erreur", "Une erreur est survenue lors de la création de la facture.")

class LigneFactureDialog(QDialog):
    """Dialogue pour ajouter une ligne à une facture"""
    
    def __init__(self, parent=None, actes_dentaires=None):
        super().__init__(parent)
        self.actes_dentaires = actes_dentaires or []
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("Ajouter un acte")
        self.resize(400, 200)
        
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        # Acte dentaire
        self.acte_combo = QComboBox()
        self.acte_combo.addItem("-- Sélectionner un acte --", None)
        
        for acte in self.actes_dentaires:
            self.acte_combo.addItem(f"{acte['code']} - {acte['libelle']}", acte['id'])
        
        self.acte_combo.currentIndexChanged.connect(self.acte_change)
        form_layout.addRow("Acte:", self.acte_combo)
        
        # Libellé
        self.libelle_edit = QLineEdit()
        form_layout.addRow("Description:", self.libelle_edit)
        
        # Quantité
        self.quantite_spin = QSpinBox()
        self.quantite_spin.setMinimum(1)
        self.quantite_spin.setMaximum(99)
        self.quantite_spin.setValue(1)
        self.quantite_spin.valueChanged.connect(self.calculer_total)
        form_layout.addRow("Quantité:", self.quantite_spin)
        
        # Prix unitaire
        self.prix_spin = QDoubleSpinBox()
        self.prix_spin.setMinimum(0)
        self.prix_spin.setMaximum(9999.99)
        self.prix_spin.setDecimals(2)
        self.prix_spin.setSuffix(" DT")
        self.prix_spin.valueChanged.connect(self.calculer_total)
        form_layout.addRow("Prix unitaire:", self.prix_spin)
        
        # Total
        self.total_label = QLabel("0.00 DT")
        form_layout.addRow("Total:", self.total_label)
        
        layout.addLayout(form_layout)
        
        # Boutons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def acte_change(self):
        """Gère le changement d'acte sélectionné"""
        acte_id = self.acte_combo.currentData()
        
        if acte_id:
            # Trouver l'acte correspondant
            acte = next((a for a in self.actes_dentaires if a['id'] == acte_id), None)
            
            if acte:
                self.libelle_edit.setText(acte['libelle'])
                self.prix_spin.setValue(acte['tarif_base'])
                self.calculer_total()
    
    def calculer_total(self):
        """Calcule le total de la ligne"""
        quantite = self.quantite_spin.value()
        prix = self.prix_spin.value()
        total = quantite * prix
        
        self.total_label.setText(f"{total:.2f} DT")
    
    def get_ligne(self):
        """Retourne les données de la ligne"""
        acte_id = self.acte_combo.currentData()
        code = ""
        
        if acte_id:
            acte = next((a for a in self.actes_dentaires if a['id'] == acte_id), None)
            if acte:
                code = acte['code']
        
        return {
            "acte_id": acte_id,
            "code": code,
            "libelle": self.libelle_edit.text(),
            "quantite": self.quantite_spin.value(),
            "prix_unitaire": self.prix_spin.value()
        }

class PaiementDialog(QDialog):
    """Dialogue pour enregistrer un paiement"""
    
    def __init__(self, parent=None, patient_id=None, numero_facture=None):
        super().__init__(parent)
        self.patient_id = patient_id
        self.numero_facture = numero_facture
        
        self.setup_ui()
        
        if patient_id:
            index = self.patient_combo.findData(patient_id)
            if index >= 0:
                self.patient_combo.setCurrentIndex(index)
                #self.patient_combo.setEnabled(False)
        
        if numero_facture:
            self.facture_edit.setText(numero_facture)
            self.facture_edit.setEnabled(False)
    
    def setup_ui(self):
        self.setWindowTitle("Enregistrer un Paiement")
        self.resize(400, 300)
        
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        # Patient
        self.patient_combo = QComboBox()
        self.charger_patients()
        form_layout.addRow("Patient:", self.patient_combo)
        
        # Date de paiement
        self.date_paiement = QDateEdit()
        self.date_paiement.setDate(QDate.currentDate())
        self.date_paiement.setCalendarPopup(True)
        form_layout.addRow("Date:", self.date_paiement)
        
        # Montant
        self.montant_spin = QDoubleSpinBox()
        self.montant_spin.setMinimum(0)
        self.montant_spin.setMaximum(9999.99)
        self.montant_spin.setDecimals(2)
        self.montant_spin.setSuffix(" DT")
        form_layout.addRow("Montant:", self.montant_spin)
        
        # Mode de paiement
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Carte bancaire", "Espèces", "Chèque", "Virement"])
        form_layout.addRow("Mode de paiement:", self.mode_combo)
        
        # Numéro de facture
        self.facture_edit = QLineEdit()
        form_layout.addRow("N° Facture:", self.facture_edit)
        
        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        form_layout.addRow("Description:", self.description_edit)
        
        layout.addLayout(form_layout)
        
        # Boutons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def charger_patients(self):
        """Charge la liste des patients dans le combobox"""
        self.patient_combo.clear()
        self.patient_combo.addItem("-- Sélectionner un patient --", None)
        
        patients = db.obtenir_patients()
        for patient in patients:
            self.patient_combo.addItem(f"{patient['nom']}, {patient['prenom']}", patient['id'])
    
    def accept(self):
        """Valide le paiement"""
        patient_id = self.patient_combo.currentData()
        if not patient_id:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un patient.")
            return
        
        montant = self.montant_spin.value()
        if montant <= 0:
            QMessageBox.warning(self, "Erreur", "Le montant doit être supérieur à zéro.")
            return
        
        date_paiement = self.date_paiement.date().toString("yyyy-MM-dd")
        mode_paiement = self.mode_combo.currentText()
        numero_facture = self.facture_edit.text() or None
        description = self.description_edit.toPlainText()
        
        # Enregistrer le paiement
        paiement_id = db.enregistrer_paiement(
            patient_id=patient_id,
            montant=montant,
            date_paiement=date_paiement,
            mode_paiement=mode_paiement,
            numero_facture=numero_facture,
            description=description
        )
        
        if paiement_id:
            QMessageBox.information(self, "Succès", "Le paiement a été enregistré avec succès.")
            super().accept()
        else:
            QMessageBox.critical(self, "Erreur", "Une erreur est survenue lors de l'enregistrement du paiement.")

class PaiementsView(QWidget):
    """Vue principale pour la gestion des paiements"""
    
    def __init__(self):
        super().__init__()
        self.patient_actuel = None
        self.setup_ui()
        self.charger_donnees()
        
        # CORRECTION 1: Connexion au signal de changement de patient
        patient_context.patient_changed.connect(self.on_patient_changed)
    
    def on_patient_changed(self, patient_id):
        """CORRECTION 1: Gère le changement de patient global"""
        self.patient_actuel = patient_id
        
        if patient_id:
            # Recharger la liste des patients
            self.charger_patients()
            # Mettre à jour les combobox de filtres
            for i in range(self.facture_patient_combo.count()):
                if self.facture_patient_combo.itemData(i) == patient_id:
                    self.facture_patient_combo.setCurrentIndex(i)
                    break
            
            for i in range(self.paiement_patient_combo.count()):
                if self.paiement_patient_combo.itemData(i) == patient_id:
                    self.paiement_patient_combo.setCurrentIndex(i)
                    break
            
            # Recharger les données pour ce patient
            self.charger_factures(patient_id)
            self.charger_paiements(patient_id)
    
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Titre
        titre_layout = QHBoxLayout()
        titre = QLabel("Gestion des Paiements")
        titre.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        titre_layout.addWidget(titre)
        
        # Boutons d'action principaux
        self.btn_nouvelle_facture = QPushButton("Nouvelle Facture")
        self.btn_nouvelle_facture.setStyleSheet("""
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
        self.btn_nouvelle_facture.clicked.connect(self.nouvelle_facture)
        titre_layout.addWidget(self.btn_nouvelle_facture)
        
        self.btn_nouveau_paiement = QPushButton("Nouveau Paiement")
        self.btn_nouveau_paiement.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)
        self.btn_nouveau_paiement.clicked.connect(self.nouveau_paiement)
        titre_layout.addWidget(self.btn_nouveau_paiement)
        
        main_layout.addLayout(titre_layout)
        
        # Onglets
        self.tabs = QTabWidget()
        
        # Onglet Factures
        self.tab_factures = QWidget()
        self.setup_tab_factures()
        self.tabs.addTab(self.tab_factures, "Factures")
        
        # Onglet Paiements
        self.tab_paiements = QWidget()
        self.setup_tab_paiements()
        self.tabs.addTab(self.tab_paiements, "Paiements")
        
        # Onglet Statistiques
        self.tab_stats = QWidget()
        self.setup_tab_stats()
        self.tabs.addTab(self.tab_stats, "Statistiques")
        
        main_layout.addWidget(self.tabs)
    
    def setup_tab_factures(self):
        """Configure l'onglet des factures"""
        layout = QVBoxLayout(self.tab_factures)
        
        # Filtres
        filtres_group = QGroupBox("Filtres")
        filtres_layout = QHBoxLayout(filtres_group)
        
        # Patient
        self.facture_patient_combo = QComboBox()
        self.facture_patient_combo.setMinimumWidth(200)
        filtres_layout.addWidget(QLabel("Patient:"))
        filtres_layout.addWidget(self.facture_patient_combo)
        
        # Période
        self.facture_periode_combo = QComboBox()
        self.facture_periode_combo.addItems(["Toutes", "Ce mois", "Ce trimestre", "Cette année"])
        filtres_layout.addWidget(QLabel("Période:"))
        filtres_layout.addWidget(self.facture_periode_combo)
        
        # Statut
        self.facture_statut_combo = QComboBox()
        self.facture_statut_combo.addItems(["Tous", "En attente", "Payée", "Partiel", "Annulée"])
        filtres_layout.addWidget(QLabel("Statut:"))
        filtres_layout.addWidget(self.facture_statut_combo)
        
        # Bouton Filtrer
        self.btn_filtrer_factures = QPushButton("Filtrer")
        self.btn_filtrer_factures.clicked.connect(self.filtrer_factures)
        filtres_layout.addWidget(self.btn_filtrer_factures)
        
        layout.addWidget(filtres_group)
        
        # Tableau des factures
        self.factures_table = QTableWidget(0, 7)
        self.factures_table.setHorizontalHeaderLabels([
            "N° Facture", "Date", "Patient", "Montant", "Payé", "Reste", "Statut"
        ])
        self.factures_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.factures_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.factures_table.doubleClicked.connect(self.voir_facture)
        layout.addWidget(self.factures_table)
        
        # Boutons d'action
        actions_layout = QHBoxLayout()
        
        self.btn_voir_facture = QPushButton("Voir Facture")
        self.btn_voir_facture.clicked.connect(self.voir_facture)
        actions_layout.addWidget(self.btn_voir_facture)
        
        self.btn_imprimer_facture = QPushButton("Imprimer")
        self.btn_imprimer_facture.clicked.connect(self.imprimer_facture)
        actions_layout.addWidget(self.btn_imprimer_facture)
        
        self.btn_payer_facture = QPushButton("Enregistrer Paiement")
        self.btn_payer_facture.clicked.connect(self.payer_facture)
        actions_layout.addWidget(self.btn_payer_facture)
        
        layout.addLayout(actions_layout)
    
    def setup_tab_paiements(self):
        """Configure l'onglet des paiements"""
        layout = QVBoxLayout(self.tab_paiements)
        
        # Filtres
        filtres_group = QGroupBox("Filtres")
        filtres_layout = QHBoxLayout(filtres_group)
        
        # Patient
        self.paiement_patient_combo = QComboBox()
        self.paiement_patient_combo.setMinimumWidth(200)
        filtres_layout.addWidget(QLabel("Patient:"))
        filtres_layout.addWidget(self.paiement_patient_combo)
        
        # Période
        self.paiement_periode_combo = QComboBox()
        self.paiement_periode_combo.addItems(["Tous", "Ce mois", "Ce trimestre", "Cette année"])
        filtres_layout.addWidget(QLabel("Période:"))
        filtres_layout.addWidget(self.paiement_periode_combo)
        
        # Mode de paiement
        self.paiement_mode_combo = QComboBox()
        self.paiement_mode_combo.addItems(["Tous", "Carte bancaire", "Espèces", "Chèque", "Virement"])
        filtres_layout.addWidget(QLabel("Mode:"))
        filtres_layout.addWidget(self.paiement_mode_combo)
        
        # Bouton Filtrer
        self.btn_filtrer_paiements = QPushButton("Filtrer")
        self.btn_filtrer_paiements.clicked.connect(self.filtrer_paiements)
        filtres_layout.addWidget(self.btn_filtrer_paiements)
        
        layout.addWidget(filtres_group)
        
        # Tableau des paiements
        self.paiements_table = QTableWidget(0, 6)
        self.paiements_table.setHorizontalHeaderLabels([
            "Date", "Patient", "Montant", "Mode", "N° Facture", "Description"
        ])
        self.paiements_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.paiements_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.paiements_table)
        
        # Boutons d'action
        actions_layout = QHBoxLayout()
        
        self.btn_voir_paiement = QPushButton("Voir Détails")
        self.btn_voir_paiement.clicked.connect(self.voir_paiement)
        actions_layout.addWidget(self.btn_voir_paiement)
        
        self.btn_imprimer_recu = QPushButton("Imprimer Reçu")
        self.btn_imprimer_recu.clicked.connect(self.imprimer_recu)
        actions_layout.addWidget(self.btn_imprimer_recu)
        
        layout.addLayout(actions_layout)
    
    def setup_tab_stats(self):
        """Configure l'onglet des statistiques"""
        layout = QVBoxLayout(self.tab_stats)
        
        # Filtres de période
        periode_group = QGroupBox("Période")
        periode_layout = QHBoxLayout(periode_group)
        
        self.stats_date_debut = QDateEdit()
        self.stats_date_debut.setDate(QDate.currentDate().addMonths(-1))
        self.stats_date_debut.setCalendarPopup(True)
        periode_layout.addWidget(QLabel("Du:"))
        periode_layout.addWidget(self.stats_date_debut)
        
        self.stats_date_fin = QDateEdit()
        self.stats_date_fin.setDate(QDate.currentDate())
        self.stats_date_fin.setCalendarPopup(True)
        periode_layout.addWidget(QLabel("Au:"))
        periode_layout.addWidget(self.stats_date_fin)
        
        # Bouton Actualiser
        self.btn_actualiser_stats = QPushButton("Actualiser")
        self.btn_actualiser_stats.clicked.connect(self.actualiser_stats)
        periode_layout.addWidget(self.btn_actualiser_stats)
        
        layout.addWidget(periode_group)
        
        # Conteneur pour les graphiques
        charts_layout = QHBoxLayout()
        
        # Graphique des paiements par mode
        self.chart_modes = QChartView()
        self.chart_modes.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.chart_modes.setMinimumHeight(300)
        charts_layout.addWidget(self.chart_modes)
        
        # Graphique des factures par statut
        self.chart_factures = QChartView()
        self.chart_factures.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.chart_factures.setMinimumHeight(300)
        charts_layout.addWidget(self.chart_factures)
        
        layout.addLayout(charts_layout)
        
        # Résumé des statistiques
        resume_group = QGroupBox("Résumé")
        resume_layout = QGridLayout(resume_group)
        
        self.label_total_factures = QLabel("Factures émises: 0")
        resume_layout.addWidget(self.label_total_factures, 0, 0)
        
        self.label_montant_factures = QLabel("Montant total facturé: 0.00 DT")
        resume_layout.addWidget(self.label_montant_factures, 0, 1)
        
        self.label_total_paiements = QLabel("Paiements reçus: 0")
        resume_layout.addWidget(self.label_total_paiements, 1, 0)
        
        self.label_montant_paiements = QLabel("Montant total payé: 0.00 DT")
        resume_layout.addWidget(self.label_montant_paiements, 1, 1)
        
        self.label_reste_a_payer = QLabel("Reste à payer: 0.00 DT")
        resume_layout.addWidget(self.label_reste_a_payer, 2, 0, 1, 2)
        
        layout.addWidget(resume_group)
    
    def charger_donnees(self):
        """Charge les données initiales"""
        # Charger les patients
        self.charger_patients()
        
        # Charger les factures
        self.charger_factures()
        
        # Charger les paiements
        self.charger_paiements()
        
        # Initialiser les statistiques
        self.actualiser_stats()
    
    def charger_patients(self):
        """Charge la liste des patients dans les combobox"""
        patients = db.obtenir_patients()
        
        # Combobox des factures
        self.facture_patient_combo.clear()
        self.facture_patient_combo.addItem("Tous les patients", None)
        
        # Combobox des paiements
        self.paiement_patient_combo.clear()
        self.paiement_patient_combo.addItem("Tous les patients", None)
        
        for patient in patients:
            nom_complet = f"{patient['nom']}, {patient['prenom']}"
            self.facture_patient_combo.addItem(nom_complet, patient['id'])
            self.paiement_patient_combo.addItem(nom_complet, patient['id'])
    
    def charger_factures(self, patient_id=None, periode=None, statut=None):
        """Charge les factures dans le tableau"""
        # TODO: Implémenter le filtrage par période et statut
        self.factures_table.setRowCount(0)
        
        # Obtenir toutes les factures
        factures = []
        if patient_id:
            factures = db.obtenir_factures_patient(patient_id)
        else:
            # Pour l'exemple, on charge les factures du premier patient
            patients = db.obtenir_patients()
            if patients:
                factures = db.obtenir_factures_patient(patients[0]['id'])
        
        # Remplir le tableau
        for facture in factures:
            row = self.factures_table.rowCount()
            self.factures_table.insertRow(row)
            
            # N° Facture
            self.factures_table.setItem(row, 0, QTableWidgetItem(facture['numero_facture']))
            
            # Date
            date_str = facture['date_facture']
            self.factures_table.setItem(row, 1, QTableWidgetItem(date_str))
            
            # Patient
            patient = db.obtenir_patient(facture['patient_id'])
            patient_nom = f"{patient['nom']}, {patient['prenom']}" if patient else "Inconnu"
            self.factures_table.setItem(row, 2, QTableWidgetItem(patient_nom))
            
            # Montant
            montant = facture['montant_total']
            self.factures_table.setItem(row, 3, QTableWidgetItem(f"{montant:.2f} DT"))
            
            # Payé
            paye = facture['montant_paye']
            self.factures_table.setItem(row, 4, QTableWidgetItem(f"{paye:.2f} DT"))
            
            # Reste
            reste = montant - paye
            reste_item = QTableWidgetItem(f"{reste:.2f} DT")
            if reste > 0:
                reste_item.setForeground(QColor("red"))
            self.factures_table.setItem(row, 5, reste_item)
            
            # Statut
            statut = facture['statut']
            statut_item = QTableWidgetItem(statut)
            
            if statut == "payée":
                statut_item.setForeground(QColor("green"))
            elif statut == "en attente":
                statut_item.setForeground(QColor("red"))
            elif statut == "partiel":
                statut_item.setForeground(QColor("orange"))
            
            self.factures_table.setItem(row, 6, statut_item)
    
    def charger_paiements(self, patient_id=None, periode=None, mode=None):
        """Charge les paiements dans le tableau"""
        # TODO: Implémenter le filtrage par période et mode
        self.paiements_table.setRowCount(0)
        
        # Obtenir tous les paiements
        paiements = []
        if patient_id:
            paiements = db.obtenir_paiements_patient(patient_id)
        else:
            # Pour l'exemple, on charge les paiements du premier patient
            patients = db.obtenir_patients()
            if patients:
                paiements = db.obtenir_paiements_patient(patients[0]['id'])
        
        # Remplir le tableau
        for paiement in paiements:
            row = self.paiements_table.rowCount()
            self.paiements_table.insertRow(row)
            
            # Date
            self.paiements_table.setItem(row, 0, QTableWidgetItem(paiement['date_paiement']))
            
            # Patient
            patient = db.obtenir_patient(paiement['patient_id'])
            patient_nom = f"{patient['nom']}, {patient['prenom']}" if patient else "Inconnu"
            self.paiements_table.setItem(row, 1, QTableWidgetItem(patient_nom))
            
            # Montant
            montant = paiement['montant']
            self.paiements_table.setItem(row, 2, QTableWidgetItem(f"{montant:.2f} DT"))
            
            # Mode
            self.paiements_table.setItem(row, 3, QTableWidgetItem(paiement['mode_paiement']))
            
            # N° Facture
            self.paiements_table.setItem(row, 4, QTableWidgetItem(paiement['numero_facture'] or ""))
            
            # Description
            self.paiements_table.setItem(row, 5, QTableWidgetItem(paiement['description'] or ""))
    
    def actualiser_stats(self):
        """Actualise les statistiques"""
        date_debut = self.stats_date_debut.date().toString("yyyy-MM-dd")
        date_fin = self.stats_date_fin.date().toString("yyyy-MM-dd")
        
        # Obtenir les statistiques
        stats = db.obtenir_statistiques_paiements(date_debut, date_fin)
        
        if not stats:
            return
        
        # Mettre à jour les labels
        stats_factures = stats.get('factures', {})
        stats_paiements = stats.get('paiements', {})
        
        nb_factures = stats_factures.get('nombre', 0)
        montant_factures = stats_factures.get('total_facture', 0)
        montant_paye = stats_factures.get('total_paye', 0)
        reste_a_payer = montant_factures - montant_paye
        
        nb_paiements = stats_paiements.get('nombre', 0)
        montant_paiements = stats_paiements.get('total', 0)
        
        self.label_total_factures.setText(f"Factures émises: {nb_factures}")
        self.label_montant_factures.setText(f"Montant total facturé: {montant_factures:.2f} DT")
        self.label_total_paiements.setText(f"Paiements reçus: {nb_paiements}")
        self.label_montant_paiements.setText(f"Montant total payé: {montant_paiements:.2f} DT")
        self.label_reste_a_payer.setText(f"Reste à payer: {reste_a_payer:.2f} DT")
        
        # Mettre à jour les graphiques
        self.actualiser_graphique_modes(stats.get('modes_paiement', {}))
        self.actualiser_graphique_factures(stats_factures)
    
    def actualiser_graphique_modes(self, stats_modes):
        """Actualise le graphique des modes de paiement"""
        # Créer une série pour le graphique en camembert
        series = QPieSeries()
        
        for mode, data in stats_modes.items():
            montant = data.get('total', 0)
            series.append(f"{mode} ({montant:.2f} DT)", montant)
        
        # Créer le graphique
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Répartition des paiements par mode")
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
        
        # Mettre à jour la vue
        self.chart_modes.setChart(chart)
    
    def actualiser_graphique_factures(self, stats_factures):
        """Actualise le graphique des factures"""
        # Créer une série pour le graphique en barres
        set_factures = QBarSet("Factures")
        set_paiements = QBarSet("Paiements")
        
        montant_factures = stats_factures.get('total_facture', 0)
        montant_paye = stats_factures.get('total_paye', 0)
        
        set_factures.append(montant_factures)
        set_paiements.append(montant_paye)
        
        series = QBarSeries()
        series.append(set_factures)
        series.append(set_paiements)
        
        # Créer le graphique
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Montants facturés vs payés")
        
        # Axe des catégories
        axisX = QBarCategoryAxis()
        axisX.append(["Période sélectionnée"])
        chart.addAxis(axisX, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axisX)
        
        # Axe des valeurs
        axisY = QValueAxis()
        axisY.setRange(0, max(montant_factures, montant_paye) * 1.1)
        chart.addAxis(axisY, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axisY)
        
        # Légende
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
        
        # Mettre à jour la vue
        self.chart_factures.setChart(chart)
    
    def filtrer_factures(self):
        """Filtre les factures selon les critères sélectionnés"""
        patient_id = self.facture_patient_combo.currentData()
        periode = self.facture_periode_combo.currentText()
        statut = self.facture_statut_combo.currentText()
        
        if statut == "Tous":
            statut = None
        
        self.charger_factures(patient_id, periode, statut)
    
    def filtrer_paiements(self):
        """Filtre les paiements selon les critères sélectionnés"""
        patient_id = self.paiement_patient_combo.currentData()
        periode = self.paiement_periode_combo.currentText()
        mode = self.paiement_mode_combo.currentText()
        
        if mode == "Tous":
            mode = None
        
        self.charger_paiements(patient_id, periode, mode)
    
    def nouvelle_facture(self):
        """Ouvre le dialogue pour créer une nouvelle facture"""
        #dialog = FactureDialog(self)
        dialog = FactureDialog(self, patient_id=self.patient_actuel)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.charger_factures()
    
    def nouveau_paiement(self):
        """Ouvre le dialogue pour enregistrer un nouveau paiement"""
        #dialog = PaiementDialog(self)
        dialog = PaiementDialog(self, patient_id=self.patient_actuel)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.charger_paiements()
    
    def voir_facture(self):
        selected_rows = self.factures_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "Sélection requise", "Veuillez sélectionner une facture.")
            return

        row = selected_rows[0].row()
        numero_facture = self.factures_table.item(row, 0).text()

        try:
            # Obtenir l'ID de la facture à partir de son numéro
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM factures WHERE numero_facture = ?", (numero_facture,))
            facture_row = cursor.fetchone()
            conn.close()

            if not facture_row:
                QMessageBox.warning(self, "Erreur", "Facture introuvable.")
                return

            facture_id = facture_row['id']
            #facture_id = db.obtenir_id_facture_depuis_numero(numero_facture)
            details = db.obtenir_details_facture(facture_id)
            facture_info = db.obtenir_facture_par_id(facture_id)

            if details:
                dialog = QDialog(self)
                dialog.setWindowTitle(f"Détails de la facture {numero_facture}")
                dialog.resize(600, 400)

                layout = QVBoxLayout(dialog)

                info_text = f"""
                <h3>Facture {numero_facture}</h3>
                <p><b>Date:</b> {facture_info['date_facture']}</p>
                <p><b>Patient:</b> {self.factures_table.item(row, 2).text()}</p>
                <p><b>Montant total:</b> {details[0]['montant_total']:.2f} DT</p>
                """
                layout.addWidget(QLabel(info_text))

                table = QTableWidget()
                table.setColumnCount(4)
                table.setHorizontalHeaderLabels(["Acte", "Quantité", "PU", "Total"])
                table.setRowCount(len(details))

                for i, detail in enumerate(details):
                    table.setItem(i, 0, QTableWidgetItem(detail['libelle']))
                    table.setItem(i, 1, QTableWidgetItem(str(detail['quantite'])))
                    table.setItem(i, 2, QTableWidgetItem(f"{detail['prix_unitaire']:.2f}"))
                    table.setItem(i, 3, QTableWidgetItem(f"{detail['montant_total']:.2f}"))

                table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                layout.addWidget(table)

                btn_fermer = QPushButton("Fermer")
                btn_fermer.clicked.connect(dialog.accept)
                layout.addWidget(btn_fermer)

                dialog.exec()

            else:
                QMessageBox.warning(self, "Erreur", "Impossible de charger les détails de la facture.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur : {str(e)}")

    def imprimer_facture(self):
        selected_rows = self.factures_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "Aucune sélection", "Veuillez sélectionner une facture.")
            return

        row = selected_rows[0].row()
        numero_facture = self.factures_table.item(row, 0).text()

        if not REPORTLAB_AVAILABLE:
            QMessageBox.critical(self, "Erreur", "Le module ReportLab n'est pas installé.")
            return

        fichier_defaut = os.path.join(path_manager.get_factures_folder(), f"facture_{numero_facture}.pdf")
        fichier, _ = QFileDialog.getSaveFileName(
            self, "Enregistrer la facture", fichier_defaut, "PDF Files (*.pdf)"
        )

        if not fichier:
            return

        try:
            # Obtenir ID + détails
            facture_id = db.obtenir_id_facture_depuis_numero(numero_facture)
            if not facture_id:
                raise ValueError("Facture introuvable.")

            details = db.obtenir_details_facture(facture_id)
            facture_info = db.obtenir_facture_par_id(facture_id)
            patient = self.factures_table.item(row, 2).text()

            if not details:
                raise ValueError("Aucun détail trouvé pour cette facture.")

            # 📄 Création PDF avec image de fond
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4

            largeur, hauteur = A4
            c = canvas.Canvas(fichier, pagesize=A4)

            # 🖼️ Ajouter image de fond si existe
            image_path = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "icons", "grosse_dent.ico")
            if os.path.exists(image_path):
                try:
                    c.drawImage(image_path, 0, 0, width=largeur, height=hauteur, mask='auto')
                except Exception as img_err:
                    QMessageBox.critical(self, "Erreur", f"Erreur lors de l'ajout de l'image de fond: {str(img_err)}")

            # ✏️ Texte général
            x_margin = 50
            y = hauteur - 80

            c.setFont("Helvetica-Bold", 18)
            c.drawString(x_margin, y, f"Facture N° {numero_facture}")

            y -= 30
            c.setFont("Helvetica", 12)
            c.drawString(x_margin, y, f"Date : {facture_info['date_facture']}")
            y -= 20
            c.drawString(x_margin, y, f"Patient : {patient}")

            # 🧾 Tableau des actes
            y -= 40
            c.setFont("Helvetica-Bold", 12)
            c.drawString(x_margin, y, "Acte")
            c.drawString(x_margin + 200, y, "Quantité")
            c.drawString(x_margin + 300, y, "PU (DT)")
            c.drawString(x_margin + 400, y, "Total (DT)")

            y -= 20
            c.setFont("Helvetica", 11)
            total = 0
            for d in details:
                c.drawString(x_margin, y, d['libelle'])
                c.drawString(x_margin + 200, y, str(d['quantite']))
                c.drawString(x_margin + 300, y, f"{d['prix_unitaire']:.2f}")
                c.drawString(x_margin + 400, y, f"{d['montant_total']:.2f}")
                total += d['montant_total']
                y -= 20

            # 🧮 Total général
            y -= 20
            c.setFont("Helvetica-Bold", 12)
            c.drawRightString(x_margin + 500, y, f"TOTAL : {total:.2f} DT")

            # ✒️ Signature (optionnel)
            c.setFont("Helvetica", 9)
            c.drawString(2 * cm, 2.5 * cm, "Signature du médecin : _______________________")

            c.save()

            QMessageBox.information(self, "Succès", "Facture PDF générée avec succès.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'impression : {str(e)}")
   
    def payer_facture(self):
        """Enregistre un paiement pour une facture"""
        selected_rows = self.factures_table.selectedIndexes()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        numero_facture = self.factures_table.item(row, 0).text()
        patient_nom = self.factures_table.item(row, 2).text()
        
        # Trouver l'ID du patient
        patient_id = None
        for i in range(self.facture_patient_combo.count()):
            if self.facture_patient_combo.itemText(i) == patient_nom:
                patient_id = self.facture_patient_combo.itemData(i)
                break
        
        dialog = PaiementDialog(self, patient_id, numero_facture)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.charger_factures()
            self.charger_paiements()
    
    def voir_paiement(self):
        """Affiche les détails d'un paiement sélectionné"""
        selected_rows = self.paiements_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "Aucune sélection", "Veuillez sélectionner un paiement.")
            return

        row = selected_rows[0].row()
        date = self.paiements_table.item(row, 0).text()
        patient = self.paiements_table.item(row, 1).text()
        montant = self.paiements_table.item(row, 2).text()
        mode = self.paiements_table.item(row, 3).text()
        numero_facture = self.paiements_table.item(row, 4).text()
        description = self.paiements_table.item(row, 5).text()

        QMessageBox.information(
            self,
            "Détails du paiement",
            f"Patient : {patient}\nDate : {date}\nMontant : {montant}\nMode : {mode}\nFacture : {numero_facture}\nDescription : {description}"
        )
    
    def imprimer_recu(self):
        """Imprime un reçu de paiement sélectionné"""
        selected_rows = self.paiements_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "Aucune sélection", "Veuillez sélectionner un paiement.")
            return

        row = selected_rows[0].row()
        date = self.paiements_table.item(row, 0).text()
        patient = self.paiements_table.item(row, 1).text()
        montant = self.paiements_table.item(row, 2).text()
        mode = self.paiements_table.item(row, 3).text()

        if not REPORTLAB_AVAILABLE:
            QMessageBox.critical(self, "Erreur", "Le module ReportLab n'est pas installé.")
            return

        fichier_defaut = os.path.join(path_manager.get_factures_folder(), "recu_paiement.pdf")
        fichier, _ = QFileDialog.getSaveFileName(self, "Enregistrer le reçu", fichier_defaut, "PDF Files (*.pdf)")

        if not fichier:
            return

        try:
            doc = SimpleDocTemplate(fichier, pagesize=A4)
            styles = getSampleStyleSheet()
            contenu = []

            contenu.append(Paragraph(f"<b>Reçu de Paiement</b>", styles["Title"]))
            contenu.append(Spacer(1, 12))
            contenu.append(Paragraph(f"Patient : {patient}", styles["Normal"]))
            contenu.append(Paragraph(f"Date : {date}", styles["Normal"]))
            contenu.append(Paragraph(f"Montant payé : {montant}", styles["Normal"]))
            contenu.append(Paragraph(f"Mode de paiement : {mode}", styles["Normal"]))
            contenu.append(Spacer(1, 24))
            contenu.append(Paragraph("Merci pour votre paiement.", styles["Normal"]))

            doc.build(contenu)
            QMessageBox.information(self, "Succès", "Reçu enregistré avec succès.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'impression du reçu :\n{str(e)}")