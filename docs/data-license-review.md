# Revue des droits — StatsBomb Open Data et médias (16 novembre 2026)

**Statut : vérification partielle, autorisation commerciale NON confirmée.**
Ceci est un état des vérifications, pas un avis juridique.

## Ce que la source officielle permet d'affirmer

La page [StatsBomb Open Data](https://github.com/hudl/open-data/blob/master/README.md) présente un sous-ensemble de données ouvert à l'intérêt pour l'analytique du football et aux projets de recherche. Son paragraphe **Terms & Conditions** impose, en cas de publication, partage ou distribution d'analyses/insights dérivés :
1. mentionner la source des données comme **StatsBomb** ;
2. utiliser le **logo StatsBomb**, disponible dans le [Media Pack](https://statsbomb.com/media-pack/).

La structure officielle contient les JSON de catalogues, matchs, événements, compositions et certains instantanés 360. **Les 360 ne sont pas un suivi vidéo ou tracking continu.**

## Ce qui N'EST PAS établi

- Licence expresse pour une application commerciale diffusée ou revendue, même si les données sont dites « open ».
- Autorisation de redistribuer les JSON, de republier les données en base, de céder/sous-licencier ou d'incorporer les données dans une plateforme tierce commerciale.
- Autorisation de projeter/découper/intégrer une vidéo de la Coupe du monde. Les **droits vidéo sont indépendants** de l'accès StatsBomb.
- Condition de licence PDF (`LICENSE.pdf`) non vérifiée exhaustivement dans cette revue : ne pas supposer qu'elle est identique au seul README.

## Politique FPI en attendant clarification

- Tests techniques et analyses en environnement de développement interne uniquement.
- Source et mentions d'attribution visibles ; pas de publication publique de graphiques dérivés sans respecter les exigences de marque et d'attribution.
- Ne pas inclure de JSON tiers, logos binaires ou séquences télévisées dans le dépôt.
- Avant démonstration de produit commercial à un tiers ou mise en ligne, demander une confirmation écrite au détenteur des droits pour le périmètre exact.
- Documenter par écrit la nature de l'audience (privée/publique), la finalité commerciale, le mode d'affichage et l'absence éventuelle de redistribution des données brutes.

## Questions à adresser à StatsBomb / Hudl

1. Les données du match Maroc–Portugal (Open Data, match 3869486) peuvent-elles être exploitées dans une démonstration privée d'un prototype FPI présenté à un partenaire commercial ?
2. L'application peut-elle télécharger et mettre en cache les JSON chez son utilisateur pour calculer des statistiques sans les redistribuer ?
3. En cas de commercialisation ou d'hébergement public de FPI, quelles licences/permissions supplémentaires sont nécessaires ?
4. Quelle forme de crédit et quelles conditions d'usage du logo pour une application Streamlit privée et ses captures de démonstration ?

**Décision légale actuelle :** pas de feu vert commercial déduit du README. L'Issue #3 reste ouverte jusqu'à réception et revue de l'autorisation appropriée.

## Documents primaires

- StatsBomb : https://github.com/hudl/open-data/blob/master/README.md
- Licence jointe par le fournisseur : https://github.com/hudl/open-data/blob/master/LICENSE.pdf
- FIFA (droits média/territoires) : https://inside.fifa.com/tournament-organisation/commercial/news/new-features-for-broadcast-fan-experience
