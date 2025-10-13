import requests
import json
import hashlib
import hmac
from datetime import datetime


class PaymentGateway:
    def __init__(self):
        self.config = {
            'moncash': {
                'client_id': os.getenv('MONCASH_CLIENT_ID'),
                'client_secret': os.getenv('MONCASH_CLIENT_SECRET'),
                'base_url': 'https://sandbox.moncashbutton.digicelgroup.com'
            },
            'natcash': {
                'api_key': os.getenv('NATCASH_API_KEY'),
                'base_url': 'https://api.natcash.com'
            },
            'unibank': {
                'merchant_id': os.getenv('UNIBANK_MERCHANT_ID'),
                'api_key': os.getenv('UNIBANK_API_KEY'),
                'base_url': 'https://api.unibank.com'
            }
        }

    def initier_paiement_moncash(self, montant, description, order_id):
        """Initie un paiement via MonCash"""
        try:
            # Authentification
            auth_url = f"{self.config['moncash']['base_url']}/oauth/token"
            auth_data = {
                'grant_type': 'client_credentials',
                'client_id': self.config['moncash']['client_id'],
                'client_secret': self.config['moncash']['client_secret']
            }

            auth_response = requests.post(auth_url, data=auth_data)
            if auth_response.status_code != 200:
                return False, "Erreur d'authentification MonCash"

            access_token = auth_response.json()['access_token']

            # Création du paiement
            payment_url = f"{self.config['moncash']['base_url']}/api/v1/payment/create"
            payment_data = {
                'amount': montant,
                'orderId': order_id,
                'description': description
            }

            headers = {'Authorization': f'Bearer {access_token}'}
            payment_response = requests.post(payment_url, json=payment_data, headers=headers)

            if payment_response.status_code == 201:
                payment_info = payment_response.json()
                return True, {
                    'payment_url': payment_info['payment_url'],
                    'transaction_id': payment_info['transaction_id'],
                    'qr_code': payment_info.get('qr_code')
                }
            else:
                return False, "Erreur création paiement MonCash"

        except Exception as e:
            return False, f"Erreur MonCash: {str(e)}"

    def initier_paiement_natcash(self, montant, telephone, description):
        """Initie un paiement via NatCash"""
        try:
            url = f"{self.config['natcash']['base_url']}/api/v1/payment"
            data = {
                'amount': montant,
                'phone_number': telephone,
                'description': description,
                'currency': 'HTG',
                'reference': f"GMES_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            }

            headers = {
                'Authorization': f"Bearer {self.config['natcash']['api_key']}",
                'Content-Type': 'application/json'
            }

            response = requests.post(url, json=data, headers=headers)

            if response.status_code == 200:
                return True, response.json()
            else:
                return False, "Erreur paiement NatCash"

        except Exception as e:
            return False, f"Erreur NatCash: {str(e)}"

    def verifier_statut_paiement(self, gateway, transaction_id):
        """Vérifie le statut d'un paiement"""
        try:
            if gateway == 'moncash':
                url = f"{self.config['moncash']['base_url']}/api/v1/payment/{transaction_id}"
                auth_response = requests.post(
                    f"{self.config['moncash']['base_url']}/oauth/token",
                    data={
                        'grant_type': 'client_credentials',
                        'client_id': self.config['moncash']['client_id'],
                        'client_secret': self.config['moncash']['client_secret']
                    }
                )

                if auth_response.status_code == 200:
                    access_token = auth_response.json()['access_token']
                    headers = {'Authorization': f'Bearer {access_token}'}
                    response = requests.get(url, headers=headers)

                    if response.status_code == 200:
                        data = response.json()
                        return True, data['status']

            elif gateway == 'natcash':
                url = f"{self.config['natcash']['base_url']}/api/v1/payment/{transaction_id}"
                headers = {'Authorization': f"Bearer {self.config['natcash']['api_key']}"}
                response = requests.get(url, headers=headers)

                if response.status_code == 200:
                    data = response.json()
                    return True, data['status']

            return False, "Statut indisponible"

        except Exception as e:
            return False, f"Erreur vérification: {str(e)}"

    def generer_qr_code(self, montant, description):
        """Génère un QR Code pour paiement"""
        try:
            # Simulation - en production, utiliser l'API du gateway
            qr_data = {
                'amount': montant,
                'description': description,
                'merchant': 'GMES Microcrédit',
                'account': 'GMES_ACCOUNT',
                'timestamp': datetime.now().isoformat()
            }

            # Retourner des données simulées pour le QR Code
            return True, {
                'qr_data': json.dumps(qr_data),
                'payment_url': f"gmes://payment/{hashlib.md5(json.dumps(qr_data).encode()).hexdigest()}"
            }

        except Exception as e:
            return False, f"Erreur génération QR: {str(e)}"


# mobile/payment_gateways.py
import os


class PaymentGateway:
    def __init__(self):
        pass

    def initier_paiement_moncash(self, montant, description, order_id):
        return True, {"payment_url": "https://example.com", "transaction_id": "test123"}

    def initier_paiement_natcash(self, montant, telephone, description):
        return True, {"transaction_id": "test123"}

    def verifier_statut_paiement(self, gateway, transaction_id):
        return True, "completed"

    def generer_qr_code(self, montant, description):
        return True, {"qr_data": "test", "payment_url": "https://example.com"}




# Instance globale
payment_gateway = PaymentGateway()