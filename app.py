from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from utils.notifications import notification_manager
import os
from dotenv import load_dotenv
from routes.auth import auth_bp  # ✅ Import corrigé

# Importer et enregistrer le blueprint auth
load_dotenv()  # Charge les variables d'environnement


# Configuration de l'application
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'gmes-microcredit-2024')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gmes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Enregistre le Blueprint
app.register_blueprint(auth_bp, url_prefix="/auth")

# Initialisation des extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'connexion'


# ==================== MODÈLES COMPLETS ====================

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    # Champs communs à tous les utilisateurs
    username = db.Column(db.String(80), unique=True, nullable=True)
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(255))
    role = db.Column(db.String(20), default='client')  # client, employe, admin
    nom = db.Column(db.String(100))
    prenom = db.Column(db.String(100))
    telephone = db.Column(db.String(20))
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

    # Champs spécifiques aux clients
    code_client = db.Column(db.String(20), unique=True, nullable=True)
    adresse = db.Column(db.Text)
    cin = db.Column(db.String(50), unique=True, nullable=True)
    date_naissance = db.Column(db.DateTime, nullable=True)
    profession = db.Column(db.String(100))
    revenu_mensuel = db.Column(db.Float, default=0)
    date_inscription = db.Column(db.DateTime, default=datetime.utcnow)
    statut = db.Column(db.String(20), default='actif')
    groupe_id = db.Column(db.Integer, db.ForeignKey('groupes.id'), nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def est_client(self):
        return self.role == 'client'

    @property
    def est_employe(self):
        return self.role == 'employe'

    @property
    def est_admin(self):
        return self.role == 'admin'

    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}".strip()

class Groupe(db.Model):
    __tablename__ = 'groupes'

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100))
    code_groupe = db.Column(db.String(20), unique=True)
    zone = db.Column(db.String(100))
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    statut = db.Column(db.String(20), default='actif')


class Pret(db.Model):
    __tablename__ = 'prets'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer)
    groupe_id = db.Column(db.Integer)
    montant = db.Column(db.Float)
    taux_interet = db.Column(db.Float, default=12.0)
    duree_mois = db.Column(db.Integer)
    date_demande = db.Column(db.DateTime, default=datetime.utcnow)
    date_approbation = db.Column(db.DateTime)
    date_decaissement = db.Column(db.DateTime)
    statut = db.Column(db.String(20), default='en_attente')
    motif = db.Column(db.String(100))
    montant_interet = db.Column(db.Float)
    montant_total = db.Column(db.Float)
    mensualite = db.Column(db.Float)


