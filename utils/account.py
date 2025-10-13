import random
from models import User, Account, db


def generate_account_number(gender):
    """Génère un numéro de compte unique"""
    prefix = "7-12519-"

    # Dernier chiffre: pair pour homme, impair pour femme
    last_digit = random.choice([0, 2, 4, 6, 8]) if gender.lower() == 'homme' else random.choice([1, 3, 5, 7, 9])

    # Générer les 4 chiffres du milieu
    middle_digits = ''.join([str(random.randint(0, 9)) for _ in range(4)])

    account_number = f"{prefix}{middle_digits}{last_digit}"

    # Vérifier l'unicité
    while User.query.filter_by(account_number=account_number).first():
        middle_digits = ''.join([str(random.randint(0, 9)) for _ in range(4)])
        account_number = f"{prefix}{middle_digits}{last_digit}"

    return account_number


def create_user_account(user_data):
    """Crée un nouvel utilisateur avec son compte"""
    try:
        # Vérifier l'unicité des données
        if User.query.filter_by(email=user_data['email']).first():
            return False, "Email déjà utilisé"

        if User.query.filter_by(phone=user_data['phone']).first():
            return False, "Téléphone déjà utilisé"

        if User.query.filter_by(id_number=user_data['id_number']).first():
            return False, "Numéro d'identité déjà utilisé"

        # Générer le numéro de compte
        account_number = generate_account_number(user_data['gender'])

        # Créer l'utilisateur
        user = User(
            account_number=account_number,
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            phone=user_data['phone'],
            email=user_data['email'],
            address=user_data['address'],
            occupation=user_data['occupation'],
            monthly_income=user_data['monthly_income'],
            monthly_expense=user_data['monthly_expense'],
            id_type=user_data['id_type'],
            id_number=user_data['id_number'],
            nationality=user_data['nationality'],
            opening_amount=user_data['opening_amount'],
            gender=user_data['gender']
        )
        user.set_password(user_data['password'])

        db.session.add(user)
        db.session.commit()

        # Créer le compte bancaire
        account = Account(
            account_number=account_number,
            user_id=user.id,
            balance=user_data['opening_amount']
        )

        db.session.add(account)
        db.session.commit()

        return True, account_number

    except Exception as e:
        db.session.rollback()
        return False, f"Erreur lors de la création: {str(e)}"