# Sources, qualité et provenance

## Source primaire : StatsBomb Open Data

- Référentiel officiel : https://github.com/hudl/open-data
- README officiel et conditions : https://github.com/hudl/open-data/blob/master/README.md
- Catalogue compétitions : https://github.com/hudl/open-data/blob/master/data/competitions.json
- Matchs Coupe du monde 2022, **identifiants candidats** compétition 43 / saison 106 : https://github.com/hudl/open-data/blob/master/data/matches/43/106.json
- Maroc–Portugal, 10/12/2022 ; **match_id candidat `3869486`**, à confirmer en consultant le catalogue.
- Événements candidats : https://github.com/hudl/open-data/blob/master/data/events/3869486.json
- Compositions candidates : https://github.com/hudl/open-data/blob/master/data/lineups/3869486.json
- 360 : contrôler l'existence et la couverture du fichier `data/three-sixty/3869486.json` ; ne pas présumer qu'il est disponible.

**Vérification obligatoire avant ingestion :** détecter le match par équipes et date, puis comparer l'ID réel au candidat ; télécharger uniquement sur demande, valider le schéma et conserver la provenance.

## Droits et attribution (Issue #3 ouverte)

Le README StatsBomb Open Data indique une disponibilité libre pour la recherche et l'intérêt pour l'analyse football, et demande la mention **StatsBomb** et l'utilisation de son logo lorsque des analyses, résultats ou recherches fondés sur ces données sont publiés, partagés ou distribués. Cela ne constitue **pas une validation automatique d'une démonstration commerciale**. Documenter l'analyse des termes avant usage externe.

Ne pas committer de datasets téléchargés, logos ni de vidéos tiers avant validation des droits. Utiliser le cache local ignoré via `.gitignore`.

## Contrat de métrique

- Match, équipe, URL, version et date de récupération.
- Champs source, périodes et arrêts de jeu, filtres, formule, unité et tests.
- Réconciliation du total match / sous-périodes.
- Pas d'inférence de tracking continu à partir des instantanés StatsBomb 360.
- Pas de chiffres arbitraires dans les vues produit ; les fixtures synthétiques restent réservées aux tests.

## Autre source potentielle

Metrica Sports sample data : https://github.com/metrica-sports/sample-data. Non retenue pour le match de référence.

**État :** identification technique préliminaire ; disponibilité exacte et droits d'usage à vérifier par l'Issue #3.