class Remboursement(db.Model):
    __tablename__ = 'remboursements'

    id = db.Column(db.Integer, primary_key=True)
    pret_id = db.Column(db.Integer)
    client_id = db.Column(db.Integer)
    montant = db.Column(db.Float)
    date_remboursement = db.Column(db.DateTime, default=datetime.utcnow)
    date_echeance = db.Column(db.DateTime)
    statut = db.Column(db.String(20), default='paye')
    type_paiement = db.Column(db.String(20))
    reference = db.Column(db.String(100))


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    utilisateur_id = db.Column(db.Integer)
    titre = db.Column(db.String(200))
    message = db.Column(db.Text)
    type_notification = db.Column(db.String(50))
    lue = db.Column(db.Boolean, default=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    lien = db.Column(db.String(500))


class NotificationManager:
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.sms_api_key = os.getenv('SMS_API_KEY')
        self.sms_api_secret = os.getenv('SMS_API_SECRET')

    def notifier_remboursement_reussi(self, user, remboursement):
        """Notification pour remboursement réussi"""
        pret = Pret.query.get(remboursement.pret_id)

        message = f"""
        ✅ Remboursement confirmé !

        Cher(e) {user.prenom} {user.nom},

        Votre remboursement de {remboursement.montant:.2f} € a été enregistré avec succès.

        📋 Détails :
        - Prêt : {pret.motif if pret else 'N/A'}
        - Référence : {remboursement.reference}
        - Date : {remboursement.date_remboursement.strftime('%d/%m/%Y %H:%M')}
        - Méthode : {remboursement.type_paiement}

        Merci pour votre ponctualité !
        L'équipe GMES Microcrédit
        """

        print(f"📧 Notification: {user.nom_complet} a effectué un remboursement de {remboursement.montant} €")

        # Envoyer les notifications
        self._envoyer_notification_db(user, "Remboursement confirmé", message, 'success')
        self._envoyer_email(user, "✅ Remboursement confirmé - GMES", message)
        self._envoyer_sms(user, f"GMES: Remboursement de {remboursement.montant} € confirmé. Merci!")

    def notifier_approbation_pret(self, user, pret):
        """Notification pour approbation de prêt"""
        message = f"""
        🎉 Félicitations ! Votre prêt est approuvé.

        Cher(e) {user.prenom} {user.nom},

        Votre demande de prêt a été approuvée.

        📋 Détails du prêt :
        - Montant : {pret.montant:.2f} €
        - Durée : {pret.duree_mois} mois
        - Mensualité : {pret.mensualite:.2f} €
        - Motif : {pret.motif}

        Les fonds seront disponibles sous 24-48h.

        L'équipe GMES Microcrédit
        """

        self._envoyer_notification_db(user, "Prêt approuvé", message, 'success')
        self._envoyer_email(user, "🎉 Prêt approuvé - GMES", message)
        self._envoyer_sms(user, f"GMES: Prêt de {pret.montant} € approuvé!")

    def notifier_rejet_pret(self, user, pret, motif):
        """Notification pour rejet de prêt"""
        message = f"""
        ❌ Statut de votre demande de prêt

        Cher(e) {user.prenom} {user.nom},

        Votre demande de prêt a été rejetée.

        📋 Détails :
        - Motif : {motif}
        - Montant demandé : {pret.montant:.2f} €

        Nous vous encourageons à :
        • Améliorer votre score de crédit
        • Revoir votre capacité de remboursement
        • Soumettre une nouvelle demande ultérieurement

        L'équipe GMES Microcrédit
        """

        self._envoyer_notification_db(user, "Prêt rejeté", message, 'warning')
        self._envoyer_email(user, "❌ Statut de votre prêt - GMES", message)
        self._envoyer_sms(user, f"GMES: Prêt rejeté. Consultez votre email pour plus de détails.")

    def notifier_rappel_remboursement(self, user, pret, jours_restants):
        """Rappel de remboursement"""
        message = f"""
        ⏰ Rappel de remboursement

        Cher(e) {user.prenom} {user.nom},

        Votre prochaine échéance de remboursement approche !

        📋 Détails :
        - Prêt : {pret.motif}
        - Mensualité : {pret.mensualite:.2f} €
        - Jours restants : {jours_restants}

        Pensez à effectuer votre paiement à temps pour éviter les pénalités.

        L'équipe GMES Microcrédit
        """

        self._envoyer_notification_db(user, f"Rappel: {jours_restants} jours", message, 'info')
        self._envoyer_email(user, f"⏰ Rappel de remboursement - {jours_restants} jours", message)
        if jours_restants <= 2:  # SMS seulement si très proche
            self._envoyer_sms(user, f"RAPPEL GMES: {pret.mensualite:.2f} € dans {jours_restants} jour(s)")

    def notifier_nouveau_groupe(self, user, groupe):
        """Notification pour nouveau groupe"""
        message = f"""
        👥 Bienvenue dans votre nouveau groupe !

        Cher(e) {user.prenom} {user.nom},

        Vous avez rejoint le groupe : {groupe.nom}

        📋 Informations du groupe :
        - Code : {groupe.code_groupe}
        - Zone : {groupe.zone}
        - Coordinateur : {groupe.coordinateur.nom_complet if groupe.coordinateur else 'À désigner'}

        Participez activement aux réunions et bénéficiez de la solidarité du groupe !

        L'équipe GMES Microcrédit
        """

        self._envoyer_notification_db(user, "Nouveau groupe", message, 'info')
        self._envoyer_email(user, "👥 Bienvenue dans votre groupe - GMES", message)

    def _envoyer_notification_db(self, user, titre, message, type_notif):
        """Enregistre la notification en base de données"""
        try:
            notification = Notification(
                utilisateur_id=user.id,
                titre=titre,
                message=message,
                type_notification=type_notif,
                lien='/notifications'
            )
            db.session.add(notification)
            db.session.commit()
        except Exception as e:
            print(f"Erreur notification DB: {e}")

    def _envoyer_email(self, user, sujet, message):
        """Envoie un email (simulé pour l'instant)"""
        try:
            if self.smtp_username and self.smtp_password:
                # Ici vous intégreriez votre service d'email
                print(f"📧 Email envoyé à {user.email}: {sujet}")
            else:
                print(f"📧 [SIMULATION] Email à {user.email}: {sujet}")
        except Exception as e:
            print(f"Erreur email: {e}")

    def _envoyer_sms(self, user, message):
        """Envoie un SMS (simulé pour l'instant)"""
        try:
            if self.sms_api_key and user.telephone:
                # Ici vous intégreriez votre service SMS
                print(f"📱 SMS envoyé à {user.telephone}: {message}")
            else:
                print(f"📱 [SIMULATION] SMS à {user.telephone}: {message}")
        except Exception as e:
            print(f"Erreur SMS: {e}")

    def notifier_retard_remboursement(self, user, pret, jours_retard):
        """Notification pour retard de remboursement"""
        message = f"""
        ⚠️ Retard de remboursement

        Cher(e) {user.prenom} {user.nom},

        Votre remboursement est en retard de {jours_retard} jour(s).

        📋 Détails :
        - Prêt : {pret.motif}
        - Mensualité : {pret.mensualite:.2f} €
        - Jours de retard : {jours_retard}

        Veuillez régulariser votre situation au plus vite pour éviter :
        • Des pénalités de retard
        • Une affectation de votre score de crédit
        • Des restrictions futures

        L'équipe GMES Microcrédit
        """

        self._envoyer_notification_db(user, f"Retard: {jours_retard} jour(s)", message, 'warning')
        self._envoyer_email(user, f"⚠️ Retard de remboursement - {jours_retard} jour(s)", message)
        self._envoyer_sms(user, f"RETARD GMES: {jours_retard} jour(s). {pret.mensualite:.2f} €")


notification_manager = NotificationManager()




def obtenir_actions_utilisateur(user_id):
    """Récupère les actions d'un utilisateur pour la gamification"""
    # Simulation - à remplacer par votre logique réelle
    actions = [
        {'type': 'remboursement_ponctuel', 'description': 'Remboursement à temps'},
        {'type': 'pret_rembourse', 'description': 'Prêt complètement remboursé'},
        {'type': 'participation_groupe', 'description': 'Participation active au groupe'}
    ]
    return actions

def calculer_historique_client(client_id):
    """Calcule l'historique d'un client pour le scoring"""
    # Simulation - à remplacer par votre logique réelle
    return {
        'nombre_prets': Pret.query.filter_by(client_id=client_id).count(),
        'prets_rembourses': Pret.query.filter_by(client_id=client_id, statut='termine').count(),
        'taux_remboursement': 85,  # À calculer dynamiquement
        'jours_retard_moyen': 2,
        'incidents_paiement': 0
    }


def calculer_statistiques_utilisateur(user):
    """Calcule les stats pour le tableau de bord"""
    from utils.ai_scoring import ai_scorer
    from utils.gamification import gamification

    stats = {}

    # Vérifier si c'est un Client (avec groupe_id) ou User (admin/employé)
    if hasattr(user, 'groupe_id'):  # C'est un Client
        # Score de crédit IA seulement pour les clients
        client_data = {
            'revenu_mensuel': getattr(user, 'revenu_mensuel', 0),
            'anciennete_client': (datetime.utcnow() - user.date_inscription).days // 30,
            'profession': getattr(user, 'profession', 'Non spécifié')
        }
        historique = calculer_historique_client(user.id)
        score = ai_scorer.calculate_credit_score(client_data, {}, historique)

        stats['score_credit'] = score
        stats['score_categorie'] = 'excellent' if score >= 750 else 'good' if score >= 650 else 'fair'
        stats['score_label'] = ai_scorer.explain_score(client_data, {}, historique)

        # Gamification seulement pour les clients
        user_actions = obtenir_actions_utilisateur(user.id)
        points = gamification.calculate_points(user_actions)
        niveau_info = gamification.get_level_progress(points)

        stats.update({
            'niveau': niveau_info['current_level'],
            'points': points,
            'progression': niveau_info['progress'],
            'badge': niveau_info['current_badge']
        })

        # Groupe seulement pour les clients
        if user.groupe_id:
            groupe = Groupe.query.get(user.groupe_id)
            stats.update({
                'groupe_nom': groupe.nom if groupe else None,
                'groupe_membres': User.query.filter_by(groupe_id=user.groupe_id).count() if user.groupe_id else 0,
            })

    # Statistiques communes à tous les utilisateurs - CORRECTIONS ICI
    stats.update({
        'prets_actifs': Pret.query.filter(
            Pret.client_id == user.id,
            Pret.statut == 'approuve'
        ).count() if hasattr(user, 'groupe_id') else 0,

        'montant_actifs': db.session.query(db.func.sum(Pret.montant)).filter(
            Pret.client_id == user.id,
            Pret.statut == 'approuve'
        ).scalar() or 0 if hasattr(user, 'groupe_id') else 0,

        'notifications_non_lues': Notification.query.filter_by(utilisateur_id=user.id, lue=False).count() if hasattr(
            Notification, 'query') else 0
    })

    return stats
# ==================== CONFIGURATION USER LOADER ====================

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # ✅ Plus simple !



# @app.route("/")
# def index():
#     return {"message": "✅ API GMES en ligne et fonctionnelle"}

@app.route("/")
def index():
    return render_template('accueil.html')

# ==================== INITIALISATION ====================

def initialiser_donnees():
    """Initialise la base de données avec des données de test"""
    try:
        print("🗃️ Création des tables...")
        db.create_all()

        print("👤 Création des comptes...")

        # Créer l'admin
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@gmes.com',
                role='admin',  # ← Type défini ici
                nom='Admin',
                prenom='System',
                telephone='+50900000000'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            print("✅ Admin créé: admin / admin123")

        # Créer un employé
        if not User.query.filter_by(username='employe').first():
            employe = User(
                username='employe',
                email='employe@gmes.com',
                role='employe',  # ← Type défini ici
                nom='Pierre',
                prenom='Jean',
                telephone='+50912345678'
            )
            employe.set_password('employe123')
            db.session.add(employe)
            print("✅ Employé créé: employe / employe123")

        # Créer un groupe
        if not Groupe.query.first():
            groupe = Groupe(
                nom="Femmes Entrepreneures",
                code_groupe="GRP001",
                zone="Port-au-Prince"
            )
            db.session.add(groupe)
            print("✅ Groupe créé")

        # Créer un client
        if not User.query.filter_by(email='client@example.com').first():
            client = User(
                code_client="CLT001",
                nom="Dupont",
                prenom="Marie",
                telephone="+50912345670",
                email="client@example.com",
                adresse="Port-au-Prince",
                cin="1234567890",
                date_naissance=datetime(1985, 5, 15),
                profession="Commerçante",
                revenu_mensuel=15000,
                groupe_id=1
            )
            client.set_password("client123")
            db.session.add(client)
            print("✅ Client créé: client@example.com / client123")

        db.session.commit()
        print("🎉 Données initialisées avec succès!")
        return True

    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation: {e}")
        import traceback
        traceback.print_exc()
        return False
# Initialiser les données au démarrage
with app.app_context():
    initialiser_donnees()


# ==================== ROUTES ====================

@app.route('/')
def accueil():
    return render_template('accueil.html')


@app.route('/connexion', methods=['GET', 'POST'])
def connexion():
    if request.method == 'POST':
        identifiant = request.form.get('identifiant')
        mot_de_passe = request.form.get('password')
        print(f"🔐 Tentative de connexion: {identifiant}")

        # ✅ RECHERCHE UNIFIÉE - Trouve tout le monde dans la même table User
        user = User.query.filter(
            (User.username == identifiant) | (User.email == identifiant)
        ).first()

        # Vérifier le mot de passe
        if user and user.check_password(mot_de_passe):
            login_user(user)

            # ✅ DÉTERMINER AUTOMATIQUEMENT L'INTERFACE (avec la classe unifiée)
            if user.role == 'admin':
                print("🎯 Redirection vers interface Admin")
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'employe':
                print("🎯 Redirection vers interface Employé")
                return redirect(url_for('employe_dashboard'))
            else:  # client
                print("🎯 Redirection vers interface Client")
                return redirect(url_for('client_dashboard'))

        return render_template('connexion.html', erreur="Identifiant ou mot de passe incorrect")

    return render_template('connexion.html')

@app.route('/deconnexion')
def deconnexion():
    logout_user()
    return redirect(url_for('accueil'))



@app.route('/test')
def test():
    return jsonify({
        'status': 'GMES Microcrédit - Système Opérationnel',
        'message': 'Tout fonctionne correctement!'
    })


# ==================== SYSTÈME DE REMBOURSEMENTS ====================

@app.route('/remboursement/nouveau', methods=['GET', 'POST'])
@login_required
def nouveau_remboursement():
    if request.method == 'POST':
        # Récupérer les données du formulaire
        pret_id = request.form.get('pret_id')
        montant = float(request.form.get('montant'))
        type_paiement = request.form.get('type_paiement')
        reference = request.form.get('reference')

        # Vérifier que le prêt appartient à l'utilisateur
        pret = Pret.query.filter_by(id=pret_id, client_id=current_user.id).first()
        if not pret:
            return render_template('nouveau_remboursement.html',
                                   error="Prêt non trouvé ou non autorisé",
                                   prets=Pret.query.filter_by(client_id=current_user.id, statut='approuve').all())

        # Vérifier que le montant est valide
        if montant <= 0:
            return render_template('nouveau_remboursement.html',
                                   error="Montant invalide",
                                   prets=Pret.query.filter_by(client_id=current_user.id, statut='approuve').all())

        # Calculer la date d'échéance (prochaine échéance)
        date_echeance = datetime.utcnow().replace(day=1)
        if date_echeance.month == 12:
            date_echeance = date_echeance.replace(year=date_echeance.year + 1, month=1)
        else:
            date_echeance = date_echeance.replace(month=date_echeance.month + 1)

        # Créer le remboursement
        remboursement = Remboursement(
            pret_id=pret_id,
            client_id=current_user.id,
            montant=montant,
            date_echeance=date_echeance,
            type_paiement=type_paiement,
            reference=reference,
            statut='paye'
        )

        db.session.add(remboursement)
        db.session.commit()

        # 🔔 NOTIFICATION de remboursement réussi
        try:
            notification_manager.notifier_remboursement_reussi(current_user, remboursement)
        except Exception as e:
            print(f"Erreur notification: {e}")

        return redirect(url_for('mes_remboursements'))

    # GET - Afficher le formulaire
    prets = Pret.query.filter_by(client_id=current_user.id, statut='approuve').all()

    # Préparer les données pour le template
    prets_avec_solde = []
    for pret in prets:
        # Calculer le solde restant
        total_rembourse = db.session.query(db.func.sum(Remboursement.montant)).filter_by(
            pret_id=pret.id, statut='paye'
        ).scalar() or 0
        solde_restant = pret.montant_total - total_rembourse

        prets_avec_solde.append({
            'pret': pret,
            'solde_restant': solde_restant,
            'prochaine_echeance': datetime.utcnow().replace(day=1)  # Simplifié
        })

    return render_template('nouveau_remboursement.html', prets=prets_avec_solde)



@app.route('/mes-remboursements')
@login_required
def mes_remboursements():
    remboursements = Remboursement.query.filter_by(client_id=current_user.id).all()

    # Associer les remboursements avec les prêts
    remboursements_avec_prets = []
    for remb in remboursements:
        pret = Pret.query.get(remb.pret_id)
        remboursements_avec_prets.append({
            'remboursement': remb,
            'pret': pret
        })

    return render_template('mes_remboursements.html', remboursements_avec_prets=remboursements_avec_prets)


@app.route('/admin/notifications')
@login_required
def admin_notifications():
    if getattr(current_user, 'role', None) != 'admin':
        return redirect(url_for('tableau_de_bord'))

    config = {
        'SMTP_SERVER': os.getenv('SMTP_SERVER'),
        'SMTP_USERNAME': os.getenv('SMTP_USERNAME'),
        'SMS_API_KEY': os.getenv('SMS_API_KEY')
    }

    return render_template('admin_notifications.html', config=config)

@app.route('/admin/remboursements')
@login_required
def admin_remboursements():
    if getattr(current_user, 'role', None) != 'admin':
        return redirect(url_for('tableau_de_bord'))

    remboursements = Remboursement.query.all()

    # Associer avec clients et prêts
    remboursements_complets = []
    for remb in remboursements:
        pret = Pret.query.get(remb.pret_id)
        client = User.query.get(remb.client_id)  # ✅ CORRECTION: Utiliser User
        remboursements_complets.append({
            'remboursement': remb,
            'pret': pret,
            'client': client
        })

    return render_template('admin_remboursements.html', remboursements_complets=remboursements_complets)

@app.route('/api/calculer-echeancier/<int:pret_id>')
@login_required
def calculer_echeancier(pret_id):
    """Calcule l'échéancier d'un prêt"""
    pret = Pret.query.get_or_404(pret_id)

    # Vérifier que le prêt appartient au client
    if pret.client_id != current_user.id:
        return jsonify({'error': 'Accès non autorisé'})

    echeances = []
    montant_restant = pret.montant_total
    date_courante = datetime.utcnow()

    for i in range(pret.duree_mois):
        date_echeance = date_courante.replace(month=date_courante.month + i)
        echeances.append({
            'numero': i + 1,
            'date': date_echeance.strftime('%d/%m/%Y'),
            'montant': pret.mensualite,
            'capital': pret.mensualite * 0.8,  # Estimation
            'interet': pret.mensualite * 0.2  # Estimation
        })

    return jsonify({
        'pret': {
            'montant': pret.montant,
            'duree': pret.duree_mois,
            'mensualite': pret.mensualite,
            'total_a_rembourser': pret.montant_total
        },
        'echeances': echeances
    })


# ==================== GESTION DES GROUPES DE SOLIDARITÉ ====================

@app.route('/groupes')
@login_required
def liste_groupes():
    groupes = Groupe.query.all()
    return render_template('liste_groupes.html', groupes=groupes)


@app.route('/groupe/<int:groupe_id>')
@login_required
def detail_groupe(groupe_id):
    groupe = Groupe.query.get_or_404(groupe_id)
    clients = User.query.filter_by(groupe_id=groupe_id).all()
    prets_du_groupe = Pret.query.filter_by(groupe_id=groupe_id).all()

    # Calculer les statistiques du groupe
    stats = {
        'nombre_membres': len(clients),
        'prets_actifs': len([p for p in prets_du_groupe if p.statut == 'approuve']),
        'montant_total_prets': sum(p.montant for p in prets_du_groupe),
        'taux_remboursement': 95  # À calculer dynamiquement
    }

    return render_template('detail_groupe.html',
                           groupe=groupe,
                           clients=clients,
                           prets=prets_du_groupe,
                           stats=stats)


@app.route('/groupe/creer', methods=['GET', 'POST'])
@login_required
def creer_groupe():
    if getattr(current_user, 'role', None) not in ['admin', 'employe']:
        return redirect(url_for('tableau_de_bord'))

    if request.method == 'POST':
        nom = request.form.get('nom')
        zone = request.form.get('zone')

        # Générer un code de groupe unique
        code_groupe = f"GRP{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        groupe = Groupe(
            nom=nom,
            code_groupe=code_groupe,
            zone=zone
        )

        db.session.add(groupe)
        db.session.commit()

        return redirect(url_for('liste_groupes'))

    return render_template('creer_groupe.html')


