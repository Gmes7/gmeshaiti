import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta


class AnalyticsDashboard:
    def __init__(self):
        self.metrics = {}

    def update_metrics(self):
        """Met à jour les métriques en temps réel"""
        # Prêts
        total_prets = Pret.query.count()
        prets_actifs = Pret.query.filter_by(statut='approuve').count()
        montant_circulation = db.session.query(db.func.sum(Pret.montant)).filter_by(statut='approuve').scalar() or 0

        # Remboursements
        remboursements_mois = Remboursement.query.filter(
            Remboursement.date_remboursement >= datetime.utcnow().replace(day=1)
        ).count()

        # Clients
        nouveaux_clients_mois = Client.query.filter(
            Client.date_inscription >= datetime.utcnow().replace(day=1)
        ).count()

        self.metrics = {
            'total_prets': total_prets,
            'prets_actifs': prets_actifs,
            'montant_circulation': montant_circulation,
            'remboursements_mois': remboursements_mois,
            'nouveaux_clients_mois': nouveaux_clients_mois,
            'taux_remboursement': self.calculate_repayment_rate(),
            'rotation_fonds': self.calculate_fund_rotation()
        }

    def create_repayment_trend_chart(self):
        """Crée un graphique de tendance des remboursements"""
        # Données des 6 derniers mois
        dates = []
        amounts = []

        for i in range(6):
            date = datetime.utcnow() - timedelta(days=30 * i)
            month_start = date.replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

            total = db.session.query(db.func.sum(Remboursement.montant)).filter(
                Remboursement.date_remboursement.between(month_start, month_end)
            ).scalar() or 0

            dates.append(month_start.strftime('%b %Y'))
            amounts.append(total)

        dates.reverse()
        amounts.reverse()

        fig = go.Figure(data=go.Scatter(x=dates, y=amounts, mode='lines+markers'))
        fig.update_layout(
            title="Tendances des Remboursements",
            xaxis_title="Mois",
            yaxis_title="Montant (HTG)"
        )

        return fig.to_json()

    def create_loan_distribution_chart(self):
        """Répartition des prêts par statut"""
        status_counts = db.session.query(Pret.statut, db.func.count(Pret.id)).group_by(Pret.statut).all()

        labels = [status[0] for status in status_counts]
        values = [status[1] for status in status_counts]

        fig = px.pie(values=values, names=labels, title="Répartition des Prêts")
        return fig.to_json()

    def create_performance_metrics(self):
        """Métriques de performance"""
        return {
            'taux_approbation': (self.metrics['prets_actifs'] / self.metrics['total_prets'] * 100) if self.metrics[
                                                                                                          'total_prets'] > 0 else 0,
            'valeur_client_moyenne': self.metrics['montant_circulation'] / max(self.metrics['prets_actifs'], 1),
            'croissance_clients': self.calculate_growth_rate(),
            'efficacite_operationnelle': self.calculate_operational_efficiency()
        }


# Instance globale
analytics = AnalyticsDashboard()