import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from datetime import datetime
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NotificationManager:
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_username = os.getenv('SMTP_USERNAME', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')

        # Configuration SMS (Twilio ou service similaire)
        self.sms_api_key = os.getenv('SMS_API_KEY', '')
        self.sms_sender = os.getenv('SMS_SENDER', 'GMES')

    def envoyer_email(self, destinataire, sujet, message_html, message_text=None):
        """
        Envoie un email de notification
        """
        try:
            if not self.smtp_username or not self.smtp_password:
                logger.warning("Configuration SMTP manquante - Email simulé")
                self._simuler_email(destinataire, sujet, message_html)
                return True

            # Création du message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = sujet
            msg['From'] = self.smtp_username
            msg['To'] = destinataire

            # Partie texte
            if message_text:
                part1 = MIMEText(message_text, 'plain')
                msg.attach(part1)

            # Partie HTML
            part2 = MIMEText(message_html, 'html')
            msg.attach(part2)

            # Envoi
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email envoyé à {destinataire}: {sujet}")
            return True

        except Exception as e:
            logger.error(f"Erreur envoi email à {destinataire}: {e}")
            # Simulation en cas d'erreur
            self._simuler_email(destinataire, sujet, message_html)
            return False

    def envoyer_sms(self, telephone, message):
        """
        Envoie un SMS de notification
        """
        try:
            if not self.sms_api_key:
                logger.warning("Configuration SMS manquante - SMS simulé")
                self._simuler_sms(telephone, message)
                return True

            # Ici vous intégreriez l'API SMS de votre choix (Twilio, etc.)
            # Exemple avec une API fictive :
            # response = requests.post(
            #     'https://api.sms-service.com/send',
            #     json={
            #         'api_key': self.sms_api_key,
            #         'to': telephone,
            #         'from': self.sms_sender,
            #         'message': message
            #     }
            # )

            # Pour l'instant, simulation
            self._simuler_sms(telephone, message)
            return True

        except Exception as e:
            logger.error(f"Erreur envoi SMS à {telephone}: {e}")
            self._simuler_sms(telephone, message)
            return False

    def _simuler_email(self, destinataire, sujet, message):
        """Simule l'envoi d'email pour le développement"""
        logger.info(f"📧 [SIMULATION] Email à {destinataire}")
        logger.info(f"📧 Sujet: {sujet}")
        logger.info(f"📧 Message: {message[:100]}...")

    def _simuler_sms(self, telephone, message):
        """Simule l'envoi de SMS pour le développement"""
        logger.info(f"📱 [SIMULATION] SMS à {telephone}")
        logger.info(f"📱 Message: {message}")

    # Notifications spécifiques au microcrédit
    def notifier_approbation_pret(self, client, pret):
        """Notification d'approbation de prêt"""
        sujet = "🎉 Votre prêt a été approuvé !"

        message_html = f"""
        <html>
        <body>
            <h2>Félicitations {client.prenom} !</h2>
            <p>Votre demande de prêt a été <strong>approuvée</strong>.</p>

            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0;">
                <h3>Détails du prêt :</h3>
                <ul>
                    <li><strong>Montant :</strong> {pret.montant} HTG</li>
                    <li><strong>Durée :</strong> {pret.duree_mois} mois</li>
                    <li><strong>Mensualité :</strong> {pret.mensualite} HTG</li>
                    <li><strong>Date d'approbation :</strong> {pret.date_approbation.strftime('%d/%m/%Y')}</li>
                </ul>
            </div>

            <p>Vous pouvez maintenant accéder à votre espace client pour plus de détails.</p>
            <p><em>L'équipe GMES Microcrédit</em></p>
        </body>
        </html>
        """

        message_text = f"""
        Félicitations {client.prenom} !
        Votre prêt de {pret.montant} HTG a été approuvé.
        Mensualité: {pret.mensualite} HTG sur {pret.duree_mois} mois.
        """

        # Envoyer email
        if client.email:
            self.envoyer_email(client.email, sujet, message_html, message_text)

        # Envoyer SMS
        sms_message = f"GMES: Prêt approuvé! {pret.montant}HTG, {pret.mensualite}HTG/mois. Rendez-vous sur votre espace client."
        self.envoyer_sms(client.telephone, sms_message)

    def notifier_rejet_pret(self, client, pret, motif=None):
        """Notification de rejet de prêt"""
        sujet = "❌ Votre demande de prêt"

        message_html = f"""
        <html>
        <body>
            <h2>Bonjour {client.prenom},</h2>
            <p>Votre demande de prêt n'a malheureusement pas été approuvée.</p>

            {f'<p><strong>Motif :</strong> {motif}</p>' if motif else ''}

            <p>Nous vous encourageons à :</p>
            <ul>
                <li>Vérifier vos informations personnelles</li>
                <li>Consulter nos conseillers</li>
                <li>Soumettre une nouvelle demande ultérieurement</li>
            </ul>

            <p><em>L'équipe GMES Microcrédit</em></p>
        </body>
        </html>
        """

        if client.email:
            self.envoyer_email(client.email, sujet, message_html)

        sms_message = f"GMES: Votre demande de prêt n'a pas été approuvée. Consultez votre email pour plus de détails."
        self.envoyer_sms(client.telephone, sms_message)

    def notifier_remboursement_reussi(self, client, remboursement):
        """Notification de remboursement réussi"""
        sujet = "✅ Remboursement confirmé"

        message_html = f"""
        <html>
        <body>
            <h2>Merci {client.prenom} !</h2>
            <p>Votre remboursement de <strong>{remboursement.montant} HTG</strong> a été enregistré avec succès.</p>

            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0;">
                <p><strong>Date :</strong> {remboursement.date_remboursement.strftime('%d/%m/%Y à %H:%M')}</p>
                <p><strong>Méthode :</strong> {remboursement.type_paiement}</p>
                <p><strong>Référence :</strong> {remboursement.reference}</p>
            </div>

            <p>Votre solde a été mis à jour dans votre espace client.</p>
            <p><em>L'équipe GMES Microcrédit</em></p>
        </body>
        </html>
        """

        if client.email:
            self.envoyer_email(client.email, sujet, message_html)

        sms_message = f"GMES: Remboursement de {remboursement.montant}HTG confirmé. Merci!"
        self.envoyer_sms(client.telephone, sms_message)

    def notifier_rappel_remboursement(self, client, pret, jours_restants):
        """Rappel de remboursement"""
        sujet = "⏰ Rappel de remboursement"

        message_html = f"""
        <html>
        <body>
            <h2>Rappel important</h2>
            <p>Bonjour {client.prenom},</p>

            <p>Votre prochaine échéance de remboursement approche :</p>
            <div style="background: #fff3cd; padding: 15px; border-radius: 5px; margin: 15px 0;">
                <p><strong>Montant :</strong> {pret.mensualite} HTG</p>
                <p><strong>Jours restants :</strong> {jours_restants}</p>
                <p><strong>Prêt :</strong> #{pret.id} - {pret.montant} HTG</p>
            </div>

            <p>Vous pouvez effectuer votre remboursement depuis votre espace client.</p>
            <p><em>L'équipe GMES Microcrédit</em></p>
        </body>
        </html>
        """

        if client.email:
            self.envoyer_email(client.email, sujet, message_html)

        sms_message = f"GMES: Rappel! {jours_restants}j pour rembourser {pret.mensualite}HTG. Prêt #{pret.id}"
        self.envoyer_sms(client.telephone, sms_message)

    def notifier_nouveau_groupe(self, client, groupe):
        """Notification de nouvel adhérent à un groupe"""
        sujet = "👥 Bienvenue dans votre groupe de solidarité"

        message_html = f"""
        <html>
        <body>
            <h2>Bienvenue {client.prenom} !</h2>
            <p>Vous avez rejoint le groupe <strong>{groupe.nom}</strong>.</p>

            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0;">
                <p><strong>Groupe :</strong> {groupe.nom}</p>
                <p><strong>Code :</strong> {groupe.code_groupe}</p>
                <p><strong>Zone :</strong> {groupe.zone}</p>
            </div>

            <p>Vous pouvez maintenant bénéficier des avantages des prêts solidaires.</p>
            <p><em>L'équipe GMES Microcrédit</em></p>
        </body>
        </html>
        """

        if client.email:
            self.envoyer_email(client.email, sujet, message_html)

        sms_message = f"GMES: Bienvenue au groupe {groupe.nom}! Code: {groupe.code_groupe}"
        self.envoyer_sms(client.telephone, sms_message)


# Instance globale
notification_manager = NotificationManager()