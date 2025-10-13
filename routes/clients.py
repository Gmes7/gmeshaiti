from flask import Blueprint, render_template, request, jsonify, session
from flask_login import login_required, current_user
from models import User, Account, Transaction
from database import db

clients_bp = Blueprint('clients', __name__)


@clients_bp.route('/dashboard')
@login_required
def dashboard():
    if not hasattr(current_user, 'account_number'):  # Vérifier si c'est un client
        return redirect(url_for('auth.login'))

    # Récupérer les informations du compte
    account = Account.query.filter_by(user_id=current_user.id).first()
    transactions = Transaction.query.filter_by(user_id=current_user.id) \
        .order_by(Transaction.date_created.desc()) \
        .limit(10).all()

    # Récupérer les prêts
    from models import Loan
    loans = Loan.query.filter_by(user_id=current_user.id).all()

    return render_template('client_portal.html',
                           account=account,
                           transactions=transactions,
                           loans=loans)


@clients_bp.route('/profile', methods=['GET', 'PUT'])
@login_required
def profile():
    if request.method == 'PUT':
        data = request.json
        user = User.query.get(current_user.id)

        if data.get('phone'):
            user.phone = data['phone']
        if data.get('email'):
            user.email = data['email']
        if data.get('address'):
            user.address = data['address']

        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Profil mis à jour'})

    return jsonify({
        'first_name': current_user.first_name,
        'last_name': current_user.last_name,
        'phone': current_user.phone,
        'email': current_user.email,
        'address': current_user.address,
        'account_number': current_user.account_number
    })


@clients_bp.route('/transactions')
@login_required
def transactions():
    page = request.args.get('page', 1, type=int)
    per_page = 20

    transactions = Transaction.query.filter_by(user_id=current_user.id) \
        .order_by(Transaction.date_created.desc()) \
        .paginate(page=page, per_page=per_page)

    return jsonify({
        'transactions': [{
            'id': t.id,
            'type': t.type,
            'amount': t.amount,
            'method': t.method,
            'status': t.status,
            'date_created': t.date_created.isoformat()
        } for t in transactions.items],
        'total_pages': transactions.pages,
        'current_page': page
    })