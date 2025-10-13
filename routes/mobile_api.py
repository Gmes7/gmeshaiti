from flask import jsonify, request
from flask_login import login_required, current_user
from flask import jsonify, request
from utils.ai_scoring import ai_scorer
from utils.gamification import gamification
from functools import wraps
import jwt
import datetime


def show_login_view(self):
    """Vue de connexion avec option faciale"""
    self.email_field = ft.TextField(
        label="Email",
        prefix_icon=ft.icons.EMAIL,
        width=300
    )

    self.password_field = ft.TextField(
        label="Mot de passe",
        password=True,
        prefix_icon=ft.icons.LOCK,
        width=300
    )

    # Option reconnaissance faciale
    face_login_button = ft.ElevatedButton(
        text="🔐 Connexion Faciale",
        icon=ft.icons.FACE,
        on_click=self.show_face_login,
        width=300,
        bgcolor=ft.colors.BLUE_100
    )

    login_view = ft.Column(
        [
            ft.Container(
                content=ft.Image(src="/static/logo.png", width=100, height=100),
                alignment=ft.alignment.center
            ),
            ft.Text("GMES Mobile", size=24, weight=ft.FontWeight.BOLD),
            ft.Text("Microcrédit Solidaire", size=16),
            ft.Divider(),

            # Option classique
            self.email_field,
            self.password_field,
            ft.ElevatedButton(
                text="Se connecter",
                icon=ft.icons.LOGIN,
                on_click=self.login,
                width=300
            ),

            ft.Divider(),
            ft.Text("OU", text_align=ft.TextAlign.CENTER),

            # Option faciale
            face_login_button,

            ft.TextButton(
                text="Créer un compte",
                on_click=lambda _: self.show_register_view()
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    self.page.clean()
    self.page.add(login_view)


@app.route('/api/recommandations-pret')
@token_required
def mobile_recommandations_pret(current_user):
    """📱 Endpoint pour les recommandations de prêt"""
    # Calcul du score et recommandations...
    return jsonify({
        'score': score,
        'recommandations': recommandations
    })

@app.route('/api/gamification/profile')
@token_required
def mobile_gamification_profile(current_user):
    """💎 Endpoint pour le profil gamification"""
    # Calcul points et niveau...
    return jsonify(profile_data)

@app.route('/api/sync/operation', methods=['POST'])
@token_required
def sync_operation(current_user):
    """Synchronise une opération hors ligne"""
    data = request.json

    operation_type = data.get('type')
    operation_data = data.get('data', {})

    try:
        if operation_type == 'loan_request':
            # Traiter la demande de prêt
            nouveau_pret = Pret(
                client_id=current_user.id,
                montant=operation_data['montant'],
                duree_mois=operation_data['duree'],
                motif=operation_data['motif'],
                statut='en_attente'
            )
            db.session.add(nouveau_pret)
            db.session.commit()

        elif operation_type == 'payment':
            # Traiter un paiement
            remboursement = Remboursement(
                pret_id=operation_data['pret_id'],
                client_id=current_user.id,
                montant=operation_data['montant'],
                statut='paye'
            )
            db.session.add(remboursement)
            db.session.commit()

        return jsonify({'status': 'success'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/health')
def health_check():
    """Endpoint de santé pour vérifier la connectivité"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'error': 'Token manquant'}), 401

        try:
            token = token.replace('Bearer ', '')
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
        except:
            return jsonify({'error': 'Token invalide'}), 401

        return f(current_user, *args, **kwargs)

    return decorated


@app.route('/api/auth/login', methods=['POST'])
def mobile_login():
    data = request.json
    user = User.query.filter_by(email=data.get('email')).first()

    if user and user.check_password(data.get('password')):
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, app.config['SECRET_KEY'])

        return jsonify({
            'token': token,
            'user': {
                'id': user.id,
                'nom': user.nom,
                'prenom': user.prenom,
                'email': user.email,
                'role': user.role
            }
        }), 200

    return jsonify({'error': 'Identifiants invalides'}), 401


@app.route('/api/mes-prets')
@token_required
def mobile_mes_prets(current_user):
    prets = Pret.query.filter_by(client_id=current_user.id).all()

    return jsonify([{
        'id': pret.id,
        'montant': pret.montant,
        'duree_mois': pret.duree_mois,
        'mensualite': pret.mensualite,
        'statut': pret.statut,
        'date_demande': pret.date_demande.isoformat()
    } for pret in prets])


@app.route('/api/demande-pret', methods=['POST'])
@token_required
def mobile_demande_pret(current_user):
    data = request.json

    # Calculs similaires à votre version web
    nouveau_pret = Pret(
        client_id=current_user.id,
        montant=data['montant'],
        duree_mois=data['duree'],
        motif=data['motif']
        # ... autres champs
    )

    db.session.add(nouveau_pret)
    db.session.commit()

    return jsonify({'message': 'Demande envoyée'}), 201


@app.route('/api/remboursements/dus')
@token_required
def mobile_remboursements_dus(current_user):
    """Remboursements en attente"""
    remboursements = Remboursement.query.filter_by(
        client_id=current_user.id,
        statut='en_attente'
    ).all()

    return jsonify([{
        'pret_id': r.pret_id,
        'montant': r.montant,
        'date_echeance': r.date_echeance.strftime('%d/%m/%Y')
    } for r in remboursements])


@app.route('/api/mon-groupe')
@token_required
def mobile_mon_groupe(current_user):
    """Informations du groupe"""
    if not current_user.groupe_id:
        return jsonify({'error': 'Aucun groupe'}), 404

    groupe = Groupe.query.get(current_user.groupe_id)
    membres = Client.query.filter_by(groupe_id=groupe.id).all()
    prets_groupe = Pret.query.filter_by(groupe_id=groupe.id).all()

    return jsonify({
        'id': groupe.id,
        'nom': groupe.nom,
        'zone': groupe.zone,
        'code_groupe': groupe.code_groupe,
        'membres': [{
            'id': m.id,
            'nom': m.nom,
            'prenom': m.prenom,
            'profession': m.profession
        } for m in membres],
        'prets_groupe': [{
            'id': p.id,
            'montant': p.montant,
            'statut': p.statut,
            'motif': p.motif,
            'client_prenom': Client.query.get(p.client_id).prenom
        } for p in prets_groupe],
        'montant_prets_total': sum(p.montant for p in prets_groupe)
    })


@app.route('/api/mes-statistiques')
@token_required
def mobile_mes_statistiques(current_user):
    """Statistiques personnelles"""
    prets = Pret.query.filter_by(client_id=current_user.id).all()
    remboursements = Remboursement.query.filter_by(client_id=current_user.id).all()

    return jsonify({
        'score_credit': 75,  # À calculer
        'ponctualite': 85,  # À calculer
        'prets_total': sum(p.montant for p in prets),
        'prets_rembourses': len([p for p in prets if p.statut == 'termine']),
        'historique_prets': [{
            'date': p.date_demande.strftime('%d/%m/%Y'),
            'montant': p.montant,
            'statut': p.statut
        } for p in prets]
    })