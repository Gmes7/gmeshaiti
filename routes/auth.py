# from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
# from flask_login import login_user, logout_user, login_required, current_user
# from models import Client as User, Admin, Employe as Employee
#
# from utils.security import hash_password, validate_password
# from database import db
#
# auth_bp = Blueprint('auth', __name__)
#
# from fastapi import APIRouter, HTTPException
# from pydantic import BaseModel
#
# router = APIRouter(prefix="/api/mobile")
# from flask import Blueprint, request, jsonify
#
#
#
# # -----------------------
# # Schémas de données
# # -----------------------
# class RegisterRequest(BaseModel):
#     first_name: str
#     last_name: str
#     phone: str
#     email: str
#     password: str
#
# class LoginRequest(BaseModel):
#     identifier: str
#     password: str
#     user_type: str = "client"
#
# # -----------------------
# # Routes
# # -----------------------
#
# @router.post("/register")
# def register_user(request: RegisterRequest):
#     """Simule la création d'un compte"""
#     # TODO : Enregistrer dans la base de données réelle
#     if request.email == "test@example.com":
#         return {"success": False, "error": "Email déjà utilisé"}
#     return {"success": True, "message": "Compte créé avec succès"}
#
# @router.post("/login")
# def login_user(request: LoginRequest):
#     """Simule la connexion"""
#     if request.identifier == "test@example.com" and request.password == "1234":
#         return {
#             "success": True,
#             "token": "fake-token-12345",
#             "user": {
#                 "first_name": "Jean",
#                 "last_name": "Dupont",
#                 "email": request.identifier
#             }
#         }
#     raise HTTPException(status_code=401, detail="Identifiants incorrects")
#
# @auth_bp.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         identifier = request.form.get('identifier')
#         password = request.form.get('password')
#         user_type = request.form.get('user_type', 'client')
#
#         # Hacher le mot de passe pour comparaison
#         hashed_password = hash_password(password)
#
#         user = None
#
#         if user_type == 'client':
#             # Connexion client avec numéro de compte ou email
#             user = User.query.filter(
#                 (User.account_number == identifier) | (User.email == identifier)
#             ).first()
#
#         elif user_type == 'admin':
#             # Connexion admin
#             user = Admin.query.filter(
#                 (Admin.username == identifier) | (Admin.email == identifier)
#             ).first()
#
#         elif user_type == 'employee':
#             # Connexion employé
#             user = Employee.query.filter(
#                 (Employee.employee_id == identifier) | (Employee.email == identifier)
#             ).first()
#
#         if user and user.check_password(password) and user.is_active:
#             login_user(user)
#             session['user_type'] = user_type
#
#             if user_type == 'client':
#                 return redirect(url_for('client_portal'))
#             elif user_type == 'admin':
#                 return redirect(url_for('admin.dashboard'))
#             elif user_type == 'employee':
#                 return redirect(url_for('employees.dashboard'))
#
#         return render_template('login.html', error="Identifiants invalides")
#
#     return render_template('login.html')
#
#
# @auth_bp.route('/logout')
# @login_required
# def logout():
#     logout_user()
#     session.clear()
#     return redirect(url_for('index'))
#
#
# @auth_bp.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         # Récupérer les données du formulaire
#         user_data = {
#             'first_name': request.form.get('first_name'),
#             'last_name': request.form.get('last_name'),
#             'phone': request.form.get('phone'),
#             'email': request.form.get('email'),
#             'address': request.form.get('address'),
#             'occupation': request.form.get('occupation'),
#             'monthly_income': float(request.form.get('monthly_income', 0)),
#             'monthly_expense': float(request.form.get('monthly_expense', 0)),
#             'id_type': request.form.get('id_type'),
#             'id_number': request.form.get('id_number'),
#             'nationality': request.form.get('nationality'),
#             'opening_amount': float(request.form.get('opening_amount', 0)),
#             'gender': request.form.get('gender'),
#             'password': request.form.get('password')
#         }
#
#         # Valider le mot de passe
#         is_valid, msg = validate_password(user_data['password'])
#         if not is_valid:
#             return render_template('reception_open_account.html', error=msg)
#
#         # Créer le compte
#         from utils.account import create_user_account
#         success, message = create_user_account(user_data)
#
#         if success:
#             return render_template('reception_open_account.html',
#                                    success=f"Compte créé avec succès! Votre numéro de compte: {message}")
#         else:
#             return render_template('reception_open_account.html', error=message)
#
#     return render_template('reception_open_account.html')
#
#
# @auth_bp.route('/forgot-password', methods=['POST'])
# def forgot_password():
#     email = request.json.get('email')
#     user_type = request.json.get('user_type', 'client')
#
#     user = None
#     if user_type == 'client':
#         user = User.query.filter_by(email=email).first()
#     elif user_type == 'admin':
#         user = Admin.query.filter_by(email=email).first()
#     elif user_type == 'employee':
#         user = Employee.query.filter_by(email=email).first()
#
#     if user:
#         # Générer un token de réinitialisation (simplifié)
#         reset_token = hash_password(user.email + str(datetime.utcnow()))
#         # Envoyer l'email avec le lien de réinitialisation
#         # Implémentation simplifiée
#         return jsonify({'status': 'success', 'message': 'Instructions envoyées par email'})
#
#     return jsonify({'status': 'error', 'message': 'Email non trouvé'})
#
#
# # ==================== ROUTES API MOBILE ====================
#
# @auth_bp.route('/api/mobile/login', methods=['POST'])
# def mobile_login():
#     """API mobile pour connexion"""
#     try:
#         data = request.get_json()
#         identifier = data.get('identifier')
#         password = data.get('password')
#         user_type = data.get('user_type', 'client')
#
#         # Logique d'authentification
#         user = None
#         if user_type == 'client':
#             user = User.query.filter(
#                 (User.account_number == identifier) | (User.email == identifier)
#             ).first()
#         elif user_type == 'admin':
#             user = Admin.query.filter(
#                 (Admin.username == identifier) | (Admin.email == identifier)
#             ).first()
#         elif user_type == 'employee':
#             user = Employee.query.filter(
#                 (Employee.employee_id == identifier) | (Employee.email == identifier)
#             ).first()
#
#         if user and user.check_password(password) and user.is_active:
#             return jsonify({
#                 'success': True,
#                 'token': f'mobile_token_{user.id}',
#                 'user': {
#                     'id': user.id,
#                     'first_name': user.first_name,
#                     'last_name': user.last_name,
#                     'email': user.email
#                 }
#             })
#         else:
#             return jsonify({'success': False, 'error': 'Identifiants invalides'}), 401
#
#     except Exception as e:
#         return jsonify({'success': False, 'error': str(e)}), 500
#
#
# @auth_bp.route('/api/mobile/register', methods=['POST'])
# def mobile_register():
#     """API mobile pour inscription"""
#     try:
#         data = request.get_json()
#
#         user_data = {
#             'first_name': data.get('first_name'),
#             'last_name': data.get('last_name'),
#             'phone': data.get('phone'),
#             'email': data.get('email'),
#             'password': data.get('password'),
#             'address': data.get('address', ''),
#             'occupation': data.get('occupation', ''),
#             'monthly_income': float(data.get('monthly_income', 0)),
#             'monthly_expense': float(data.get('monthly_expense', 0)),
#             'id_type': data.get('id_type', ''),
#             'id_number': data.get('id_number', ''),
#             'nationality': data.get('nationality', ''),
#             'opening_amount': float(data.get('opening_amount', 0)),
#             'gender': data.get('gender', '')
#         }
#
#         # Valider le mot de passe
#         is_valid, msg = validate_password(user_data['password'])
#         if not is_valid:
#             return jsonify({'success': False, 'error': msg}), 400
#
#         # Créer le compte
#         from utils.account import create_user_account
#         success, message = create_user_account(user_data)
#
#         if success:
#             return jsonify({'success': True, 'message': f'Compte créé: {message}'})
#         else:
#             return jsonify({'success': False, 'error': message}), 400
#
#     except Exception as e:
#         return jsonify({'success': False, 'error': str(e)}), 500

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from datetime import datetime

