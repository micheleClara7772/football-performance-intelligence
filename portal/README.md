# FPI · Bibliothèque de matchs et briefings du staff

Accès privé : https://fpi-staff.vercel.app. Les comptes et les publications antérieures utilisent le même stockage et les mêmes sessions. Les anciens dossiers sont associés à Maroc–Portugal. Le serveur récupère les preuves temporelles par identifiant StatsBomb. Chaque correction d’un dossier déjà publié conserve la dernière version approuvée jusqu’à la publication suivante.

## Utiliser le portail

Depuis la bibliothèque, sélectionner une rencontre puis Créer un dossier. Donner un titre métier, choisir l’équipe, l’objectif, le scénario et les bornes de l’analyse. Les deux périodes et les deux temps sont obligatoires. Par défaut l’analyse couvre le match jusqu’à la fin réellement enregistrée (hors tirs au but). Ouvrir la revue pour modifier le titre, la conclusion, le point à discuter et l’option de publication du nombre de candidats.

Regrouper les situations par joueur, zone, type ou période, ou filtrer ces dimensions. Le terrain montre la situation sélectionnée, le sens de l’attaque et le dernier tiers. Un trait continu indique une passe, un tracé discontinu une conduite. La source événementielle et les événements de contexte sont accessibles dans la fiche. Retenir des observations et désigner jusqu’à trois illustrations principales. Après trois décisions positives simultanées, le staff voit le temps écoulé depuis la création, pauses comprises.

Relire avant validation, valider puis publier. Le coach suit le lien privé après connexion. La fiche imprimable (A4 paysage) contient le message du staff, jusqu’à trois illustrations et le point à discuter. Les dossiers de test historiques restent identifiables par leur auteur. Supprimer un brouillon et archiver une publication sont des commandes distinctes, avec confirmation. Une publication archivée quitte les espaces actifs.

## Horloges et données

Source : StatsBomb Open Data, Coupe du monde 2022, compétition 43 saison 106. Maroc–Portugal (3869486) et Argentine–France (3869685). Chaque intervalle d’analyse est une paire (période, minute:seconde) de début et de fin. Les événements sont inclus selon leur instant de départ, bornes incluses. Le temps additionnel et les prolongations sont traités dans leur période respective. Les séances de tirs au but sont exclues de l’analyse tactique. Le résultat des tirs au but est indiqué à part.

La fenêtre d’observation s’étend de huit secondes avant l’événement à huit secondes après, ou jusqu’à la fin mesurée de l’action si elle est plus longue. Les bornes restent dans la période. L’instant de l’action, la fenêtre de contexte, la période d’analyse et le minutage vidéo sont des informations distinctes.

Depuis portal, régénérer le catalogue avec python scripts/prepare.py /chemin/106.json /chemin/3869486.json /chemin/3869685.json. Les fichiers proviennent de https://github.com/statsbomb/open-data . Les 254 et 309 situations reposent sur les définitions de passes ou conduites progressives, entrées dans le dernier tiers, renversements et pertes candidates (dépossessions et contrôles manqués). L’assistant factuel interroge le périmètre autorisé. Il utilise le joueur nommé ou celui de la situation et traite les questions de suivi.

## Vidéo et présentation

Les liens de résumé sont externes. Pour associer une source HTTPS vidéo directe, l’analyste indique la seconde du média correspondant au début de la fenêtre d’observation et confirme ses vérifications d’usage et de synchronisation. Le coach voit le bouton de séquence uniquement si l’action et la source ont été publiées ensemble. Aucun suivi intégral des joueurs et du ballon sur ces rencontres n’est certifié. L’image de stade du portail est une illustration générique (Unsplash, photo-1522778119026-d647f0596c20).

## Exploitation

Fonction Node, Vercel Blob privé, écritures conditionnelles avec ETag. La racine du projet est portal. Le projet est déployé à partir des fichiers de ce dossier. Le jeton de stockage et le condensat SHA-256 du code initial sont des variables de projet. Les codes d’invitation individuels expirent après 24 heures ; les sessions durent huit heures. Les rôles et accès directs sont contrôlés côté serveur.

Vérifications : npm ci, npm test, node --check public/app.js et python scripts/check_evidence.py. Pour tester l’interface avec deux comptes de recette, utiliser scripts/browser_smoke.py avec les identifiants dédiés et l’URL dans les variables FPI_TEST_URL, FPI_STAFF_NAME, FPI_STAFF_PASSWORD, FPI_COACH_NAME, FPI_COACH_PASSWORD. Ce test crée et publie un dossier.

## Lecture par possession

La chronologie regroupe les actions par possession StatsBomb et par période. Les étapes du terrain suivent les événements offensifs horodatés et localisés de l’équipe en possession. L’issue distingue un tir dans la même possession, la dernière action documentée et l’équipe à laquelle appartient la possession suivante. Le score avant l’action respecte l’ordre des événements et exclut les tirs au but. Les annotations du staff restent associées à leur événement. Les possessions illustrant une sélection sont figées avec la publication. Les publications historiques conservent leurs anciennes preuves jusqu’à une nouvelle revue.

Le menu de comparaison propose une autre possession de la même équipe, dans la même bande latérale et avec un critère de sélection commun. Sur mobile, les deux terrains sont consultables par balayage horizontal. La fiche de briefing reproduit jusqu’aux cinq premières étapes de l’action choisie. Le PDF de recette docs/recette/briefing-maroc.pdf illustre l’entrée marocaine à 54:57.

Les boutons Supprimer sont accessibles depuis la liste ou le dossier pour son auteur et les administrateurs. La confirmation précise l’effet sur le lien d’une publication. Les dossiers archivés peuvent également être supprimés par ces rôles. Les tests de suppression utilisent des dossiers temporaires.
