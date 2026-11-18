# FPI — détection de personnes et ballons à partir des images

**Implémentation du 18 novembre 2026 :** le programme traite réellement les pixels d'une vidéo et non seulement les événements du fournisseur. Détecteur **YOLOX-Nano ONNX (CPU)** utilisant deux classes de COCO : `person` et `sports ball`. Les objets sont indiqués comme **candidats**, jamais comme identités de joueurs certifiées.

## Utiliser la démonstration gratuite dans FPI

1. Dans FPI, ouvrir **Vidéo** puis descendre à **4. Détection automatique dans un fichier vidéo autorisé**.
2. Cocher **Utiliser l'extrait de démonstration libre SoccerTrack v2 (CC BY 4.0)**.
3. Cocher la confirmation d'autorisation de traitement de la vidéo.
4. Choisir 15 secondes et 16 frames (ou 4 pour un essai court) ; cliquer **Détecter les joueurs et ballons candidats**.
5. Le système télécharge le modèle public uniquement sur demande et vérifie sa somme **SHA-256**, puis traite la vidéo SoccerTrack par des frames réparties sur sa durée. Les photos annotées affichent les boîtes de candidats ; le JSON contient positions, temps, scores et mises en garde.
6. Si aucun ballon n'apparaît, le résultat doit rester **0**, avec un avertissement. La petite taille du ballon dans une caméra panoramique peut rendre les détections impossibles.

**Source de la démonstration :** [SoccerTrack v2](https://github.com/AtomScott/SoccerTrack-v2), © Atom Scott et contributeurs, jeu de données [CC BY 4.0](https://github.com/AtomScott/SoccerTrack-v2/blob/main/LICENSE-DATA). Usage avec attribution. Ce sont des séquences de football amateur, **PAS Maroc–Portugal 2022**.

Le mode upload permet d'analyser **un fichier local que l'utilisateur a le droit de transmettre et de traiter**, maximum 100 Mo, formats MP4, MOV, MKV, AVI, WebM. L'upload est temporaire et le fichier original est supprimé après traitement, sans export de la vidéo.

## Traiter un fichier intégral autorisé en dehors du Cloud

Le Cloud gratuit limite volontairement à 100 Mo et 40 frames. Sur un Codespace où la vidéo est disponible licitement, exécuter :

```bash
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m fpi.video_analysis.cli \
    --video /chemin/vers/mon-match-complet-autorise.mp4 \
    --out outputs/detection-match.json \
    --interval-seconds 15 \
    --max-frames 0 \
    --consent-rights
```

L'option `--max-frames 0` échantillonne la vidéo **sur toute sa durée**, sans se limiter aux premières minutes. Par défaut, 90 minutes / 15 s ≈ 360 instants analysés, chacun pouvant générer plusieurs tuiles. **Ce n'est pas l'analyse de chaque frame à 25/30 fps et ce n'est pas du tracking continu.** Le coût CPU et la durée varient selon résolution, machine et modèle ; ils ne sont pas garantis.

## Preuves et limites mesurées

- **Vidéo authentique libre** : test ONNX réel sur 18 frames de l'extrait SoccerTrack `docs/assets/demo-tracking.mp4` : 18 frames contenaient des boîtes de personnes candidates (183 boîtes), **0 ballon candidat**.
- **Photographies authentiques et annotées** : trois images de validation [Football Image Dataset](https://github.com/skaczylo/Football-Image-Dataset), déclarées [CC BY 4.0](https://github.com/skaczylo/Football-Image-Dataset/blob/main/LICENSE) : 6 ballons candidats ; trois sont situés à proximité du ballon annoté (une correspondance par image). **Ce petit échantillon n'est pas une mesure de précision/rappel global ni une validation vidéo continue.** Attention : ces images sont extraites de retransmissions ; vérifier les droits sous-jacents avant tout usage public.
- Tests de post-traitement : décodage des ancres YOLOX, classe COCO `person` 0 et `sports ball` 32, limites de coordonnées, suppression des doublons, fichier vidéo synthétique décodable, gestion des erreurs, téléchargement du modèle contrôlé et vérifié.
- Contrôles de provenance : vidéo de démonstration téléchargée éphémèrement sur le runner, aucun match FIFA téléchargé, aucun fichier complet ajouté au dépôt, rapport de détection sans contenu multimédia. Les captures SoccerTrack dérivées sont des preuves de test, avec attribution.
- La classe `person` inclut potentiellement arbitres, remplaçants, spectateurs et entraîneurs. Une boîte n'est pas un joueur identifié. L'absence de ballon détecté n'est **jamais** une preuve de son absence réelle.
- Pas d'identification des maillots, attribution automatique aux équipes, suivi stable des identités, possession, trajectoire, vitesse, métrique de pressing déduite des images, synchronisation StatsBomb–vidéo ni validation sur **90 minutes de Maroc–Portugal**.

**Moteur** : [YOLOX](https://github.com/Megvii-BaseDetection/YOLOX) (code Apache 2.0) et poids de sa publication officielle. Les termes précis applicables aux poids pré-entraînés doivent être vérifiés séparément avant une exploitation commerciale. Les dépendances Python sont verrouillées dans `requirements/video-py311-linux.lock`, aucun abonnement, GPU ou API nécessaire pour le CPU.

## Chemin vers une véritable analyse complète du quart de finale 2022

- Obtenir un fichier intégral **dont les droits d'extraction et de traitement** couvrent cet usage. Un lien FIFA+/Footballia/Dailymotion ne confère pas automatiquement ces droits.
- Comparer les détections à des boîtes manuelles annotées sur plusieurs segments de **la véritable vidéo cible** et mesurer précision, rappel, couverture par minute, faux positifs, confusion arbitre/joueur et fausses balles.
- Adapter la détection du ballon à la taille réelle dans le panoramique (modèle dédié, tuiles, échantillonnage plus dense), puis seulement étudier les trajectoires.
- Faire une première synchronisation de l'horloge vidéo avec les événements du match **par repères humains vérifiés**, sans alignement automatique inventé.
- Documenter les limites de ressources du service gratuit avant une analyse longue.

**Issue de suivi :** [#29 — vision vidéo complète et suivi des objets](https://github.com/micheleClara7772/football-performance-intelligence/issues/29). Cette étape reste ouverte tant qu'il manque un fichier cible exploitable et une évaluation précise sur le match entier.
