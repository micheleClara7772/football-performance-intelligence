# FPI — suivi de référence au 18 novembre 2026

**Objectif :** revue interne à 16 h (Paris), revue partenaire envisagée à 22 h. Statut technique : **MVP cinq modules intégré dans main**. Statut de mise en ligne : **déploiement Streamlit Community Cloud en attente d'autorisation du propriétaire** ; aucune URL publique vérifiée. **Droits commerciaux StatsBomb/FIFA non confirmés.**

[GitHub Project](https://github.com/users/micheleClara7772/projects/1/views/1) · [125 contrôles manuels — Issue #15](https://github.com/micheleClara7772/football-performance-intelligence/issues/15) · [Procédure d'hébergement](deploiement-gratuit.md) · [Plan démo](demo.md) · [Bilan et réserves](mvp-acceptance-2026-11-18.md)

## État des cinq modules

| Module | État technique | Limites / décisions ouvertes |
|---|---|---|
| Tableau de bord | Fonctionnel, **3 381 événements** de Maroc–Portugal vérifiés, tirs 9/12, passes tentées 249/731 | Un seul match de référence ; pas un historique multi-match |
| Tactique / annotations | Deux périodes, 8 signaux avancés événementiels, positions, notes observation/hypothèse, export/réimport JSON testé | Repère vidéo **manuel** ; pas de détection de pixels, tracking ni synchronisation réelle |
| Vidéo | **Replay intégral FIFA+ externe**, deux résumés FIFA/YouTube externes, iframe YouTube **facultative** | **FIFA+ ne doit pas être intégré**, lecture effective iframe YouTube non confirmée, droits commerciaux non acquis |
| Assistant libre | **Saisie libre** en français : tirs, passes, xG, joueurs, comparaison, zones et signaux avancés ; sans LLM | Compréhension linguistique limitée aux métriques disponibles, pas d'IA générative ni frais d'API |
| Séances | Quatre thèmes, durée 45/60/75, effectifs 6–30, consignes/matériel/variantes, édition, export validé | Brouillon, validation entraîneur indispensable |

**Parcours guidé :** Tableau de bord → Analyse tactique et annotations → Vidéo → Assistant → Séances. Navigation Chromium de cinq modules réussie, sans garantie de lecture réelle du flux vidéo tiers.

## Historique des Pull Requests fusionnées

- [#19](https://github.com/micheleClara7772/football-performance-intelligence/pull/19) : fondations initiales.
- [#20](https://github.com/micheleClara7772/football-performance-intelligence/pull/20) : tactique, assistant factuel, séances et stabilisation.
- [#21](https://github.com/micheleClara7772/football-performance-intelligence/pull/21) : annotations et rechargement JSON vérifiés.
- [#22](https://github.com/micheleClara7772/football-performance-intelligence/pull/22) : Streamlit Community Cloud prêt, lien officiel FIFA+ complet et aperçu YouTube facultatif.
- [#23](https://github.com/micheleClara7772/football-performance-intelligence/pull/23) : assistant **8 questions**, séances enrichies et validation de l'export.
- [#24](https://github.com/micheleClara7772/football-performance-intelligence/pull/24) : parcours guidé, repères de replay versionnés et cache atomique concurrent.

**Derniers tests validés avant fusion #24 :** [CI Python #44277188457](https://github.com/micheleClara7772/football-performance-intelligence/actions/runs/44277188457), [événements StatsBomb réels + navigateur #44277188528](https://github.com/micheleClara7772/football-performance-intelligence/actions/runs/44277188528). Le navigateur vérifie que l'iframe YouTube existe, pas que ses images ont effectivement joué.

## Évolutions vérifiées le 18 novembre

- [PR #26](https://github.com/micheleClara7772/football-performance-intelligence/pull/26) : assistant à **saisie libre**, moteur local gratuit, questions reformulables et refus des demandes non mesurables. [CI Python](https://github.com/micheleClara7772/football-performance-intelligence/actions/runs/44282967303) et [Chromium StatsBomb réel](https://github.com/micheleClara7772/football-performance-intelligence/actions/runs/44282962003) réussies.
- [PR #27](https://github.com/micheleClara7772/football-performance-intelligence/pull/27) : **rapport automatique 125 cas : 60 calculs + 10 contrôles navigateur réussis ; 55 nécessitent une intervention humaine**. [Preuve GitHub Actions](https://github.com/micheleClara7772/football-performance-intelligence/actions/runs/44282825736).
- [PR #28](https://github.com/micheleClara7772/football-performance-intelligence/pull/28) : **8 signaux avancés sur le match entier** à partir des événements, métriques et limites expliquées dans [advanced-metrics.md](advanced-metrics.md). [Validation complète](https://github.com/micheleClara7772/football-performance-intelligence/actions/runs/44284095730).
- [Issue #29](https://github.com/micheleClara7772/football-performance-intelligence/issues/29) : analyse **de la vidéo complète elle-même** (joueurs, ballon, tracking) bloquée par l'absence d'un fichier/usage autorisé et de tests visuels sur vérité terrain.
- [Revue des sources vidéo alternatives](video-source-review-2026-11-18.md) : Footballia, Dailymotion, RTVE Play, FIFA+, sans droits de réutilisation présumés.

## Points critiques à traiter avant de déclarer « prêt à être présenté »

1. **[#15](https://github.com/micheleClara7772/football-performance-intelligence/issues/15), [#16](https://github.com/micheleClara7772/football-performance-intelligence/issues/16)** — recette humaine complète et répétition 7–10 min ; **34 des 125 cases humaines** avaient été cochées ; la CI en vérifie séparément **70**, sans cocher les 55 restantes.
2. **Hébergement** — connecter le GitHub privé à Streamlit Community Cloud, choisir Python 3.11, faire déployer par le propriétaire et tester **la véritable URL** en navigation privée.
3. **Vidéo** — confirmer l'accès au replay FIFA+ complet depuis l'environnement utilisateur ; l'embed Youtube est expérimental (anciens refus 153).
4. **[#3](https://github.com/micheleClara7772/football-performance-intelligence/issues/3)** — clarification du droit d'utilisation/publication commerciale des données StatsBomb et de ses obligations d'attribution/logo.
5. **[#9](https://github.com/micheleClara7772/football-performance-intelligence/issues/9), [#10](https://github.com/micheleClara7772/football-performance-intelligence/issues/10), [#11](https://github.com/micheleClara7772/football-performance-intelligence/issues/11)** — droits de diffusion / intégration vidéo et synchronisation annotée, non réalisés ; annotations textuelles manuelles seules disponibles.
6. **[#2](https://github.com/micheleClara7772/football-performance-intelligence/issues/2)** — mise à jour automatique des colonnes GitHub Project V2 non assurée par ce connecteur ; les labels d'Issues ne déplacent pas les cartes du Project.

## Décision

**GO technique pour les tests internes sur la version fusionnée.** **NO-GO non levé pour promettre une URL publique déjà active, une vidéo FIFA+ intégrée ou des droits commerciaux obtenus.** Toute démonstration au partenaire doit être réévaluée au regard de la licence et du fonctionnement public effectivement constaté.
