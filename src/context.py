# -*- coding: utf-8 -*-
"""
Contexte global pour le logiciel médical DentalSoft
Gère l'état partagé entre toutes les vues
"""

from PySide6.QtCore import QObject, Signal

class GlobalContext(QObject):
    """Contexte global pour partager l'état entre les vues"""
    
    # Signaux pour notifier les changements
    patient_changed = Signal(int)  # patient_id
    
    def __init__(self):
        super().__init__()
        self._selected_patient_id = None
        self._selected_patient_name = ""
    
    @property
    def selected_patient_id(self):
        """ID du patient actuellement sélectionné"""
        return self._selected_patient_id
    
    @selected_patient_id.setter
    def selected_patient_id(self, patient_id):
        """Définit le patient sélectionné et émet le signal"""
        if self._selected_patient_id != patient_id:
            self._selected_patient_id = patient_id
            self.patient_changed.emit(patient_id if patient_id else 0)
    
    @property
    def selected_patient_name(self):
        """Nom du patient actuellement sélectionné"""
        return self._selected_patient_name
    
    @selected_patient_name.setter
    def selected_patient_name(self, name):
        """Définit le nom du patient sélectionné"""
        self._selected_patient_name = name
    
    def clear_selection(self):
        """Efface la sélection du patient"""
        self.selected_patient_id = None
        self.selected_patient_name = ""

# Instance globale unique
context = GlobalContext()

