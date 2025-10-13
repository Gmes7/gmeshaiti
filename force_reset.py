import os
import sys
import subprocess


def force_clean():
    print("🧹 NETTOYAGE FORCÉ EN COURS...")

    # Supprimer tous les fichiers cache
    cache_dirs = [
        '__pycache__',
        'models/__pycache__',
        'routes/__pycache__',
        'utils/__pycache__',
        'instance'
    ]

    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            import shutil
            shutil.rmtree(cache_dir)
            print(f"🗑️  Supprimé: {cache_dir}")

    # Supprimer la base de données
    db_files = ['gmes_microcredit.db', 'test.db']
    for db_file in db_files:
        if os.path.exists(db_file):
            os.remove(db_file)
            print(f"🗑️  Supprimé: {db_file}")

    print("✅ Nettoyage terminé!")


def recreate_database():
    print("\n🗃️  CRÉATION DE LA BASE DE DONNÉES...")

    # Importer et créer l'app
    from app import app
    from database import db

    with app.app_context():
        # Forcer la suppression de toutes les tables
        db.drop_all()

        # Recréer toutes les tables
        db.create_all()

        # Ajouter des données de test
        from models import Admin, Employe, Client, Groupe, Pret
        from datetime import datetime

        # Admin
        admin = Admin(
            nom_utilisateur="admin",
            email="admin@gmes.com",
            role="super_admin"
        )
        admin.definir_mot_de_passe("admin123")
        db.session.add(admin)

        # Employés
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

        # Groupe
        groupe = Groupe(
            nom="Femmes Entrepreneures",
            code_groupe="GRP001",
            zone="Port-au-Prince",
            responsable_id=1
        )
        db.session.add(groupe)

        # Client
        client = Client(
            code_client="CLT001",
            nom="Dupont",
            prenom="Marie",
            telephone="+50912345670",
            email="client@example.com",
            adresse="Port-au-Prince",
            cin="1234567890",
            date_naissance=datetime(1985, 5, 15),
            profession="Commerçante",
            revenu_mensuel=15000,
            groupe_id=1
        )
        client.definir_mot_de_passe("client123")
        db.session.add(client)

        # Prêt de test
        pret = Pret(
            client_id=1,
            groupe_id=1,
            montant=25000,
            taux_interet=12.0,
            duree_mois=12,
            statut="approuve",
            montant_interet=3000,
            montant_total=28000,
            mensualite=2333.33,
            motif="Commerce"
        )
        db.session.add(pret)

        db.session.commit()

    print("✅ Base de données créée avec succès!")


if __name__ == '__main__':
    force_clean()
    recreate_database()
    print("\n🎉 SYSTÈME GMES MICROCRÉDIT PRÊT!")
    print("📋 Comptes de test:")
    print("   👨‍💼 Admin: admin / admin123")
    print("   👨‍💻 Agent: AGT001 / employe123")
    print("   👤 Client: client@example.com / client123")
    print("\n🚀 Lancez: python app.py")