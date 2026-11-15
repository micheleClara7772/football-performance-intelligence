# Compte rendu de validation FPI — 16 novembre 2026

**Branche vérifiée :** `feat/tactical-insights-training`.  
**PR :** https://github.com/micheleClara7772/football-performance-intelligence/pull/20  
**Workflow de données réelles et navigateur :** https://github.com/micheleClara7772/football-performance-intelligence/actions/runs/43774202940  
**Workflow de tests Python :** https://github.com/micheleClara7772/football-performance-intelligence/actions/runs/43774202919

## 1. Contrôle sur les véritables données

- Source : StatsBomb Open Data via GitHub, match `3869486`, Maroc–Portugal, 10/12/2022, score 1–0.
- Lecture du catalogue officiel, téléchargement sur demande, validation d'identité/structure et relecture du cache dans la CI.
- **3 381 événements validés.**
- Tirs (périodes 1+2) : **Maroc 9**, **Portugal 12**.
- Passes tentées (périodes 1+2) : **Maroc 249**, **Portugal 731**.
- Les calculs collectifs, tactiques, chronologiques, réponse factuelle, générateur de séances ont réussi leurs contrôles.
- Les données brutes ont été téléchargées dans le runner GitHub temporaire ; aucune donnée du match n'a été intégrée aux commits.

## 2. Contrôle par navigateur

Un Chromium headless a ouvert Streamlit et vérifié :
1. Dashboard avec graphiques Plotly et données réelles, sans état « pas de données » ;
2. Analyse tactique avec comparaisons des mi-temps et graphique ;
3. Assistant factuel avec question et réponse calculée ;
4. Générateur de séances avec proposition et bouton d'export JSON ;
5. Écran Vidéo avec message explicite sur le module non implémenté.

**Résultat : PASS ; cinq captures enregistrées dans l'artefact `fpi-browser-proof` du workflow.**

### Revue visuelle des captures (1440 × 960)

- Navigation lisible et cohérente sur les cinq écrans.
- Dashboard : score, chiffres et diagramme d'évolution correctement affichés.
- Tactique : équipe, indicateur, valeurs de première/deuxième mi-temps et graphique visibles.
- Assistant : statut « aucun modèle IA », question et réponse sourcée affichés.
- Séances : formulaire, sélection du thème, durée, effectif et début de la proposition visibles.
- Vidéo : signalement honnête du module non implémenté.
- Défauts mineurs à corriger avant livraison publique : certains noms d'équipes restent en anglais (« Morocco »), présentation encore rudimentaire, graphiques/cartes à améliorer ; les captures sur le premier écran ne permettent pas de juger tous les éléments sous la ligne de flottaison.

**Limite :** ce test navigateur automatique avec revue des captures n'est pas encore un test utilisateur complet (navigation manuelle prolongée, responsive, lecteur vidéo réel, téléchargements sur plusieurs plateformes).

## 3. Droits

- Attribution à StatsBomb et usage du logo pour publication/partage d'analyses : confirmés par README officiel.
- **Autorisation commerciale : non confirmée.**
- Droits vidéo FIFA : **non confirmés**.
- Voir [revue de licence](data-license-review.md).

## 4. Arbitrage vidéo

- Recommandation : utiliser exclusivement des clips filmés par l'utilisateur ou dûment licenciés, avec lecteur et annotations, en les dissociant clairement du match de référence.
- Visualisations des événements StatsBomb autorisées par le projet comme aide à l'analyse, mais elles ne sont pas des images vidéo.
- Source et droits de la vidéo doivent être validés avant réalisation et présentation ; l'Issue #9 reste ouverte.
- Voir [ADR vidéo](video-decision.md).

## Décision sur la Pull Request #20

Le **socle technique sur données réelles est validé** avec preuve CI et navigateur. La Pull Request reste **draft et non fusionnée** jusqu'à arbitrage sur l'étendue finale du lot et revue des limites ; cette validation n'est **pas** un feu vert à la distribution commerciale.
