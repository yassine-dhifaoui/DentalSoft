import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from src.path_manager import get_database_path

class DatabaseManager:
    """Gestionnaire de base de données SQLite pour DentalSoft"""
    def __init__(self, db_path: str = None):
        """
        Initialise la base de données
        
        Args:
            db_path: Chemin vers le fichier de base de données (optionnel)
        """
        # Utiliser path_manager pour obtenir le chemin de la base
        self.db_path = db_path if db_path else get_database_path()
        
        # Plus besoin de créer manuellement les dossiers (path_manager s'en charge)
        # Initialiser la base de données
        self.init_database()

    def get_connection(self) -> sqlite3.Connection:
        """Retourne une connexion à la base de données"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Pour accéder aux colonnes par nom
        return conn
    
    def init_database(self):
        """Initialise les tables de la base de données"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Table des patients
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS patients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nom TEXT NOT NULL,
                    prenom TEXT NOT NULL,
                    date_naissance DATE,
                    telephone TEXT,
                    email TEXT,
                    adresse TEXT,
                    remarques_generales TEXT,
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    derniere_visite DATE
                )
            ''')
            
            # Table des rendez-vous
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rendez_vous (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER NOT NULL,
                    date_rdv DATE NOT NULL,
                    heure_rdv TIME NOT NULL,
                    type_rdv TEXT NOT NULL,
                    description TEXT,
                    statut TEXT DEFAULT 'planifie',
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (patient_id) REFERENCES patients (id)
                )
            ''')
            
            # Table des examens dentaires
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS examens_dentaires (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER NOT NULL,
                    numero_dent INTEGER NOT NULL,
                    statut_dent TEXT NOT NULL,
                    notes TEXT,
                    date_examen DATE NOT NULL,
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (patient_id) REFERENCES patients (id)
                )
            ''')
            
            # Table de l'imagerie médicale
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS imagerie (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER NOT NULL,
                    nom_fichier TEXT NOT NULL,
                    type_image TEXT NOT NULL,
                    chemin_fichier TEXT NOT NULL,
                    description TEXT,
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (patient_id) REFERENCES patients (id)
                )
            ''')
            
            # Table des ordonnances
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ordonnances (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER NOT NULL,
                    date_ordonnance DATE NOT NULL,
                    medicaments TEXT NOT NULL,
                    recommandations TEXT,
                    chemin_pdf TEXT,
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (patient_id) REFERENCES patients (id)
                )
            ''')
            
            # Table de l'historique des examens
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS historique_examens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER NOT NULL,
                    date_examen DATE NOT NULL,
                    type_examen TEXT NOT NULL,
                    dent_concernee TEXT,
                    description TEXT NOT NULL,
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (patient_id) REFERENCES patients (id)
                )
            ''')
            
            # Table des paiements
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS paiements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER NOT NULL,
                    montant REAL NOT NULL,
                    date_paiement DATE NOT NULL,
                    mode_paiement TEXT NOT NULL,
                    numero_facture TEXT,
                    description TEXT,
                    statut TEXT DEFAULT 'payé',
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (patient_id) REFERENCES patients (id)
                )
            ''')
            
            # Table des actes dentaires (pour la facturation)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS actes_dentaires (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT NOT NULL,
                    libelle TEXT NOT NULL,
                    tarif_base REAL NOT NULL,
                    description TEXT
                )
            ''')
            
            # Table des factures
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS factures (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER NOT NULL,
                    numero_facture TEXT NOT NULL,
                    date_facture DATE NOT NULL,
                    montant_total REAL NOT NULL,
                    montant_paye REAL DEFAULT 0,
                    statut TEXT DEFAULT 'en attente',
                    details TEXT,
                    chemin_pdf TEXT,
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (patient_id) REFERENCES patients (id)
                )
            ''')
            
            # Table des détails de facture (lignes)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS details_facture (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    facture_id INTEGER NOT NULL,
                    acte_id INTEGER,
                    libelle TEXT NOT NULL,
                    quantite INTEGER DEFAULT 1,
                    prix_unitaire REAL NOT NULL,
                    montant_total REAL NOT NULL,
                    FOREIGN KEY (facture_id) REFERENCES factures (id),
                    FOREIGN KEY (acte_id) REFERENCES actes_dentaires (id)
                )
            ''')
            
            conn.commit()
            
            # Insérer les actes dentaires de base si la table est vide
            self._insert_base_actes(cursor)
            conn.commit()
            
        except Exception as e:
            conn.rollback()
        finally:
            conn.close()
    
    def _insert_base_actes(self, cursor):
        """Insère les actes dentaires de base si la table est vide"""
        # Vérifier si des actes existent déjà
        cursor.execute("SELECT COUNT(*) FROM actes_dentaires")
        if cursor.fetchone()[0] > 0:
            return  # Des actes existent déjà
        
        # Insérer les actes dentaires de base
        actes_base = [
            ("SC12", "Détartrage", 28.92, "Détartrage et polissage"),
            ("SC17", "Traitement d'une carie 1 face", 16.87, "Traitement d'une carie sur une face"),
            ("SC18", "Traitement d'une carie 2 faces", 28.92, "Traitement d'une carie sur deux faces"),
            ("SC33", "Traitement d'une carie 3 faces", 40.97, "Traitement d'une carie sur trois faces"),
            ("SC19", "Dévitalisation incisive/canine", 33.74, "Traitement endodontique d'une incisive ou canine"),
            ("SC24", "Dévitalisation prémolaire", 48.20, "Traitement endodontique d'une prémolaire"),
            ("SC34", "Dévitalisation molaire", 81.94, "Traitement endodontique d'une molaire"),
            ("SC30", "Extraction simple", 33.44, "Extraction d'une dent permanente"),
            ("SC31", "Extraction complexe", 66.88, "Extraction chirurgicale d'une dent"),
            ("C001", "Consultation", 50.0, "Consultation de base"),
            ("P001", "Plombage", 120.0, "Plombage composite"),
            ("C002", "Couronne", 600.0, "Couronne céramique")
        ]
        
        for acte in actes_base:
            cursor.execute('''
                INSERT INTO actes_dentaires (code, libelle, tarif_base, description)
                VALUES (?, ?, ?, ?)
            ''', acte)

    # ==================== GESTION DES PATIENTS ====================
    
    def ajouter_patient(self, nom: str, prenom: str, date_naissance: str = None, 
                       telephone: str = None, email: str = None, adresse: str = None, 
                       remarques: str = None) -> int:
        """Ajoute un nouveau patient"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO patients (nom, prenom, date_naissance, telephone, email, adresse, remarques_generales)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (nom, prenom, date_naissance, telephone, email, adresse, remarques))
            
            patient_id = cursor.lastrowid
            conn.commit()
            return patient_id
            
        except Exception as e:
            conn.rollback()
            return None
        finally:
            conn.close()
    
    def obtenir_patients(self) -> List[Dict]:
        """Retourne la liste de tous les patients"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, nom, prenom, telephone, email, derniere_visite
                FROM patients
                ORDER BY nom, prenom
            ''')
            
            patients = []
            for row in cursor.fetchall():
                patients.append({
                    'id': row['id'],
                    'nom': row['nom'],
                    'prenom': row['prenom'],
                    'nom_complet': f"{row['nom']}, {row['prenom']}",
                    'telephone': row['telephone'],
                    'email': row['email'],
                    'derniere_visite': row['derniere_visite']
                })
            
            return patients
            
        except Exception as e:
            return []
        finally:
            conn.close()
    
    def obtenir_patient(self, patient_id: int) -> Optional[Dict]:
        """Retourne les informations d'un patient spécifique"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM patients WHERE id = ?
            ''', (patient_id,))
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
            
        except Exception as e:
            return None
        finally:
            conn.close()
    
    def search_patients(self, search_term):
        """Recherche des patients par nom, prénom ou téléphone"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            search_pattern = f"%{search_term}%"
            cursor.execute('''
                SELECT id, nom, prenom, telephone, email, date_naissance, adresse
                FROM patients 
                WHERE nom LIKE ? OR prenom LIKE ? OR telephone LIKE ?
                ORDER BY nom, prenom
            ''', (search_pattern, search_pattern, search_pattern))
            
            return cursor.fetchall()
            
        except Exception as e:
            return []
        finally:
            conn.close()
    
    def get_patients(self) -> List[Tuple]:
        """Retourne la liste de tous les patients (format tuple pour compatibilité)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, nom, prenom, telephone, email, date_naissance, adresse
                FROM patients
                ORDER BY nom, prenom
            ''')
            
            return cursor.fetchall()
            
        except Exception as e:
            return []
        finally:
            conn.close()
    
    def get_patient_by_id(self, patient_id: int) -> Optional[Tuple]:
        """Retourne les informations d'un patient par son ID (format tuple)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, nom, prenom, telephone, email, date_naissance, adresse
                FROM patients WHERE id = ?
            ''', (patient_id,))
            
            return cursor.fetchone()
            
        except Exception as e:
            return None
        finally:
            conn.close()

    def get_patient_remarks(self, patient_id: int) -> Optional[str]:
        """Récupère les remarques générales d'un patient"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT remarques_generales FROM patients 
                WHERE id = ?
            ''', (patient_id,))
            
            result = cursor.fetchone()
            return result['remarques_generales'] if result else None
            
        except Exception as e:
            return None
        finally:
            conn.close()

    def get_last_visit_date(self, patient_id: int) -> Optional[str]:
        """Récupère la date de la dernière visite"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT MAX(date_examen) as derniere_visite
                FROM historique_examens 
                WHERE patient_id = ?
            ''', (patient_id,))
            
            result = cursor.fetchone()
            if result and result['derniere_visite']:
                # Convertir la date au format français
                from datetime import datetime
                date_obj = datetime.strptime(result['derniere_visite'], '%Y-%m-%d')
                return date_obj.strftime('%d/%m/%Y')
            return None
            
        except Exception as e:
            return None
        finally:
            conn.close()

    def get_patient_exam_history(self, patient_id: int) -> List[Tuple]:
        """Récupère l'historique des examens d'un patient"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT date_examen, type_examen, dent_concernee, description
                FROM historique_examens 
                WHERE patient_id = ?
                ORDER BY date_examen DESC
            ''', (patient_id,))
            
            return cursor.fetchall()
            
        except Exception as e:
            return []
        finally:
            conn.close()

    def update_patient_remarks(self, patient_id: int, remarques: str):
        """Met à jour les remarques générales d'un patient"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE patients 
                SET remarques_generales = ?
                WHERE id = ?
            ''', (remarques, patient_id))
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            return False
        finally:
            conn.close()

    # ==================== GESTION DES EXAMENS DENTAIRES ====================
    
    def sauvegarder_examen_dentaire(self, patient_id: int, numero_dent: int, 
                                   statut_dent: str, notes: str = None, 
                                   date_examen: str = None):
        """Sauvegarde l'état d'une dent lors d'un examen"""
        if date_examen is None:
            date_examen = datetime.now().strftime('%Y-%m-%d')
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Vérifier si un examen existe déjà pour cette dent
            cursor.execute('''
                SELECT id FROM examens_dentaires 
                WHERE patient_id = ? AND numero_dent = ?
                ORDER BY date_creation DESC LIMIT 1
            ''', (patient_id, numero_dent))
            
            existing = cursor.fetchone()
            
            if existing:
                # Mettre à jour l'examen existant
                cursor.execute('''
                    UPDATE examens_dentaires 
                    SET statut_dent = ?, notes = ?, date_examen = ?
                    WHERE id = ?
                ''', (statut_dent, notes, date_examen, existing['id']))
            else:
                # Créer un nouvel examen
                cursor.execute('''
                    INSERT INTO examens_dentaires (patient_id, numero_dent, statut_dent, notes, date_examen)
                    VALUES (?, ?, ?, ?, ?)
                ''', (patient_id, numero_dent, statut_dent, notes, date_examen))
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
        finally:
            conn.close()
    
    def obtenir_examens_dentaires_patient(self, patient_id: int) -> Dict[int, Dict]:
        """Retourne l'état de toutes les dents d'un patient"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT numero_dent, statut_dent, notes, date_examen
                FROM examens_dentaires 
                WHERE patient_id = ?
                ORDER BY date_creation DESC
            ''', (patient_id,))
            
            examens = {}
            for row in cursor.fetchall():
                numero_dent = row['numero_dent']
                if numero_dent not in examens:  # Garder seulement le plus récent
                    examens[numero_dent] = {
                        'statut': row['statut_dent'],
                        'notes': row['notes'],
                        'date_examen': row['date_examen']
                    }
            
            return examens
            
        except Exception as e:
            return {}
        finally:
            conn.close()

    def ajouter_historique_examen(self, patient_id: int, type_examen: str, 
                                 dent_concernee: str, description: str, 
                                 date_examen: str = None):
        """Ajoute une entrée à l'historique des examens"""
        if date_examen is None:
            date_examen = datetime.now().strftime('%Y-%m-%d')
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO historique_examens (patient_id, date_examen, type_examen, dent_concernee, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (patient_id, date_examen, type_examen, dent_concernee, description))
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
        finally:
            conn.close()
    
    def obtenir_historique_patient(self, patient_id: int) -> List[Dict]:
        """Retourne l'historique des examens d'un patient"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT date_examen, type_examen, dent_concernee, description
                FROM historique_examens 
                WHERE patient_id = ?
                ORDER BY date_examen DESC
            ''', (patient_id,))
            
            return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            return []
        finally:
            conn.close()

    # ==================== GESTION DES RENDEZ-VOUS ====================
    
    def ajouter_rendez_vous(self, patient_id: int, date_rdv: str, heure_rdv: str, 
                           type_rdv: str, description: str = None) -> int:
        """Ajoute un nouveau rendez-vous"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO rendez_vous (patient_id, date_rdv, heure_rdv, type_rdv, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (patient_id, date_rdv, heure_rdv, type_rdv, description))
            
            rdv_id = cursor.lastrowid
            conn.commit()
            return rdv_id
            
        except Exception as e:
            conn.rollback()
            return None
        finally:
            conn.close()
    
    def obtenir_rendez_vous_jour(self, date: str) -> List[Dict]:
        """Retourne les rendez-vous d'une date donnée"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT r.*, p.nom, p.prenom, p.telephone
                FROM rendez_vous r
                JOIN patients p ON r.patient_id = p.id
                WHERE r.date_rdv = ?
                ORDER BY r.heure_rdv
            ''', (date,))
            
            rendez_vous = []
            for row in cursor.fetchall():
                rendez_vous.append({
                    'id': row['id'],
                    'patient_id': row['patient_id'],
                    'patient_nom': f"{row['nom']}, {row['prenom']}",
                    'telephone': row['telephone'],
                    'heure': row['heure_rdv'],
                    'type': row['type_rdv'],
                    'description': row['description'],
                    'statut': row['statut']
                })
            
            return rendez_vous
            
        except Exception as e:
            return []
        finally:
            conn.close()
    
    def obtenir_rendez_vous_patient(self, patient_id: int) -> List[Dict]:
        """Retourne tous les rendez-vous d'un patient"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM rendez_vous 
                WHERE patient_id = ?
                ORDER BY date_rdv DESC, heure_rdv DESC
            ''', (patient_id,))
            
            return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            return []
        finally:
            conn.close()
    
    def obtenir_rendez_vous_date(self, date_str: str) -> List[Dict]:
        """Retourne tous les rendez-vous d'une date donnée"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT r.*, p.nom, p.prenom
                FROM rendez_vous r
                LEFT JOIN patients p ON r.patient_id = p.id
                WHERE r.date_rdv = ?
                ORDER BY r.heure_rdv
            ''', (date_str,))
            
            rendez_vous = []
            for row in cursor.fetchall():
                rdv = dict(row)
                rdv['patient_nom'] = f"{rdv['nom']}, {rdv['prenom']}" if rdv['nom'] else "Patient inconnu"
                rendez_vous.append(rdv)
            
            return rendez_vous
            
        except Exception as e:
            return []
        finally:
            conn.close()
    
    def modifier_rendez_vous(self, rdv_id: int, patient_id: int, date_rdv: str, 
                           heure_rdv: str, type_rdv: str, description: str, statut: str) -> bool:
        """Modifie un rendez-vous existant"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE rendez_vous 
                SET patient_id = ?, date_rdv = ?, heure_rdv = ?, type_rdv = ?, 
                    description = ?, statut = ?
                WHERE id = ?
            ''', (patient_id, date_rdv, heure_rdv, type_rdv, description, statut, rdv_id))
            
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            conn.rollback()
            return False
        finally:
            conn.close()

    def supprimer_rendez_vous(self, rdv_id: int) -> bool:
        """Supprime un rendez-vous"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM rendez_vous WHERE id = ?', (rdv_id,))
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def update_appointment(self, appointment_id, data):
        """Met à jour un rendez-vous"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE rendez_vous 
                SET patient_id = ?, date_rdv = ?, heure_rdv = ?, 
                    type_rdv = ?, description = ?, statut = ?
                WHERE id = ?
            ''', (
                data.get('patient_id'),
                data.get('date_rdv'),
                data.get('heure_rdv'),
                data.get('type_rdv'),
                data.get('description'),
                data.get('statut'),
                appointment_id
            ))
            
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def delete_appointment(self, appointment_id):
        """Supprime un rendez-vous"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM rendez_vous WHERE id = ?', (appointment_id,))
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            conn.rollback()
            return False
        finally:
            conn.close()

    # ==================== GESTION DE L'IMAGERIE ====================
    
    def ajouter_image(self, patient_id: int, nom_fichier: str, type_image: str, 
                     chemin_fichier: str, description: str = None) -> int:
        """Ajoute une image médicale"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO imagerie (patient_id, nom_fichier, type_image, chemin_fichier, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (patient_id, nom_fichier, type_image, chemin_fichier, description))
            
            image_id = cursor.lastrowid
            conn.commit()
            return image_id
            
        except Exception as e:
            conn.rollback()
            return None
        finally:
            conn.close()
    
    def obtenir_images_patient(self, patient_id: int) -> List[Dict]:
        """Retourne toutes les images d'un patient"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM imagerie 
                WHERE patient_id = ?
                ORDER BY date_creation DESC
            ''', (patient_id,))
            
            return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            return []
        finally:
            conn.close()

    def supprimer_image(self, image_id: int) -> bool:
        """Supprime une image de la base de données"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                DELETE FROM imagerie WHERE id = ?
            ''', (image_id,))
            
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            conn.rollback()
            return False
        finally:
            conn.close()

    def obtenir_image_par_id(self, image_id: int) -> Dict:
        """Retourne une image par son ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM imagerie WHERE id = ?
            ''', (image_id,))
            
            result = cursor.fetchone()
            return dict(result) if result else {}
            
        except Exception as e:
            return {}
        finally:
            conn.close()

    # ==================== GESTION DES ORDONNANCES ====================
    
    def ajouter_ordonnance(self, patient_id: int, medicaments: str, 
                          recommandations: str = None, chemin_pdf: str = None, 
                          date_ordonnance: str = None) -> int:
        """Ajoute une ordonnance"""
        if date_ordonnance is None:
            date_ordonnance = datetime.now().strftime('%Y-%m-%d')
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO ordonnances (patient_id, date_ordonnance, medicaments, recommandations, chemin_pdf)
                VALUES (?, ?, ?, ?, ?)
            ''', (patient_id, date_ordonnance, medicaments, recommandations, chemin_pdf))
            
            ordonnance_id = cursor.lastrowid
            conn.commit()
            return ordonnance_id
            
        except Exception as e:
            conn.rollback()
            return None
        finally:
            conn.close()
    
    def obtenir_ordonnances_patient(self, patient_id: int) -> List[Dict]:
        """Retourne toutes les ordonnances d'un patient"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM ordonnances 
                WHERE patient_id = ?
                ORDER BY date_ordonnance DESC
            ''', (patient_id,))
            
            return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            return []
        finally:
            conn.close()

    # ==================== GESTION DES FACTURES ET PAIEMENTS ====================
    
    def ajouter_facture(self, patient_id: int, date_facture: str, montant_total: float, 
                       details: str, lignes_facture: list, statut: str = "en attente") -> int:
        """Ajoute une nouvelle facture"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Générer un numéro de facture unique
            annee = date_facture.split('-')[0]
            cursor.execute("SELECT COUNT(*) FROM factures WHERE numero_facture LIKE ?", (f"F{annee}-%",))
            count = cursor.fetchone()[0] + 1
            numero_facture = f"F{annee}-{count:03d}"
            
            # Insérer la facture
            cursor.execute('''
                INSERT INTO factures (patient_id, numero_facture, date_facture, montant_total, statut, details)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (patient_id, numero_facture, date_facture, montant_total, statut, details))
            
            facture_id = cursor.lastrowid
            
            # Insérer les lignes de la facture
            for ligne in lignes_facture:
                acte_id = ligne.get("acte_id")
                libelle = ligne.get("libelle")
                quantite = ligne.get("quantite", 1)
                prix_unitaire = ligne.get("prix_unitaire")
                montant_ligne = quantite * prix_unitaire
                
                cursor.execute('''
                    INSERT INTO details_facture (facture_id, acte_id, libelle, quantite, prix_unitaire, montant_total)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (facture_id, acte_id, libelle, quantite, prix_unitaire, montant_ligne))
            
            conn.commit()
            return facture_id
            
        except Exception as e:
            conn.rollback()
            return None
        finally:
            conn.close()

    def enregistrer_paiement(self, patient_id: int, montant: float, date_paiement: str, 
                            mode_paiement: str, numero_facture: str = None, 
                            description: str = None) -> int:
        """Enregistre un paiement et met à jour le statut de la facture associée"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Insérer le paiement
            cursor.execute('''
                INSERT INTO paiements (patient_id, montant, date_paiement, mode_paiement, numero_facture, description)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (patient_id, montant, date_paiement, mode_paiement, numero_facture, description))
            
            paiement_id = cursor.lastrowid
            
            # Mettre à jour la facture si un numéro est fourni
            if numero_facture:
                # Récupérer la facture
                cursor.execute('''
                    SELECT id, montant_total, montant_paye FROM factures WHERE numero_facture = ?
                ''', (numero_facture,))
                
                facture = cursor.fetchone()
                if facture:
                    facture_id = facture['id']
                    montant_total = facture['montant_total']
                    montant_paye = facture['montant_paye'] + montant
                    
                    # Déterminer le nouveau statut
                    if montant_paye >= montant_total:
                        nouveau_statut = "payée"
                    elif montant_paye > 0:
                        nouveau_statut = "partiel"
                    else:
                        nouveau_statut = "en attente"
                    
                    # Mettre à jour la facture
                    cursor.execute('''
                        UPDATE factures SET montant_paye = ?, statut = ? WHERE id = ?
                    ''', (montant_paye, nouveau_statut, facture_id))
            
            conn.commit()
            return paiement_id
            
        except Exception as e:
            conn.rollback()
            return None
        finally:
            conn.close()

    def obtenir_facture_par_id(self, facture_id: int) -> dict:
        """Retourne les infos de la facture à partir de son ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM factures WHERE id = ?", (facture_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            return None
        finally:
            conn.close()

    def obtenir_id_facture_depuis_numero(self, numero_facture: str) -> int:
        """Retourne l'ID d'une facture à partir de son numéro"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT id FROM factures WHERE numero_facture = ?', (numero_facture,))
            row = cursor.fetchone()
            return row["id"] if row else None
        except Exception as e:
            return None
        finally:
            conn.close()

    def obtenir_factures_patient(self, patient_id: int) -> list:
        """Retourne toutes les factures d'un patient"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM factures 
                WHERE patient_id = ?
                ORDER BY date_facture DESC
            ''', (patient_id,))
            
            return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            return []
        finally:
            conn.close()

    def obtenir_details_facture(self, facture_id: int) -> list:
        """Retourne les détails d'une facture"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT df.*, ad.code 
                FROM details_facture df
                LEFT JOIN actes_dentaires ad ON df.acte_id = ad.id
                WHERE df.facture_id = ?
                ORDER BY df.id
            ''', (facture_id,))
            
            return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            return []
        finally:
            conn.close()

    def obtenir_paiements_patient(self, patient_id: int) -> list:
        """Retourne tous les paiements d'un patient"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM paiements 
                WHERE patient_id = ?
                ORDER BY date_paiement DESC
            ''', (patient_id,))
            
            return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            return []
        finally:
            conn.close()

    def obtenir_paiements_facture(self, numero_facture: str) -> list:
        """Retourne tous les paiements associés à une facture"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM paiements 
                WHERE numero_facture = ?
                ORDER BY date_paiement DESC
            ''', (numero_facture,))
            
            return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            return []
        finally:
            conn.close()

    def obtenir_actes_dentaires(self) -> list:
        """Retourne la liste de tous les actes dentaires disponibles"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM actes_dentaires 
                ORDER BY code
            ''')
            
            return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            return []
        finally:
            conn.close()

    def obtenir_statistiques_paiements(self, date_debut: str, date_fin: str) -> dict:
        """Retourne des statistiques sur les paiements pour une période donnée"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Total des paiements
            cursor.execute('''
                SELECT SUM(montant) as total, COUNT(*) as nombre
                FROM paiements 
                WHERE date_paiement BETWEEN ? AND ?
            ''', (date_debut, date_fin))
            
            stats_paiements = dict(cursor.fetchone())
            # Correction TypeError : valeurs par défaut si None
            stats_paiements['total'] = stats_paiements['total'] or 0.0
            stats_paiements['nombre'] = stats_paiements['nombre'] or 0
            
            # Répartition par mode de paiement
            cursor.execute('''
                SELECT mode_paiement, SUM(montant) as total, COUNT(*) as nombre
                FROM paiements 
                WHERE date_paiement BETWEEN ? AND ?
                GROUP BY mode_paiement
            ''', (date_debut, date_fin))
            
            stats_modes = {}
            for row in cursor.fetchall():
                stats_modes[row['mode_paiement']] = {
                    'total': row['total'] or 0.0,
                    'nombre': row['nombre'] or 0
                }
            
            # Factures émises
            cursor.execute('''
                SELECT COUNT(*) as nombre, SUM(montant_total) as total_facture, 
                       SUM(montant_paye) as total_paye
                FROM factures 
                WHERE date_facture BETWEEN ? AND ?
            ''', (date_debut, date_fin))
            
            stats_factures = dict(cursor.fetchone())
            # Correction TypeError : valeurs par défaut si None
            stats_factures['nombre'] = stats_factures['nombre'] or 0
            stats_factures['total_facture'] = stats_factures['total_facture'] or 0.0
            stats_factures['total_paye'] = stats_factures['total_paye'] or 0.0
            
            return {
                'paiements': stats_paiements,
                'modes_paiement': stats_modes,
                'factures': stats_factures
            }
            
        except Exception as e:
            return {
                'paiements': {'total': 0.0, 'nombre': 0},
                'modes_paiement': {},
                'factures': {'nombre': 0, 'total_facture': 0.0, 'total_paye': 0.0}
            }
        finally:
            conn.close()

    def close_connection(self):
        """Ferme la connexion à la base de données"""
        pass  # SQLite se ferme automatiquement


# Instance globale de la base de données
db = DatabaseManager()

# Fonctions de compatibilité globales
def get_patients():
    """Fonction globale pour obtenir tous les patients"""
    return db.get_patients()

def get_patient_by_id(patient_id):
    """Fonction globale pour obtenir un patient par ID"""
    return db.get_patient_by_id(patient_id)

def search_patients(search_term):
    """Fonction globale de recherche de patients"""
    return db.search_patients(search_term)

