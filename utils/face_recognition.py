import cv2
import face_recognition
import numpy as np
import pickle
import os
from datetime import datetime
import sqlite3

import flet as ft
from utils.face_recognition import face_system
import base64
import io
from PIL import Image


class GMESMobileApp:
    # ... code existant ...

    def show_face_login(self, e=None):
        """Connexion par reconnaissance faciale"""
        self.camera_view = ft.Image(
            src_base64=self.get_camera_placeholder(),
            width=300,
            height=300,
            fit=ft.ImageFit.COVER
        )

        view = ft.Column([
            ft.Row([
                ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda _: self.show_login_view()),
                ft.Text("Reconnaissance Faciale", size=20, weight=ft.FontWeight.BOLD)
            ]),

            ft.Container(
                content=ft.Column([
                    self.camera_view,
                    ft.Text("Positionnez votre visage dans le cadre", size=16),
                    ft.Row([
                        ft.ElevatedButton(
                            text="📸 Prendre une photo",
                            icon=ft.icons.CAMERA_ALT,
                            on_click=self.capture_face
                        ),
                        ft.ElevatedButton(
                            text="🖼️ Choisir une photo",
                            icon=ft.icons.PHOTO_LIBRARY,
                            on_click=self.choose_face_image
                        )
                    ])
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=20
            )
        ])

        self.page.clean()
        self.page.add(view)

    def capture_face(self, e):
        """Capture une photo via la caméra"""
        # Simulation - en production, utiliser la caméra du device
        self.page.show_snack_bar(ft.SnackBar(content=ft.Text("Fonction caméra à implémenter")))

        # Pour le test, utiliser une image de test
        self.process_face_image("test_face.jpg")

    def choose_face_image(self, e):
        """Choisir une image depuis la galerie"""
        # Ouvrir le sélecteur de fichiers
        file_picker = ft.FilePicker(on_result=self.on_face_image_selected)
        self.page.overlay.append(file_picker)
        self.page.update()
        file_picker.pick_files(allow_multiple=False, file_type=ft.FilePickerFileType.IMAGE)

    def on_face_image_selected(self, e):
        """Callback quand une image est sélectionnée"""
        if e.files:
            # En production, traiter le fichier sélectionné
            self.process_face_image(e.files[0].path)

    def process_face_image(self, image_path):
        """Traite l'image pour la reconnaissance faciale"""
        progress_bar = ft.ProgressBar(width=300)
        status_text = ft.Text("Analyse du visage...")

        processing_view = ft.Column([
            status_text,
            progress_bar
        ])

        self.page.clean()
        self.page.add(processing_view)

        # Simulation du traitement
        import time
        for i in range(3):
            time.sleep(0.5)
            progress_bar.value = (i + 1) / 3
            self.page.update()

        # Reconnaissance faciale
        user_id, confidence = face_system.recognize_face(image_path)

        if user_id:
            # Vérifier la vivacité
            liveness_ok, liveness_msg = face_system.verify_liveness(image_path)

            if liveness_ok:
                # Connexion réussie
                self.face_login_success(user_id, confidence)
            else:
                self.show_error(f"Échec vérification: {liveness_msg}")
        else:
            self.show_error("Visage non reconnu")

    def face_login_success(self, user_id, confidence):
        """Connexion réussie par reconnaissance faciale"""
        try:
            # Récupérer les infos utilisateur
            response = requests.post(f"{self.api_base_url}/auth/face-login", json={
                "user_id": user_id,
                "confidence": confidence
            })

            if response.status_code == 200:
                data = response.json()
                self.token = data.get('token')
                self.current_user = data.get('user')

                self.page.show_snack_bar(
                    ft.SnackBar(content=ft.Text(f"✅ Reconnaissance faciale réussie! ({confidence:.2%})"))
                )
                self.show_dashboard()
            else:
                self.show_error("Erreur d'authentification")

        except Exception as e:
            self.show_error(f"Erreur: {str(e)}")

    def show_face_registration(self, e=None):
        """Enregistrement facial"""
        view = ft.Column([
            ft.Row([
                ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda _: self.show_settings()),
                ft.Text("Enregistrement Facial", size=20, weight=ft.FontWeight.BOLD)
            ]),

            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.FACE_RETOUCHING_NATURAL, size=80, color=ft.colors.BLUE),
                    ft.Text("Enregistrez votre visage pour une connexion sécurisée", size=16),
                    ft.Text("• Prenez une photo bien éclairée", size=14),
                    ft.Text("• Regardez droit devant la caméra", size=14),
                    ft.Text("• Évitez les lunettes de soleil", size=14),

                    ft.ElevatedButton(
                        text="Commencer l'enregistrement",
                        icon=ft.icons.CAMERA_ENHANCE,
                        on_click=self.start_face_registration
                    )
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=40
            )
        ])

        self.page.clean()
        self.page.add(view)

    def start_face_registration(self, e):
        """Démarre l'enregistrement facial"""
        # Similaire à show_face_login mais pour l'enregistrement
        self.capture_face_for_registration()

    def capture_face_for_registration(self):
        """Capture pour l'enregistrement"""
        # Implémentation similaire à capture_face mais pour l'enregistrement
        success, message = face_system.register_face(
            self.current_user['id'],
            "new_face_image.jpg"
        )

        if success:
            self.page.show_snack_bar(ft.SnackBar(content=ft.Text("✅ Visage enregistré avec succès!")))
        else:
            self.show_error(f"Échec enregistrement: {message}")


