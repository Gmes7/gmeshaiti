from models import Loan, User, Account, db
from datetime import datetime


def calculate_loan_details(amount, duration, interest_rate):
    """Calcule les détails d'un prêt"""
    monthly_rate = interest_rate / 100 / 12
    monthly_payment = amount * monthly_rate * (1 + monthly_rate) ** duration / ((1 + monthly_rate) ** duration - 1)
    total_amount = monthly_payment * duration

    return {
        'monthly_payment': round(monthly_payment, 2),
        'total_amount': round(total_amount, 2),
        'total_interest': round(total_amount - amount, 2)
    }


def can_request_loan(user_id, amount):
    """Vérifie si l'utilisateur peut demander un prêt"""
    user = User.query.get(user_id)
    account = Account.query.filter_by(user_id=user_id).first()

    if not user or not account:
        return False, "Utilisateur ou compte non trouvé"

    # Vérifier le solde (doit être ≥ 1/3 du montant demandé)
    if account.balance < (amount / 3):
        return False, f"Solde insuffisant. Votre solde doit être d'au moins {amount / 3:.2f}"

    # Vérifier s'il y a des prêts en cours
    active_loans = Loan.query.filter_by(user_id=user_id, status='approved').count()
    if active_loans >= 1:
        return False, "Vous avez déjà un prêt en cours"

    return True, "Éligible au prêt"


def create_loan_request(user_id, loan_data):
    """Crée une demande de prêt"""
    try:
        # Vérifier l'éligibilité
        eligible, message = can_request_loan(user_id, loan_data['amount'])
        if not eligible:
            return False, message

        # Calculer les détails du prêt
        details = calculate_loan_details(
            loan_data['amount'],
            loan_data['duration'],
            loan_data['interest_rate']
        )

        # Créer la demande de prêt
        loan = Loan(
            user_id=user_id,
            amount=loan_data['amount'],
            duration=loan_data['duration'],
            interest_rate=loan_data['interest_rate'],
            monthly_payment=details['monthly_payment'],
            total_amount=details['total_amount'],
            status='pending'
        )

        db.session.add(loan)
        db.session.commit()

        return True, "Demande de prêt créée avec succès"

    except Exception as e:
        db.session.rollback()
        return False, f"Erreur lors de la création de la demande: {str(e)}"