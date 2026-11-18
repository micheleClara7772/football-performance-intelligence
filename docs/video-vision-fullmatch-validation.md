# FPI — analyse d'une rencontre complète : protocole et mesures

État : le moteur réel COCO YOLOX est déjà disponible sur `main`. Cette branche ajoute un modèle **facultatif** spécialisé ballon (ONNX), un banc de mesure sur boîtes indépendamment annotées et un contrôle de **durée de 92 minutes**. **La précision sur un match réel complet n'est PAS prouvée par le test de durée synthétique.**

## Choix après recherche documentaire (novembre 2026)

| Solution | Intérêt | Limite constatée |
|---|---|---|
| YOLOX-Nano COCO, déjà livré | CPU sans paiement ; détecte les personnes sur un vrai clip | 0 ballon sur 18 frames panoramiques SoccerTrack ; COCO `person` n'identifie pas un joueur |
| YOLOX en tuiles 4×3 | 3 ballons annotés localisés sur 3 images distinctes en CI | Coûte du CPU et ne garantit pas un rappel élevé en panoramique |
| [YOLOv9 spécialisé ballon](https://huggingface.co/acatorcini/yolov9-soccer-ball) | ONNX téléchargeable, entraînement sur ballons petits | **Poids AGPL-3.0** ; généralisabilité à vérifier sur notre vidéo ; non activé par défaut |
| [SoccerTrack v2](https://huggingface.co/datasets/atomscott/soccertrack-v2) | 10 matchs intégrals (934 min), vidéos et annotations frame par frame, CC BY 4.0 | Référentiel d'images **gated** : le compte HF doit accepter les conditions d'accès ; fichiers lourds (~145 Go pour tout le dataset) |
| SoccerNet | Séquences et données de suivi longues | Vidéos protégées/accès soumis à conditions ou NDA suivant le jeu |

**Attention** : ONNX Runtime n'annule ni ne remplace la licence AGPL du modèle spécialisé. Toute redistribution/publication/commercialisation doit faire l'objet d'un examen. L'alternative de base YOLOX sans ce modèle reste disponible.

## Usage de la CLI privée, gratuite, sur Codespaces

Ne pas installer sur le PC personnel ; utiliser un Codespace ou runner privé avec les fichiers autorisés. Ne pas mettre les vidéos, données personnelles ou poids de modèle dans Git.

```bash
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt

# Optionnel : pour rechercher des ballons petits, obtenir explicitement
# les poids ONNX séparément licenciés AGPL-3.0 et les conserver en privé.
mkdir -p data/models
curl --fail --location --retry 2 \
  'https://huggingface.co/acatorcini/yolov9-soccer-ball/resolve/main/v9b_best.onnx' \
  --output data/models/v9b_best.onnx

.venv/bin/python -m fpi.video_analysis.cli \
  --video /chemin/prive/match-autorise.mp4 \
  --out outputs/mon-match-detections.json \
  --interval-seconds 5 --max-frames 0 \
  --ball-onnx data/models/v9b_best.onnx \
  --ball-threshold 0.20 --ball-columns 2 --ball-rows 1 \
  --consent-rights
```

Sur 90 minutes à 5 secondes : environ **1080 instants** demandés. Ces instants couvrent toute la vidéo, **mais pas toutes les 135 000 frames d'une rencontre 25 fps**. Le coût CPU peut être important, particulièrement pour le modèle spécialisé 1280×1280 et les tuiles. Si la machine est limitée, commencer à 15 s (360 images).

Sans `--ball-onnx`, le moteur d'origine YOLOX continue de fonctionner. Le `--ball-onnx` est un choix explicite, pas une garantie de ballons trouvés.

## Référence annotée et évaluation honnête

Sur le jeu vidéo que l'on a le droit d'analyser, sélectionner des frames dans toute la chronologie (début, deuxième mi-temps, plans larges, arrêts de jeu, coups de pied arrêtés) et annoter **toutes les personnes et tous les ballons visibles** sur chacune des frames retenues (y compris les frames sans ballon). Exemple de fichier `annotations.json` :

```json
{
  "frames": [
    {
      "time_seconds": 15.0,
      "objects": [
        {"label": "person", "bbox_xyxy": [30, 40, 63, 109]},
        {"label": "ball", "bbox_xyxy": [100, 88, 108, 96]}
      ]
    },
    {"time_seconds": 30.0, "objects": []}
  ]
}
```

Les coordonnées `bbox_xyxy` sont exprimées en **pixels du fichier vidéo d'origine**. Les frames sans objets sont évaluées comme absence d'objets, pas ignorées.

```bash
.venv/bin/python scripts/evaluate_video_detections.py \
  --detections outputs/mon-match-detections.json \
  --annotations /chemin/prive/annotations.json \
  --out outputs/mon-match-evaluation.json \
  --iou 0.30 --time-tolerance 0.6
```

Rapport calculé pour chaque classe : vrais positifs, faux positifs, omissions, précision, rappel et F1, sur les **seules frames entièrement annotées**. Ce n'est ni une mesure de poursuite d'identité (MOTA/HOTA), ni une mesure de possession, ni une métrique tactique certifiée. Pour attester la qualité d'une analyse de match complet, il faut répartir les annotations sur l'ensemble du vrai match et annoncer leur nombre et leurs limites.

## Ce que prouvent les tests

1. `tests/test_football_ball.py` : le décodage du modèle ONNX simulé, transformation letterbox, et sélection du modèle spécialisé pour la classe ballon ; **pas une mesure de qualité du modèle**.
2. `scripts/validate_specialist_ball.py` : **véritable modèle spécialisé** téléchargé de Hugging Face et exécuté sur trois images réelles annotées d'un autre dataset ; imprime nombre de correspondances, sans exagérer la taille de l'échantillon.
3. `scripts/validate_full_duration.py` : génère une vidéo synthétique originale de **92 minutes**, parcourt vraiment ses frames à intervalles de 5 minutes et vérifie le décodage/horodatage de fin ; le « détecteur » de ce seul test est simulé pour isoler les erreurs d'I/O, **pas pour prouver le rappel sur un match**.
4. `scripts/validate_video_model.py` : détecteur YOLOX original avec vraies inférences et vraies images, maintien en non-régression.

## Travail encore nécessaire pour déclarer « validé match intégral »

- Obtenir le droit d'accès au jeu [SoccerTrack v2](https://huggingface.co/datasets/atomscott/soccertrack-v2) dans le compte Hugging Face qui téléchargera les données (licence **CC BY 4.0** et conditions gated). Télécharger **un seul match**, pas les 145 Go.
- Exécuter la CLI sur ses **deux mi-temps** et enregistrer les rapports séparés. Rapprocher les timestamps de chaque mi-temps sans inventer leur correspondance avec les horloges officielles.
- Annoter et mesurer les images du match sur **la durée entière**, notamment le petit ballon en plan panoramique, et déterminer des seuils de précision/rappel acceptables avec le partenaire.
- Pour **Maroc–Portugal 2022** : acquérir séparément une vidéo avec **droits d'extraction et de traitement automatisé** ; le simple replay FIFA+ n'autorise pas cela. SoccerTrack est un autre match libre, excellent pour valider le moteur, mais n'est pas Maroc–Portugal.
- La séparation joueurs/arbitres, le suivi continu des identités et les métriques spatiales fiables nécessitent encore des modèles et tests dédiés.

Ne pas présenter un benchmark sur trois photos ou 92 minutes d'images synthétiques comme une validation d'une vraie rencontre intégrale.
