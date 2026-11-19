# FPI — parcours entraîneur et analyse Maroc–Portugal

**Décision du 19 novembre 2026 : Maroc–Portugal constitue le sujet principal.** Le clip SoccerTrack du match 117093 ne dure que 12 secondes. Il illustre un essai de détection/suivi automatique, pas une analyse de la rencontre de la Coupe du monde.

## Parcours visible par l'entraîneur

1. **Le match** — faits réels, score, passes et tirs.
2. **Revoir les actions** — replay FIFA+ officiel et résumés YouTube, plus recherche des tirs, récupérations, interceptions et passes associées à un tir à partir des événements StatsBomb.
3. **Analyse tactique** — mi-temps, cartes d'actions, indices descriptifs et notes.
4. **Questions** — demande libre de statistiques du match, sans LLM payant.
5. **Séances** — propositions modifiables par l'entraîneur.
6. **Démo technique** — clip d'un autre match, métriques du suivi et outil d'upload expérimental dans une section repliée.

## Faut-il uploader la vidéo de Maroc–Portugal ?

- **Non** pour les statistiques et les actions enregistrées du match ; elles proviennent déjà de StatsBomb. Le replay officiel peut s'ouvrir à part sur FIFA+.
- **Oui, il faut un fichier exploitable et des droits de traitement** pour détecter directement les joueurs et le ballon dans les pixels de cette rencontre. Ce fichier peut provenir d'un partenaire détenteur des droits ; l'utilisateur n'a pas nécessairement à faire lui-même l'upload.
- Une URL YouTube ou FIFA+ ne suffit ni à obtenir ces permissions ni à exécuter une analyse automatisée. La synchronisation entre événements et vidéo n'est pas acquise.
- L'upload actuel (100 Mo) est un outil de R&D, insuffisant pour un match intégral. Il ne doit pas être présenté comme le parcours normal de l'entraîneur.

## Critères de recette

- Les deux boutons de navigation de la démo technique doivent mener aux pages ciblées sans erreur Streamlit.
- L'application doit ouvrir sur le match Maroc–Portugal, pas SoccerTrack.
- « Revoir les actions » ne demande pas de fichier, affiche les vrais événements filtrables et renvoie aux médias officiels sans copier les images FIFA.
- Les intitulés visibles sont accessibles aux entraîneurs ; les noms de modèles et sources techniques ne sont pas le point central.
- Les tests Python, l'application Streamlit et un parcours réel Chromium doivent réussir avant fusion.

Les limites restent explicites : l'analyse automatique des pixels de Maroc–Portugal et le suivi continu du ballon ne sont pas livrés ; voir Issue #29.
