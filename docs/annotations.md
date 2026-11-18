# FPI — Premier lot d'annotations d'événements

**Branche de développement : `feat/event-annotations`**. Aucun media vidéo n'est téléchargé ou intégré.

## Périmètre

- Choisir une équipe, une mi-temps, un type d'action et un intervalle de minutes.
- Choisir un **événement réel** fourni par StatsBomb avec ID, minute et seconde de match.
- Rédiger une **observation** ou une **hypothèse** (interprétation non présentée comme fait).
- Associer facultativement un résumé FIFA **par URL officielle** et son repère manuel **saisi manuellement**.
- Exporter / réimporter les notes en JSON. Les notes restent en mémoire de session jusqu'à l'export ; elles ne sont pas envoyées à un serveur tiers.
- Lors du réimport, vérifier l'identifiant du match, l'événement et ses coordonnées temporelles contre les événements du match chargé.

## Limites

- Aucun alignement automatique d'une minute de match avec une minute d'un montage YouTube.
- Le lecteur YouTube intégré affiche l'erreur 153 en Codespaces ; les liens externes FIFA restent le repli.
- Aucun clip créé, extrait, modifié, téléchargé, réhébergé ou distribué.
- Pas de persistance automatique des notes au-delà de la session : exporter le JSON est nécessaire.
- Les événements sans identifiant ou horodatage utilisable sont exclus de la sélection.
- Les droits commerciaux StatsBomb et FIFA sont toujours ouverts.

## Définition de terminé de cette tranche

- [ ] Tests unitaires de filtrage, minute manuelle, export/réimport, erreur de provenance.
- [ ] Test d'interface avec les vrais événements du match 3869486.
- [ ] Revue du résultat dans Codespaces et absence de médias tiers committés.
- [ ] Pull Request distincte de la PR #20, sans fusion automatique.

Ce volet est un sous-ensemble faisable sans vidéo de l'[Issue #11](https://github.com/micheleClara7772/football-performance-intelligence/issues/11), dont le périmètre complet reste bloqué par la synchronisation sur vidéos autorisées.


## Compatibilité des exports (version 2)

Les nouveaux exports utilisent `schema_version: 2` et `video_sync: manual_player_clock_only`, car le repère peut être celui du replay intégral FIFA+ ou d'un résumé YouTube. **Ce n'est jamais une synchronisation automatique au match.** Les anciens fichiers version 1 (`manual_summary_clock_only`) restent importables. Le replay FIFA+ est consulté **uniquement via un lien externe**, conformément aux conditions du diffuseur.
