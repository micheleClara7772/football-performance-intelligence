# FPI — déploiement gratuit sur Streamlit Community Cloud

**But :** une URL publique `*.streamlit.app` sans abonnement payant ni installation sur l'ordinateur, en conservant le dépôt GitHub **privé**.

## Vérifications techniques et limites

- Streamlit Community Cloud est proposé gratuitement : https://docs.streamlit.io/deploy/streamlit-community-cloud
- Les repos GitHub privés sont acceptés, mais **l'autorisation OAuth d'accès au dépôt exige le compte du propriétaire** : https://docs.streamlit.io/deploy/streamlit-community-cloud/get-started/connect-your-github-account
- Une app issue d'un dépôt privé est initialement privée et peut être rendue publique via ses paramètres de partage : https://docs.streamlit.io/deploy/streamlit-community-cloud/share-your-app
- Le dépôt a un `requirements.txt` en racine. Il installe les versions exactes du lock Linux et `-e .` afin que le package `src/fpi` soit importable.
- Le code et les tests ont été préparés pour Python **3.11**. Cette version doit être sélectionnée dans les options avancées ; la version par défaut peut différer.
- Le serveur peut être mis en veille ou soumis aux limites de ressources du service gratuit ; aucun service gratuit ne garantit une disponibilité 24h/24.

## Étapes à réaliser une seule fois par le propriétaire du compte

1. Ouvrir **https://share.streamlit.io/** et se connecter avec GitHub.
2. Autoriser l'accès **au dépôt privé** `micheleClara7772/football-performance-intelligence`. Préférer l'accès à ce seul dépôt si l'interface le permet.
3. Cliquer **Create app** → **I have an app** / **Deploy from GitHub**.
4. Repository : `micheleClara7772/football-performance-intelligence` ; branche : **main** ; fichier de lancement : **app.py**.
5. Dans **Advanced settings**, sélectionner **Python 3.11**. Ne pas ajouter de jeton StatsBomb ou FIFA : FPI n'en utilise aucun.
6. Déployer, ouvrir l'adresse réellement obtenue, vérifier la page d'accueil et les cinq rubriques.
7. Dans **Share / Settings → Sharing**, choisir **This app is public and searchable** uniquement si ce niveau de visibilité a été validé par le propriétaire et que les obligations d'utilisation sont respectées. Le dépôt source peut rester privé.
8. Copier la **vraie URL** affichée. Ne jamais inventer l'adresse à partir du nom du dépôt.
9. Dans FPI, les données ne sont chargées qu'après un clic utilisateur sur **Importer depuis StatsBomb**. Sur le cloud, le cache peut disparaître après redémarrage : réimporter si nécessaire.

## Recette de mise en ligne

- [ ] URL `https://...streamlit.app` réellement obtenue et ouverte dans un navigateur non connecté à GitHub.
- [ ] App servie avec Python 3.11 ; logs sans erreur `ModuleNotFoundError`.
- [ ] Cinq rubriques visibles et état vide honnête avant import.
- [ ] Import explicite du match Maroc 1–0 Portugal : 3 381 événements ; tirs 9/12, passes tentées 249/731.
- [ ] Tableau de bord, Tactique/Annotations (export/import), Assistant factuel, Séances (export JSON) parcourus.
- [ ] Lien externe FIFA+ vers le match **intégral** et liens YouTube officiels vers les **résumés** vérifiés.
- [ ] Tentative iframe YouTube **des seuls résumés** vérifiée sur l'URL publique ; lecture non présumée avant observation humaine.
- [ ] Absence de média, données tierces brutes ou secrets exposés dans GitHub.
- [ ] Préparation de la présentation externe soumise à clarification des droits StatsBomb/FIFA.

## Droits : ne pas déduire l'autorisation de la disponibilité publique

Les conditions FIFA+ interdisent de placer ses plateformes dans une iframe tierce :
https://inside.fifa.com/terms-of-service-fifaplus

Le replay officiel FIFA+ est donc **externe seulement**. L'utilisateur ne possède pas une licence de réhébergement de cette rediffusion. Les obligations commerciales de StatsBomb sont encore examinées dans l'Issue #3. **Le déploiement d'une coquille applicative ne confère aucun droit de diffuser des vidéos ou données licenciées.**

**Hébergement :** Streamlit Community Cloud est une piste gratuite ; aucun service externe n'est créé ni facturé par le dépôt lui-même.
