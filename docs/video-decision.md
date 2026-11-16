# ADR vidéo FPI — proposition d'arbitrage au 16 novembre 2026

**Statut : solution recommandée, approbation de la source média encore nécessaire.**  
**Décision antérieure :** aucune stratégie vidéo n'avait été approuvée au 15/11. Cette proposition ne doit pas être assimilée à une approbation de vidéo tierce ni à une autorisation d'exploitation de la Coupe du monde.

## Décision technique recommandée pour le MVP

**Option principale : lecteur de séquences originales ou dûment licenciées, fournies par l'utilisateur ou le club (option D du cadrage).**
- Fichier vidéo .mp4/.webm fourni à la démonstration avec droits explicites de lecture, annotation et projection dans le contexte prévu.
- Lecteur annotable : sélection de timestamps, étiquettes/notes tactiques révisables, navigation et export des annotations.
- Stockage local ou en mémoire seulement, jamais commit dans GitHub ; aucune réutilisation externe ni upload cloud sans autorisation.
- L'interface doit indiquer explicitement « vidéo d'illustration provenant d'une autre rencontre / d'un entraînement » si elle n'illustre pas Maroc–Portugal.
- Les timestamps des événements StatsBomb **ne sont pas automatiquement attribués** à une vidéo distincte du match, car ce serait trompeur.

**Option complémentaire : chronologie ou animation 2D des événements StatsBomb (option C), présentée séparément comme visualisation de données, jamais comme replay ou véritable séquence filmée.**

## Options écartées à court terme

- **A — flux/replay officiel Maroc–Portugal :** impossible à intégrer au MVP sans conditions d'intégration, synchronisation, DRM et droits de présentation autorisés vérifiés.
- **B — clips sous licence commerciale :** recevable seulement si une licence écrite couvrant l'extraction, l'annotation, la projection et l'application FPI est obtenue. Achat ou abonnement non autorisé par défaut.
- **Reprise de vidéos YouTube/FIFA sans autorisation écrite :** non retenue. L'accessibilité publique ne suffit pas à autoriser téléchargement, extraction de clips et intégration commerciale.

## Critères de validation de l'option recommandée

- [ ] L'utilisateur confirme disposer d'une vidéo originale ou d'une licence adaptée.
- [ ] Le périmètre exact des droits (annotation, démo, stockage, partage) est documenté.
- [ ] Un lecteur affiche le clip sans fuite de données ni versionnement des médias.
- [ ] Les annotations/timestamps sont testés sur la vidéo réellement autorisée.
- [ ] La démonstration n'affirme jamais qu'un clip tiers représente Maroc–Portugal.
- [ ] Un fonctionnement de repli honnête est prévu si la vidéo autorisée manque.

**Recommandation :** développer un lecteur générique à clips autorisés après confirmation de la source. Jusqu'à cette confirmation, l'Issue #9 reste ouverte et le module n'est pas déclaré terminé.

## Sources de référence

- FIFA : https://inside.fifa.com/fr/tournament-organisation/commercial/news/de-nouvelles-fonctionnalites-pour-ameliorer-lexperience-des-telespectateurs
- Règlement compétition Qatar 2022 : https://digitalhub.fifa.com/ (droits média, reproduction et diffusion soumis à autorisation)
- StatsBomb Open Data (se rapporte aux données événementielles **et non** aux vidéos) : https://github.com/hudl/open-data

## Sources d'images réelles retenues pour un aperçu technique interne (16/11/2026)

Deux résumés **authentiques** du quart de finale, publiés sur la chaîne officielle FIFA sur YouTube :
- Résumé prolongé : https://www.youtube.com/watch?v=5GVitElttLY
- Résumé original : https://www.youtube.com/watch?v=M766FGsv5do

La documentation Streamlit permet de présenter une URL YouTube avec `st.video` et un lien de secours vers la vidéo officielle. Un lecteur YouTube intégré reste soumis aux règles YouTube, aux paramètres d'intégration de la chaîne, au réseau et aux éventuelles restrictions géographiques. **Le fonctionnement réel du lecteur doit être vérifié chez l'utilisateur.**

Cette intégration ne télécharge ni ne copie le média et n'offre pas la synchronisation événement-film ; les minutes du montage ne correspondent pas aux minutes de match StatsBomb. L'aperçu est réservé à un contexte technique non commercial à ce stade. **L'utilisation commerciale dans un produit, une démonstration à un partenaire ou la création de séquences dérivées nécessite une analyse de droits et, le cas échéant, l'autorisation préalable du titulaire.** Les conditions FIFA publiées limitent les usages commerciaux non autorisés : https://inside.fifa.com/fr/terms-of-service et https://inside.fifa.com/fr/terms-of-service-fifaplus

**Statut :** de vraies images officielles accessibles par une source externe, mais aucune licence d'usage commercial ou de création de clips accordée ; Issue #9 ouverte.
