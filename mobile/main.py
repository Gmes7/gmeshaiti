#
# import flet as ft
# import requests
# import time
# from datetime import datetime
#
# import asyncio
# import json
# import os
#
# # CORRECTION de l'import
# try:
#     from payment_gateways import payment_gateway
#     from offline_manager import offline_manager
# except ImportError:
#     # Mode simulation si les fichiers n'existent pas
#     payment_gateway = None
#     offline_manager = None
#     print("⚠️ Mode simulation - fichiers de paiement non trouvés")
#
# class GMESMobileApp:
#     def __init__(self):
#         self.api_base_url = "http://localhost:5000"
#         self.token = None
#         self.current_user = None
#         self.is_online = True
#         self.offline_manager = offline_manager
#         self.check_connectivity()
#
#     def main(self, page: ft.Page):
#         page.title = "GMES Microcrédit"
#         page.theme_mode = ft.ThemeMode.LIGHT
#         page.padding = 20
#         page.scroll = ft.ScrollMode.ADAPTIVE
#
#         # Contrôleur de vue principal
#         self.page = page
#         self.show_login_view()
#
#     def show_login_view(self):
#         """Vue de connexion"""
#         self.email_field = ft.TextField(
#             label="Email",
#             prefix_icon=ft.icons.EMAIL,  # ← CORRECTION
#             width=300
#         )
#
#         self.password_field = ft.TextField(
#             label="Mot de passe",
#             password=True,
#             can_reveal_password=True,
#             prefix_icon=ft.icons.LOCK,  # ← CORRECTION
#             width=300
#         )
#
#         login_button = ft.ElevatedButton(
#             text="Se connecter",
#             icon=ft.icons.LOGIN,  # ← CORRECTION
#             on_click=self.login,  # ← CORRECTION
#             width=300
#         )
#
#         register_button = ft.TextButton(
#             text="Créer un compte",
#             on_click=lambda e: self.show_register_view()  # ← CORRECTION
#         )
#
#         login_view = ft.Column(
#             [
#                 ft.Container(
#                     content=ft.Text("GMES Logo", size=24),  # ← SIMULATION logo
#                     alignment=ft.alignment.center
#                 ),
#                 ft.Text("GMES Mobile", size=24, weight=ft.FontWeight.BOLD),
#                 ft.Text("Microcrédit Solidaire", size=16),
#                 ft.Divider(),
#                 self.email_field,
#                 self.password_field,
#                 login_button,
#                 register_button
#             ],
#             alignment=ft.MainAxisAlignment.CENTER,
#             horizontal_alignment=ft.CrossAxisAlignment.CENTER
#         )
#
#         self.page.clean()
#         self.page.add(login_view)
#         self.page.update()  # ← TRÈS IMPORTANT!
#
#     def show_register_view(self, e=None):  # ← AJOUT du paramètre e
#         """Vue d'inscription"""
#         self.nom_field = ft.TextField(label="Nom", width=300)  # ← self. pour y accéder
#         self.prenom_field = ft.TextField(label="Prénom", width=300)
#         self.telephone_field = ft.TextField(label="Téléphone", width=300)
#         self.email_field_register = ft.TextField(label="Email", width=300)
#         self.password_field_register = ft.TextField(label="Mot de passe", password=True, width=300)
#
#         register_view = ft.Column(
#             [
#                 ft.IconButton(
#                     icon=ft.icons.ARROW_BACK,
#                     on_click=lambda e: self.show_login_view()  # ← CORRECTION
#                 ),
#                 ft.Text("Créer un compte", size=20, weight=ft.FontWeight.BOLD),
#                 self.nom_field,
#                 self.prenom_field,
#                 self.telephone_field,
#                 self.email_field_register,
#                 self.password_field_register,
#                 ft.ElevatedButton(
#                     text="S'inscrire",
#                     on_click=self.register,  # ← CORRECTION - appel direct
#                     width=300
#                 )
#             ]
#         )
#
#         self.page.clean()
#         self.page.add(register_view)
#         self.page.update()  # ← TRÈS IMPORTANT!
#
#     def register(self, e):
#         """Inscription via l'API"""
#         try:
#             # Vérifier que tous les champs sont remplis
#             if not all([
#                 self.nom_field.value,
#                 self.prenom_field.value,
#                 self.telephone_field.value,
#                 self.email_field_register.value,
#                 self.password_field_register.value
#             ]):
#                 self.show_error("Veuillez remplir tous les champs")
#                 return
#
#             # Appel réel à l'API
#             response = requests.post(f"{self.api_base_url}/register", json={
#                 "first_name": self.prenom_field.value,
#                 "last_name": self.nom_field.value,
#                 "phone": self.telephone_field.value,
#                 "email": self.email_field_register.value,
#                 "password": self.password_field_register.value
#             })
#
#             if response.status_code == 200:
#                 self.page.snack_bar = ft.SnackBar(content=ft.Text("Compte créé avec succès!"))
#                 self.page.snack_bar.open = True
#                 self.page.update()
#                 time.sleep(1)
#                 self.show_login_view()
#             else:
#                 self.show_error("Erreur lors de la création du compte")
#
#         except Exception as ex:
#             self.show_error(f"Erreur: {str(ex)}")
#
#     def show_dashboard(self, e=None):  # ← AJOUT du paramètre e
#         """Tableau de bord principal"""
#         # Header avec infos utilisateur (simulation si current_user n'existe pas)
#         user_info = self.current_user or {'prenom': 'Utilisateur', 'nom': 'Test', 'email': 'test@example.com'}
#
#         header = ft.Container(
#             content=ft.Row([
#                 ft.CircleAvatar(
#                     content=ft.Text(user_info['prenom'][0].upper()),
#                     bgcolor=ft.colors.BLUE
#                 ),
#                 ft.Column([
#                     ft.Text(f"{user_info['prenom']} {user_info['nom']}",
#                             weight=ft.FontWeight.BOLD),
#                     ft.Text(user_info['email'], size=12)
#                 ])
#             ]),
#             padding=10
#         )
#
#         # Cartes de statistiques
#         stats_cards = ft.Row([
#             self.create_stat_card("💰", "Solde", "5,000 HTG", 'green'),
#             self.create_stat_card("📊", "Prêts", "2 Actifs", 'blue'),
#             self.create_stat_card("⏰", "Prochain", "15/12/2024", 'orange'),
#         ])
#
#         # Menu principal
#         menu_grid = ft.GridView(
#             runs_count=2,
#             max_extent=150,
#             child_aspect_ratio=1.0,
#             spacing=10,
#             run_spacing=10,
#             controls=[
#                 self.create_menu_card("📋", "Mes Prêts", self.show_my_loans),
#                 self.create_menu_card("💳", "Rembourser", self.show_payment),
#                 self.create_menu_card("👥", "Mon Groupe", self.show_my_group),
#                 self.create_menu_card("📊", "Statistiques", self.show_stats),
#                 self.create_menu_card("🔔", "Notifications", self.show_notifications),
#                 self.create_menu_card("⚙️", "Paramètres", self.show_settings),
#             ]
#         )
#
#         dashboard = ft.Column([
#             header,
#             stats_cards,
#             ft.Divider(),
#             ft.Text("Actions rapides", weight=ft.FontWeight.BOLD),
#             menu_grid
#         ])
#
#         self.page.clean()
#         self.page.add(dashboard)
#         self.page.update()  # ← TRÈS IMPORTANT!
#
#     def show_stats(self, e=None):
#         """Vue des statistiques (simplifiée)"""
#         view = ft.Column([
#             ft.Row([
#                 ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda e: self.show_dashboard()),
#                 ft.Text("Statistiques", size=20, weight=ft.FontWeight.BOLD)
#             ]),
#             ft.Text("Statistiques personnelles", size=16),
#             ft.ElevatedButton("Retour", on_click=lambda e: self.show_dashboard())
#         ])
#
#         self.page.clean()
#         self.page.add(view)
#         self.page.update()
#
#     def create_stat_card(self, icon, title, value, color):
#         return ft.Container(
#             content=ft.Column([
#                 ft.Text(icon, size=20),
#                 ft.Text(value, size=16, weight=ft.FontWeight.BOLD),
#                 ft.Text(title, size=12)
#             ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
#             width=100,
#             height=80,
#             bgcolor=f"{color}50",
#             border_radius=10,
#             padding=10
#         )
#
#     def show_notifications(self, e=None):
#         """Vue des notifications (simplifiée)"""
#         view = ft.Column([
#             ft.Row([
#                 ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda e: self.show_dashboard()),
#                 ft.Text("Notifications", size=20, weight=ft.FontWeight.BOLD)
#             ]),
#             ft.Text("Liste des notifications", size=16),
#             ft.ElevatedButton("Retour", on_click=lambda e: self.show_dashboard())
#         ])
#
#         self.page.clean()
#         self.page.add(view)
#         self.page.update()
#
#     def show_settings(self, e=None):
#         """Vue des paramètres (simplifiée)"""
#         view = ft.Column([
#             ft.Row([
#                 ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda e: self.show_dashboard()),
#                 ft.Text("Paramètres", size=20, weight=ft.FontWeight.BOLD)
#             ]),
#             ft.Text("Paramètres de l'application", size=16),
#             ft.ElevatedButton("Déconnexion", on_click=self.logout)
#         ])
#
#         self.page.clean()
#         self.page.add(view)
#         self.page.update()
#
#
#
#
#
#     def create_menu_card(self, icon, title, on_click):
#         return ft.GestureDetector(
#             on_tap=on_click,
#             content=ft.Container(
#                 content=ft.Column([
#                     ft.Text(icon, size=24),
#                     ft.Text(title, size=12, text_align=ft.TextAlign.CENTER)
#                 ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
#                 bgcolor=ft.colors.BLUE_50,
#                 border_radius=10,
#                 padding=15
#             )
#         )
#
#     def show_my_loans(self, e=None):
#         """Vue des prêts de l'utilisateur"""
#         try:
#             # Récupérer les prêts depuis l'API
#             headers = {"Authorization": f"Bearer {self.token}"}
#             response = requests.get(f"{self.api_base_url}/mes-prets", headers=headers)
#
#             if response.status_code == 200:
#                 prets = response.json()
#
#                 pret_cards = []
#                 for pret in prets:
#                     card = ft.Card(
#                         content=ft.Container(
#                             content=ft.Column([
#                                 ft.Row([
#                                     ft.Text(f"Prêt #{pret['id']}", weight=ft.FontWeight.BOLD),
#                                     ft.Container(
#                                         content=ft.Text(
#                                             pret['statut'].replace('_', ' ').title(),
#                                             color=ft.colors.WHITE,
#                                             size=12
#                                         ),
#                                         bgcolor=self.get_status_color(pret['statut']),
#                                         padding=5,
#                                         border_radius=5
#                                     )
#                                 ]),
#                                 ft.Text(f"Montant: {pret['montant']:,} HTG"),
#                                 ft.Text(f"Mensualité: {pret['mensualite']:,} HTG"),
#                                 ft.Text(f"Durée: {pret['duree_mois']} mois"),
#                             ]),
#                             padding=15
#                         )
#                     )
#                     pret_cards.append(card)
#
#                 view = ft.Column([
#                     ft.Row([
#                         ft.IconButton(
#                             icon=ft.Icon(name="arrow_back"),
#                             on_click=lambda _: self.show_dashboard()),
#                         ft.ElevatedButton(
#                             text="Nouvelle Demande",
#                             icon="add",
#                             on_click=self.show_loan_request
#                         ),
#                     ]),  # ← PARENTHESE FERMANTE AJOUTÉE ICI
#                     *pret_cards
#                 ])  # ← PARENTHESE FERMANTE AJOUTÉE ICI
#
#                 self.page.clean()
#                 self.page.add(view)
#
#         except Exception as e:
#             self.show_error(f"Erreur: {str(e)}")
#
#     def show_loan_request(self, e=None):
#         """Vue de demande de prêt"""
#         montant_field = ft.TextField(label="Montant (HTG)", keyboard_type=ft.KeyboardType.NUMBER)
#         duree_field = ft.Dropdown(
#             label="Durée (mois)",
#             options=[
#                 ft.dropdown.Option("6", "6 mois"),
#                 ft.dropdown.Option("12", "12 mois"),
#                 ft.dropdown.Option("24", "24 mois"),
#             ]
#         )
#         motif_field = ft.TextField(label="Motif du prêt", multiline=True)
#
#         calcul_button = ft.TextButton(
#             text="Calculer la mensualité",
#             on_click=lambda _: self.calculer_mensualite(montant_field.value, duree_field.value)
#         )
#
#         self.mensualite_text = ft.Text("", size=16, weight=ft.FontWeight.BOLD)
#
#         view = ft.Column([
#             ft.Row([
#                 ft.IconButton(
#                     icon=ft.Icon(name="arrow_back"),  # ← Correction
#                     on_click=lambda _: self.show_my_loans()
#                 ),
#                 ft.Text("Nouvelle Demande", size=20, weight=ft.FontWeight.BOLD)
#             ]),
#             montant_field,
#             duree_field,
#             motif_field,
#             calcul_button,
#             self.mensualite_text,
#             ft.ElevatedButton(
#                 text="Soumettre la demande",
#                 icon="send",  # ← string directement
#                 on_click=lambda _: self.soumettre_demande(
#                     montant_field.value,
#                     duree_field.value,
#                     motif_field.value
#                 ),
#                 width=300
#             )
#         ])
#
#         self.page.clean()
#         self.page.add(view)
#
#     def check_connectivity(self):
#         """Vérifie la connectivité"""
#         try:
#             response = requests.get(f"{self.api_base_url}/health", timeout=5)
#             self.is_online = response.status_code == 200
#         except:
#             self.is_online = False
#
#     # === MÉTHODES API ===
#
#     def login(self, e):
#         """Connexion à l'API"""
#         try:
#             url = f"{self.api_base_url}/api/mobile/login"
#             print(f"🔗 URL: {url}")
#             print(f"📧 Email: {self.email_field.value}")
#             print(f"🔑 Password: {self.password_field.value}")
#
#             response = requests.post(url, json={
#                 "identifier": self.email_field.value,
#                 "password": self.password_field.value,
#                 "user_type": "client"
#             })
#
#             print(f"📡 Status: {response.status_code}")
#             print(f"📦 Response: {response.text}")
#         # try:
#             response = requests.post(f"{self.api_base_url}/login", json={
#                 "identifier": self.email_field.value,
#                 "password": self.password_field.value,
#                 "user_type": "client"  # ← IMPORTANT
#             })
#
#             if response.status_code == 200:
#                 data = response.json()
#                 self.token = data.get('token')
#                 self.current_user = data.get('user')
#
#                 # Vérifier que le token et user sont bien reçus
#                 if not self.token or not self.current_user:
#                     self.show_error("Réponse API invalide")
#                     return
#
#                 self.show_dashboard()
#                 self.page.snack_bar = ft.SnackBar(content=ft.Text("Connexion réussie!"))
#                 self.page.snack_bar.open = True
#                 self.page.update()
#             else:
#                 # Afficher le message d'erreur de l'API si disponible
#                 try:
#                     error_data = response.json()
#                     self.show_error(error_data.get('message', 'Identifiant ou mot de passe incorrect'))
#                 except:
#                     self.show_error(f"Erreur API: {response.status_code}")
#
#         except Exception as e:
#             self.show_error(f"Erreur de connexion: {str(e)}")
#
#
#     def calculer_mensualite(self, montant, duree):
#         """Calcul de mensualité via l'API"""
#         try:
#             response = requests.post(f"{self.api_base_url}/calcul-pret", json={
#                 "montant": float(montant),
#                 "duree": int(duree)
#             })
#
#             if response.status_code == 200:
#                 data = response.json()
#                 self.mensualite_text.value = f"Mensualité: {data['mensualite']:,} HTG"
#                 self.mensualite_text.update()
#
#         except Exception as e:
#             self.show_error(f"Erreur de calcul: {str(e)}")
#
#     def soumettre_demande(self, montant, duree, motif):
#         """Soumission de demande de prêt"""
#         try:
#             headers = {"Authorization": f"Bearer {self.token}"}
#             response = requests.post(f"{self.api_base_url}/demande-pret", headers=headers, json={
#                 "montant": float(montant),
#                 "duree": int(duree),
#                 "motif": motif
#             })
#
#             if response.status_code == 201:
#                 self.page.snack_bar=ft.SnackBar(content=ft.Text("Demande envoyée avec succès!"))
#                 self.show_my_loans()
#             else:
#                 self.show_error("Erreur lors de l'envoi de la demande")
#
#         except Exception as e:
#             self.show_error(f"Erreur: {str(e)}")
#
#
#     def show_error(self, message):
#         self.page.snack_bar = ft.SnackBar(
#             content=ft.Text(message),
#             bgcolor=ft.colors.RED_400
#         )
#         self.page.snack_bar.open = True
#         self.page.update()
#
#     def get_status_color(self, statut):
#         """Couleur selon le statut"""
#         colors = {
#             'approuve': 'green',
#             'en_attente': 'orange',
#             'rejete': 'red',
#             'termine': 'blue'
#         }
#         return colors.get(statut, 'grey')
#
#     def show_my_group(self, e=None):
#         """Vue du groupe (simplifiée)"""
#         view = ft.Column([
#             ft.Row([
#                 ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda e: self.show_dashboard()),
#                 ft.Text("Mon Groupe", size=20, weight=ft.FontWeight.BOLD)
#             ]),
#             ft.Text("Gestion de groupe", size=16),
#             ft.ElevatedButton("Retour", on_click=lambda e: self.show_dashboard())
#         ])
#
#         self.page.clean()
#         self.page.add(view)
#         self.page.update()
#
#
#
#
#     def process_payment(self, remboursement, method_id):
#         """Traitement du paiement"""
#         # Simulation de paiement
#         progress_bar = ft.ProgressBar(width=300)
#         status_text = ft.Text("Traitement en cours...")
#
#         view = ft.Column([
#             ft.Row([
#                 ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda _: self.show_payment_methods(remboursement)),
#                 ft.Text("Paiement", size=20, weight=ft.FontWeight.BOLD)
#             ]),
#             ft.Container(
#                 content=ft.Column([
#                     ft.Icon(ft.icons.ACCOUNT_BALANCE_WALLET, size=50, color=ft.colors.BLUE),
#                     ft.Text(f"Paiement de {remboursement['montant']:,} HTG", size=16, weight=ft.FontWeight.BOLD),
#                     ft.Text(f"Méthode: {method_id}"),
#                     progress_bar,
#                     status_text
#                 ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
#                 padding=50
#             )
#         ])
#
#         self.page.clean()
#         self.page.add(view)
#
#         # Simulation de traitement
#         import time
#         for i in range(5):
#             time.sleep(0.5)
#             progress_bar.value = (i + 1) / 5
#             self.page.update()
#
#         # Paiement réussi
#         status_text.value = "✅ Paiement confirmé!"
#         progress_bar.value = 1.0
#         self.page.update()
#
#         # Enregistrer le paiement
#         try:
#             headers = {"Authorization": f"Bearer {self.token}"}
#             response = requests.post(f"{self.api_base_url}/remboursement/payer", headers=headers, json={
#                 "pret_id": remboursement["pret_id"],
#                 "montant": remboursement["montant"],
#                 "methode": method_id
#             })
#
#             if response.status_code == 200:
#                 self.page.show_snack_bar(ft.SnackBar(content=ft.Text("Paiement enregistré avec succès!")))
#
#         except Exception as e:
#             self.show_error(f"Erreur: {str(e)}")
#
#         # Retour au dashboard après 2 secondes
#         time.sleep(2)
#         self.show_dashboard()
#
#
#     # def show_my_group(self, e=None):
#     #     """Vue du groupe solidaire"""
#     #     try:
#     #         headers = {"Authorization": f"Bearer {self.token}"}
#     #         response = requests.get(f"{self.api_base_url}/mon-groupe", headers=headers)
#     #
#     #         if response.status_code == 200:
#     #             groupe_data = response.json()
#     #
#     #             # Membres du groupe
#     #             membres_list = ft.Column([], scroll=ft.ScrollMode.ALWAYS)
#     #             for membre in groupe_data.get('membres', []):
#     #                 membre_card = ft.ListTile(
#     #                     leading=ft.CircleAvatar(
#     #                         content=ft.Text(membre['prenom'][0].upper()),
#     #                         bgcolor=ft.colors.BLUE
#     #                     ),
#     #                     title=ft.Text(f"{membre['prenom']} {membre['nom']}"),
#     #                     subtitle=ft.Text(membre.get('profession', 'Non spécifié')),
#     #                 )
#     #                 membres_list.controls.append(membre_card)
#     #
#     #             # Prêts du groupe
#     #             prets_groupe = ft.Column([])
#     #             for pret in groupe_data.get('prets_groupe', []):
#     #                 pret_card = ft.Card(
#     #                     content=ft.Container(
#     #                         content=ft.Column([
#     #                             ft.Row([
#     #                                 ft.Text(f"{pret['client_prenom']}", weight=ft.FontWeight.BOLD),
#     #                                 ft.Text(f"{pret['montant']:,} HTG")
#     #                             ]),
#     #                             ft.Text(f"Statut: {pret['statut']}"),
#     #                             ft.Text(f"Motif: {pret['motif']}")
#     #                         ]),
#     #                         padding=10
#     #                     )
#     #                 )
#     #                 prets_groupe.controls.append(pret_card)
#     #
#     #             view = ft.Column([
#     #                 ft.Row([
#     #                     ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda _: self.show_dashboard()),
#     #                     ft.Text("Mon Groupe", size=20, weight=ft.FontWeight.BOLD)
#     #                 ]),
#     #
#     #                 # Info groupe
#     #                 ft.Card(
#     #                     content=ft.Container(
#     #                         content=ft.Column([
#     #                             ft.Text(groupe_data['nom'], size=18, weight=ft.FontWeight.BOLD),
#     #                             ft.Text(f"Zone: {groupe_data['zone']}"),
#     #                             ft.Text(f"Code: {groupe_data['code_groupe']}"),
#     #                             ft.Row([
#     #                                 ft.Text(f"👥 {len(groupe_data.get('membres', []))} membres"),
#     #                                 ft.Text(f"💰 {groupe_data.get('montant_prets_total', 0):,} HTG total"),
#     #                             ])
#     #                         ]),
#     #                         padding=15
#     #                     )
#     #                 ),
#     #
#     #                 # Membres
#     #                 ft.Text("Membres du groupe", size=16, weight=ft.FontWeight.BOLD),
#     #                 ft.Container(
#     #                     content=membres_list,
#     #                     height=200
#     #                 ),
#     #
#     #                 # Prêts solidaires
#     #                 ft.Row([
#     #                     ft.Text("Prêts solidaires", size=16, weight=ft.FontWeight.BOLD),
#     #                     ft.IconButton(
#     #                         icon=ft.icons.ADD,
#     #                         on_click=self.show_demande_pret_solidaire
#     #                     )
#     #                 ]),
#     #                 prets_groupe if prets_groupe.controls else ft.Text("Aucun prêt solidaire actif"),
#     #
#     #                 # Actions
#     #                 ft.ElevatedButton(
#     #                     text="Voir réunions",
#     #                     icon=ft.icons.CALENDAR_TODAY,
#     #                     on_click=self.show_reunions_groupe
#     #                 )
#     #             ])
#     #
#     #             self.page.clean()
#     #             self.page.add(view)
#     #
#     #     except Exception as e:
#     #         self.show_error(f"Erreur: {str(e)}")
#     #
#
#     def show_demande_pret_solidaire(self, e=None):
#         """Demande de prêt solidaire"""
#         montant_field = ft.TextField(label="Montant (HTG)", keyboard_type=ft.KeyboardType.NUMBER)
#         duree_field = ft.Dropdown(
#             label="Durée (mois)",
#             options=[ft.dropdown.Option(str(i), f"{i} mois") for i in [6, 12, 18, 24]]
#         )
#         motif_field = ft.TextField(label="Motif du prêt", multiline=True)
#         garant_field = ft.Dropdown(
#             label="Garant solidaire",
#             options=[]  # À remplir avec les membres du groupe
#         )
#
#         view = ft.Column([
#             ft.Row([
#                 ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda _: self.show_my_group()),
#                 ft.Text("Prêt Solidaire", size=20, weight=ft.FontWeight.BOLD)
#             ]),
#             ft.Text("Demande de prêt avec garantie solidaire", size=14),
#             montant_field,
#             duree_field,
#             motif_field,
#             garant_field,
#             ft.ElevatedButton(
#                 text="Soumettre au groupe",
#                 icon=ft.icons.GROUP_ADD,
#                 on_click=lambda _: self.soumettre_pret_solidaire(
#                     montant_field.value,
#                     duree_field.value,
#                     motif_field.value,
#                     garant_field.value
#                 )
#             )
#         ])
#
#         self.page.clean()
#         self.page.add(view)
#
#
#     def show_stats(self, e=None):
#         """Vue des statistiques personnelles"""
#         try:
#             headers = {"Authorization": f"Bearer {self.token}"}
#             response = requests.get(f"{self.api_base_url}/mes-statistiques", headers=headers)
#
#             if response.status_code == 200:
#                 stats = response.json()
#
#                 # Graphique simple (simulation)
#                 historique_remboursements = ft.BarChart(
#                     bar_groups=[
#                         ft.BarChartGroup(
#                             x=0,
#                             bar_rods=[ft.BarChartRod(from_y=0, to_y=stats.get('ponctualite', 85), color=ft.colors.BLUE)]
#                         )
#                     ],
#                     border=ft.border.all(1, ft.colors.GREY_400),
#                     left_axis=ft.ChartAxis(labels_size=40),
#                     bottom_axis=ft.ChartAxis(labels_size=16),
#                     horizontal_grid_lines=ft.ChartGridLines(interval=10, color=ft.colors.GREY_300),
#                     tooltip_bgcolor=ft.colors.WHITE,
#                     max_y=100,
#                     interactive=True,
#                     expand=True,
#                 )
#
#                 view = ft.Column([
#                     ft.Row([
#                         ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda _: self.show_dashboard()),
#                         ft.Text("Mes Statistiques", size=20, weight=ft.FontWeight.BOLD)
#                     ]),
#
#                     # Cartes de stats
#                     ft.Row([
#                         self.create_stat_card("📈", "Score crédit", f"{stats.get('score_credit', 75)}/100"),
#                         self.create_stat_card("⏰", "Ponctualité", f"{stats.get('ponctualite', 85)}%"),
#                     ]),
#
#                     ft.Row([
#                         self.create_stat_card("💰", "Prêts total", f"{stats.get('prets_total', 0):,} HTG"),
#                         self.create_stat_card("✅", "Prêts remb.", f"{stats.get('prets_rembourses', 0)}"),
#                     ]),
#
#                     # Graphique
#                     ft.Text("Historique de ponctualité", size=16, weight=ft.FontWeight.BOLD),
#                     ft.Container(
#                         content=historique_remboursements,
#                         height=200,
#                         padding=10
#                     ),
#
#                     # Détails
#                     ft.ExpansionTile(
#                         title=ft.Text("Détails des prêts"),
#                         subtitle=ft.Text("Voir l'historique complet"),
#                         controls=[
#                             ft.DataTable(
#                                 columns=[
#                                     ft.DataColumn(ft.Text("Date")),
#                                     ft.DataColumn(ft.Text("Montant")),
#                                     ft.DataColumn(ft.Text("Statut")),
#                                 ],
#                                 rows=[
#                                     ft.DataRow(cells=[
#                                         ft.DataCell(ft.Text(pret["date"])),
#                                         ft.DataCell(ft.Text(f"{pret['montant']:,} HTG")),
#                                         ft.DataCell(ft.Text(pret["statut"])),
#                                     ]) for pret in stats.get('historique_prets', [])
#                                 ]
#                             )
#                         ]
#                     )
#                 ])
#
#                 self.page.clean()
#                 self.page.add(view)
#
#         except Exception as e:
#             self.show_error(f"Erreur: {str(e)}")
#
#
#     # def show_notifications(self, e=None):
#     #     """Vue des notifications"""
#     #     try:
#     #         headers = {"Authorization": f"Bearer {self.token}"}
#     #         response = requests.get(f"{self.api_base_url}/notifications", headers=headers)
#     #
#     #         if response.status_code == 200:
#     #             notifications = response.json()
#     #
#     #             notification_list = ft.Column([])
#     #
#     #             for notif in notifications:
#     #                 # Icône selon le type
#     #                 icons = {
#     #                     'pret': ft.icons.ACCOUNT_BALANCE,
#     #                     'remboursement': ft.icons.PAYMENT,
#     #                     'groupe': ft.icons.GROUP,
#     #                     'alerte': ft.icons.WARNING,
#     #                     'info': ft.icons.INFO
#     #                 }
#     #
#     #                 notification_tile = ft.ListTile(
#     #                     leading=ft.Icon(icons.get(notif['type'], ft.icons.NOTIFICATIONS)),
#     #                     title=ft.Text(notif['titre']),
#     #                     subtitle=ft.Text(notif['message']),
#     #                     trailing=ft.Text(notif['date']),
#     #                     on_click=lambda e, n=notif: self.show_notification_detail(n)
#     #                 )
#     #                 notification_list.controls.append(notification_tile)
#     #
#     #             view = ft.Column([
#     #                 ft.Row([
#     #                     ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda _: self.show_dashboard()),
#     #                     ft.Text("Notifications", size=20, weight=ft.FontWeight.BOLD),
#     #                     ft.IconButton(icon=ft.icons.DELETE, on_click=self.vider_notifications)
#     #                 ]),
#     #                 ft.ElevatedButton(
#     #                     text="Marquer tout comme lu",
#     #                     icon=ft.icons.CHECK,
#     #                     on_click=self.marquer_comme_lu
#     #                 ),
#     #                 notification_list if notification_list.controls else ft.Container(
#     #                     content=ft.Column([
#     #                         ft.Icon(ft.icons.NOTIFICATIONS_OFF, size=50, color=ft.colors.GREY),
#     #                         ft.Text("Aucune notification", size=16)
#     #                     ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
#     #                     padding=50
#     #                 )
#     #             ])
#     #
#     #             self.page.clean()
#     #             self.page.add(view)
#     #
#     #     except Exception as e:
#     #         self.show_error(f"Erreur: {str(e)}")
#
#
#     def show_notification_detail(self, notification):
#         """Détail d'une notification"""
#         actions = ft.Row([])
#
#         if notification['type'] == 'pret' and notification.get('pret_id'):
#             actions.controls.append(
#                 ft.ElevatedButton(
#                     text="Voir le prêt",
#                     on_click=lambda _: self.show_loan_detail(notification['pret_id'])
#                 )
#             )
#
#         view = ft.Column([
#             ft.Row([
#                 ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda _: self.show_notifications()),
#                 ft.Text("Détail", size=20, weight=ft.FontWeight.BOLD)
#             ]),
#             ft.Card(
#                 content=ft.Container(
#                     content=ft.Column([
#                         ft.Text(notification['titre'], size=18, weight=ft.FontWeight.BOLD),
#                         ft.Text(notification['date'], size=12, color=ft.colors.GREY),
#                         ft.Divider(),
#                         ft.Text(notification['message'], size=14),
#                         actions
#                     ]),
#                     padding=20
#                 )
#             )
#         ])
#
#         self.page.clean()
#         self.page.add(view)
#
#
#     # def show_settings(self, e=None):
#     #     """Vue des paramètres"""
#     #     # Simulation des préférences
#     #     notifications_active = ft.Switch(value=True, label="Notifications push")
#     #     sms_alertes = ft.Switch(value=True, label="Alertes SMS")
#     #     mode_sombre = ft.Switch(value=False, label="Mode sombre")
#     #
#     #     view = ft.Column([
#     #         ft.Row([
#     #             ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda _: self.show_dashboard()),
#     #             ft.Text("Paramètres", size=20, weight=ft.FontWeight.BOLD)
#     #         ]),
#     #
#     #         ft.Text("Préférences", size=16, weight=ft.FontWeight.BOLD),
#     #         notifications_active,
#     #         sms_alertes,
#     #         mode_sombre,
#     #
#     #         ft.Divider(),
#     #
#     #         ft.Text("Compte", size=16, weight=ft.FontWeight.BOLD),
#     #         ft.ListTile(
#     #             leading=ft.Icon(ft.icons.PERSON),
#     #             title=ft.Text("Informations personnelles"),
#     #             on_click=lambda _: self.show_profile()
#     #         ),
#     #         ft.ListTile(
#     #             leading=ft.Icon(ft.icons.SECURITY),
#     #             title=ft.Text("Sécurité et mot de passe"),
#     #             on_click=lambda _: self.show_security()
#     #         ),
#     #
#     #         ft.Divider(),
#     #
#     #         ft.ListTile(
#     #             leading=ft.Icon(ft.icons.HELP),
#     #             title=ft.Text("Aide et support"),
#     #             on_click=lambda _: self.show_help()
#     #         ),
#     #         ft.ListTile(
#     #             leading=ft.Icon(ft.icons.DESCRIPTION),
#     #             title=ft.Text("Conditions d'utilisation"),
#     #             on_click=lambda _: self.show_terms()
#     #         ),
#     #
#     #         ft.Divider(),
#     #
#     #         ft.ElevatedButton(
#     #             text="Déconnexion",
#     #             icon=ft.icons.LOGOUT,
#     #             color='red',
#     #             on_click=self.logout
#     #         )
#     #     ])
#     #
#     #     self.page.clean()
#     #     self.page.add(view)
#
#
#     def logout(self, e):
#         """Déconnexion"""
#         self.token = None
#         self.current_user = None
#         self.show_login_view()
#         self.page.show_snack_bar(ft.SnackBar(content=ft.Text("Déconnexion réussie!")))
#
#
#
#
#     def check_connectivity(self):
#         """Vérifie la connectivité"""
#         try:
#             response = requests.get(f"{self.api_base_url}/health", timeout=5)
#             self.is_online = response.status_code == 200
#         except:
#             self.is_online = False
#
#     def show_offline_indicator(self):
#         """Affiche l'indicateur hors ligne"""
#         if not self.is_online:
#             self.page.banner = ft.Banner(
#                 bgcolor=ft.colors.AMBER_100,
#                 leading=ft.Icon(ft.icons.WIFI_OFF, color=ft.colors.ORANGE),
#                 content=ft.Text("Mode hors ligne - Synchronisation automatique à la reconnexion"),
#                 actions=[
#                     ft.TextButton("Actualiser", on_click=self.retry_connection),
#                 ],
#             )
#             self.page.banner.open = True
#         else:
#             if hasattr(self.page, 'banner'):
#                 self.page.banner.open = False
#
#         self.page.update()
#
#     def retry_connection(self, e):
#         """Tente de se reconnecter"""
#         self.check_connectivity()
#         self.show_offline_indicator()
#
#         if self.is_online:
#             self.sync_offline_data()
#
#     def sync_offline_data(self):
#         """Synchronise les données hors ligne"""
#         if not self.token:
#             return
#
#         success_count, total_count = offline_manager.sync_with_server(
#             self.api_base_url, self.token
#         )
#
#         if success_count > 0:
#             self.page.show_snack_bar(
#                 ft.SnackBar(content=ft.Text(f"✅ {success_count}/{total_count} opérations synchronisées"))
#             )
#
#     def submit_loan_request_offline(self, montant, duree, motif):
#         """Soumet une demande de prêt en mode hors ligne"""
#         operation_data = {
#             'type': 'loan_request',
#             'montant': montant,
#             'duree': duree,
#             'motif': motif,
#             'timestamp': datetime.utcnow().isoformat()
#         }
#
#         operation_id = offline_manager.save_offline_operation(
#             'loan_request', operation_data
#         )
#
#         # Mettre en cache pour affichage immédiat
#         cached_loans = offline_manager.get_cached_data('my_loans') or []
#         cached_loans.append({
#             'id': f"offline_{operation_id}",
#             'montant': montant,
#             'duree_mois': duree,
#             'statut': 'en_attente_hors_ligne',
#             'date_demande': datetime.utcnow().strftime('%d/%m/%Y')
#         })
#         offline_manager.cache_data('my_loans', cached_loans)
#
#         return operation_id
#
#     def show_payment(self, e=None):
#         """Vue de paiement (simplifiée)"""
#         view = ft.Column([
#             ft.Row([
#                 ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda e: self.show_dashboard()),
#                 ft.Text("Paiement", size=20, weight=ft.FontWeight.BOLD)
#             ]),
#             ft.Text("Fonctionnalité de paiement", size=16),
#             ft.ElevatedButton("Retour", on_click=lambda e: self.show_dashboard())
#         ])
#
#         self.page.clean()
#         self.page.add(view)
#         self.page.update()
#
#
#     def show_payment_methods(self, remboursement):
#         """Choix du mode de paiement AVEC OPTIONS DIGITALES"""
#         methods = [
#             {"icon": "📱", "name": "MonCash", "id": "moncash", "type": "digital"},
#             {"icon": "💳", "name": "NatCash", "id": "natcash", "type": "digital"},
#             {"icon": "🏦", "name": "Transfert Bancaire", "id": "bank", "type": "traditional"},
#             {"icon": "📠", "name": "QR Code", "id": "qrcode", "type": "digital"},
#             {"icon": "💵", "name": "Espèces", "id": "cash", "type": "traditional"},
#         ]
#
#         digital_methods = [m for m in methods if m['type'] == 'digital']
#         traditional_methods = [m for m in methods if m['type'] == 'traditional']
#
#         method_cards = []
#
#         # Méthodes digitales
#         if digital_methods:
#             method_cards.append(ft.Text("Paiements Digitaux", size=16, weight=ft.FontWeight.BOLD))
#             for method in digital_methods:
#                 card = self.create_payment_method_card(method, remboursement)
#                 method_cards.append(card)
#
#         # Méthodes traditionnelles
#         if traditional_methods:
#             method_cards.append(ft.Text("Méthodes Traditionnelles", size=16, weight=ft.FontWeight.BOLD))
#             for method in traditional_methods:
#                 card = self.create_payment_method_card(method, remboursement)
#                 method_cards.append(card)
#
#         view = ft.Column([
#             ft.Row([
#                 ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda _: self.show_payment()),
#                 ft.Text("Mode de paiement", size=20, weight=ft.FontWeight.BOLD)
#             ]),
#             ft.Text(f"Montant: {remboursement['montant']:,} HTG", size=18, weight=ft.FontWeight.BOLD),
#             *method_cards
#         ])
#
#         self.page.clean()
#         self.page.add(view)
#
#     def create_payment_method_card(self, method, remboursement):
#         """Crée une carte de méthode de paiement"""
#         return ft.Card(
#             content=ft.Container(
#                 content=ft.Row([
#                     ft.Text(method["icon"], size=20),
#                     ft.Column([
#                         ft.Text(method["name"], weight=ft.FontWeight.BOLD),
#                         ft.Text("Paiement instantané" if method["type"] == "digital" else "Paiement standard",
#                                 size=12, color=ft.colors.GREY)
#                     ], expand=True),
#                     ft.Icon(ft.icons.CHEVRON_RIGHT, color=ft.colors.BLUE)
#                 ]),
#                 padding=15,
#                 on_click=lambda e, m=method: self.process_digital_payment(remboursement, m["id"])
#             )
#         )
#
#     def process_digital_payment(self, remboursement, method_id):
#         """Traite un paiement digital"""
#         if method_id == 'moncash':
#             self.process_moncash_payment(remboursement)
#         elif method_id == 'natcash':
#             self.process_natcash_payment(remboursement)
#         elif method_id == 'qrcode':
#             self.process_qrcode_payment(remboursement)
#         else:
#             self.process_payment(remboursement, method_id)  # Méthode existante
#
#     def process_moncash_payment(self, remboursement):
#         """Paiement via MonCash"""
#         progress_bar = ft.ProgressBar(width=300)
#         status_text = ft.Text("Initialisation du paiement MonCash...")
#
#         view = ft.Column([
#             ft.Row([
#                 ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda _: self.show_payment_methods(remboursement)),
#                 ft.Text("Paiement MonCash", size=20, weight=ft.FontWeight.BOLD)
#             ]),
#             ft.Container(
#                 content=ft.Column([
#                     ft.Icon(ft.icons.PHONE_ANDROID, size=50, color=ft.colors.ORANGE),
#                     ft.Text("MonCash", size=24, weight=ft.FontWeight.BOLD),
#                     ft.Text(f"Montant: {remboursement['montant']:,} HTG", size=16),
#                     progress_bar,
#                     status_text,
#                     ft.ElevatedButton(
#                         text="Ouvrir l'application MonCash",
#                         icon=ft.icons.OPEN_IN_NEW,
#                         on_click=lambda _: self.lancer_moncash(remboursement)
#                     )
#                 ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
#                 padding=50
#             )
#         ])
#
#         self.page.clean()
#         self.page.add(view)
#
#         # Initier le paiement
#         success, result = payment_gateway.initier_paiement_moncash(
#             remboursement['montant'],
#             f"Remboursement prêt #{remboursement['pret_id']}",
#             f"GMES_{remboursement['pret_id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
#         )
#
#         if success:
#             status_text.value = "✅ Paiement initié! Ouvrez MonCash pour confirmer."
#             self.monitor_payment_status('moncash', result['transaction_id'], remboursement)
#         else:
#             status_text.value = f"❌ Erreur: {result}"
#
#         self.page.update()
#
#     def process_natcash_payment(self, remboursement):
#         """Paiement via NatCash"""
#         view = ft.Column([
#             ft.Row([
#                 ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda _: self.show_payment_methods(remboursement)),
#                 ft.Text("Paiement NatCash", size=20, weight=ft.FontWeight.BOLD)
#             ]),
#             ft.Container(
#                 content=ft.Column([
#                     ft.Icon(ft.icons.PAYMENT, size=50, color=ft.colors.BLUE),
#                     ft.Text("NatCash", size=24, weight=ft.FontWeight.BOLD),
#                     ft.Text(f"Montant: {remboursement['montant']:,} HTG", size=16),
#
#                     ft.TextField(
#                         label="Numéro de téléphone",
#                         prefix_icon=ft.icons.PHONE,
#                         keyboard_type=ft.KeyboardType.PHONE,
#                         width=300
#                     ),
#
#                     ft.ElevatedButton(
#                         text="Envoyer la demande de paiement",
#                         icon=ft.icons.SEND,
#                         on_click=lambda _: self.envoyer_demande_natcash(remboursement)
#                     )
#                 ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
#                 padding=50
#             )
#         ])
#
#         self.page.clean()
#         self.page.add(view)
#
#     def process_qrcode_payment(self, remboursement):
#         """Paiement via QR Code"""
#         success, qr_data = payment_gateway.generer_qr_code(
#             remboursement['montant'],
#             f"Remboursement GMES - Prêt #{remboursement['pret_id']}"
#         )
#
#         if success:
#             view = ft.Column([
#                 ft.Row([
#                     ft.IconButton(icon=ft.icons.ARROW_BACK,
#                                   on_click=lambda _: self.show_payment_methods(remboursement)),
#                     ft.Text("Paiement QR Code", size=20, weight=ft.FontWeight.BOLD)
#                 ]),
#                 ft.Container(
#                     content=ft.Column([
#                         ft.Icon(ft.icons.Qr_CODE, size=50, color=ft.colors.GREEN),
#                         ft.Text("Scannez le QR Code", size=18, weight=ft.FontWeight.BOLD),
#                         ft.Text("Avec votre application mobile de paiement", size=14),
#
#                         # Placeholder pour le QR Code
#                         ft.Container(
#                             content=ft.Column([
#                                 ft.Text("[QR CODE]", size=40),
#                                 ft.Text("Simulation QR Code", size=12, color=ft.colors.GREY)
#                             ], alignment=ft.MainAxisAlignment.CENTER,
#                                 horizontal_alignment=ft.CrossAxisAlignment.CENTER),
#                             width=200,
#                             height=200,
#                             bgcolor=ft.colors.GREY_100,
#                             border_radius=10,
#                             padding=20
#                         ),
#
#                         ft.Text(f"Montant: {remboursement['montant']:,} HTG", size=16, weight=ft.FontWeight.BOLD),
#                         ft.Text("Description: Remboursement GMES", size=14),
#
#                         ft.ElevatedButton(
#                             text="J'ai payé",
#                             icon=ft.icons.CHECK,
#                             on_click=lambda _: self.verifier_paiement_qr(remboursement, qr_data['payment_url'])
#                         )
#                     ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
#                     padding=50
#                 )
#             ])
#         else:
#             view = ft.Column([
#                 ft.Text("❌ Erreur génération QR Code", size=16),
#                 ft.Text(qr_data, size=14)
#             ])
#
#         self.page.clean()
#         self.page.add(view)
#
#     def lancer_moncash(self, remboursement):
#         """Ouvre l'application MonCash"""
#         # En production, utiliser les deep links
#         self.page.show_snack_bar(ft.SnackBar(content=ft.Text("Ouverture de MonCash...")))
#
#     def envoyer_demande_natcash(self, remboursement):
#         """Envoie une demande de paiement NatCash"""
#         telephone = "509XXXXXXXX"  # Récupérer depuis le champ
#         success, result = payment_gateway.initier_paiement_natcash(
#             remboursement['montant'],
#             telephone,
#             f"Remboursement prêt GMES #{remboursement['pret_id']}"
#         )
#
#         if success:
#             self.page.show_snack_bar(ft.SnackBar(content=ft.Text("✅ Demande envoyée à NatCash!")))
#             self.monitor_payment_status('natcash', result['transaction_id'], remboursement)
#         else:
#             self.show_error(f"Erreur NatCash: {result}")
#
#     def monitor_payment_status(self, gateway, transaction_id, remboursement):
#         """Surveille le statut du paiement"""
#         import threading
#         import time
#
#         def check_status():
#             for i in range(30):  # Vérifier pendant 5 minutes
#                 time.sleep(10)  # Toutes les 10 secondes
#
#                 success, status = payment_gateway.verifier_statut_paiement(gateway, transaction_id)
#
#                 if success and status == 'completed':
#                     # Paiement réussi
#                     self.page.show_snack_bar(ft.SnackBar(content=ft.Text("✅ Paiement confirmé!")))
#                     self.enregistrer_paiement_reussi(remboursement, gateway, transaction_id)
#                     break
#                 elif success and status == 'failed':
#                     self.page.show_snack_bar(ft.SnackBar(content=ft.Text("❌ Paiement échoué")))
#                     break
#
#         thread = threading.Thread(target=check_status)
#         thread.daemon = True
#         thread.start()
#
#     def enregistrer_paiement_reussi(self, remboursement, gateway, transaction_id):
#         """Enregistre un paiement réussi"""
#         try:
#             headers = {"Authorization": f"Bearer {self.token}"}
#             response = requests.post(f"{self.api_base_url}/remboursement/payer", headers=headers, json={
#                 "pret_id": remboursement["pret_id"],
#                 "montant": remboursement["montant"],
#                 "methode": gateway,
#                 "transaction_id": transaction_id,
#                 "statut": "paye"
#             })
#
#             if response.status_code == 200:
#                 self.page.show_snack_bar(ft.SnackBar(content=ft.Text("Paiement enregistré avec succès!")))
#                 time.sleep(2)
#                 self.show_dashboard()
#             else:
#                 self.show_error("Erreur enregistrement paiement")
#
#         except Exception as e:
#             self.show_error(f"Erreur: {str(e)}")
#
#
# # Lancement de l'application
# def main():
#     app = GMESMobileApp()
#     ft.app(target=app.main)
#
#
# if __name__ == "__main__":
#     main()

