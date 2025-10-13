from app import create_app
from database import db
from models import Admin, Employe, User, Groupe, Pret
from datetime import datetime


def initialiser_base_donnees():
    app = create_app()

    with app.app_context():
        print("🗃️  Création des tables...")
        db.create_all()

        print("👤 Création des comptes administrateur...")
        # Admin principal
        if not Admin.query.first():
            admin = Admin(
                nom_utilisateur="admin",
                email="admin@gmes-microcredit.com",
                role="super_admin"
            )
            admin.definir_mot_de_passe("admin123")
            db.session.add(admin)
            print("✅ Admin créé: admin / admin123")

        print("👥 Création des employés...")
        # Employés
        if not Employe.query.first():
            employes = [
                Employe(
                    matricule="AGT001",
                    nom="Pierre",
                    prenom="Jean",
                    email="agent@gmes.com",
                    telephone="+50912345678",
                    poste="agent_credit",
                    date_embauche=datetime.utcnow()
                ),
                Employe(
                    matricule="CAI001",
                    nom="Marie",
                    prenom="Claude",
                    email="caissier@gmes.com",
                    telephone="+50912345679",
                    poste="caissier",
                    date_embauche=datetime.utcnow()
                )
            ]
            for emp in employes:
                emp.definir_mot_de_passe("employe123")
                db.session.add(emp)
            print("✅ Employés créés: AGT001 / employe123")

        print("👥 Création des groupes...")
        # Groupe
        if not Groupe.query.first():
            groupe = Groupe(
                nom="Femmes Entrepreneures",
                code_groupe="GRP001",
                zone="Port-au-Prince",
                responsable_id=1
            )
            db.session.add(groupe)
            print("✅ Groupe créé: Femmes Entrepreneures")

        print("👤 Création du client de démonstration...")
        # Client de test
        if not User.query.first():
            client = User(
                code_client="CLT001",
                nom="Dupont",
                prenom="Marie",
                telephone="+50912345670",
                email="client@example.com",
                adresse="Port-au-Prince, Haiti",
                cin="1234567890",
                date_naissance=datetime(1985, 5, 15),
                profession="Commerçante",
                revenu_mensuel=15000,
                groupe_id=1
            )
            client.definir_mot_de_passe("client123")
            db.session.add(client)
            print("✅ Client créé: client@example.com / client123")

        print("💰 Création d'un prêt de démonstration...")
        # Prêt de démonstration
        if not Pret.query.first():
            pret = Pret(
                client_id=1,
                groupe_id=1,
                montant=25000,
                taux_interet=12.0,
                duree_mois=12,
                date_demande=datetime.utcnow(),
                statut="approuve",
                montant_interet=3000,
                montant_total=28000,
                mensualite=2333.33,
                motif="Commerce"
            )
            db.session.add(pret)
            print("✅ Prêt de démonstration créé: 25,000 HTG")

        db.session.commit()
        print("🎉 Base de données GMES Microcrédit initialisée avec succès!")
        print("\n📋 COMPTES DE TEST:")
        print("   👨‍💼 Admin:        admin / admin123")
        print("   👨‍💻 Agent:        AGT001 / employe123")
        print("   💰 Caissier:      CAI001 / employe123")
        print("   👤 Client:        client@example.com / client123")
        print("\n🌐 Accédez à: http://localhost:5000")


if __name__ == '__main__':
    initialiser_base_donnees()