@app.route('/groupe/<int:groupe_id>/rejoindre')
@login_required
def rejoindre_groupe(groupe_id):
    # ... code existant ...

    current_user.groupe_id = groupe_id
    db.session.commit()

    # 🔔 NOTIFICATION de nouveau groupe
    notification_manager.notifier_nouveau_groupe(current_user, groupe)

    return redirect(url_for('detail_groupe', groupe_id=groupe_id))


@app.route('/groupe/<int:groupe_id>/quitter')
@login_required
def quitter_groupe(groupe_id):
    # Seuls les clients peuvent quitter des groupes
    if hasattr(current_user, 'role'):
        return redirect(url_for('tableau_de_bord'))

    # Vérifier que le client est bien dans ce groupe
    if current_user.groupe_id != groupe_id:
        return redirect(url_for('tableau_de_bord'))

    current_user.groupe_id = None
    db.session.commit()

    return redirect(url_for('liste_groupes'))


@app.route('/groupe/<int:groupe_id>/demande-pret-solidaire', methods=['GET', 'POST'])
@login_required
def demande_pret_solidaire(groupe_id):
    # Vérifier que l'utilisateur est un client membre du groupe
    if hasattr(current_user, 'role') or current_user.groupe_id != groupe_id:
        return redirect(url_for('tableau_de_bord'))

    groupe = Groupe.query.get_or_404(groupe_id)

    if request.method == 'POST':
        montant = float(request.form.get('montant'))
        duree = int(request.form.get('duree'))
        motif = request.form.get('motif')

        # Calculs automatiques
        taux_mensuel = 12.0 / 100 / 12
        mensualite = montant * taux_mensuel * (1 + taux_mensuel) ** duree / ((1 + taux_mensuel) ** duree - 1)
        montant_interet = (mensualite * duree) - montant
        montant_total = mensualite * duree

        nouveau_pret = Pret(
            client_id=current_user.id,
            groupe_id=groupe_id,
            montant=montant,
            duree_mois=duree,
            motif=motif,
            mensualite=round(mensualite, 2),
            montant_interet=round(montant_interet, 2),
            montant_total=round(montant_total, 2),
            statut='en_attente_solidaire'  # Statut spécial pour prêts solidaires
        )

        db.session.add(nouveau_pret)
        db.session.commit()

        return redirect(url_for('detail_groupe', groupe_id=groupe_id))

    return render_template('demande_pret_solidaire.html', groupe=groupe)