import flet as ft
import requests
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.auth import  auth_bp

app = FastAPI(title="GMES API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

@app.get("/")
def root():
    return {"message": "GMES API en ligne ✅"}


class GMESMobileApp:
    def __init__(self):
        self.api_base_url = "http://localhost:5000"
        self.token = None
        self.current_user = None

    def main(self, page: ft.Page):
        page.title = "GMES Microcrédit"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 20
        page.scroll = ft.ScrollMode.ADAPTIVE

        self.page = page
        self.show_login_view()

    def show_login_view(self):
        """Vue de connexion"""
        self.email_field = ft.TextField(
            label="Email ou Numéro de compte",
            prefix_icon=ft.icons.EMAIL,
            width=300
        )

        self.password_field = ft.TextField(
            label="Mot de passe",
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.icons.LOCK,
            width=300
        )

        login_button = ft.ElevatedButton(
            text="Se connecter",
            icon=ft.icons.LOGIN,
            on_click=self.login,
            width=300
        )

        register_button = ft.TextButton(
            text="Créer un compte",
            on_click=lambda e: self.show_register_view()
        )

        login_view = ft.Column(
            [
                ft.Container(
                    content=ft.Text("GMES", size=24, weight=ft.FontWeight.BOLD),
                    alignment=ft.alignment.center
                ),
                ft.Text("Microcrédit Solidaire", size=16),
                ft.Divider(),
                self.email_field,
                self.password_field,
                login_button,
                register_button
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )

        self.page.clean()
        self.page.add(login_view)
        self.page.update()

    def show_register_view(self, e=None):
        """Vue d'inscription"""
        self.nom_field = ft.TextField(label="Nom", width=300)
        self.prenom_field = ft.TextField(label="Prénom", width=300)
        self.telephone_field = ft.TextField(label="Téléphone", width=300)
        self.email_register_field = ft.TextField(label="Email", width=300)
        self.password_register_field = ft.TextField(label="Mot de passe", password=True, width=300)

        register_view = ft.Column(
            [
                ft.IconButton(
                    icon=ft.icons.ARROW_BACK,
                    on_click=lambda e: self.show_login_view()
                ),
                ft.Text("Créer un compte", size=20, weight=ft.FontWeight.BOLD),
                self.nom_field,
                self.prenom_field,
                self.telephone_field,
                self.email_register_field,
                self.password_register_field,
                ft.ElevatedButton(
                    text="S'inscrire",
                    on_click=self.handle_register,
                    width=300
                )
            ]
        )

        self.page.clean()
        self.page.add(register_view)
        self.page.update()

    def handle_register(self, e):
        """Gère l'inscription"""
        try:
            if not all([
                self.nom_field.value,
                self.prenom_field.value,
                self.telephone_field.value,
                self.email_register_field.value,
                self.password_register_field.value
            ]):
                self.show_error("Veuillez remplir tous les champs")
                return

            response = requests.post(
                f"{self.api_base_url}/api/mobile/register",
                json={
                    "first_name": self.prenom_field.value,
                    "last_name": self.nom_field.value,
                    "phone": self.telephone_field.value,
                    "email": self.email_register_field.value,
                    "password": self.password_register_field.value
                }
            )

            data = response.json()

            if data.get('success'):
                self.show_success("Compte créé avec succès!")
                import time
                time.sleep(2)
                self.show_login_view()
            else:
                self.show_error(data.get('error', 'Erreur lors de la création du compte'))

        except Exception as ex:
            self.show_error(f"Erreur: {str(ex)}")

    def login(self, e):
        try:
            import socket
            # Test de connexion basique
            print("🔍 Test de connexion réseau...")
            try:
                socket.create_connection(("localhost", 5000), timeout=5)
                print("✅ Serveur accessible")
            except:
                print("❌ Serveur inaccessible")
                self.show_error("Serveur indisponible")
                return

            url = f"{self.api_base_url}/api/mobile/login"
            print(f"🎯 URL finale: {url}")

            # Test avec une requête HTTP simple
            import urllib.request
            try:
                response = urllib.request.urlopen(f"{self.api_base_url}/")
                print(f"✅ Test HTTP réussi: {response.status}")
            except Exception as e:
                print(f"❌ Test HTTP échoué: {e}")
                self.show_error(f"Connexion impossible: {e}")
                return

            # Votre requête normale
            print("🔄 Envoi requête login...")
            response = requests.post(url, json={
                "identifier": self.email_field.value,
                "password": self.password_field.value,
                "user_type": "client"
            }, timeout=10)

            print(f"📡 Statut: {response.status_code}")
            print(f"📦 Réponse: {response.text}")

            # ... reste du code

        except Exception as ex:
            print(f"💥 ERREUR COMPLÈTE: {ex}")
            import traceback
            traceback.print_exc()
            self.show_error(f"Erreur: {str(ex)}")

    def show_dashboard(self, e=None):
        """Tableau de bord principal"""
        user_info = self.current_user or {'first_name': 'Utilisateur', 'last_name': '', 'email': ''}

        header = ft.Container(
            content=ft.Row([
                ft.CircleAvatar(
                    content=ft.Text(user_info.get('first_name', 'U')[0].upper()),
                    bgcolor=ft.colors.BLUE
                ),
                ft.Column([
                    ft.Text(f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}",
                            weight=ft.FontWeight.BOLD),
                    ft.Text(user_info.get('email', ''), size=12)
                ])
            ]),
            padding=10
        )

        stats_cards = ft.Row([
            self.create_stat_card("💰", "Solde", "5,000 HTG", ft.colors.GREEN),
            self.create_stat_card("📊", "Prêts", "2 Actifs", ft.colors.BLUE),
            self.create_stat_card("⏰", "Prochain", "15/12/2024", ft.colors.ORANGE),
        ])

        menu_grid = ft.GridView(
            runs_count=2,
            max_extent=150,
            child_aspect_ratio=1.0,
            spacing=10,
            run_spacing=10,
            controls=[
                self.create_menu_card("📋", "Mes Prêts", self.show_my_loans),
                self.create_menu_card("💳", "Rembourser", self.show_payment),
                self.create_menu_card("👥", "Mon Groupe", self.show_my_group),
                self.create_menu_card("📊", "Statistiques", self.show_stats),
                self.create_menu_card("🔔", "Notifications", self.show_notifications),
                self.create_menu_card("⚙️", "Paramètres", self.show_settings),
            ]
        )

        dashboard = ft.Column([
            header,
            stats_cards,
            ft.Divider(),
            ft.Text("Actions rapides", weight=ft.FontWeight.BOLD),
            menu_grid
        ])

        self.page.clean()
        self.page.add(dashboard)
        self.page.update()

    def create_stat_card(self, icon, title, value, color):
        return ft.Container(
            content=ft.Column([
                ft.Text(icon, size=20),
                ft.Text(value, size=16, weight=ft.FontWeight.BOLD),
                ft.Text(title, size=12)
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            width=100,
            height=80,
            bgcolor=f"{color}50",
            border_radius=10,
            padding=10
        )

    def create_menu_card(self, icon, title, on_click):
        return ft.GestureDetector(
            on_tap=on_click,
            content=ft.Container(
                content=ft.Column([
                    ft.Text(icon, size=24),
                    ft.Text(title, size=12, text_align=ft.TextAlign.CENTER)
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=ft.colors.BLUE_50,
                border_radius=10,
                padding=15
            )
        )

    def show_my_loans(self, e=None):
        view = ft.Column([
            ft.Row([ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda e: self.show_dashboard()),
                    ft.Text("Mes Prêts", size=20, weight=ft.FontWeight.BOLD)]),
            ft.Text("Gestion des prêts", size=16),
        ])
        self.page.clean()
        self.page.add(view)
        self.page.update()

    def show_payment(self, e=None):
        view = ft.Column([
            ft.Row([ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda e: self.show_dashboard()),
                    ft.Text("Paiement", size=20, weight=ft.FontWeight.BOLD)]),
            ft.Text("Fonctionnalité de paiement", size=16),
        ])
        self.page.clean()
        self.page.add(view)
        self.page.update()

    def show_my_group(self, e=None):
        view = ft.Column([
            ft.Row([ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda e: self.show_dashboard()),
                    ft.Text("Mon Groupe", size=20, weight=ft.FontWeight.BOLD)]),
            ft.Text("Gestion de groupe", size=16),
        ])
        self.page.clean()
        self.page.add(view)
        self.page.update()

    def show_stats(self, e=None):
        view = ft.Column([
            ft.Row([ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda e: self.show_dashboard()),
                    ft.Text("Statistiques", size=20, weight=ft.FontWeight.BOLD)]),
            ft.Text("Statistiques personnelles", size=16),
        ])
        self.page.clean()
        self.page.add(view)
        self.page.update()

    def show_notifications(self, e=None):
        view = ft.Column([
            ft.Row([ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda e: self.show_dashboard()),
                    ft.Text("Notifications", size=20, weight=ft.FontWeight.BOLD)]),
            ft.Text("Liste des notifications", size=16),
        ])
        self.page.clean()
        self.page.add(view)
        self.page.update()

    def show_settings(self, e=None):
        view = ft.Column([
            ft.Row([ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda e: self.show_dashboard()),
                    ft.Text("Paramètres", size=20, weight=ft.FontWeight.BOLD)]),
            ft.ElevatedButton("Déconnexion", on_click=self.logout)
        ])
        self.page.clean()
        self.page.add(view)
        self.page.update()

    def logout(self, e):
        self.token = None
        self.current_user = None
        self.show_login_view()

    def show_success(self, message):
        self.page.snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor=ft.colors.GREEN)
        self.page.snack_bar.open = True
        self.page.update()

    def show_error(self, message):
        self.page.snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor=ft.colors.RED)
        self.page.snack_bar.open = True
        self.page.update()


def main():
    ft.app(target=GMESMobileApp().main)


if __name__ == "__main__":
    main()