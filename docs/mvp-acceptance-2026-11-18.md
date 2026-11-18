# FPI — dossier d'acceptation technique du 18 novembre 2026

**Cible :** revue interne à 16 h et, sous réserves, présentation partenaire envisagée à 22 h. **Ce dossier ne constitue pas une recette humaine complète.**

## Livrables intégrés dans main

- PR [#21](https://github.com/micheleClara7772/football-performance-intelligence/pull/21) — annotations StatsBomb, export et réimport vérifiés avec seconde session Chromium.
- PR [#22](https://github.com/micheleClara7772/football-performance-intelligence/pull/22) — `requirements.txt`, thème Streamlit, documentation de déploiement gratuit, liens FIFA+ intégral et résumés YouTube.
- PR [#23](https://github.com/micheleClara7772/football-performance-intelligence/pull/23) — assistant factuel huit questions, séances enrichies, validation avant export.
- PR [#24](https://github.com/micheleClara7772/football-performance-intelligence/pull/24) — parcours guidé, références vidéo manuelles v2, écriture cache atomique concurrente.

- PR [#26](https://github.com/micheleClara7772/football-performance-intelligence/pull/26) — assistant francophone à saisie libre déterministe, sans API ni paiement.
- PR [#27](https://github.com/micheleClara7772/football-performance-intelligence/pull/27) — rapport automatique 125 codes : 60 PASS calculs, 10 PASS navigateur, 55 A_VALIDER_HUMAINEMENT, aucune case humaine cochée par automatisme.
- PR [#28](https://github.com/micheleClara7772/football-performance-intelligence/pull/28) — 8 indicateurs avancés calculés à partir des deux mi-temps d'événements StatsBomb, **pas des images**.

## Tableau de preuves CI avant fusion

| Lot | Tests Python et versionnement | Test de données StatsBomb réelles + navigateur | État |
|---|---|---|---|
| PR #21 | [#44274775143](https://github.com/micheleClara7772/football-performance-intelligence/actions/runs/44274775143) : succès | [#44274775559](https://github.com/micheleClara7772/football-performance-intelligence/actions/runs/44274775559) : succès | Fusionnée |
| PR #22 | [#44276337150](https://github.com/micheleClara7772/football-performance-intelligence/actions/runs/44276337150) : succès | [#44276337197](https://github.com/micheleClara7772/football-performance-intelligence/actions/runs/44276337197) : succès | Fusionnée |
| PR #23 | [#44276247454](https://github.com/micheleClara7772/football-performance-intelligence/actions/runs/44276247454) : succès | [#44276247457](https://github.com/micheleClara7772/football-performance-intelligence/actions/runs/44276247457) : succès | Fusionnée |
| PR #24 | [#44277188457](https://github.com/micheleClara7772/football-performance-intelligence/actions/runs/44277188457) : succès | [#44277188528](https://github.com/micheleClara7772/football-performance-intelligence/actions/runs/44277188528) : succès | Fusionnée |
| PR #26 | [#44282967303](https://github.com/micheleClara7772/football-performance-intelligence/actions/runs/44282967303) : succès | [#44282962003](https://github.com/micheleClara7772/football-performance-intelligence/actions/runs/44282962003) : succès | Fusionnée |
| PR #27 | [#44282826862](https://github.com/micheleClara7772/football-performance-intelligence/actions/runs/44282826862) : succès | [#44282825736](https://github.com/micheleClara7772/football-performance-intelligence/actions/runs/44282825736) : succès, 70 cas auto | Fusionnée |
| PR #28 | [#44284095982](https://github.com/micheleClara7772/football-performance-intelligence/actions/runs/44284095982) : succès | [#44284095730](https://github.com/micheleClara7772/football-performance-intelligence/actions/runs/44284095730) : succès, 70 cas auto | Fusionnée |

**Constat validé :** Maroc 1–0 Portugal ; 3 381 événements ; 9/12 tirs et 249/731 passes tentées sur périodes 1/2. Les tests naviguent dans les cinq rubriques, produisent une annotation et rechargent effectivement le JSON dans une nouvelle session.

**Limites des tests :** Playwright contrôle la présence de l'iframe YouTube et des liens, **pas la lecture des images** ; il ne vérifie pas l'OAuth Streamlit Cloud ni la disponibilité régionale de FIFA+. Un workflow vert ne remplace ni les **125 contrôles manuels** de [l'Issue #15](https://github.com/micheleClara7772/football-performance-intelligence/issues/15), ni l'avis du partenaire.

## Répartition de la recette automatisée

Le dernier rapport **fpi-auto-acceptance-125** prouve 60 cas par calculs et contrôles métier, ainsi que 10 cas par parcours navigateur, sur le match réel. **55 cas** restent `A_VALIDER_HUMAINEMENT` : lecture effective des images, ergonomie/acceptation, OAuth/publication Cloud, licences et décisions. Les 34 cases préalablement cochées par l'utilisateur ne sont pas modifiées ni additionnées aux 70 validations comme si tous les scénarios étaient distincts.

Pour trouver les 125 statuts individuels, ouvrir [l'exécution Actions #44284095730](https://github.com/micheleClara7772/football-performance-intelligence/actions/runs/44284095730), puis l'artefact `fpi-auto-acceptance-125`.

## Travaux restant à faire avant validation externe

- [ ] **Par le propriétaire** : connecter GitHub à Streamlit Community Cloud, déployer **main** / **app.py** / **Python 3.11**, rendre public si approprié. [Guide](deploiement-gratuit.md). **Aucune URL publique n'a été vérifiée.**
- [ ] Tester le site effectivement déployé depuis un navigateur non connecté, la navigation, l'import et les exports.
- [ ] Contrôler la lecture humaine du replay FIFA+ officiel **hors FPI** et, si souhaité, de l'iframe YouTube facultative.
- [ ] Finir la recette de l'utilisateur : **34/125 cases humaines avaient été cochées**, sans modification automatique ; ne pas modifier ces cases sans résultat humain.
- [ ] Valider explicitement les droits commerciaux StatsBomb, ses exigences d'attribution et de logo ([#3](https://github.com/micheleClara7772/football-performance-intelligence/issues/3)).
- [ ] Valider droits média FIFA avant tout usage de vidéo ou diffusion commerciale ([#9](https://github.com/micheleClara7772/football-performance-intelligence/issues/9), [#10](https://github.com/micheleClara7772/football-performance-intelligence/issues/10)).
- [ ] Répéter le scénario et consigner les résultats dans [#16](https://github.com/micheleClara7772/football-performance-intelligence/issues/16).

## Analyse vidéo complète : non livrée, malgré les signaux avancés

Le match intégral FIFA+ est consultable chez le diffuseur ; Footballia et Dailymotion proposent d'autres visions du match mais aucune licence d'extraction et d'analyse n'a été confirmée. Une capture/destruction de DRM ou une intégration sans autorisation n'est pas intégrée à FPI. Le moteur CV de suivi ballon/joueurs est suivi comme chantier distinct dans [#29](https://github.com/micheleClara7772/football-performance-intelligence/issues/29) ; les 8 nouveaux signaux sont calculés **sur données événementielles**.

## Verdict et responsabilités

**GO pour revue technique interne du MVP cinq modules.** **GO public non encore vérifié** (aucune URL), **GO vidéo intégrale embarquée impossible actuellement** sans licence d'intégration, et **GO commercial partenaire non établi** tant que les droits ne sont pas examinés. Aucune prétention de conformité juridique globale ni de recette manuelle exhaustive.

Aucun coût d'hébergement nécessaire sur le plan gratuit Streamlit Community Cloud, sous réserve de ses limitations ; aucune connexion de compte ne peut être inventée ou autorisée automatiquement.
