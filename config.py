import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'gmes-secret-key-2024-development'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///gmes.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configuration des langues
    LANGUAGES = ['fr', 'en', 'es', 'ht']
    BABEL_DEFAULT_LOCALE = 'fr'

    # Configuration des publicités
    ADS_CONFIG_FILE = '.ads_config.json'

    # Configuration email
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    # Taux d'intérêt par défaut
    DEFAULT_INTEREST_RATE = 12.0  # 12% annuel

    # Configuration du portail employé
    EMPLOYE_ROLES = ['manager', 'agent', 'cashier', 'advisor']