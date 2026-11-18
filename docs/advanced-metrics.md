# Signaux tactiques avancés issus des événements de match

Implémentation gratuite dans `fpi.analysis.advanced` et l'onglet **Analyse tactique → Signaux avancés**.

Ces indicateurs portent sur le **match entier, périodes 1 et 2**, à partir des **événements StatsBomb Open Data** importés. Ils n'exigent pas de vidéo et **ne sont pas des résultats de vision par ordinateur**.

| Indicateur | Définition exacte et limites |
|---|---|
| Passes progressives (proxy) | Passe réussie, début x<80, fin x-début x >=15 dans le repère 120×80 |
| Renversement latéral (proxy) | Passe réussie avec déplacement latéral abs(y_fin-y_début)>=35 |
| Récupération haute | Événement `Ball Recovery` dont x>=60 |
| Récupération dernier tiers | Événement `Ball Recovery` dont x>=80 |
| Passe associée à un tir | `pass.shot_assist=true` explicitement fourni |
| Passe décisive | `pass.goal_assist=true` explicitement fourni |
| Tir depuis la surface (proxy) | `Shot` situé dans le rectangle x>=102 et 18<=y<=62 |
| Récupération après pression (proximité) | Récupération <=8s après une pression enregistrée de la même équipe et de la même période |

Les identifiants de possession StatsBomb (s'ils existent) peuvent aussi produire le nombre de séquences annotées et de séquences contenant un tir. **Il ne s'agit pas du temps de possession**. Donnée absente = valeur vide, jamais un zéro inventé.

**Limites critiques :** une proximité entre une pression et une récupération ne prouve aucune relation causale ; un passeur peut participer à plusieurs actions ; la position d'un événement ne permet pas de suivre un joueur, de reconstruire le placement défensif ou d'extraire automatiquement les images FIFA.

Enrichissement du futur : détection vidéo des joueurs et du ballon via un modèle libre et un fichier complet **licencié**, évaluation sur vérité terrain, synchronisation manuelle initiale du flux avec les événements StatsBomb. Sans licence ni fichier autorisé, cette partie ne peut pas être testée de façon honnête.
