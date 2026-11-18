# Football Performance Intelligence — MVP

**État vérifié le 18 novembre 2026.** Cinq modules intégrés dans `main`, calculés depuis des événements StatsBomb réels du match **Maroc 1–0 Portugal** (10 décembre 2022, match `3869486`). L'import explicite permet de valider **3 381 événements**. Le dépôt est privé ; l'application n'est **pas encore accessible via une URL publique** tant que le propriétaire n'a pas créé l'application Streamlit Cloud.

## Accès immédiat aux informations

- **[Déploiement gratuit — action du propriétaire](docs/deploiement-gratuit.md)** : connecter GitHub à https://share.streamlit.io/, choisir `main`, `app.py`, Python 3.11 ; recopier seulement une URL effectivement attribuée.
- **[Dossier de livraison / points à valider](docs/mvp-acceptance-2026-11-18.md)** : tests automatiques, limites, décision de démo.
- **[Parcours de démonstration](docs/demo.md)** : scénario reproductible et plans de secours.
- **[Suivi des Issues](docs/suivi-actuel.md)** · **[Recette complète : 125 contrôles](docs/recette-pre17.md)** · [Issue qualité #15](https://github.com/micheleClara7772/football-performance-intelligence/issues/15).

## Modules testés

1. **Tableau de bord collectif** — match, tirs, passes, xG fournisseur, mi-temps et sources.
2. **Analyse tactique** — comparaisons, chronologie, positions d'événements, **8 signaux avancés sur les 2 mi-temps**, annotations StatsBomb, export/réimport JSON vérifiés en navigateur.
3. **Vidéos officielles** — rediffusion **intégrale** Maroc–Portugal sur **FIFA+ via lien externe uniquement**, résumés officiels FIFA/YouTube via lien externe et iframe YouTube facultative **dont la lecture réelle n'est pas garantie**.
4. **Assistant libre gratuit** — questions en français saisies sans menu figé : réponses calculées depuis StatsBomb, sans LLM ni API payante ; demandes sans métrique identifiable refusées.
5. **Séances** — quatre objectifs, trois exercices initiaux, matériel/variantes/consignes éditables, contrôle de la durée et des champs avant export JSON, validation humaine nécessaire.

Un bouton « Continuer » permet de parcourir les cinq modules. Les valeurs de référence vérifiées sont : **3 381 événements**, **Maroc 9 / Portugal 12 tirs**, **Maroc 249 / Portugal 731 passes tentées** sur les mi-temps 1/2.

## Contrôles techniques

Les PR **#19 à #28** sont intégrées dans `main`. La [dernière validation StatsBomb réel + Chromium + matrice de recette](https://github.com/micheleClara7772/football-performance-intelligence/actions/runs/44284095730) et les [tests Python](https://github.com/micheleClara7772/football-performance-intelligence/actions/runs/44284095982) sont réussis.

**Recette historique 125 cas : 60 contrôles calculés, 10 contrôles navigateur, 55 contrôles restants à vérifier humainement.** Les 34 cases que l'utilisateur avait cochées dans l'Issue #15 restent inchangées ; voir [le rapport automatique](docs/automatic-acceptance.md).

## Exploration du match intégral

- [FIFA+ officiel](https://www.plus.fifa.com/en/showcase/relive-qatar-2022/2725ef5c-b40e-43b8-ba26-27081c5f17a6) : replay complet sur la plateforme diffuseur, pas en iframe.
- D'autres pistes de visionnage sont recensées dans [la revue des sources vidéo](docs/video-source-review-2026-11-18.md), sans présumer de leurs licences d'extraction.
- **La détection de joueurs et du ballon dans les pixels n'est pas encore livrée.** Elle exige un fichier vidéo exploitable/autorisé et une évaluation, suivie dans l'[Issue #29](https://github.com/micheleClara7772/football-performance-intelligence/issues/29). Les huit signaux avancés actuels proviennent **des événements StatsBomb**, pas d'images FIFA.

## Conditions et périmètre

**L'utilisateur a choisi le 18 novembre un MVP sur un match, sans vues 360 ni LLM payant.** Aucune licence commerciale FIFA/StatsBomb n'est confirmée ; la diffusion à un partenaire à 22 h doit rester conditionnée à la clarification des droits et du périmètre. L'autorisation de déployer le code FPI ne donne pas de droits sur des vidéos ou données tierces.

**FIFA+ interdit l'intégration de sa plateforme dans une iframe tierce :** le match complet doit donc être ouvert sur la plateforme officielle. Ne pas confondre l'existence de l'iframe YouTube des résumés avec une lecture réellement vérifiée.

## Développement

Python 3.11, Streamlit, Pandas, Plotly, Pytest, `src/fpi`, tests sous `tests/`. Dépendances versionnées dans `requirements/py311-linux.lock`, avec `requirements.txt` pour Streamlit Cloud. Voir [DEVELOPMENT.md](DEVELOPMENT.md) et [architecture](docs/architecture.md).

**Échéances demandées :** revue interne mercredi 18 novembre 2026 à **16 h (Paris)** ; partenaire envisagé à **22 h**, **sous réserve des autorisations et des tests réels**. Aucune livraison asynchrone ni disponibilité horaire garantie par une simple fusion GitHub.
