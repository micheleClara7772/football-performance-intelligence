# Analyse tactique — mesures descriptives et limites

**Statut : lot 02 proposé en Pull Request ; ne pas confondre mesures et explication causale.**

Les indicateurs ci-dessous portent **uniquement sur les périodes 1 et 2**, à partir des événements StatsBomb réellement importés et validés. Un compteur décrit l'annotation du fournisseur, pas une réalité tactique exhaustive.

| Indicateur | Règle transparente |
| --- | --- |
| Tirs | Nombre d'événements `Shot` par équipe et mi-temps |
| Passes tentées | Nombre d'événements `Pass` |
| Passes réussies | `Pass` sans `pass.outcome` |
| Pressures | Nombre d'événements `Pressure` (pas une intensité ni un taux de réussite du pressing) |
| Ball recoveries | Nombre d'événements `Ball Recovery` |
| Interceptions | Nombre d'événements `Interception` |
| Origines des passes | Zone selon coordonnée x : défensive <40, milieu [40,80[, offensive >=80 |
| Entrées vers dernier tiers | `Pass` réussie ou `Carry` commençant x<80 et terminant x>=80 ; exclut les autres moyens de progression |
| Chronologie | Six intervalles de 15 minutes réglementaires, dernier intervalle de chaque mi-temps comprenant les arrêts de jeu |
| Positions d'événements | Coordonnées observées du fournisseur sur terrain 120×80, non du tracking continu |
| xG | Somme `shot.statsbomb_xg` si la valeur existe pour **tous les tirs** du segment, sinon non disponible |

**Ce qui n'est pas inférable :** intention d'un entraîneur, pression spatiale sans tracking, qualité d'un bloc défensif, causalité d'une variation, volume de possession ou vérité d'un pressing à partir du seul nombre d'événements Pressure.

## Module de séance

Les exercices sont proposés à partir d'un **objectif choisi par l'entraîneur**. Les comptes de tirs, passes et entrées dans le dernier tiers forment un contexte factuel, pas un diagnostic automatique. Durées et consignes sont éditables ; la séance doit être approuvée par le staff avant utilisation.

## Assistant

L'onglet « Assistant IA » contient à ce stade uniquement des **réponses déterministes à questions prédéfinies**. Aucun fournisseur LLM n'est connecté, aucune réponse libre n'est générée. Ne pas le présenter comme une IA opérationnelle lors de la démonstration.

## Validation

Tests unitaires exclusivement avec données synthétiques ; tests CI GitHub ; test interactif sur de **vraies données** encore nécessaire avant une démonstration. Source et droits : voir `docs/data-sources.md` et Issue #3.
