# Football Performance Intelligence (FPI) — Contexte de passation produit et technique

**Pour le collaborateur qui reprend la spécification et pour son assistant IA.** Photographie du 21 novembre 2026. La lecture du dépôt porte sur `main` au [commit 708307a, intégration de la PR nº 53](https://github.com/micheleClara7772/football-performance-intelligence/commit/708307a948dbafb6d24a911c8ca97bec3e3537ee). Les éléments livrés ci-dessous sont documentés dans le dépôt. Cette passation n’inclut pas de nouvelle recette en production.

## 1. Le problème que l’équipe cherche à résoudre

Après une rencontre, le staff dispose d’images, de statistiques, de notes prises sur le banc et d’intuitions parfois contradictoires. Il doit retrouver les actions pertinentes, revoir ce qui les précède, comparer réussites et échecs, puis expliquer au coach ce qui mérite son attention. Pendant cette revue, une autre échéance approche déjà : le prochain match. Le coach doit décider quoi conserver, quoi corriger, comment jouer contre cet adversaire et quoi travailler avec les joueurs disponibles.

FPI vise à raccourcir le chemin entre ces deux moments. Le staff doit pouvoir partir d’une question de football, retrouver ses preuves et préparer un débrief. Le coach doit pouvoir comprendre l’argument, le contester, choisir une priorité, la faire travailler et vérifier au match suivant si les joueurs reconnaissent la situation. L’outil complète les logiciels vidéo et statistiques que les équipes utilisent déjà. Réutiliser un découpage existant évite à l’analyste de coder une deuxième fois la même rencontre.

**Trois bénéfices à évaluer séparément :**

- **Temps gagné.** Diminuer le temps entre une question précise et une sélection de séquences que l’analyste juge montrables.
- **Qualité de lecture.** Aider le staff à trouver du contexte, une réussite comparable ou un contre-exemple qui change son interprétation.
- **Pilotage de la préparation.** Permettre de retrouver, pour une rencontre à venir, la priorité retenue, la personne qui la prépare, le travail prévu et le repère à observer le jour du match.

## 2. Utilisateurs, décisions et conditions d’usage

| Utilisateur | Travail attendu | Décision qui lui appartient |
|---|---|---|
| Analyste vidéo ou membre du staff chargé de la revue | Examiner les situations, corriger un classement douteux, retrouver le contexte, annoter et ordonner les illustrations. | Juger si une séquence étaye réellement le constat transmis. |
| Adjoint ou responsable d’un thème | Relier plusieurs lectures, préparer le débrief ou transformer une priorité en exercice adapté à l’effectif. | Proposer le contenu et l’organisation du travail dont il a la charge. |
| Entraîneur principal | Lire une synthèse, examiner les preuves, demander un autre angle, arbitrer les priorités et formuler les consignes. | Choisir le plan de match et le comportement attendu des joueurs. |
| Joueurs ou groupe de postes | Recevoir une consigne et revoir l’action qui l’illustre pendant la causerie ou la séance. | L’accès individuel des joueurs au logiciel reste à cadrer. Un briefing présenté par le coach couvre déjà un premier usage. |

Le travail peut se répartir entre spécialistes ou être réalisé par une même personne. Les rôles techniques Staff et Coach du portail existent déjà. L’affectation métier d’un thème à l’adjoint, à l’analyste ou au coach reste à définir avec chaque encadrement. Prévoir le cas du coach qui suit plusieurs équipes. L’interface et les consignes doivent rester utilisables en français. Le vocabulaire final est à éprouver avec Wissem Maaref et son staff.

## 3. Ce que contient réellement le dépôt

| Livrable | État documenté et implications pour la reprise |
|---|---|
| **Portail privé staff/coach** | Le dossier `portal/` documente une bibliothèque de rencontres et un parcours réel de création, revue, validation et publication d’un dossier. Le coach connecté reçoit une version approuvée, avec message, jusqu’à trois illustrations et point à discuter. Une correction en cours conserve la publication précédente jusqu’à la republication. Le briefing est imprimable en A4 paysage. [Portail privé](https://fpi-staff.vercel.app) · [Guide du portail](../portal/README.md) |
| **Analyse par possession dans le portail** | Chronologie par période et possession StatsBomb, localisation des actions offensives, contexte, annotations et issue de la possession. La comparaison propose une possession de la même équipe, sur une bande latérale similaire, avec un critère de sélection commun. Ces dessins représentent les événements localisés. Une illustration publiée conserve sa version. [Évolution nº 53](https://github.com/micheleClara7772/football-performance-intelligence/pull/53) |
| **Catalogue du portail** | Deux matchs professionnels de la Coupe du monde 2022 : Maroc–Portugal (3869486) et Argentine–France (3869685). Le guide décrit respectivement 254 et 309 situations candidates, sélectionnées à partir de critères de progression, entrée dans le dernier tiers, renversement ou perte candidate. Ces volumes comptent des situations retenues par les règles. [Méthode et horloges](../portal/README.md) |
| **Premier MVP Streamlit** | Python 3.11, Pandas, Plotly et tests Pytest. Cinq modules documentés : tableau de bord, analyse tactique, accès vidéo, assistant factuel francophone et séances éditables avec export JSON. Référence Maroc–Portugal : 3 381 événements, 9 et 12 tirs, 249 et 731 passes tentées respectivement. Les huit signaux avancés décrits dans ce MVP sont calculés à partir d’événements. Le README racine daté du 18 novembre concernait notamment le déploiement Streamlit ; consulter le guide du portail pour l’accès privé ultérieur. [README](../README.md) · [Dossier de recette](mvp-acceptance-2026-11-18.md) |
| **Assistant et séances** | Streamlit accepte des questions libres en français et calcule des réponses pour les métriques reconnues, sans API LLM payante. Le portail documente un assistant factuel limité au périmètre autorisé, avec questions de suivi. Streamlit propose quatre objectifs de séance et des exercices éditables. Le parcours complet reliant un plan de match, une décision du coach, plusieurs séances et leur bilan reste une cible produit. |
| **Vision par ordinateur** | Le dépôt décrit un détecteur CPU YOLOX-Nano, un traitement de fichier vidéo, une commande d’échantillonnage sur la durée du fichier et une démo de suivi de joueurs avec ByteTrack. Sur le clip SoccerTrack de 12 secondes : 60 images à 5 FPS, IDF1 de 62,99 %, dix changements d’identité et aucun ballon détecté. Cette preuve concerne un extrait technique distinct des deux rencontres professionnelles du portail. [Guide vision](video-computer-vision.md) · [Suivi du chantier nº 29](https://github.com/micheleClara7772/football-performance-intelligence/issues/29) |
| **Maquette de parcours exploratoire** | Le prototype présenté dans la conversation utilisait un match fictif, des séquences tactiques animées, deux vues Staff/Coach et une proposition de séance simulée. Il servait à tester l’enchaînement des écrans avant intégration. Le questionnaire de dix arbitrages, les choix recommandés dans ce questionnaire et la maquette n’ont pas valeur de validation utilisateur. |

**Repère de reprise technique.** Le portail utilise une fonction Node et Vercel Blob privé, avec contrôle des rôles côté serveur et écritures conditionnelles. Le MVP Python et le portail ont des points d’entrée et des capacités distincts. Vérifier où vit chaque fonction avant d’ouvrir une issue d’implémentation. Le guide d’architecture historique décrit aussi des intentions antérieures. [Guide de développement](../DEVELOPMENT.md) · [Architecture historique](architecture.md) · [Exploitation du portail](../portal/README.md)

## 4. Le parcours cible à spécifier avec le staff

Les étapes ci-dessous forment un canevas de travail. Plusieurs peuvent avancer en parallèle. Le nombre de jours entre deux matchs, les disponibilités et la répartition des tâches varient entre club et sélection.

| Étape et entrée | Geste utilisateur | Sortie et continuité |
|---|---|---|
| 1. Ouvrir la préparation d’une rencontre | Sélectionner l’équipe, le prochain adversaire et l’échéance. Reprendre les questions déjà posées par le staff. | Une préparation commune, où l’on sait ce qui reste à examiner, à arbitrer ou à travailler. Écran central proposé. |
| 2. Revoir sa propre équipe | Ouvrir le dernier match ou un dossier antérieur. Filtrer les situations, revoir l’avant et l’après, conserver une réussite comparable. | Une observation sourcée, son contexte et une éventuelle hypothèse du staff. Réutiliser la bibliothèque et la revue existantes. |
| 3. Étudier l’adversaire | Chercher dans les rencontres disponibles comment il agit dans une situation comparable : pressing sur relance, transition après perte ou coup de pied arrêté. | Une tendance située et ses exceptions. Le staff peut poursuivre avec ses propres matchs et ses notes si les images adverses manquent. |
| 4. Préparer et transmettre | Ordonner les preuves, distinguer point fort et point à travailler, formuler la question à trancher et publier la sélection. | Un briefing court et vérifiable par le coach. Le brouillon peut évoluer pendant que la dernière version approuvée reste consultable. |
| 5. Arbitrer le plan | Le coach examine les preuves des deux équipes, ajoute sa lecture, demande une autre action ou fixe une consigne. | Priorité retenue, groupe concerné, responsable du suivi et comportement attendu. Une observation peut rester sans suite. |
| 6. Construire le travail terrain | Le coach ou l’adjoint renseigne effectif, gardiens, espace, matériel, durée et séances restantes. Il adapte la proposition de l’assistant. | Fiche terrain avec organisation, consigne, progression, critère observable et séquence de référence. Un message vidéo peut suffire pour certains thèmes. |
| 7. Vérifier en compétition | Avant le coup d’envoi, retrouver les repères décidés. Pendant ou après le match, noter ce qui s’est produit et joindre les preuves disponibles. | Bilan de la priorité et question pour la préparation suivante. La saisie manuelle permet de tester cet usage avant toute analyse vidéo en direct. |

### Exemple de décision à conserver de bout en bout

**Scénario fictif de recette métier.** Le staff relève deux pertes côté droit. Il retrouve aussi une sortie réussie contre un pressing comparable. Sur cette troisième action, le milieu offre une solution intérieure avant la réception du latéral. L’analyste transmet les trois séquences et demande au coach d’observer le moment du soutien. Une séquence adverse suggère que le prochain opposant ferme souvent ce couloir. Le coach choisit de travailler la disponibilité du milieu. L’adjoint construit un jeu où l’opposition reproduit ce pressing. Au match suivant, son repère est simple : « Quand le latéral reçoit, le milieu est-il déjà disponible ? »

Le parcours doit également accepter un autre arbitrage : demander un contre-exemple supplémentaire, exploiter un point fort, choisir un renversement ou classer le sujet. Un même constat peut conduire à plusieurs décisions cohérentes.

## 5. Données, vidéo et rôle de l’IA

- **Événement fournisseur.** Une passe, un tir ou une dépossession possède une source et une définition. Une « perte candidate » du catalogue actuel a un périmètre précis. Spécifier séparément les pertes collectives, récupérations, tirs et occasions considérées comme manquées par le staff. Définir le dénominateur et la période pour toute comparaison.
- **Horloges.** Conserver la période, le temps de match, l’instant de l’événement, les bornes du contexte et les secondes du fichier vidéo. Le portail prend huit secondes de part et d’autre, prolonge si l’action dure davantage et borne la fenêtre à la période. Une vidéo avec générique, coupures ou ralentis exige un calage distinct. Les prolongations restent identifiables, les tirs au but sont traités séparément.
- **Preuves vidéo.** Le besoin cible est de découper de vrais matchs professionnels, de relire et ajuster les bornes puis de conserver les extraits retenus pour le coach. Aujourd’hui le portail peut associer une source vidéo directe et un décalage confirmé à une situation. Un lien vers un replay externe ou un résumé sert au visionnage. Consigner pour tout média sa provenance, sa couverture, le périmètre d’utilisation établi et la correspondance avec la rencontre.
- **Sources envisagées.** StatsBomb Open Data alimente les événements. FIFA+ et des résumés officiels ont été étudiés pour le visionnage. FullMatchSports a été proposé comme piste de recherche. Son exploitation effective pour ingestion, annotation ou partage reste à établir pour chaque média. SoccerTrack peut servir aux essais ou à l’entraînement technique ; le parcours entraîneur demandé porte sur des matchs professionnels.
- **IA factuelle.** Accepter des formulations libres en français, restituer les actions ou calculs sources, préciser le périmètre couvert et signaler une donnée absente. Une proposition de coupe, une interprétation tactique et une consigne du coach doivent rester identifiables. Une absence de détection du ballon ne suffit pas à conclure à une perte.
- **Vision intégrale.** Établir une preuve sur un fichier professionnel exploitable : identifier la rencontre, traiter les deux périodes, constituer un échantillon de référence annoté et mesurer séparément suivi des joueurs, visibilité du ballon, détection d’événements et utilité des extraits. Mesurer les erreurs sur plans larges, changements de caméra et occultations. Convenir avec le staff des seuils acceptables et du temps de correction. Aucune performance sur 90 minutes ne se déduit de la démo de 12 secondes.
- **Coût et accès.** Préférence exprimée pour un fonctionnement gratuit, un environnement distant isolé et une IA sans service payant imposé. L’objectif initial de démonstration par URL a évolué vers la possibilité d’un accès privé pour le staff et le coach. Le portail documente cet accès privé. Vérifier toute extension d’audience et tout coût de calcul avant de les inclure dans une livraison.

## 6. Objets métier à transmettre au back-end

Proposition de vocabulaire pour discuter des contrats avec l’équipe qui développe en parallèle. Vérifier les représentations du portail avant de définir de nouvelles tables ou API.

| Objet | Informations à préserver |
|---|---|
| Rencontre et préparation | Équipe suivie, adversaire, date, compétition, matchs sources et état d’avancement. La préparation du prochain match peut référencer plusieurs rencontres passées. |
| Situation et preuve | Identifiant source stable, équipe, période, horodatage, définition du signal, possession et issue, version des données. Pour les images : source, décalage, bornes et état de vérification. |
| Observation du staff | Auteur, titre, description, angle tactique, situations retenues et contre-exemples. Conserver la distinction entre fait et interprétation. |
| Briefing publié | Version approuvée, destinataire, ordre des illustrations, message et point à discuter. Préserver la lecture des dossiers historiques. |
| Priorité du coach | Décision, objectif observable, justification, groupe concerné, responsable et éventuelle demande de précision. |
| Séance et bilan | Paramètres terrain, exercice modifiable, consigne, critère, liens vers la priorité et les preuves, observation ultérieure et suite décidée. |

## 7. Travail de spécification à reprendre

1. **Observer une préparation réelle avec Wissem.** Lui demander de reprendre une rencontre récente, du premier support ouvert à la consigne effectivement donnée. Faire préciser qui cherche les images, qui les valide, quand les séances sont fixées et à quel moment une décision a changé. Relever les mots utilisés et les outils que le staff veut conserver.
2. **Cartographier l’existant écran par écran.** Parcourir le portail avec les deux rôles et le MVP Streamlit avec le même cas. Pour chaque besoin, relever la fonction réutilisable, la friction et l’information qui se perd entre deux écrans. La comparaison des possessions et la publication sont déjà documentées.
3. **Tester le maillon encore manquant.** Prototyper le rapprochement de l’analyse propre et de l’analyse adverse, le choix d’une priorité, son affectation à une séance puis son bilan. Rechercher aussi ce que fait le staff avec un seul entraînement disponible ou sans vidéo adverse. Tester ce parcours avant l’intégration officielle ; Figma est une option envisagée pour affiner les écrans.
4. **Lever l’incertitude vidéo en parallèle.** Documenter la source intégrale retenue, reproduire l’évaluation et présenter les erreurs au staff. Séparer la validation de navigation, la justesse des événements et la qualité du suivi dans les pixels.
5. **Rédiger les spécifications par décision.** Pour chaque besoin, produire une histoire utilisateur, ses entrées, la sortie attendue, les permissions, le comportement en cas de donnée absente et un test observable. Proposer des priorités et signaler les arbitrages qui nécessitent le coach. Les anciennes échéances de démonstration sont historiques ; convenir d’un nouveau jalon avec l’équipe.

### Questions ouvertes à soumettre au collaborateur et au staff

- Quelle préparation réelle servirait de référence ? Quels canevas, tags et formats d’import sont déjà utilisés ?
- Quel geste prend le plus de temps : retrouver l’action, vérifier sa pertinence, fabriquer le montage, transmettre le briefing ou bâtir la séance ?
- Quelles situations ont des définitions assez partagées pour une première automatisation ? Quel contexte doit rester visible pour juger une « occasion manquée » ?
- Qui doit pouvoir voir, corriger, publier et rouvrir une préparation lorsqu’un coach suit plusieurs équipes ?
- Quel support arrive jusqu’aux joueurs : vidéo collective, fiche A4, consigne de ligne, briefing individuel ? Qui le présente ?
- Quel retour après l’entraînement ou le match permet de décider qu’une priorité est acquise, à reprendre ou à abandonner ?

### Critères de recette proposés

| Mise en situation | Ce que l’on doit pouvoir observer |
|---|---|
| Le staff retient deux pertes et une réussite. | Le coach retrouve la même sélection, son ordre, son contexte et la question du staff. L’analyste peut montrer la source de chaque affirmation. |
| Le staff corrige un dossier publié. | La version approuvée reste lisible jusqu’à la publication suivante. Le brouillon demeure sous le contrôle des personnes autorisées. |
| Une séquence manque ou le ballon est invisible. | La couverture est explicite. Le staff peut conserver une observation humaine, la corriger ou l’écarter. |
| Le coach retient un objectif et l’adjoint adapte la séance. | La fiche conserve la consigne exacte, les contraintes terrain et le lien vers la décision. Un changement d’objectif entraîne une revue explicite de l’exercice. |
| Le prochain match se termine. | Le staff retrouve ce qu’il voulait observer, ajoute un résultat et peut comparer sa lecture initiale aux actions nouvelles. |

Mesurer d’abord sur une tâche réelle le temps de préparation actuel, puis le temps avec FPI, le nombre de séquences proposées puis rejetées, et la capacité du coach à retrouver la justification d’une consigne. Aucun seuil chiffré ni gain commercial n’a été validé avec le staff.

## 8. Références pour comprendre les pratiques

- **Analyse de l’adversaire et plan de match.** James Turner décrit comment le pays de Galles rapproche les caractéristiques de l’adversaire de son propre projet de jeu, avec des délais variables en tournoi. [Entretien FIFA en français](https://www.fifatrainingcentre.com/fr/environment/interviews/watch/james-turner.php)
- **Travail de l’adjoint.** Walter Samuel décrit sa contribution à la préparation des séances et les échanges avec l’encadrement argentin. [Entretien FIFA](https://www.fifatrainingcentre.com/en/environment/interviews/fifa-world-cup-2022-lessons-and-insights/walter-samuel.php)
- **Chaîne vidéo déjà pratiquée.** Hudl décrit la distribution, l’enrichissement des tags, l’import de données et la revue post-match. Ces étapes aident à identifier les doubles saisies à éviter. [Workflow post-match](https://www.hudl.com/blog/high-performance-workflows-post-match-analysis-and-review)
- **Passage du thème tactique à l’exercice.** Une séance FIFA consacrée à la récupération haute explicite organisation, consignes et progression jusqu’à l’opposition. [Exemple terrain](https://www.fifatrainingcentre.com/en/practice/elite-sessions/transition-to-defending/regaining-possession-high-up-the-pitch.php)

## 9. Instruction prête à donner à l’assistant IA du collaborateur

> Tu contribues à la spécification de Football Performance Intelligence. Lis ce document, le README du portail et les pièces du dépôt liées à ton sujet. Cite le fichier, la version ou le témoignage qui fonde chaque exigence importante. Distingue capacité existante, besoin exprimé, proposition à tester et décision encore ouverte. Pars d’un cas réel de préparation : qui agit, sur quelle information, pour prendre quelle décision, et qui utilise le résultat ensuite ? Propose les écrans, les transitions, les contrats de données à réutiliser, les cas dégradés et les critères de recette. Identifie ce qui est faisable avec les données présentes et ce qui exige une preuve vidéo ou une validation terrain. Garde les choix tactiques sous la responsabilité du staff. Termine par les arbitrages à soumettre au coach ; pour chaque arbitrage, propose des options courtes, une recommandation et sa justification. La maquette et les valeurs d’exemple servent à discuter le parcours avant toute intégration officielle.
