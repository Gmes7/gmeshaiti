import hashlib
import re
from flask import current_app


def hash_password(password):
    """Hash un mot de passe avec SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


def validate_password(password):
    """Valide la force du mot de passe"""
    if len(password) < 8:
        return False, "Le mot de passe doit contenir au moins 8 caractères"

    if not re.search(r"[A-Z]", password):
        return False, "Le mot de passe doit contenir au moins une majuscule"

    if not re.search(r"[a-z]", password):
        return False, "Le mot de passe doit contenir au moins une minuscule"

    if not re.search(r"\d", password):
        return False, "Le mot de passe doit contenir au moins un chiffre"

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Le mot de passe doit contenir au moins un caractère spécial"

    return True, "Mot de passe valide"


def validate_phone(phone):
    """Valide le format du numéro de téléphone"""
    # Format international ou local
    pattern = r'^(\+?\d{1,4}?[-.\s]?)?(\(?\d{1,4}?\)?[-.\s]?)?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}$'
    return re.match(pattern, phone) is not None


def validate_email(email):
    """Valide le format de l'email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None