@app.route('/api/statistiques-groupes')
@login_required
def statistiques_groupes():
    if getattr(current_user, 'role', None) != 'admin':
        return jsonify({'error': 'Accès non autorisé'})

    groupes = Groupe.query.all()
    statistiques = []

    for groupe in groupes:
        clients = User.query.filter_by(groupe_id=groupe.id).all()
        prets = Pret.query.filter_by(groupe_id=groupe.id).all()

        stats = {
            'groupe_id': groupe.id,
            'nom_groupe': groupe.nom,
            'nombre_membres': len(clients),
            'prets_actifs': len([p for p in prets if p.statut == 'approuve']),
            'montant_total_prets': sum(p.montant for p in prets),
            'zone': groupe.zone
        }
        statistiques.append(stats)

    return jsonify(statistiques)


# ==================== RAPPORTS ET STATISTIQUES ====================

@app.route('/admin/rapports')
@login_required
def admin_rapports():
    if getattr(current_user, 'role', None) != 'admin':
        return redirect(url_for('tableau_de_bord'))

    # Calculer les statistiques globales
    stats = calculer_statistiques_globales()

    return render_template('admin_rapports.html', stats=stats)


@app.route('/admin/rapport-prets')
@login_required
def rapport_prets():
    if getattr(current_user, 'role', None) != 'admin':
        return redirect(url_for('tableau_de_bord'))

    # Filtres
    date_debut = request.args.get('date_debut')
    date_fin = request.args.get('date_fin')
    statut = request.args.get('statut')

    # Requête de base
    query = Pret.query

    # Appliquer les filtres
    if date_debut:
        query = query.filter(Pret.date_demande >= datetime.strptime(date_debut, '%Y-%m-%d'))
    if date_fin:
        query = query.filter(Pret.date_demande <= datetime.strptime(date_fin, '%Y-%m-%d'))
    if statut:
        query = query.filter(Pret.statut == statut)

    prets = query.all()

    # Préparer les données pour le rapport
    prets_rapport = []
    for pret in prets:
        client = User.query.get(pret.client_id)
        prets_rapport.append({
            'pret': pret,
            'client': client
        })

    return render_template('rapport_prets.html',
                           prets_rapport=prets_rapport,
                           filters={'date_debut': date_debut, 'date_fin': date_fin, 'statut': statut})


