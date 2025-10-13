import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib
import os
from datetime import datetime


class AIScoringSystem:
    def __init__(self):
        self.model_path = "models/scoring_model.pkl"
        self.load_model()

    def load_model(self):
        """Charge ou initialise le modèle de scoring"""
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
        else:
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.is_trained = False

    def calculate_credit_score(self, client_data, pret_data, historique):
        """Calcule un score de crédit intelligent"""
        # Features pour le modèle
        features = self.extract_features(client_data, pret_data, historique)

        if self.is_trained:
            score = self.model.predict_proba([features])[0][1] * 1000
        else:
            # Score basique en attendant l'entraînement
            score = self.calculate_basic_score(client_data, historique)

        return min(850, max(300, score))

    def extract_features(self, client_data, pret_data, historique):
        """Extrait les features pour le modèle ML"""
        features = []

        # Données client
        features.append(client_data.get('revenu_mensuel', 0) / 1000)
        features.append(client_data.get('anciennete_client', 0))  # en mois
        features.append(1 if client_data.get('profession') in ['Commerçant', 'Entrepreneur'] else 0)

        # Données prêt
        features.append(pret_data.get('montant', 0) / 1000)
        features.append(pret_data.get('duree_mois', 0))
        montant_pret_ratio = pret_data.get('montant', 0) / max(client_data.get('revenu_mensuel', 1), 1)
        features.append(montant_pret_ratio)

        # Historique
        features.append(historique.get('nombre_prets', 0))
        features.append(historique.get('prets_rembourses', 0))
        features.append(historique.get('taux_remboursement', 0))
        features.append(historique.get('jours_retard_moyen', 0))
        features.append(historique.get('incidents_paiement', 0))

        return features

    def calculate_basic_score(self, client_data, historique):
        """Score basique en attendant l'IA"""
        score = 600  # Score de base

        # Ajustements selon le profil
        revenu = client_data.get('revenu_mensuel', 0)
        if revenu > 20000:
            score += 50
        elif revenu > 10000:
            score += 25

        # Historique de remboursement
        taux_remb = historique.get('taux_remboursement', 0)
        score += taux_remb * 2

        # Ancienneté
        anciennete = client_data.get('anciennete_client', 0)
        if anciennete > 24:  # 2 ans
            score += 30
        elif anciennete > 12:  # 1 an
            score += 15

        return score

    def train_model(self, training_data):
        """Entraîne le modèle avec des données historiques"""
        X = [self.extract_features(*data) for data in training_data]
        y = [data[2].get('defaut', 0) for data in training_data]  # 1 si défaut, 0 sinon

        self.model.fit(X, y)
        self.is_trained = True

        # Sauvegarder le modèle
        joblib.dump(self.model, self.model_path)

        return f"Modèle entraîné sur {len(X)} échantillons"

    def explain_score(self, client_data, pret_data, historique):
        """Explique les facteurs influençant le score"""
        factors = []

        revenu = client_data.get('revenu_mensuel', 0)
        if revenu < 5000:
            factors.append("Revenu mensuel faible")
        elif revenu > 20000:
            factors.append("Revenu mensuel élevé")

        taux_remb = historique.get('taux_remboursement', 0)
        if taux_remb > 95:
            factors.append("Excellent historique de remboursement")
        elif taux_remb < 80:
            factors.append("Historique de remboursement à améliorer")

        anciennete = client_data.get('anciennete_client', 0)
        if anciennete < 6:
            factors.append("Client récent")
        elif anciennete > 24:
            factors.append("Client fidèle")

        return factors


# Instance globale
ai_scorer = AIScoringSystem()