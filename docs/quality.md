# Definition of Done
Une tâche n'est terminée que si : code sur main, comportement testé, données réelles autorisées (ou synthétiques explicitement identifiées), intégration au parcours, sources et limites documentées, validation notée dans l'Issue.

## Tests transversaux
- Scores et chronologie, réconciliation métriques par période.
- Sources, unités, filtres et graphiques.
- Match et timestamps de la vidéo, droits et annotations.
- IA : distinguer faits, hypothèses et conseils ; reconnaître les données manquantes.
- Séances : durées, contraintes, édition et validation.
- API indisponible : aucun résultat simulé présenté comme vrai.

**Audit du 18 novembre :** navigation automatisée des cinq modules réussie avec de vraies données StatsBomb ; parcours métier et publication Cloud pas encore validés manuellement. Consulter [la recette 125 points](recette-pre17.md) et [le bilan](mvp-acceptance-2026-11-18.md).


## Recette automatique 18 novembre

[La matrice automatique des 125 cas](automatic-acceptance.md) suit chaque code et attache des preuves à 60 assertions + 10 cas navigateur. Le [dernier run](https://github.com/micheleClara7772/football-performance-intelligence/actions/runs/44284095730) est réussi ; 55 cas restent honnêtement à vérifier humainement. Les métriques avancées du [module tactique](advanced-metrics.md) sont dérivées uniquement d'événements et non de détection vidéo. Tout bug constaté par le propriétaire doit rester suivi dans l'Issue #15.
