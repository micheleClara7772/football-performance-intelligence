# FPI — Développer sans installer les dépendances sur le PC

**L'application n'est pas hébergée automatiquement.** Le premier lot est exécuté en CI GitHub Actions dans des machines éphémères, et les dépendances Python sont dans leur `.venv`. Cela n'installe **aucune dépendance FPI sur ton PC** et ne nécessite pas d'abonnement Cursor.

## Démarrer depuis le navigateur, si souhaité

Le dépôt contient `.devcontainer/devcontainer.json` pour un environnement distant compatible **GitHub Codespaces**. L'ouverture d'un Codespace crée une machine distante et peut consommer ton quota GitHub ; **vérifie les quotas et frais potentiels avant toute création**. Aucun Codespace n'est créé automatiquement par ce dépôt.

Dans le Codespace (terminal intégré au navigateur), après le postCreateCommand :

```bash
.venv/bin/python -m streamlit run app.py --server.address 0.0.0.0
```

Le port 8501 est déclaré dans la configuration devcontainer. Utilise l'onglet `PORTS` du Codespace pour afficher l'application. Les données StatsBomb ne seront téléchargées qu'après clic sur « Importer depuis StatsBomb » dans l'interface.

## Reproduction locale, si choisie plus tard

### PowerShell (nécessite Python déjà installé sur le PC)

```powershell
py -3.11 -m venv .venv
.venv\Scripts\python.exe -m pip install -e '.[dev]'
.venv\Scripts\python.exe -m streamlit run app.py
```

### Linux / macOS

```bash
python3.11 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m streamlit run app.py
```

**Un `venv` local isole les dépendances, mais les télécharge quand même sur la machine locale.** Pour zéro installation FPI sur le PC, rester dans Codespaces ou un autre environnement distant. Ne pas copier `.venv` lors de l'export : pousser le code sur GitHub, reconstruire l'environnement à partir de `pyproject.toml` et du devcontainer.

## Vérifications

```bash
.venv/bin/python scripts/verify_scaffold.py
.venv/bin/python -m pytest
```

`pyproject.toml` définit des **plages de versions compatibles**, pas encore un verrouillage complet des versions transitives. Un lockfile devra être généré et testé avant de promettre des reconstructions à l'identique.

## Données et licences

Match de référence **Maroc 1–0 Portugal (10 décembre 2022)**. Catalogue StatsBomb 2022 : `matches/43/106.json`, match ID `3869486` (source vérifiée, **revalidation automatique à l'import**). Le stockage `data/raw/` est ignoré. Aucune vidéo ni fichier de données tiers n'est livré dans ce dépôt. Voir `docs/data-sources.md` et l'Issue #3 avant une présentation commerciale.

## État des cinq sections

- Dashboard : premiers indicateurs réels après import explicite ; sinon état vide.
- Analyse tactique : mesures descriptives et emplacements des tirs (pas d'interprétation automatique).
- Vidéo : stratégie à déterminer.
- Assistant IA : non configuré.
- Séances : en préparation.

## Lot 02 — exploration tactique et séances (branche de revue)

La vue Analyse tactique propose une comparaison des mi-temps, une chronologie d'événements et des positions dans le repère StatsBomb. Le module Séances propose un brouillon modifiable sur choix explicite du thème par l'entraîneur. L'onglet Assistant IA n'effectue **aucun appel de modèle** : il répond provisoirement à des questions factuelles prédéfinies. La vidéo reste à arbitrer.

Définitions et limites : `docs/tactical-metrics.md`. Ne pas confondre une variation descriptive avec sa cause tactique.
