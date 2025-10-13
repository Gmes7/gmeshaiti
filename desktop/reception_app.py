import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import requests
import json


class ReceptionApp:
    def __init__(self):
        self.root = ttk.Window(themename="superhero")
        self.root.title("GMES - Ouverture de Compte")
        self.root.geometry("800x600")

        self.api_base = "http://localhost:5000"

        self.create_widgets()
        self.load_ads()

    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=BOTH, expand=True)

        # Frame pour les publicités
        ads_frame = ttk.Frame(main_frame)
        ads_frame.pack(fill=X, pady=(0, 20))

        self.ads_label = ttk.Label(ads_frame, text="", font=('Arial', 10), wraplength=700)
        self.ads_label.pack(fill=X)

        # Notebook pour les onglets
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=BOTH, expand=True)

        # Onglet Ouverture de compte
        account_frame = ttk.Frame(notebook, padding=10)
        notebook.add(account_frame, text="Ouverture de Compte")

        self.create_account_form(account_frame)

        # Onglet Connexion
        login_frame = ttk.Frame(notebook, padding=10)
        notebook.add(login_frame, text="Connexion")

        self.create_login_form(login_frame)

    def create_account_form(self, parent):
        # Formulaire d'ouverture de compte
        form_frame = ttk.Frame(parent)
        form_frame.pack(fill=BOTH, expand=True)

        # Ligne 1
        ttk.Label(form_frame, text="Nom:").grid(row=0, column=0, sticky=W, pady=5)
        self.last_name = ttk.Entry(form_frame, width=30)
        self.last_name.grid(row=0, column=1, pady=5, padx=(0, 10))

        ttk.Label(form_frame, text="Prénom:").grid(row=0, column=2, sticky=W, pady=5)
        self.first_name = ttk.Entry(form_frame, width=30)
        self.first_name.grid(row=0, column=3, pady=5)

        # Ligne 2
        ttk.Label(form_frame, text="Téléphone:").grid(row=1, column=0, sticky=W, pady=5)
        self.phone = ttk.Entry(form_frame, width=30)
        self.phone.grid(row=1, column=1, pady=5, padx=(0, 10))

        ttk.Label(form_frame, text="Email:").grid(row=1, column=2, sticky=W, pady=5)
        self.email = ttk.Entry(form_frame, width=30)
        self.email.grid(row=1, column=3, pady=5)

        # Continuer avec tous les autres champs...

        # Bouton de soumission
        ttk.Button(form_frame, text="Ouvrir le Compte",
                   command=self.submit_account, style=PRIMARY).grid(row=10, column=0, columnspan=4, pady=20)

    def create_login_form(self, parent):
        # Formulaire de connexion
        form_frame = ttk.Frame(parent)
        form_frame.pack(fill=BOTH, expand=True)

        ttk.Label(form_frame, text="Identifiant (Email ou Numéro de compte):").pack(pady=5)
        self.login_identifier = ttk.Entry(form_frame, width=40)
        self.login_identifier.pack(pady=5)

        ttk.Label(form_frame, text="Mot de passe:").pack(pady=5)
        self.login_password = ttk.Entry(form_frame, width=40, show="*")
        self.login_password.pack(pady=5)

        ttk.Button(form_frame, text="Se Connecter",
                   command=self.login, style=PRIMARY).pack(pady=20)

    def load_ads(self):
        try:
            response = requests.get(f"{self.api_base}/ads/active")
            if response.status_code == 200:
                ads = response.json()
                if ads:
                    ad_text = " | ".join([ad['title'] for ad in ads])
                    self.ads_label.config(text=ad_text)
        except:
            self.ads_label.config(text="Publicités non disponibles")

    def submit_account(self):
        # Récupérer et valider les données
        account_data = {
            'first_name': self.first_name.get(),
            'last_name': self.last_name.get(),
            'phone': self.phone.get(),
            'email': self.email.get(),
            # ... autres champs
        }

        try:
            response = requests.post(f"{self.api_base}/auth/register", data=account_data)
            if response.status_code == 200:
                messagebox.showinfo("Succès", "Compte créé avec succès!")
                self.clear_form()
            else:
                messagebox.showerror("Erreur", "Erreur lors de la création du compte")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur de connexion: {str(e)}")

    def login(self):
        login_data = {
            'identifier': self.login_identifier.get(),
            'password': self.login_password.get(),
            'user_type': 'client'
        }

        try:
            response = requests.post(f"{self.api_base}/auth/login", data=login_data)
            if response.status_code == 200:
                messagebox.showinfo("Succès", "Connexion réussie!")
                # Ouvrir le portail client
                self.open_client_portal()
            else:
                messagebox.showerror("Erreur", "Identifiants invalides")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur de connexion: {str(e)}")

    def clear_form(self):
        # Vider tous les champs du formulaire
        self.first_name.delete(0, tk.END)
        self.last_name.delete(0, tk.END)
        self.phone.delete(0, tk.END)
        self.email.delete(0, tk.END)
        # ... autres champs

    def open_client_portal(self):
        # Ouvrir une nouvelle fenêtre pour le portail client
        client_window = tk.Toplevel(self.root)
        client_window.title("Portail Client GMES")
        client_window.geometry("1000x700")

        # Implémenter l'interface du portail client
        self.create_client_dashboard(client_window)

    def create_client_dashboard(self, parent):
        # Interface du portail client
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=BOTH, expand=True)

        # Onglet Tableau de bord
        dashboard_frame = ttk.Frame(notebook)
        notebook.add(dashboard_frame, text="Tableau de Bord")

        # Onglet Transactions
        transactions_frame = ttk.Frame(notebook)
        notebook.add(transactions_frame, text="Transactions")

        # Onglet Prêts
        loans_frame = ttk.Frame(notebook)
        notebook.add(loans_frame, text="Prêts")

        # Remplir avec les données...

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = ReceptionApp()
    app.run()