# FPI — exécution autonome de la validation d'un match intégral

Statut (18 novembre 2026) : **travail en cours**. La vidéo d'un vrai match de 90 minutes n'a **pas encore** été acquise ni testée de bout en bout. La nouvelle association de boîtes et les calculs spatiaux sont des modules expérimentaux. Ne pas fermer l'Issue #29 sur les seuls tests unitaires.

## 1. Acquisition légitime, une seule rencontre

Dataset : [SoccerTrack v2](https://huggingface.co/datasets/atomscott/soccertrack-v2), licence de données CC BY 4.0, version `v1.2`, 10 rencontres réparties en 20 vidéos de mi-temps (environ 145 Go au total). Le site exige une **acceptation explicite** des conditions en étant connecté à Hugging Face. Aucune API FPI ne peut consentir à la place de l'utilisateur.

En environnement privé gratuit et isolé :

```bash
python -m scripts.prepare_soccertrack --match-id 117093
# Aucun téléchargement dans ce premier appel.
# Après validation humaine des conditions sur Hugging Face :
python -m pip install huggingface_hub
hf auth login   # ne jamais consigner son jeton dans Git, un issue ou des logs
python -m scripts.prepare_soccertrack --match-id 117093 --download --access-confirmed
```

`117093` est le match **M2 / validation**, choisi pour ne pas utiliser le jeu de test final M7/M9. Le téléchargement limite les chemins aux deux mi-temps et aux annotations `gsr/`, `ball/`, `bas/` correspondantes ; même cette sélection peut nécessiter des gigaoctets et plusieurs heures de calcul CPU. Ne jamais uploader de vidéo ni de poids sur le dépôt ou sur Streamlit Cloud.

**Spécification critique** : les `gsr/*.json` livrés ont un **objet COCO SoccerNet** (`images`, `annotations`, `attributes`, `bbox_image`, `bbox_pitch`) et non le tableau plat initialement documenté. Certains fichiers dépassent **2 Go par mi-temps**. L'outil de conversion/benchmark doit les parcourir en flux, sans `json.load` complet, et utiliser les dimensions réelles de la vidéo. Les JSON d'annotation de balle `ball/` contiennent une **trajectoire reconstruite/interpolée**, ce qui n'est pas une vérité terrain de boîtes de balle visible dans les pixels. Ne pas la noter comme un détecteur d'objets. Références : documentation [format GSR](https://github.com/AtomScott/SoccerTrack-v2/blob/main/docs/format-gsr.md), [release v1.2](https://huggingface.co/datasets/atomscott/soccertrack-v2).

### Convertir la vérité terrain spatiale sans épuiser la mémoire

Les fichiers GSR peuvent peser plus de 2 Go chacun. Installer `ijson` **dans le Codespace** pour parcourir les annotations sans les charger en mémoire, puis générer des positions pitch indépendantes du modèle :

```bash
python -m pip install "ijson>=3.2,<4"
python -m scripts.convert_soccertrack_gsr \
  --gsr data/raw/soccertrack-v2/gsr/117093/117093_1st.json \
  --out outputs/gsr-reference-half1.json --every-seconds 5
python -m fpi.video_analysis.team_metrics \
  --positions outputs/gsr-reference-half1.json --out outputs/gsr-shape-half1.json
```

Répéter pour `117093_2nd.json`. Cela **mesure les annotations de référence**, pas les sorties de FPI. Un test du parseur sur des objets simulant le format livré est inclus dans la CI ; aucune réelle annotation de plusieurs gigaoctets n'est disponible dans le runner public. Aucun alignement inter-mi-temps n'est présumé.

## 2. Benchmark comparatif reproductible

Après accès à une vraie vidéo autorisée, produire les rapports YOLOX et hybride sur exactement la même grille temporelle. Exemple *à adapter au fichier privé* :

```bash
python -m fpi.video_analysis.cli --video /private/half-1.mp4 --out outputs/yolox.json \
  --interval-seconds 5 --max-frames 0 --consent-rights
python -m fpi.video_analysis.cli --video /private/half-1.mp4 --out outputs/specialist.json \
  --interval-seconds 5 --max-frames 0 --ball-onnx data/models/v9b_best.onnx \
  --consent-rights
python -m scripts.compare_video_detectors \
  --yolox outputs/yolox.json --specialist outputs/specialist.json \
  --annotations /private/fully-labelled-image-boxes.json --out outputs/comparison.json
```

Les modèles ne peuvent être départagés **provisoirement** que lorsque >=100 frames et >=30 vrais ballons **indépendamment annotés** figurent dans le benchmark, avec toutes ces frames détectées par chaque modèle. Il s'agit d'un seuil d'échantillon opérationnel, **pas d'une preuve de signification statistique**. Ajouter un lot de plans lointains, des frames sans ballon, le début et la fin des deux périodes, et mesurer aussi les latences CPU réelles. L'outil `scripts.evaluate_video_detections` calcule précision, rappel et F1. L'essai actuel de 3 images **ne satisfait pas** ce critère.

## 3. Suivi temporel provisoire

Le module `fpi.video_analysis.tracking` associe des boîtes proches entre images rapprochées, par classe et par géométrie. Il **rompt les identités** après un écart temporel supérieur au seuil : c'est intentionnel pour éviter d'inventer le suivi sur des images espacées de 15 secondes.

```bash
# Analyses denses nécessaires (par exemple 0,2 s, à tester selon capacités CPU).
python -m fpi.video_analysis.cli --video /private/short-clip.mp4 \
  --out outputs/dense.json --interval-seconds 0.2 --max-frames 0 --consent-rights
python -m fpi.video_analysis.tracking --detections outputs/dense.json \
  --out outputs/provisional-tracks.json --max-gap-seconds 0.6
```

### Vrai ByteTrack optionnel

L'adaptateur `fpi.video_analysis.bytetrack_adapter` utilise désormais la bibliothèque [Roboflow Trackers](https://github.com/roboflow/trackers) **2.7.0** (Apache-2.0), et non l'ancien `sv.ByteTrack` retiré de Supervision 0.31. Il doit être utilisé dans un environnement de calcul privé. La CI exécute un test réel de l'algorithme sur des boîtes de synthèse, sans télécharger de vidéo.

```bash
python -m pip install "trackers==2.7.0" # venv privé, dépendances optionnelles
python -m fpi.video_analysis.bytetrack_adapter \
  --detections outputs/dense.json --out outputs/bytetrack-tracks.json \
  --max-gap-seconds 0.6
```

Les pistes sont séparées par classe et par segment temporel. **Même avec un vrai ByteTrack, les identités sont provisoires** tant qu'aucune mesure de continuité d'identité sur un véritable match annoté n'a été effectuée. Il ne différencie pas les joueurs des arbitres et ne connaît pas les équipes.

Ceci **n'est pas ByteTrack/BoT-SORT**, pas une vraie identification de joueur, et ne reconstitue pas l'identité après une occlusion ou une coupure de caméra. **Validation suivante** : mesurer les métriques MOT/IDF1/HOTA sur des segments réels avec identité annotée, implémenter un tracker dédié, séparer arbitres, joueurs et équipes. Ne pas montrer ces IDs provisoires comme des numéros de maillot.

## 4. Métriques collectives sur coordonnées terrain

Le module `fpi.video_analysis.team_metrics` accepte uniquement des observations en **mètres calibrés**, au centre d'un terrain 105 × 68. Exemple du schéma d'entrée :

```json
{
  "coordinate_space": "pitch_meters_center_origin",
  "source": "soccertrack-v2-gsr-reference",
  "frames": [
    {
      "time_seconds": 0.0,
      "players": [
        {"role": "player", "team": "left", "x_m": -20.0, "y_m": 5.0}
      ]
    }
  ]
}
```

```bash
python -m fpi.video_analysis.team_metrics --positions /private/calibrated-positions.json \
  --out outputs/team-shape.json --min-players 5
```

Sorties : largeur, profondeur, centre moyen, dispersion, occupation 3 × 3. **Ces nombres viennent de positions terrain fournies**, et non encore de détections automatiquement calibrées. La prochaine étape exige calibration vidéo→terrain, association d'équipes, filtrage de qualité et comparaisons à la vérité terrain. La vitesse/distance/possession/pression **ne sont pas calculées** sans validation adéquate.

## 5. Adaptation à Maroc–Portugal, 10 décembre 2022

Les vidéos FIFA+ sont destinées au visionnage sur la plateforme. Un droit de streaming ne constitue pas une autorisation de télécharger, décoder ou enrichir les images. Identifier une source vidéo **autorisée pour le traitement automatisé et la démonstration**, puis tester la chaîne sur les deux mi-temps, aligner manuellement les horloges vidéo et StatsBomb, comparer à un ensemble indépendant d'annotations, vérifier les droits des modèles (le spécialiste YOLOv9 actuel est **AGPL-3.0**).

**Critère de clôture Issue #29** : autorisation documentaire + vidéo intégrale réelle des deux périodes + modèles exécutés + détection et suivi évalués quantitativement + métriques calibrées avec incertitudes + rapport de qualité reproductible + validation métier. Aucun de ces éléments n'est implicite dans un workflow CI vert.
