class GamificationSystem:
    def __init__(self):
        self.levels = {
            1: {"name": "Débutant", "points": 0, "badge": "🥉"},
            2: {"name": "Actif", "points": 100, "badge": "🥈"},
            3: {"name": "Fidèle", "points": 300, "badge": "🥇"},
            4: {"name": "Expert", "points": 600, "badge": "💎"},
            5: {"name": "Legendaire", "points": 1000, "badge": "👑"}
        }

    def calculate_points(self, user_actions):
        """Calcule les points basés sur les actions utilisateur"""
        points = 0

        for action in user_actions:
            if action['type'] == 'remboursement_ponctuel':
                points += 10
            elif action['type'] == 'pret_rembourse':
                points += 50
            elif action['type'] == 'participation_groupe':
                points += 5
            elif action['type'] == 'reference':
                points += 25
            elif action['type'] == 'formation_completee':
                points += 15

        return points

    def get_current_level(self, points):
        """Détermine le niveau actuel"""
        current_level = 1
        for level, data in self.levels.items():
            if points >= data['points']:
                current_level = level
            else:
                break
        return current_level

    def get_level_progress(self, points):
        """Calcule la progression dans le niveau actuel"""
        current_level = self.get_current_level(points)
        current_level_data = self.levels[current_level]
        next_level_data = self.levels.get(current_level + 1, current_level_data)

        points_in_level = points - current_level_data['points']
        points_needed = next_level_data['points'] - current_level_data['points']

        progress = (points_in_level / points_needed) * 100 if points_needed > 0 else 100

        return {
            'current_level': current_level,
            'current_level_name': current_level_data['name'],
            'current_badge': current_level_data['badge'],
            'points': points,
            'progress': progress,
            'points_to_next': points_needed - points_in_level,
            'next_level': current_level + 1 if current_level < len(self.levels) else None
        }

    def get_rewards(self, level):
        """Récompenses selon le niveau"""
        rewards = {
            1: ["Accès aux prêts de base", "Support prioritaire"],
            2: ["Taux d'intérêt réduit de 0.5%", "Prêts jusqu'à 50,000 HTG"],
            3: ["Taux d'intérêt réduit de 1%", "Prêts jusqu'à 100,000 HTG", "Assurance gratuite"],
            4: ["Taux d'intérêt réduit de 1.5%", "Prêts jusqu'à 200,000 HTG", "Conseiller dédié"],
            5: ["Taux d'intérêt réduit de 2%", "Prêts illimités", "VIP Service"]
        }
        return rewards.get(level, [])

    def show_gamified_dashboard(self, e=None):
        """Tableau de bord avec gamification"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{self.api_base_url}/gamification/profile", headers=headers)

            if response.status_code == 200:
                profile = response.json()

                # Barre de progression
                progress_bar = ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(f"Niveau {profile['level']} - {profile['level_name']}"),
                            ft.Text(f"{profile['points']} pts")
                        ]),
                        ft.ProgressBar(
                            value=profile['progress'] / 100,
                            width=300,
                            color=ft.colors.BLUE
                        ),
                        ft.Text(f"Prochain niveau: {profile['points_to_next']} pts")
                    ])
                )

                # Badge et récompenses
                rewards_view = ft.Column([
                    ft.Row([
                        ft.Text(profile['badge'], size=40),
                        ft.Column([
                            ft.Text("Récompenses actuelles:", weight=ft.FontWeight.BOLD),
                            *[ft.Text(f"• {reward}") for reward in profile['rewards']]
                        ])
                    ])
                ])

                # Actions récentes
                actions_list = ft.Column([
                    ft.Text("Dernières actions:", weight=ft.FontWeight.BOLD),
                    *[ft.ListTile(
                        leading=ft.Icon(ft.icons.CHECK_CIRCLE, color=ft.colors.GREEN),
                        title=ft.Text(action['description']),
                        subtitle=ft.Text(f"+{action['points']} pts")
                    ) for action in profile['recent_actions']]
                ])

                view = ft.Column([
                    ft.Row([
                        ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda _: self.show_dashboard()),
                        ft.Text("Mon Progrès", size=20, weight=ft.FontWeight.BOLD)
                    ]),

                    progress_bar,
                    rewards_view,
                    actions_list,

                    ft.ElevatedButton(
                        text="🎯 Voir les défis",
                        on_click=self.show_challenges
                    )
                ])

                self.page.clean()
                self.page.add(view)

        except Exception as e:
            self.show_error(f"Erreur: {str(e)}")

    def show_challenges(self, e=None):
        """Défis et objectifs"""
        challenges = [
            {
                "title": "Remboursement parfait",
                "description": "Effectuez 3 remboursements sans retard",
                "reward": "25 pts",
                "progress": "1/3",
                "icon": "💎"
            },
            {
                "title": "Parrainage",
                "description": "Parrainez 2 nouveaux clients",
                "reward": "50 pts",
                "progress": "0/2",
                "icon": "👥"
            },
            {
                "title": "Formation complète",
                "description": "Terminez le module de formation financière",
                "reward": "30 pts",
                "progress": "Non commencé",
                "icon": "📚"
            }
        ]

        challenge_cards = []
        for challenge in challenges:
            card = ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(challenge["icon"], size=20),
                            ft.Text(challenge["title"], weight=ft.FontWeight.BOLD, expand=True),
                            ft.Text(challenge["reward"], color=ft.colors.GREEN)
                        ]),
                        ft.Text(challenge["description"], size=12),
                        ft.Row([
                            ft.Text("Progression:", size=12),
                            ft.Text(challenge["progress"], size=12, weight=ft.FontWeight.BOLD)
                        ]),
                        ft.ElevatedButton(
                            text="Commencer",
                            on_click=lambda e, c=challenge: self.start_challenge(c)
                        )
                    ]),
                    padding=15
                )
            )
            challenge_cards.append(card)

        view = ft.Column([
            ft.Row([
                ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda _: self.show_gamified_dashboard()),
                ft.Text("Défis et Objectifs", size=20, weight=ft.FontWeight.BOLD)
            ]),
            *challenge_cards
        ])

        self.page.clean()
        self.page.add(view)


# Instance globale
gamification = GamificationSystem()