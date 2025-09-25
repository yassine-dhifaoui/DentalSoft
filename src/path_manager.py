# -*- coding: utf-8 -*-
"""
Gestionnaire de chemins centralisé pour DentalSoft
Utilise UNIQUEMENT le dossier Documents pour tout stocker
"""

import os
import sys
from pathlib import Path

class PathManager:
    """Gestionnaire centralisé des chemins - TOUT dans Documents"""
    
    def __init__(self):
        self._app_data_folder = None
        self._images_folder = None
        self._initialize_paths()
    
    def _initialize_paths(self):
        """Initialise les chemins - TOUT dans le dossier Documents"""
        # Utiliser TOUJOURS le dossier Documents (Windows, Linux, macOS)
        documents_folder = os.path.expanduser("~/Documents")
        
        # Dossier principal de l'application dans Documents
        self._app_data_folder = os.path.join(documents_folder, "DentalSoft")
        
        # Dossier des images dans le dossier principal
        self._images_folder = os.path.join(self._app_data_folder, "images")
        
        # Créer tous les dossiers nécessaires
        self._create_directories()
    
    def _create_directories(self):
        """Crée tous les dossiers nécessaires dans Documents/DentalSoft"""
        directories = [
            self._app_data_folder,                                    # Documents/DentalSoft/
            self._images_folder,                                      # Documents/DentalSoft/images/
            os.path.join(self._app_data_folder, "exports"),          # Documents/DentalSoft/exports/
            os.path.join(self._app_data_folder, "backups"),          # Documents/DentalSoft/backups/
            os.path.join(self._app_data_folder, "ordonnances"),      # Documents/DentalSoft/ordonnances/
            os.path.join(self._app_data_folder, "factures")          # Documents/DentalSoft/factures/
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def get_app_data_folder(self):
        """
        Retourne le dossier principal de données de l'application
        
        Returns:
            str: Documents/DentalSoft
        """
        return self._app_data_folder
    
    def get_database_path(self):
        """
        Retourne le chemin complet de la base de données
        
        Returns:
            str: Documents/DentalSoft/DentalSoft.db
        """
        return os.path.join(self._app_data_folder, "DentalSoft.db")
    
    def get_images_folder(self):
        """
        Retourne le dossier des images d'imagerie médicale
        
        Returns:
            str: Documents/DentalSoft/images
        """
        return self._images_folder
    
    def get_exports_folder(self):
        """
        Retourne le dossier des exports (PDF, rapports, etc.)
        
        Returns:
            str: Documents/DentalSoft/exports
        """
        exports_folder = os.path.join(self._app_data_folder, "exports")
        os.makedirs(exports_folder, exist_ok=True)
        return exports_folder
    
    def get_backups_folder(self):
        """
        Retourne le dossier des sauvegardes
        
        Returns:
            str: Documents/DentalSoft/backups
        """
        backups_folder = os.path.join(self._app_data_folder, "backups")
        os.makedirs(backups_folder, exist_ok=True)
        return backups_folder
    
    def get_ordonnances_folder(self):
        """
        Retourne le dossier des ordonnances PDF
        
        Returns:
            str: Documents/DentalSoft/ordonnances
        """
        ordonnances_folder = os.path.join(self._app_data_folder, "ordonnances")
        os.makedirs(ordonnances_folder, exist_ok=True)
        return ordonnances_folder
    
    def get_factures_folder(self):
        """
        Retourne le dossier des factures PDF
        
        Returns:
            str: Documents/DentalSoft/factures
        """
        factures_folder = os.path.join(self._app_data_folder, "factures")
        os.makedirs(factures_folder, exist_ok=True)
        return factures_folder
    
    def ensure_directory(self, path):
        """
        S'assure qu'un dossier existe, le crée si nécessaire
        
        Args:
            path (str): Chemin du dossier à créer
        """
        os.makedirs(path, exist_ok=True)

# Instance globale unique du gestionnaire de chemins
path_manager = PathManager()

# Fonctions de compatibilité pour l'existant
def get_app_data_folder():
    """Fonction de compatibilité - utilise l'instance globale"""
    return path_manager.get_app_data_folder()

def get_database_path():
    """Fonction de compatibilité - utilise l'instance globale"""
    return path_manager.get_database_path()

def get_images_folder():
    """Fonction de compatibilité - utilise l'instance globale"""
    return path_manager.get_images_folder()