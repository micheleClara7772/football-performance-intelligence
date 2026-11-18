# FPI — Développer sans installer les dépendances sur le PC

**L'application n'est pas hébergée automatiquement.** Le premier lot est exécuté en CI GitHub Actions dans des machines éphémères, et les dépendances Python sont dans leur `.venv`. Cela n'installe **aucune dépendance FPI sur ton PC** et ne nécessite pas d'abonnement Cursor.

## Démarrer depuis le navigateur, si souhaité

Le dépôt contient `.devcontainer/devcontainer.json` pour un environnement distant compatible **GitHub Codespaces**. L'ouverture d'un Codespace crée une machine distante et peut consommer ton quota GitHub ; **vérifie les quotas et frais potentiels avant toute création**. Aucun Codespace n'est créé automatiquement par ce dépôt.

Dans le Codespace (terminal intégré au navigateur), après le `postCreateCommand` qui installe les dépendances verrouillées :

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
.venv/bin/python -m pip install -r requirements/py311-linux.lock
.venv/bin/python -m pip install --no-deps -e .
.venv/bin/python -m pip check
.venv/bin/python -m streamlit run app.py
```

**Un `venv` local isole les dépendances, mais les télécharge quand même sur la machine locale.** Pour zéro installation FPI sur le PC, rester dans Codespaces ou un autre environnement distant. Ne pas copier `.venv` lors de l'export : pousser le code sur GitHub, reconstruire l'environnement à partir de `pyproject.toml` et du devcontainer.

## Vérifications

```bash
.venv/bin/python scripts/verify_scaffold.py
.venv/bin/python -m pytest
```

`pyproject.toml` conserve des plages de compatibilité. Pour **reproduire l'environnement de référence Python 3.11 Linux**, les versions directes et transitives sont figées dans `requirements/py311-linux.lock`, produites à partir d'un véritable environnement GitHub Actions du 16/11/2026. Le navigateur des tests est figé séparément dans `requirements/py311-linux-browser.lock`. Les workflows vérifient `pip check` et la correspondance exacte entre le lock et `pip freeze`. Cette liste verrouille les **versions**, pas les empreintes de fichiers de distribution ; elle ne constitue pas une garantie de reproductibilité bit à bit ni un audit de sécurité. Pour Windows/macOS, le `pyproject.toml` reste la méthode d'installation de repli, et une résolution/validation par plateforme sera nécessaire avant de promettre une reconstruction identique.

## Données et licences

Match de référence **Maroc 1–0 Portugal (10 décembre 2022)**. Catalogue StatsBomb 2022 : `matches/43/106.json`, match ID `3869486` (source vérifiée, **revalidation automatique à l'import**). Le stockage `data/raw/` est ignoré. Aucune vidéo ni fichier de données tiers n'est livré dans ce dépôt. Voir `docs/data-sources.md` et l'Issue #3 avant une présentation commerciale.

## État des cinq sections

- Dashboard : premiers indicateurs réels après import explicite ; sinon état vide.
- Analyse tactique : mesures descriptives et emplacements des tirs (pas d'interprétation automatique).
- Vidéo : vrais résumés FIFA via liens externes, lecteur intégré désactivé à cause de l'erreur YouTube 153 observée ; droits commerciaux ouverts.
- Assistant IA : questions factuelles prédéfinies (aucun LLM connecté).
- Séances : propositions éditables et exportables en JSON, à valider par un entraîneur.

## Lot 02 — exploration tactique et séances (branche de revue)

La vue Analyse tactique propose une comparaison des mi-temps, une chronologie d'événements et des positions dans le repère StatsBomb. Le module Séances propose un brouillon modifiable sur choix explicite du thème par l'entraîneur. L'onglet Assistant IA n'effectue **aucun appel de modèle** : il répond provisoirement à des questions factuelles prédéfinies. La vidéo reste à arbitrer.

Définitions et limites : `docs/tactical-metrics.md`. Ne pas confondre une variation descriptive avec sa cause tactique.


## Stabilisation du 16 novembre — dépendances reproductibles

Les environnements Python 3.11 sont créés dans Codespaces ou les runners GitHub, jamais sur l'ordinateur utilisateur. Le lock `requirements/py311-linux.lock` (versions exactes) est désormais versionné et utilisé dans Codespaces et la CI. Il est construit depuis la résolution effectivement installée dans GitHub Actions le 16/11/2026. Les tests de réinstallation depuis le lock doivent encore être confirmés sur la nouvelle tête de PR avant de déclarer ce point terminé.

Le replay intégral FIFA+ officiel est proposé par lien externe, car FIFA+ interdit les iframes non autorisées. Les résumés YouTube sont accessibles via liens externes, avec un essai facultatif du lecteur natif Streamlit (résultat de lecture non garanti, erreur 153 antérieure). Les labels d'équipes sont traduits pour l'affichage uniquement ; les chaînes StatsBomb `Morocco` / `Portugal` restent inchangées dans les calculs et dans les données source.


## Déploiement Streamlit Community Cloud (sans frais d'hébergement)

Le dépôt contient désormais `requirements.txt` en racine. Il installe les dépendances du lock Linux/Python 3.11 et le paquet local `fpi`. Le même parcours d'installation est vérifié dans GitHub Actions. Le propriétaire peut utiliser [le guide de déploiement gratuit](docs/deploiement-gratuit.md) et garder le dépôt source privé. La création du compte/l'autorisation GitHub Streamlit doivent être effectuées par le propriétaire. Aucun sous-domaine n'est présumé créé tant que l'URL n'a pas été réellement ouverte.
