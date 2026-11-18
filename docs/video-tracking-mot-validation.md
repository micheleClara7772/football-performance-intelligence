# FPI — vrai suivi temporel ByteTrack sur vidéo SoccerTrack

## Statut

Expérience de validation sur les **12 premières secondes** du véritable clip panoramique SoccerTrack v2 `mot/clips/117093.mp4` (4 min de vidéo disponible), à **5 images/s** : 60 instants consécutifs, caméra 4096×1080. Référence de boîtes avec identifiants de joueurs dans `mot/117093.txt`. Les médias proviennent d'un dataset privé gated que l'utilisateur a autorisé, sous licence de données CC BY 4.0, avec attribution explicite.

## Exécution automatisée

Le workflow [FPI — vraie vidéo SoccerTrack annotée ByteTrack et IDF1](../.github/workflows/soccertrack-dense-tracking.yml) lit le secret GitHub `HF_TOKEN` sans l'imprimer, vérifie les tailles avant téléchargement et utilise un runner CPU temporaire.

- YOLOX 4×3 (personnes, score 0,20), spécialisé YOLOv9 en ONNX (ballon, score 0,20, licence des poids **AGPL-3.0**, non redistribués).
- **Vrai ByteTrack** (bibliothèque Roboflow Trackers 2.7.0), 5 Hz, échantillonnage dense sans trou de 15 secondes ; IDs de suivi provisoires des boîtes reconnues.
- Évaluation **MOTMetrics IDF1, IDP, IDR, nombre de changements d'ID et détections appariées** sur les vrais IDs MOT de ce segment à IoU minimal 0,30.
- Encodage d'une vidéo MP4 annotée `soccertrack-tracks-117093-first12s.mp4`, à largeur 1600 px, avec rectangles, identifiants et crédit SoccerTrack v2. Vidéo et rapport JSON disponibles uniquement par l'artefact privé GitHub Actions, automatiquement expiré au bout de 3 jours.

**Non validé :** identité sur 90 minutes, suivi du ballon avec vérité terrain, différenciation automatique fiable des équipes et des arbitres, séquences de coups de caméra, maîtrise des occlusions, passage des pixels au terrain, vitesse, possession ou pressing. La vidéo porte la mention « IDs provisoires ».

## Pourquoi commencer par 12 secondes ?

La vidéo panoramique d'origine est en 25 fps. À 5 fps, 60 détections du YOLOv9 spécialisé 1280×1280 demandent plusieurs minutes CPU ; augmenter la durée/qualité nécessite un benchmark de coût et de précision. Les métriques réelles sur 12 secondes servent à vérifier la stabilité d'identité **avant** de généraliser à 4 minutes puis à une rencontre intégrale.

**Issue #29 reste ouverte.**