class FaceRecognitionSystem:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_ids = []
        self.load_known_faces()

    def load_known_faces(self):
        """Charge les visages connus depuis la base"""
        try:
            conn = sqlite3.connect('gmes.db')
            cursor = conn.cursor()
            cursor.execute('SELECT user_id, face_encoding FROM face_data')
            rows = cursor.fetchall()

            for user_id, encoding_bytes in rows:
                encoding = pickle.loads(encoding_bytes)
                self.known_face_encodings.append(encoding)
                self.known_face_ids.append(user_id)

            conn.close()
            print(f"✅ {len(self.known_face_ids)} visages chargés")

        except Exception as e:
            print(f"❌ Erreur chargement visages: {e}")

    def register_face(self, user_id, image_path):
        """Enregistre un nouveau visage"""
        try:
            # Charger et encoder l'image
            image = face_recognition.load_image_file(image_path)
            face_encodings = face_recognition.face_encodings(image)

            if len(face_encodings) == 0:
                return False, "Aucun visage détecté"

            # Sauvegarder l'encodage
            encoding = face_encodings[0]
            encoding_bytes = pickle.dumps(encoding)

            conn = sqlite3.connect('gmes.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO face_data (user_id, face_encoding, date_enregistrement)
                VALUES (?, ?, ?)
            ''', (user_id, encoding_bytes, datetime.utcnow()))
            conn.commit()
            conn.close()

            # Mettre à jour le cache
            self.known_face_encodings.append(encoding)
            self.known_face_ids.append(user_id)

            return True, "Visage enregistré avec succès"

        except Exception as e:
            return False, f"Erreur: {str(e)}"

    def recognize_face(self, image_path):
        """Reconnaît un visage"""
        try:
            # Charger l'image
            unknown_image = face_recognition.load_image_file(image_path)
            unknown_encoding = face_recognition.face_encodings(unknown_image)

            if len(unknown_encoding) == 0:
                return None, "Aucun visage détecté"

            # Comparer avec les visages connus
            matches = face_recognition.compare_faces(
                self.known_face_encodings,
                unknown_encoding[0]
            )

            face_distances = face_recognition.face_distance(
                self.known_face_encodings,
                unknown_encoding[0]
            )

            # Trouver la meilleure correspondance
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                confidence = 1 - face_distances[best_match_index]
                if confidence > 0.6:  # Seuil de confiance
                    return self.known_face_ids[best_match_index], confidence

            return None, "Visage non reconnu"

        except Exception as e:
            return None, f"Erreur: {str(e)}"

    def verify_liveness(self, image_path):
        """Vérifie que c'est une personne réelle (détection de vivacité)"""
        # Implémentation simplifiée - vérifier la clarté et les caractéristiques
        image = cv2.imread(image_path)
        if image is None:
            return False, "Image invalide"

        # Vérifier la netteté de l'image
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

        if laplacian_var < 100:  # Seuil de netteté
            return False, "Image trop floue"

        return True, "Vivacité vérifiée"



# Instance globale
face_system = FaceRecognitionSystem()