@app.route('/admin/rapport-remboursements')
@login_required
def rapport_remboursements():
    if getattr(current_user, 'role', None) != 'admin':
        return redirect(url_for('tableau_de_bord'))

    # Filtres
    date_debut = request.args.get('date_debut')
    date_fin = request.args.get('date_fin')

    query = Remboursement.query

    if date_debut:
        query = query.filter(Remboursement.date_remboursement >= datetime.strptime(date_debut, '%Y-%m-%d'))
    if date_fin:
        query = query.filter(Remboursement.date_remboursement <= datetime.strptime(date_fin, '%Y-%m-%d'))

    remboursements = query.all()

    # Préparer les données
    remboursements_rapport = []
    for remb in remboursements:
        pret = Pret.query.get(remb.pret_id)
        client = User.query.get(remb.client_id)
        remboursements_rapport.append({
            'remboursement': remb,
            'pret': pret,
            'client': client
        })

    return render_template('rapport_remboursements.html',
                           remboursements_rapport=remboursements_rapport,
                           filters={'date_debut': date_debut, 'date_fin': date_fin})


@app.route('/api/statistiques-temps-reel')
@login_required
def statistiques_temps_reel():
    if getattr(current_user, 'role', None) != 'admin':
        return jsonify({'error': 'Accès non autorisé'})

    stats = calculer_statistiques_globales()
    return jsonify(stats)




