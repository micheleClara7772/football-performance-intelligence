# FPI — Où en est-on ? Quelles sont les prochaines étapes ?

**Point de pilotage actualisé le 16 novembre 2026 (soirée, heure de Paris), après fusion de la PR #20.**  
**Démonstration envisagée : vendredi 20 novembre 2026, rendez-vous encore à confirmer.**

[Ouvrir le tableau GitHub Project](https://github.com/users/micheleClara7772/projects/1/views/1) · [Voir les 18 Issues](https://github.com/micheleClara7772/football-performance-intelligence/issues) · [PR #20](https://github.com/micheleClara7772/football-performance-intelligence/pull/20)

## 1. État réel et preuves

| Élément | Situation |
|---|---|
| Dépôt privé, plan de suivi | Créés ; GitHub Project privé et Issues importées confirmés par l'utilisateur |
| Version 1 (socle) | **Fusionnée** dans `main` via [PR #19](https://github.com/micheleClara7772/football-performance-intelligence/pull/19) |
| Version 2 (tactique / assistant factuel / séances / extraits FIFA) | **PR #20 fusionnée dans main** (commit `fb037707`) ; contrôles réussis. Le nouveau lot d'annotations est ouvert en [PR #21](https://github.com/micheleClara7772/football-performance-intelligence/pull/21) (brouillon, non fusionné) |
| CI Python, tests automatisés | [Dernier run sur la PR #20 : réussi](https://github.com/micheleClara7772/football-performance-intelligence/actions/runs/43947283070) |
| Données réelles + navigateur Chromium | [Dernier run sur la PR #20 : réussi](https://github.com/micheleClara7772/football-performance-intelligence/actions/runs/43947283120) |
| Recette utilisateur Codespaces | Streamlit fonctionne, **3 381 événements** importés manuellement ; cinq rubriques ouvertes et tableaux/graphes affichés |
| Cache des données | Pas de téléchargement automatique ; import volontaire, puis relecture du cache tant que le Codespace conserve ses fichiers |
| Vraies images FIFA | Résumé YouTube **lisible sur YouTube** ; lecture intégrée FPI **en échec (YouTube 153)** ; iframe retirée de la démonstration, bouton externe fonctionnel |
| IA | Assistant **factuel déterministe**, pas encore de modèle LLM connecté |
| Séances | Proposition éditable et export JSON, validation humaine nécessaire ; contenu à enrichir |
| Droits | **StatsBomb commercial : non confirmé ; vidéo FIFA commerciale : non confirmée** |
| Environnement | Codespace distant utilisé et **arrêté par l'utilisateur** ; pas d'installation FPI sur son PC |
| Reproductibilité technique | Versions Python 3.11/Linux **figées dans `requirements/py311-linux.lock` (39 paquets)** et utilisées dans CI/Codespaces ; installation et `pip check` réussis, sans hashes binaires |

**Important :** la navigation des cinq rubriques ne signifie pas que les cinq modules finaux sont intégralement livrés. L'ancien « 0/7 étapes vérifiées » du socle documentaire était obsolète, mais le **parcours métier complet en sept étapes** n'est pas encore homologué.

## Validation complète avant le chantier du 17 novembre

**[Checklist détaillée : 125 contrôles](recette-pre17.md)** — cocher directement les cases dans [l'Issue qualité #15](https://github.com/micheleClara7772/football-performance-intelligence/issues/15). Les tests automatisés ont réussi, mais les contrôles manuels restent **à faire**. La [PR #21](https://github.com/micheleClara7772/football-performance-intelligence/pull/21) est toujours en brouillon et non fusionnée.

## 2. Ce qu'on fait maintenant, dans l'ordre

### Lundi 16 novembre — Stabiliser la PR #20 (P0)

**Pilote : développement FPI / GitHub ; validation produit : porteur du projet.**  
Tickets : [#4](https://github.com/micheleClara7772/football-performance-intelligence/issues/4), [#8](https://github.com/micheleClara7772/football-performance-intelligence/issues/8), [#15](https://github.com/micheleClara7772/football-performance-intelligence/issues/15).

- [x] Remplacer `use_container_width` par `width="stretch"` et franciser les principaux libellés visibles, sans altérer les valeurs StatsBomb.
- [x] Mettre l'accès YouTube officiel en avant ; retirer le lecteur intégré en erreur 153 de la démonstration.
- [x] Vérifier les 27 fichiers du diff (aucune vidéo, donnée tierce ni secret repérés) ; rejouer les [tests Python](https://github.com/micheleClara7772/football-performance-intelligence/actions/runs/43947283070) et le [test réel/navigateur](https://github.com/micheleClara7772/football-performance-intelligence/actions/runs/43947283120) sur la même tête de PR.
- [x] Versionner les 39 dépendances Python 3.11/Linux et les dépendances du navigateur, vérifier la reconstruction isolée avec `pip check`.
- [x] Sortir la PR #20 du mode brouillon : **prête pour revue**.
- [x] Le porteur a explicitement autorisé la fusion et la **PR #20 est fusionnée**. Les droits commerciaux StatsBomb/FIFA restent ouverts.

**Critère de fin :** PR #20 verte, limites documentées, pas de vidéo copiée ni de chiffres fictifs.

### Mardi 17 novembre — Analyse tactique et annotations traçables (démarré le 16 au soir)

Tickets : [#6](https://github.com/micheleClara7772/football-performance-intelligence/issues/6), [#7](https://github.com/micheleClara7772/football-performance-intelligence/issues/7), [#8](https://github.com/micheleClara7772/football-performance-intelligence/issues/8), [#11](https://github.com/micheleClara7772/football-performance-intelligence/issues/11).

- [ ] Revoir les définitions et limites des tirs, passes, périodes, entrées dans le dernier tiers et cartes.
- [x] Première implémentation des annotations textuelles sur [PR #21](https://github.com/micheleClara7772/football-performance-intelligence/pull/21) : minute du **match StatsBomb** distincte du minutage **manuel du montage YouTube** (tests en cours).
- [x] Prévoir notes observation/hypothèse, source StatsBomb et éventuelle URL officielle FIFA ; aucun média copié.
- [ ] Vérifier sur la PR #21 le parcours navigateur, l'export, les erreurs et le rechargement JSON d'annotations. **#11 reste bloquée pour la synchronisation vidéo complète tant que #10 n'est pas autorisée.**

### Mercredi 18 novembre — Relier les cinq modules

Tickets : [#12](https://github.com/micheleClara7772/football-performance-intelligence/issues/12), [#13](https://github.com/micheleClara7772/football-performance-intelligence/issues/13), [#14](https://github.com/micheleClara7772/football-performance-intelligence/issues/14).

- [ ] IA : maintenir les réponses exactes sourcées ; toute API LLM payante reste soumise à un choix/accord explicite.
- [ ] Séances : objectifs, exercices, matériel, contraintes, variantes, édition et validation humaine.
- [ ] Tester les sept étapes du parcours, avec indication honnête des manques et lien vidéo externe comme repli.

### Jeudi 19 novembre — Qualité et répétition

Tickets : [#15](https://github.com/micheleClara7772/football-performance-intelligence/issues/15), [#16](https://github.com/micheleClara7772/football-performance-intelligence/issues/16).

- [ ] Tests complets, erreurs réseau, absence de données, sécurité, absence de secrets et de médias non autorisés.
- [ ] Répétition chronométrée de 7–10 minutes ; plan B si YouTube ou StatsBomb ne répondent pas.
- [ ] Vérifier la confirmation du rendez-vous ; ne pas laisser un Codespace actif inutilement.

### Vendredi 20 novembre — Démonstration envisagée / retour

Ticket : [#18](https://github.com/micheleClara7772/football-performance-intelligence/issues/18).

- [ ] Si rendez-vous et droits appropriés confirmés : démonstration selon le périmètre autorisé.
- [ ] Sinon : présentation limitée aux éléments dont les droits sont validés, ou report.
- [ ] Noter les retours et définir le post-MVP. [#17 (360)](https://github.com/micheleClara7772/football-performance-intelligence/issues/17) est facultatif / P2, **pas** sur le chemin critique.

## 3. Blocages réels — à ne pas masquer

1. **[#3 — StatsBomb](https://github.com/micheleClara7772/football-performance-intelligence/issues/3) :** licence/permission commerciale pas validée ; les tests privés et l'ingestion technique sont réussis.
2. **[#9 — Vidéo FIFA](https://github.com/micheleClara7772/football-performance-intelligence/issues/9) :** YouTube disponible directement, mais erreur 153 en iframe FPI ; droit de diffusion/annotation commerciale non confirmé.
3. **[#10 — Lecteur vidéo complet](https://github.com/micheleClara7772/football-performance-intelligence/issues/10) et [#11 — synchronisation](https://github.com/micheleClara7772/football-performance-intelligence/issues/11) :** dépendent d'une source audiovisuelle autorisée et d'un repérage vérifié.
4. **[#2 — Suivi GitHub Project](https://github.com/micheleClara7772/football-performance-intelligence/issues/2) :** Project créé/import validé par l'utilisateur ; les champs personnalisés et la synchronisation automatique des colonnes ne sont pas vérifiés via le connecteur.

## 4. Comment lire les statuts

- **Done** : terminé avec preuves ;
- **In Review** : code existant, vérification ou fusion manquante ;
- **In Progress** : en cours, pas encore complet ;
- **Ready** : prochain chantier prêt à démarrer ;
- **Blocked** : dépendance juridique, technique ou projet ouverte ;
- **Backlog** : prévu après les priorités immédiates.

Les labels `status:*` des **Issues** sont maintenus avec le fichier [backlog/issues.json](../backlog/issues.json). **Limite technique :** le connecteur GitHub de cette conversation ne peut pas modifier directement les champs du **Project V2**. Les changements d'étiquettes d'Issues **ne déplacent pas automatiquement les cartes entre les colonnes du tableau** : ne pas confondre les deux.

**La PR #20 est fusionnée. La PR #21 reste un lot de développement indépendant et non fusionné.**

**La page présente constitue le suivi de référence.** Les engagements de livraison dépendent des tests, des droits des contenus et de la confirmation du rendez-vous.
