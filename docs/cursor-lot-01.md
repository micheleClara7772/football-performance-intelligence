# Lot Cursor 01 — démarrage du MVP FPI

**Statut : spécification prête ; aucune opération dans Cursor encore effectuée.**
**Échéance visée : 16 novembre 2026.**
**Issues principales : #3, #4 et #5.**
**Dépôt :** https://github.com/micheleClara7772/football-performance-intelligence

## Consigne prête à coller dans Cursor Agent

Tu es chargé de développer la première tranche verticale de Football Performance Intelligence (FPI). Travaille sur le dépôt GitHub existant. Avant de coder, lis `README.md`, `docs/architecture.md`, `docs/product.md`, `docs/data-sources.md`, `docs/quality.md` et `docs/video-decision.md`. Consulte les Issues #3, #4, #5.

Crée la branche `feat/bootstrap-fpi` depuis `main`. Ne modifie pas directement `main` ; ouvre une Pull Request à la fin, sans fusion automatique.

### Développement à réaliser

1. **Python et installation.** Python 3.11+, dépendances Streamlit/Pandas/Plotly/pytest, package `src/fpi`, `pyproject.toml` avec installation éditable (`pip install -e ".[dev]"`), et un `app.py` racine. Documente et teste les commandes sous Windows PowerShell, et documente macOS/Linux.
2. **Application navigable.** Cinq sections : Dashboard, Analyse tactique, Vidéo, Assistant IA et Séances. Les modules non implémentés affichent clairement « en préparation ». Aucun faux KPI, faux graphique ou résultat généré à partir de données inventées ne doit apparaître dans l'interface.
3. **Données réelles.** Implémente dans `src/fpi/data` un chargeur local, un validateur et un téléchargement **explicite, sur demande** via StatsBomb Open Data. Recherche le match Maroc–Portugal (10/12/2022) par date/équipes dans le catalogue 2022 ; confirme le match_id pressenti `3869486`. Vérifie présence/schéma des événements. Utilise un cache `data/` ignoré par Git, et documente les URLs et dates de récupération. Aucune récupération silencieuse à l'import ni à chaque rafraîchissement Streamlit. Affiche une erreur claire hors ligne / si données absentes.
4. **Premières métriques.** Construis des fonctions déterministes pour compter les tirs et découper les événements par période, avec définitions et provenance. Affiche seulement les nombres réellement calculés. Conserve la séparation ingestion → métriques → UI.
5. **Tests.** Ajoute des tests pytest avec petites fixtures artificielles limitées aux tests : filtre des périodes, comptage des tirs, absence/fichier malformé et validations d'identité du match. La commande `python scripts/verify_scaffold.py` continue de passer ; la CI existante intègre aussi pytest.
6. **Documentation.** Ajoute instructions d'installation, commandes de lancement (`streamlit run app.py`), état des modules, limites des données et description des tests.

### Contraintes non négociables

- Le match Maroc–Portugal est le scénario approuvé ; l'outil doit garder un découplage équipe/données pour extension future.
- StatsBomb Open Data exige attribution et logo pour la publication ou le partage d'analyses ; les droits de démonstration commerciale ne sont pas encore validés. Ne committe aucune copie de données tierces ou média sous licence ambiguë. Ne ferme pas l'Issue #3 avant vérification de licence et disponibilité effective.
- **Ne décide pas de la stratégie vidéo.** La section Vidéo doit indiquer « stratégie en cours de validation ». Ne télécharge pas de replay.
- L'IA n'a pas encore de modèle choisi : aucun appel distant ni clé requis pour lancer l'application. Les séances restent « en préparation » jusqu'à implémentation réelle.
- Pas de secrets, de fausses citations, de faux résultats, de cloud payant, ni de prétention que le MVP est terminé.
- Ne fusionne pas la Pull Request avant validation.

### Validation attendue

- Installation des dépendances exécutée sans échec dans un environnement propre.
- `streamlit run app.py` ouvre les cinq sections.
- Mode sans données honnête ; récupération sur demande du match réel ou message d'erreur exploitable.
- `python -m pytest` vert et `python scripts/verify_scaffold.py` vert.
- Pull Request vers `main`, liée aux Issues #3/#4/#5, avec commandes réellement exécutées, résultats des tests, capture d'écran, limites connues et prochaine action.

**Rends compte des blocages plutôt que d'inventer une réussite.**
