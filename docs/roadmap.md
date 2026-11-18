# FPI — feuille de route à jour au 18 novembre 2026

| Créneau (heure de Paris) | Action / responsable | Preuve attendue |
|---|---|---|
| **Avant 16 h** | Code MVP cinq modules fusionné (développement FPI) | CI Python et Chromium vertes sur les PR concernées ; dernier lot #24 vert |
| **Avant 16 h** | **Propriétaire** : connecter GitHub à Streamlit Community Cloud, autoriser le dépôt privé, sélectionner main / app.py / Python 3.11 | Vraie URL `*.streamlit.app`, logs de démarrage sains |
| **16 h** | Revue interne utilisateur | Import réel et 5 modules, export/réimport notes, séances, lien FIFA+ intégral |
| **Après retour** | Corriger toute anomalie critique en branche et avec tests avant fusion | Issues liées et CI sur chaque tête de PR |
| **Avant 22 h** | Répétition de démo 7–10 minutes, test réseau/URL, plan de secours | [Scénario](demo.md), [Issue #16](https://github.com/micheleClara7772/football-performance-intelligence/issues/16) |
| **22 h envisagé** | Présentation à un partenaire **si usage et droits autorisés** | Décision explicite GO/NO-GO au regard des droits StatsBomb/FIFA |

**Le code fusionné n'est pas une URL publique déployée.** Le lecteur complet FIFA+ doit s'ouvrir à l'extérieur ; l'iframe facultative YouTube ne garantit pas de lecture des résumés. Assistant factuel, sans LLM. Vues 360, multi-match, suivi vidéo et sync auto hors MVP.

[Suivi complet](suivi-actuel.md) · [Guide d'hébergement gratuit](deploiement-gratuit.md) · [Bilan de conformité](mvp-acceptance-2026-11-18.md).
