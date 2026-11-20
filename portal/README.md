# FPI · Portail privé

Application de démonstration déployée sur https://fpi-staff.vercel.app. Le répertoire portal est la racine du déploiement Vercel. L’ancienne application Streamlit reste disponible dans le dépôt. Le projet Vercel reçoit les fichiers sources directement, la connexion Git automatique n’est pas configurée.

## Accès et utilisation

Lors de la première connexion, saisir le code individuel à usage unique et choisir un mot de passe de 12 caractères minimum. Les invitations ordinaires expirent après 24 heures. L’administrateur peut créer une invitation, renouveler l’accès, modifier le rôle ou révoquer un utilisateur. Les sessions durent huit heures.

Depuis le compte Staff, choisir le mode, l’équipe et le scénario, puis lancer l’analyse. Ouvrir la revue, déplier les événements, saisir une observation, la retenir et enregistrer chaque décision. Valider la sélection puis publier. Une publication ne contient que les événements retenus. La version précédente reste accessible pendant les corrections. Depuis le compte Entraîneur, ouvrir le dossier, explorer la carte et les preuves, interroger les actions, filtrer et exporter le dossier JSON.

## Périmètre

Maroc–Portugal, quart de finale du 10 décembre 2022. Les 3 381 événements de StatsBomb Open Data donnent 254 situations distinctes. L’extraction reprend les seuils de progression et de renversement de src/fpi/analysis/advanced.py et étend les situations aux conduites et contrôles manqués. Les coordonnées sont propres à l’équipe agissante. Les candidats après perte sont limités aux dépossessions et contrôles manqués en possession. Une passe ratée n’est pas systématiquement une perte en jeu ouvert. Les événements suivants sur huit secondes sont des éléments de contexte.

Les libellés des scénarios, la carte, les compteurs et la recherche sont déterministes. Les comparaisons de mi-temps et de zones portent sur les actions sélectionnées. Les hypothèses tactiques et leurs annotations sont du ressort du staff. Une recherche libre est limitée aux termes pris en charge. Aucun LLM n’est déployé.

Le lien FIFA+ est externe. Aucun traitement des images du match professionnel, découpage de séquences, entraînement ou synchronisation vidéo n’est livré ici. Aucun contenu SoccerTrack n’est servi par le portail. La PR expérimentale #50 et l’issue #29 poursuivent un chantier distinct.

## Source et reproductibilité

Source : https://github.com/statsbomb/open-data – données événementielles de StatsBomb. Fichier data/events/3869486.json, SHA-256 455127b456021593874476ee8b5dad01b0166b8da814c095300b6ed608a08993. Métadonnées vérifiées dans data/matches/43/106.json. Télécharger le fichier source puis exécuter python scripts/prepare.py /chemin/3869486.json. Les données condensées restent côté serveur.

## Architecture et vérifications

Fonction Node sur Vercel, ressources statiques dans public, état en Vercel Blob privé à Francfort. L’état contient comptes, sessions hachées, invitations hachées, brouillons, validations, historique de décisions et dernière publication. Une écriture conditionnelle sur l’ETag évite d’écraser une mise à jour concurrente. Le serveur vérifie les rôles et propriétaires pour chaque action. Le navigateur reçoit uniquement les données autorisées. Ce stockage monofichier est destiné à un petit staff en démonstration.

Configurer BLOB_READ_WRITE_TOKEN avec le projet Blob privé. Pour une installation vierge, fournir uniquement le SHA-256 d’un code aléatoire dans FPI_BOOTSTRAP_HASH et remettre ce code en privé à l’administrateur. Le code initial ne fonctionne que lorsque le magasin est vide. Les secrets ne sont pas stockés dans Git.

Dans portal, lancer npm ci, npm test, node --check public/app.js et python3 scripts/check_evidence.py. Les tests couvrent les deux modes, les deux équipes, les deux scénarios, les permissions, le conflit de version, le rejet et la conservation du publié. Le contrôle direct sur l’URL de production a confirmé le refus du brouillon par les routes de consultation, de recherche et de publication, puis la visibilité d’une seule action retenue après publication.

### Recette du 21 novembre 2026, heure de Paris

Le parcours a également été exécuté sur le site en production avec deux navigateurs Chromium séparés. Le staff a lancé les transitions du Maroc, retenu et annoté une action, validé puis publié. Le coach a ouvert le dossier, comparé les pertes entre mi-temps et téléchargé un JSON contenant uniquement l’action retenue. Les vues Staff et Entraîneur ont été contrôlées à 375, 768, 1024 et 1440 pixels avec vérification de la largeur et captures dans docs/recette. Le rejeu par requêtes API a testé séparément la progression du Portugal et le maintien du publié pendant une correction. Les cinq dossiers de recette restent visibles à l’administrateur, dont trois publications. Leur auteur « Recette staff » est affiché dans la liste. Les comptes techniques de recette restent actifs.

Le socle gratuit de démonstration utilise une seule rencontre et un magasin Blob privé. La base PostgreSQL gratuite préparée sur Render pendant la vérification d’hébergement reste vide et indépendante de l’application. La conformité WCAG complète et la montée en charge ne sont pas certifiées.