@app.before_request
def list_routes():
    if not hasattr(app, 'routes_listed'):
        print("=== ROUTES DISPONIBLES ===")
        for rule in app.url_map.iter_rules():
            print(f"{rule.rule} -> {rule.endpoint}")
        print("==========================")
        app.routes_listed = True

@app.route('/test-mobile-routes')
def test_mobile_routes():
    routes = []
    for rule in app.url_map.iter_rules():
        if 'mobile' in str(rule.rule):
            routes.append(f"{rule.rule} -> {rule.endpoint}")
    return "<br>".join(routes) if routes else "Aucune route mobile trouvée"




@app.route('/admin/export-prets-excel')
@login_required
def export_prets_excel():
    if getattr(current_user, 'role', None) != 'admin':
        return redirect(url_for('tableau_de_bord'))

    prets = Pret.query.all()

    # Créer un DataFrame (simulé)
    data = []
    for pret in prets:
        client = User.query.get(pret.client_id)
        data.append({
            'ID Prêt': pret.id,
            'Client': f"{client.prenom} {client.nom}" if client else "N/A",
            'Montant': pret.montant,
            'Durée (mois)': pret.duree_mois,
            'Mensualité': pret.mensualite,
            'Statut': pret.statut,
            'Date Demande': pret.date_demande.strftime('%d/%m/%Y'),
            'Motif': pret.motif
        })

    # Pour l'instant, retourner un JSON (implémentez l'export Excel plus tard)
    return jsonify({
        'message': 'Export Excel des prêts',
        'nombre_prets': len(data),
        'data': data
    })


