# -*- coding: utf-8 -*-
"""
Système de contexte patient global pour le logiciel médical Dentail
Permet de synchroniser le patient sélectionné entre toutes les vues
"""

from PySide6.QtCore import QObject, Signal
from database import db

class PatientContext(QObject):
    """Contexte global pour la gestion du patient sélectionné"""
    
    # Signal émis quand le patient change
    patient_changed = Signal(int, str)  # patient_id, patient_name
    patient_added = Signal()  # Signal émis quand un nouveau patient est ajouté
    
    def __init__(self):
        super().__init__()
        self._selected_patient_id = None
        self._selected_patient_name = ""
        self._selected_patient_data = None
    
    @property
    def selected_patient_id(self):
        """ID du patient sélectionné"""
        return self._selected_patient_id
    
    @property
    def selected_patient_name(self):
        """Nom du patient sélectionné"""
        return self._selected_patient_name
    
    @property
    def selected_patient_data(self):
        """Données complètes du patient sélectionné"""
        return self._selected_patient_data
    
    def set_patient(self, patient_id, patient_name=None):
        """
        Définit le patient sélectionné globalement
        
        Args:
            patient_id (int): ID du patient
            patient_name (str, optional): Nom du patient (sera récupéré si non fourni)
        """
        if patient_id != self._selected_patient_id:
            self._selected_patient_id = patient_id
            
            if patient_id:
                # Récupérer les données complètes du patient
                self._selected_patient_data = db.obtenir_patient(patient_id)
                
                if self._selected_patient_data:
                    self._selected_patient_name = patient_name or self._selected_patient_data.get('nom_complet', '')
                else:
                    self._selected_patient_name = patient_name or f"Patient {patient_id}"
            else:
                self._selected_patient_name = ""
                self._selected_patient_data = None
            
            # Émettre le signal de changement
            self.patient_changed.emit(self._selected_patient_id or 0, self._selected_patient_name)
    
    def clear_patient(self):
        """Efface la sélection de patient"""
        self.set_patient(None)
    
    def get_patient_info(self):
        """
        Retourne les informations du patient sélectionné
        
        Returns:
            dict: Informations du patient ou None si aucun patient sélectionné
        """
        return self._selected_patient_data
    
    def is_patient_selected(self):
        """
        Vérifie si un patient est sélectionné
        
        Returns:
            bool: True si un patient est sélectionné
        """
        return self._selected_patient_id is not None

# Instance globale du contexte patient
patient_context = PatientContext()