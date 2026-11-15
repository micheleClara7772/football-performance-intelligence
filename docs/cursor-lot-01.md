# Lot Cursor 01 — démarrage du MVP FPI

**Statut : spécification prête ; aucune opération dans Cursor encore effectuée.**
**Échéance visée : 16 novembre 2026.**
**Issues principales : #3, #4 et #5.**
**Dépôt :** https://github.com/micheleClara7772/football-performance-intelligence

## Consigne prête à coller dans Cursor Agent

Tu es chargé de développer la première tranche verticale de Football Performance Intelligence (FPI). Travaille sur le dépôt GitHub existant. Avant de coder, lis `README.md`, `docs/architecture.md`, `docs/product.md`, `docs/data-sources.md`, `docs/quality.md` et `docs/video-decision.md`. Consulte les Issues #3, #4, #5.

Crée la branche `feat/bootstrap-fpi` depuis `main`. Ne modifie pas directement `main` ; ouvre une Pull Request à la fin, sans fusion automatique.

### Exigence prioritaire : environnement de développement isolé, reproductible et exportable

**Contrainte utilisateur :** ne pas installer les dépendances FPI globalement sur son ordinateur et, dans la mesure du possible, ne faire tourner aucune installation ni aucun service de développement FPI sur sa machine locale.

1. **Choix prioritaire : exécution distante** (par exemple un GitHub Codespace existant ou un environnement Linux distant) **uniquement si l'accès depuis Cursor est réellement pris en charge et après vérification des quotas/coûts**. Ne pas déclencher de facturation, créer de ressource payante ou exécuter de commande privilégiée sans accord explicite.
2. **Reproductibilité :** ajouter un `.devcontainer/devcontainer.json` et sa définition d'image/configuration adaptée à Python 3.11 pour pouvoir reconstruire l'environnement ailleurs. Aucun besoin d'installer les packages Python globalement. Éviter de supposer que Docker est déjà installé sur le PC : une utilisation locale de Dev Containers exige un moteur de conteneurs local.
3. **Dans l'environnement isolé (distant de préférence)**, créer un `.venv/` **propre au projet** et l'utiliser pour chaque installation, exécution et test. Utiliser explicitement l'interpréteur `.venv/bin/python` (Linux/macOS) ou `.venv\\Scripts\\python.exe` (Windows) pour éviter les erreurs de terminal. `.venv/` est déjà ignoré par Git.
4. Un `venv` local **n'assure pas à lui seul zéro installation sur le PC** : il requiert une installation Python de base et installe toujours les dépendances sur le disque local, seulement dans le dossier isolé. **Ne pas le substituer silencieusement à la demande d'environnement distant**.
5. **Livrable exportable** : versionner `pyproject.toml` et un jeu de versions résolues ou un fichier de verrouillage reproductible, la configuration devcontainer, `.env.example` sans secrets, les scripts de lancement et le README. Ne jamais versionner `.venv/`, `.env`, caches, secrets, données tierces non autorisées ou images de conteneurs. La portabilité se fait par **recréation** de l'environnement, jamais par copie du `venv`.
6. **Si Cursor ne peut pas accéder à un environnement distant autorisé**, documenter précisément le blocage et demander un arbitrage avant toute installation locale, activation d'un service payant ou changement d'éditeur. Aucun basculement implicite vers une installation globale sur Windows.

### Développement à réaliser

1. **Python et installation isolée.** Python 3.11+, dépendances Streamlit/Pandas/Plotly/pytest, package `src/fpi`, `pyproject.toml` avec installation éditable (`python -m pip install -e ".[dev]"` via l'interpréteur du `.venv`), et un `app.py` racine. Tester les commandes **dans l'environnement distant isolé** et documenter Windows PowerShell et macOS/Linux pour un export ultérieur, sans y installer de dépendances maintenant.
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
- Pas de secrets, de fausses citations, de faux résultats, de cloud payant ou consommation de quota payant sans validation, ni de prétention que le MVP est terminé.
- Pas d'installation système ou globale sur le poste utilisateur. Pas d'installation Docker locale par défaut. Si l'exécution distante est inaccessible depuis Cursor, remonter le blocage avant de continuer.
- Ne fusionne pas la Pull Request avant validation.

### Validation attendue

- Installation des dépendances exécutée sans échec **uniquement dans l'environnement isolé**, avec chemin de l'interpréteur et lieu d'exécution vérifiés.
- Reproduction de l'environnement documentée par configuration devcontainer, dépendances verrouillées et README ; aucune dépendance globale ni `.venv` commité.
- Situation de l'exécution distante confirmée : URL/type d'environnement et coût nul ou accord préalable ; sinon blocage explicite.
- `streamlit run app.py` ouvre les cinq sections.
- Mode sans données honnête ; récupération sur demande du match réel ou message d'erreur exploitable.
- `python -m pytest` vert et `python scripts/verify_scaffold.py` vert.
- Pull Request vers `main`, liée aux Issues #3/#4/#5, avec commandes réellement exécutées, résultats des tests, capture d'écran, limites connues et prochaine action.

**Rends compte des blocages plutôt que d'inventer une réussite.**