@app.route('/cron/rappels-quotidiens')
def rappels_quotidiens():
    """
    Route pour les rappels automatiques (à appeler via cron job)
    """
    try:
        # Prêts avec remboursements en retard
        prets_actifs = Pret.query.filter_by(statut='approuve').all()

        for pret in prets_actifs:
            client = User.query.get(pret.client_id)

            # Calculer les jours jusqu'à la prochaine échéance
            # (simplifié pour l'exemple)
            jours_restants = 5  # À calculer dynamiquement

            if jours_restants <= 3:  # Rappel 3 jours avant
                notification_manager.notifier_rappel_remboursement(
                    client, pret, jours_restants
                )

        return jsonify({
            'status': 'success',
            'message': f'Rappels envoyés pour {len(prets_actifs)} prêts'
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/admin/test-notification')
@login_required
def test_notification():
    """Route de test pour les notifications"""
    if getattr(current_user, 'role', None) != 'admin':
        return redirect(url_for('tableau_de_bord'))

    # Test avec le premier client
    client = User.query.first()
    pret = Pret.query.filter_by(client_id=client.id).first()

    if pret and client:
        notification_manager.notifier_approbation_pret(client, pret)
        return jsonify({'status': 'Notification de test envoyée'})

    return jsonify({'error': 'Aucun client/pret trouvé pour le test'})

# Fonctions utilitaires pour les statistiques
def calculer_statistiques_globales():
    """Calcule les statistiques globales du système"""
    total_clients = User.query.filter_by(role='client').count()  # ✅ Seulement les clients
    total_prets = Pret.query.count()
    prets_actifs = Pret.query.filter_by(statut='approuve').count()
    prets_en_attente = Pret.query.filter_by(statut='en_attente').count()

    # Calcul des montants
    montant_total_prets = db.session.query(db.func.sum(Pret.montant)).scalar() or 0
    montant_prets_actifs = db.session.query(db.func.sum(Pret.montant)).filter(
        Pret.statut == 'approuve'
    ).scalar() or 0

    # Remboursements
    total_remboursements = Remboursement.query.count()
    montant_total_rembourse = db.session.query(db.func.sum(Remboursement.montant)).scalar() or 0

    # Groupes
    total_groupes = Groupe.query.count()

    # Calcul du taux de remboursement (simplifié)
    taux_remboursement = 0
    if montant_prets_actifs > 0:
        taux_remboursement = (montant_total_rembourse / montant_prets_actifs) * 100

    # ✅ CORRECTION de la jointure problématique
    clients_avec_prets_count = db.session.query(User).join(
        Pret, User.id == Pret.client_id
    ).filter(User.role == 'client').distinct(User.id).count()

    return {
        'clients': {
            'total': total_clients,
            'avec_prets': clients_avec_prets_count,  # ✅ Utiliser la version corrigée
            'nouveaux_ce_mois': User.query.filter(
                User.date_inscription >= datetime.utcnow().replace(day=1),
                User.role == 'client'  # ✅ Seulement les clients
            ).count()
        },
        'prets': {
            'total': total_prets,
            'actifs': prets_actifs,
            'en_attente': prets_en_attente,
            'montant_total': round(montant_total_prets, 2),
            'montant_actifs': round(montant_prets_actifs, 2)
        },
        'remboursements': {
            'total': total_remboursements,
            'montant_total': round(montant_total_rembourse, 2),
            'taux_remboursement': round(taux_remboursement, 1)
        },
        'groupes': {
            'total': total_groupes,
            'membres_moyen': total_clients / total_groupes if total_groupes > 0 else 0
        },
        'performance': {
            'taux_approbation': (prets_actifs / total_prets * 100) if total_prets > 0 else 0,
            'rotation_fonds': calculer_rotation_fonds()
        }
    }
def calculer_rotation_fonds():
    """Calcule la rotation des fonds (simplifié)"""
    # Implémentation simplifiée
    return 2.5  # Exemple fixe


@app.route('/tableau-bord-personnalise')
@login_required
def tableau_bord_personnalise():
    """Tableau de bord avec widgets personnalisables"""
    if getattr(current_user, 'role', None) != 'admin':
        return redirect(url_for('tableau_de_bord'))

    stats = calculer_statistiques_globales()

    # Données pour les graphiques
    prets_par_statut = db.session.query(
        Pret.statut,
        db.func.count(Pret.id)
    ).group_by(Pret.statut).all()

    prets_par_mois = db.session.query(
        db.func.strftime('%Y-%m', Pret.date_demande),
        db.func.count(Pret.id)
    ).group_by(db.func.strftime('%Y-%m', Pret.date_demande)).all()

    return render_template('tableau_bord_personnalise.html',
                           stats=stats,
                           prets_par_statut=prets_par_statut,
                           prets_par_mois=prets_par_mois)

@app.route('/demande-pret', methods=['GET', 'POST'])
@login_required
def demande_pret():
    if request.method == 'POST':
        montant = float(request.form.get('montant'))
        duree = int(request.form.get('duree'))
        motif = request.form.get('motif')

        # Calculs automatiques
        taux_mensuel = 12.0 / 100 / 12
        mensualite = montant * taux_mensuel * (1 + taux_mensuel) ** duree / ((1 + taux_mensuel) ** duree - 1)
        montant_interet = (mensualite * duree) - montant
        montant_total = mensualite * duree

        nouveau_pret = Pret(
            client_id=current_user.id,
            montant=montant,
            duree_mois=duree,
            motif=motif,
            mensualite=round(mensualite, 2),
            montant_interet=round(montant_interet, 2),
            montant_total=round(montant_total, 2)
        )

        db.session.add(nouveau_pret)
        db.session.commit()

        return redirect(url_for('mes_prets'))

    return render_template('demande_pret.html')


@app.route('/mes-prets')
@login_required
def mes_prets():
    prets = Pret.query.filter_by(client_id=current_user.id).all()
    return render_template('mes_prets.html', prets=prets)


@app.route('/api/calcul-pret', methods=['POST'])
def calcul_pret():
    data = request.json
    montant = float(data['montant'])
    duree = int(data['duree'])
    taux_annuel = 12.0

    taux_mensuel = taux_annuel / 100 / 12
    mensualite = montant * taux_mensuel * (1 + taux_mensuel) ** duree / ((1 + taux_mensuel) ** duree - 1)
    total_rembourser = mensualite * duree
    cout_credit = total_rembourser - montant

    return jsonify({
        'mensualite': round(mensualite, 2),
        'total_rembourser': round(total_rembourser, 2),
        'cout_credit': round(cout_credit, 2)
    })


@app.route('/debug/users')
def debug_users():
    """Route de debug pour voir les utilisateurs en base"""
    users = User.query.all()
    clients = User.query.filter_by(role='client').all()  # ✅ CORRECTION

    result = {
        'users': [{'id': u.id, 'username': u.username, 'role': u.role} for u in users],
        'clients': [{'id': c.id, 'email': c.email, 'nom': c.nom} for c in clients]
    }

    return jsonify(result)

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    # Vérifier que c'est bien un admin (sans hasattr)
    if getattr(current_user, 'role', None) != 'admin':
        return redirect(url_for('tableau_de_bord'))
    return render_template('admin_dashboard.html')

@app.route('/employe/dashboard')
@login_required
def employe_dashboard():
    # Vérifier que c'est bien un employé (sans hasattr)
    if getattr(current_user, 'role', None) != 'employe':
        return redirect(url_for('tableau_de_bord'))
    return render_template('employe_dashboard.html')

@app.route('/client/dashboard')
@login_required
def client_dashboard():
    # Vérifier que c'est bien un client (sans hasattr)
    if getattr(current_user, 'role', None):  # Si c'est un User, pas un Client
        return redirect(url_for('tableau_de_bord'))
    return render_template('client_dashboard.html')


@app.route('/pret/<int:pret_id>/<action>')
@login_required
def gerer_pret(pret_id, action):
    if getattr(current_user, 'role', None) not in ['admin', 'employe']:
        return redirect(url_for('tableau_de_bord'))

    pret = Pret.query.get_or_404(pret_id)
    client = User.query.get(pret.client_id)

    if action == 'approuver':
        pret.statut = 'approuve'
        pret.date_approbation = datetime.utcnow()

        # 🔔 NOTIFICATION d'approbation
        notification_manager.notifier_approbation_pret(client, pret)

    elif action == 'rejeter':
        pret.statut = 'rejete'
        motif = request.args.get('motif', 'Critères non satisfaits')

        # 🔔 NOTIFICATION de rejet
        notification_manager.notifier_rejet_pret(client, pret, motif)

    db.session.commit()
    return redirect(url_for('prets_en_attente'))


@app.route('/prets-en-attente')
@login_required
def prets_en_attente():
    # Vérifier que c'est un admin ou employé (sans hasattr)
    if getattr(current_user, 'role', None) in ['admin', 'employe']:
        prets = Pret.query.filter_by(statut='en_attente').all()

        # Récupérer les informations clients manuellement
        prets_avec_clients = []
        for pret in prets:
            client = User.query.get(pret.client_id)
            prets_avec_clients.append({
                'pret': pret,
                'client': client
            })

        return render_template('admin_prets_attente.html', prets_avec_clients=prets_avec_clients)
    else:
        return redirect(url_for('tableau_de_bord'))


# ==================== NOUVELLES ROUTES POUR LE DASHBOARD ====================

@app.route('/tableau-de-bord')
@login_required
def tableau_de_bord():
    """Tableau de bord principal avec toutes les fonctionnalités"""
    stats = calculer_statistiques_utilisateur(current_user)
    return render_template('tableau_de_bord.html', user=current_user, stats=stats)



# Routes pour les nouvelles fonctionnalités
@app.route('/score-credit')
@login_required
def score_credit():
    """Page détaillée du score de crédit"""
    return render_template('score_credit.html')


@app.route('/recommandations-pret')
@login_required
def recommandations_pret():
    """Recommandations de prêt personnalisées"""
    return render_template('recommandations_pret.html')


@app.route('/profil-gamification')
@login_required
def profil_gamification():
    """Profil gamification détaillé"""
    return render_template('profil_gamification.html')


@app.route('/reconnaissance-faciale')
@login_required
def reconnaissance_faciale():
    """Gestion de la reconnaissance faciale"""
    return render_template('reconnaissance_faciale.html')


@app.route('/analytics-personnel')
@login_required
def analytics_personnel():
    """Analytics et statistiques du personnel"""
    if not current_user.est_admin and not current_user.est_employe:
        return redirect(url_for('tableau_de_bord'))

    # Vos données d'analytics ici
    stats = calculer_statistiques_globales()
    return render_template('analytics_personnel.html', stats=stats)

# Routes gamification manquantes
@app.route('/defis')
@login_required
def defis():
    return render_template('defis.html')

@app.route('/badges')
@login_required
def badges():
    return render_template('badges.html')

@app.route('/classement')
@login_required
def classement():
    return render_template('classement.html')


@app.route('/previsions-remboursement')
@login_required
def previsions_remboursement():
    """Prévisions et calendrier de remboursement"""
    if current_user.est_client:
        # Pour les clients : leurs propres prévisions
        prets = Pret.query.filter_by(client_id=current_user.id, statut='approuve').all()
    else:
        # Pour admin/employé : toutes les prévisions
        prets = Pret.query.filter_by(statut='approuve').all()

    return render_template('previsions_remboursement.html', prets=prets)

@app.route('/notifications')
@login_required
def notifications():
    """Page des notifications utilisateur"""
    notifications = Notification.query.filter_by(utilisateur_id=current_user.id).order_by(Notification.date_creation.desc()).all()
    return render_template('notifications.html', notifications=notifications)


@app.route('/parametres')
@login_required
def parametres():
    """Page des paramètres utilisateur"""
    return render_template('parametres.html')

@app.route('/profil')
@login_required
def profil():
    """Page de profil utilisateur"""
    return render_template('profil.html', user=current_user)
# ==================== LANCEMENT ====================

@app.route('/securite')
@login_required
def securite():
    """Page de sécurité et paramètres de compte"""
    return render_template('securite.html')

@app.route('/test-mobile')
def test_mobile():
    return redirect(url_for('test_mobile_routes'))


@app.route('/admin/gerer-employes')
@login_required
def gerer_employes():
    """Page de gestion des employés"""
    if not current_user.est_admin:
        return redirect(url_for('tableau_de_bord'))

    employes = User.query.filter_by(role='employe').all()
    return render_template('gerer_employes.html', employes=employes)


@app.route('/admin/creer-employe', methods=['GET', 'POST'])
@login_required
def creer_employe():
    """Créer un nouvel employé"""
    if not current_user.est_admin:
        return redirect(url_for('tableau_de_bord'))

    if request.method == 'POST':
        # Récupérer les données du formulaire
        username = request.form.get('username')
        email = request.form.get('email')
        nom = request.form.get('nom')
        prenom = request.form.get('prenom')
        telephone = request.form.get('telephone')
        password = request.form.get('password')

        # Vérifier si l'utilisateur existe déjà
        if User.query.filter_by(username=username).first():
            return render_template('creer_employe.html', error="Ce nom d'utilisateur existe déjà")

        if User.query.filter_by(email=email).first():
            return render_template('creer_employe.html', error="Cet email existe déjà")

        # Créer le nouvel employé
        nouvel_employe = User(
            username=username,
            email=email,
            nom=nom,
            prenom=prenom,
            telephone=telephone,
            role='employe'
        )
        nouvel_employe.set_password(password)

        db.session.add(nouvel_employe)
        db.session.commit()

        return redirect(url_for('gerer_employes'))

    return render_template('creer_employe.html')
@app.route('/mobile/dashboard')
@login_required
def mobile_dashboard():
    stats = calculer_statistiques_utilisateur(current_user)
    return render_template('mobile_dashboard.html', stats=stats)


# ... votre code existant ...

if __name__ == '__main__':
    with app.app_context():
        initialiser_donnees()

    # Configuration pour Render
    import os

    port = int(os.environ.get("PORT", 5000))

    print("🚀 GMES Microcrédit - Prêt pour la production")
    print(f"🌐 URL: https://votre-app.onrender.com")

    app.run(host="0.0.0.0", port=port, debug=False)