auth_bp = Blueprint('auth', __name__)


# Fonctions utilitaires simplifiées
def hash_password(password):
    """Hash simplifié d'un mot de passe"""
    from werkzeug.security import generate_password_hash
    return generate_password_hash(password)


def validate_password(password):
    """Validation simplifiée du mot de passe"""
    if len(password) < 6:
        return False, "Le mot de passe doit contenir au moins 6 caractères"
    return True, "OK"


# Routes d'authentification de base
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Route de connexion alternative"""
    return redirect(url_for('connexion'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Route d'inscription basique"""
    return """
    <h1>Inscription</h1>
    <p>Fonctionnalité en développement</p>
    <a href="/connexion">Retour à la connexion</a>
    """


@auth_bp.route('/logout')
@login_required
def logout():
    """Déconnexion"""
    logout_user()
    session.clear()
    return redirect(url_for('index'))


# Routes API Mobile simplifiées
@auth_bp.route('/api/mobile/login', methods=['POST'])
def mobile_login():
    """API mobile pour connexion"""
    try:
        data = request.get_json()
        identifier = data.get('identifier')
        password = data.get('password')

        # Import ici pour éviter les dépendances circulaires
        from app import User

        # Recherche de l'utilisateur
        user = User.query.filter(
            (User.username == identifier) | (User.email == identifier)
        ).first()

        if user and user.check_password(password):
            login_user(user)
            return jsonify({
                'success': True,
                'token': f'mobile_token_{user.id}',
                'user': {
                    'id': user.id,
                    'first_name': user.prenom,
                    'last_name': user.nom,
                    'email': user.email
                }
            })
        else:
            return jsonify({'success': False, 'error': 'Identifiants invalides'}), 401

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@auth_bp.route('/api/mobile/register', methods=['POST'])
def mobile_register():
    """API mobile pour inscription simplifiée"""
    try:
        data = request.get_json()

        # Import ici pour éviter les dépendances circulaires
        from app import User, db

        # Vérifier si l'email existe déjà
        if User.query.filter_by(email=data.get('email')).first():
            return jsonify({'success': False, 'error': 'Email déjà utilisé'}), 400

        # Créer un nouvel utilisateur
        new_user = User(
            email=data.get('email'),
            prenom=data.get('first_name', ''),
            nom=data.get('last_name', ''),
            telephone=data.get('phone', ''),
            role='client'
        )
        new_user.set_password(data.get('password'))

        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Compte créé avec succès',
            'user_id': new_user.id
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@auth_bp.route('/api/mobile/test')
def mobile_test():
    """Route de test pour l'API mobile"""
    return jsonify({
        'status': 'OK',
        'message': 'API mobile fonctionnelle',
        'timestamp': datetime.utcnow().isoformat()
    })