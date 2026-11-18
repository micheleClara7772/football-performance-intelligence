# FPI — scénario de démonstration interne (7 à 10 minutes)

**Statut : scénario prêt, répétition humaine non encore confirmée.** 
**Match unique :** Maroc–Portugal, 10 décembre 2022, FIFA Qatar 2022, source StatsBomb Open Data, ID 3869486. **Événements réels : 3 381.**

| Temps | Étape | Geste visible et élément de preuve |
|---|---|---|
| **0–1 min** | Accueil et import | FPI sur le port Codespaces privé ou la **vraie** URL Streamlit Cloud ; cliquer « Importer depuis StatsBomb » si cache absent, montrer 3 381 |
| **1–2 min** | Tableau de bord | Score 1–0, Maroc 9 tirs/249 passes ; Portugal 12 tirs/731 passes ; 1re/2e mi-temps, provenance |
| **2–4 min** | Tactique | Choisir une équipe et deux indicateurs, chronologie ; préciser cartes d'événements ≠ tracking ; onglet Annotations : sélectionner une action réelle et entrer une observation |
| **4–5 min** | Preuve vidéo | Ouvrir le **match intégral sur FIFA+ dans un nouvel onglet externe**. Ne pas le présenter comme intégré. Montrer éventuellement un résumé officiel YouTube (lien externe fiable). Mentionner que les repères de vidéo sont **manuels** |
| **5–6 min** | Notes exportables | Dans FPI, associer facultativement une URL FIFA+ et un horodatage manuel, exporter JSON ; réimporter le fichier dans une autre session si le temps le permet |
| **6–7 min** | Assistant | Poser deux des **8 questions guidées** (tirs, passes, xG, entrées dernier tiers) ; préciser « assistant factuel sans LLM » |
| **7–9 min** | Séance | Choisir objectif, 60 min, 18 joueurs, modifier consigne/matériel/variante ; vérifier total exact ; exporter JSON `À valider par l'entraîneur` |
| **9–10 min** | Conclusion | Expliquer limites (un seul match, données événementielles, vidéos officielles externes, droits et synchronisation non accordés) ; recueillir les retours |

## Préparation et plans de secours

- [ ] Ouvrir FPI et importer les événements du match **avant** la réunion si le cache est absent.
- [ ] Tester le véritable lien Streamlit Cloud (non créé automatiquement) dans un navigateur non connecté, en vérifiant l'accès public autorisé.
- [ ] Prévoir Codespaces privé comme secours si Cloud échoue ; ne pas rendre un port privé public pour contourner un 401.
- [ ] Tester le lien FIFA+ intégral, le lien YouTube officiel et la disponibilité géographique ; ne pas diffuser une vidéo sans droits.
- [ ] Tester au moins une annotation, export JSON, import JSON et export de séance.
- [ ] Préparer la présentation **sans images FIFA** si elles sont indisponibles ; ne jamais substituer une animation prétendument issue de la rencontre.
- [ ] Si StatsBomb est indisponible et aucun cache fiable : expliquer l'indisponibilité ; **ne pas montrer de chiffres simulés**.
- [ ] Si l'iframe YouTube affiche l'erreur 153 : désactiver l'essai et ouvrir le lien officiel externe.
- [ ] **Avant une présentation externe**, vérifier les obligations d'attribution StatsBomb et l'autorisation de tout contenu vidéo ou dérivé.
- [ ] Consigner les réactions dans [Issue #16](https://github.com/micheleClara7772/football-performance-intelligence/issues/16) et [Issue #18](https://github.com/micheleClara7772/football-performance-intelligence/issues/18).

**Décision de droits :** il n'existe à ce jour aucune confirmation de droits commerciaux StatsBomb/FIFA. La disponibilité d'un flux public, d'un dépôt privé ou d'une URL hébergée ne les remplace pas.
