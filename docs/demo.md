# FPI — démonstration « vidéo d'abord » (soir du 18 novembre 2026)

## Parcours de 7 minutes, sans aucun téléchargement utilisateur

**0:00 – 0:30 · Entrée en matière.** Ouvrir FPI sur la page **Démo vidéo**, qui doit être la page d'accueil. Lire la vidéo annotée SoccerTrack directement dans l'application : aucun upload, jeton ou modèle à installer. Expliquer : « C'est une séquence *réelle*, issue d'un match amateur SoccerTrack v2, pas Maroc–Portugal. »

**0:30 – 2:00 · Ce que fait vraiment la vision.** Montrer les rectangles autour des personnes et les identifiants de tracking ByteTrack. Pauser/rejouer à volonté. Expliquer YOLOX (détection) → ByteTrack (association) → comparaison aux identifiants de vérité terrain MOT. Le film intégré dure 12 secondes, à 5 images analysées/s, et ne montre pas d'identification des équipes.

**2:00 – 2:45 · Preuves, sans exagération.** En face du lecteur, lire les vrais indicateurs : **IDF1 63,0 % ; précision des boîtes appariées 87,2 % ; rappel 63,8 % ; 10 changements d'ID** sur 60 images / 1320 annotations de référence. Montrer que le ballon **n'a pas été détecté** sur ce segment ; le modèle n'est pas encore utilisable pour les trajectoires de ballon sur 90 minutes.

**2:45 – 3:30 · Match Maroc–Portugal.** C'est **une autre source** : StatsBomb Open Data, non synchronisée automatiquement à la vidéo SoccerTrack. Dans le dashboard, montrer le score 1-0, les 3381 événements réels et les 9/12 tirs. Importer depuis StatsBomb si le cache n'est pas prêt : ne pas inventer des valeurs.

**3:30 – 5:15 · Discussion tactique.** Ouvrir Analyse tactique → Signaux avancés (récupérations hautes, progressions, changements d'aile), puis annotations. Ces signaux sont des **proxys calculés à partir des événements** et non des résultats du tracking de la vidéo.

**5:15 – 6:00 · Assistant & séance.** Poser une question en français dans l'assistant local factuel (pas LLM génératif). Choisir un objectif d'entraînement ; modifier l'exercice avant export JSON ; rappeler la validation par le staff.

**6:00 – 7:00 · Demander un feedback métier** : « Quels 2 ou 3 indicateurs vidéo vous aideraient réellement à préparer une rencontre ? », « Quelle précision minimale accepteriez-vous ? », « Quelle séquence voudriez-vous annoter en priorité ? » Expliquer la feuille de route : plus de suivi continu, équipe/arbitre, ballon et vrai calibrage en mètres.

## Plans de secours

- Vérifier que `assets/fpi-video/real-bytetrack-12s.mp4` et le rapport JSON ont été intégrés par le [workflow de vidéo de démo](../.github/workflows/publish-video-demo.yml). Il doit s'agir d'un MP4 **H.264** jouable dans un navigateur, pas seulement d'un MP4 OpenCV au codec MPEG-4 Visual.
- Si cette vidéo n'est pas disponible, la page de démo montre la **vidéo source publique** SoccerTrack (sans tracking) et un état explicite ; **ne pas la présenter comme une vidéo annotée**.
- L'application Streamlit Cloud **n'existe pas automatiquement après un push GitHub**. Son propriétaire doit connecter le dépôt privé une fois, créer l'app sur https://share.streamlit.io et tester l'URL dans un autre navigateur.
- Si la connexion Streamlit Cloud est absente à l'heure du rendez-vous : utiliser une fenêtre Codespaces sur un port préalablement testé, avec `python -m streamlit run app.py --server.address 0.0.0.0`, en respectant les permissions de l'accès privé.
- FIFA+ n'est pas téléchargé : aucune autorisation de traitement du match Maroc–Portugal n'est acquise. L'ouvrir depuis son site officiel, dans un onglet séparé, uniquement pour le visionnage.
- Licence des images SoccerTrack : **CC BY 4.0** ; citer Atom Scott et les contributeurs, indiquer que les superpositions sont générées par FPI. Pas de redistribution de poids AGPL YOLOv9 dans le dépôt.

**Critère de succès ce soir :** la vidéo annotée s'affiche et se lit immédiatement, une métrique honnête est visible à côté, la navigation fonctionne, un import StatsBomb est possible, l'entraîneur comprend quelle partie est déjà réelle et quelle partie reste en R&D.
