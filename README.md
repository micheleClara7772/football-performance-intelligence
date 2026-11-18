# Football Performance Intelligence — MVP

**État vérifié le 18 novembre 2026.** Cinq modules intégrés dans `main`, calculés depuis des événements StatsBomb réels du match **Maroc 1–0 Portugal** (10 décembre 2022, match `3869486`). L'import explicite permet de valider **3 381 événements**. Le dépôt est privé ; l'application n'est **pas encore accessible via une URL publique** tant que le propriétaire n'a pas créé l'application Streamlit Cloud.

## Accès immédiat aux informations

- **[Déploiement gratuit — action du propriétaire](docs/deploiement-gratuit.md)** : connecter GitHub à https://share.streamlit.io/, choisir `main`, `app.py`, Python 3.11 ; recopier seulement une URL effectivement attribuée.
- **[Dossier de livraison / points à valider](docs/mvp-acceptance-2026-11-18.md)** : tests automatiques, limites, décision de démo.
- **[Parcours de démonstration](docs/demo.md)** : scénario reproductible et plans de secours.
- **[Suivi des Issues](docs/suivi-actuel.md)** · **[Recette complète : 125 contrôles](docs/recette-pre17.md)** · [Issue qualité #15](https://github.com/micheleClara7772/football-performance-intelligence/issues/15).

## Modules testés

1. **Tableau de bord collectif** — match, tirs, passes, xG fournisseur, mi-temps et sources.
2. **Analyse tactique** — indicateurs descriptifs, comparaisons, chronologie, cartes de localisation et annotations par ID d'événement StatsBomb ; export/réimport JSON vérifiés en navigateur.
3. **Vidéos officielles** — rediffusion **intégrale** Maroc–Portugal sur **FIFA+ via lien externe uniquement**, résumés officiels FIFA/YouTube via lien externe et iframe YouTube facultative **dont la lecture réelle n'est pas garantie**.
4. **Assistant factuel** — **8 questions guidées**, sans LLM, sans API payante, réponses traçables aux calculs.
5. **Séances** — quatre objectifs, trois exercices initiaux, matériel/variantes/consignes éditables, contrôle de la durée et des champs avant export JSON, validation humaine nécessaire.

Un bouton « Continuer » permet de parcourir les cinq modules. Les valeurs de référence vérifiées sont : **3 381 événements**, **Maroc 9 / Portugal 12 tirs**, **Maroc 249 / Portugal 731 passes tentées** sur les mi-temps 1/2.

## Contrôles techniques

Toutes les PR **#19, #20, #21, #22, #23, #24** sont fusionnées après contrôles GitHub Actions. Dernière tranche : [Python / tests #44277188457](https://github.com/micheleClara7772/football-performance-intelligence/actions/runs/44277188457) et [StatsBomb réel / Chromium #44277188528](https://github.com/micheleClara7772/football-performance-intelligence/actions/runs/44277188528), tous deux réussis avant fusion. Les résultats automatiques ne remplacent **ni la recette manuelle ni la vérification du déploiement public**.

## Conditions et périmètre

**L'utilisateur a choisi le 18 novembre un MVP sur un match, sans vues 360 ni LLM payant.** Aucune licence commerciale FIFA/StatsBomb n'est confirmée ; la diffusion à un partenaire à 22 h doit rester conditionnée à la clarification des droits et du périmètre. L'autorisation de déployer le code FPI ne donne pas de droits sur des vidéos ou données tierces.

**FIFA+ interdit l'intégration de sa plateforme dans une iframe tierce :** le match complet doit donc être ouvert sur la plateforme officielle. Ne pas confondre l'existence de l'iframe YouTube des résumés avec une lecture réellement vérifiée.

## Développement

Python 3.11, Streamlit, Pandas, Plotly, Pytest, `src/fpi`, tests sous `tests/`. Dépendances versionnées dans `requirements/py311-linux.lock`, avec `requirements.txt` pour Streamlit Cloud. Voir [DEVELOPMENT.md](DEVELOPMENT.md) et [architecture](docs/architecture.md).

**Échéances demandées :** revue interne mercredi 18 novembre 2026 à **16 h (Paris)** ; partenaire envisagé à **22 h**, **sous réserve des autorisations et des tests réels**. Aucune livraison asynchrone ni disponibilité horaire garantie par une simple fusion GitHub.
