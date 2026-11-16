# Feuille de route FPI — 16 au 20 novembre 2026

Le suivi opérationnel détaillé et ses preuves sont dans **[Suivi actuel](suivi-actuel.md)**.

**Bilan du 16 novembre :** PR #20 stabilisée puis **fusionnée dans main** avec accord du porteur, [CI Python + dépendances verrouillées réussie](https://github.com/micheleClara7772/football-performance-intelligence/actions/runs/43947283070), [import réel et parcours navigateur réussis](https://github.com/micheleClara7772/football-performance-intelligence/actions/runs/43947283120). La nouvelle [PR #21](https://github.com/micheleClara7772/football-performance-intelligence/pull/21) prépare les annotations textuelles d'événements (brouillon, non fusionnée).

| Date | Prochaine action | Issues | Validation |
|---|---|---|---|
| **16 nov.** | Stabiliser PR #20 : avertissements Streamlit, interface française, fallback YouTube, revue CI, dépendances reproductibles | #4, #8, #15 | Tests verts sur la tête de PR, revue avant fusion |
| **17 nov.** | Revoir les métriques et préparer les annotations horodatées sans confusion avec le replay | #6, #7, #8, #11 | Calculs sourcés, annotations exportables, limites documentées |
| **18 nov.** | Consolider assistant factuel, séances éditables et parcours des cinq modules | #12, #13, #14 | Démo de bout en bout avec états honnêtes |
| **19 nov.** | Vérification sécurité/risques, répétition 7–10 min, scénario de secours | #15, #16 | Exécution reproductible, limites et droits explicités |
| **20 nov.** | Présentation envisagée si date et droits confirmés, puis synthèse des retours | #18 | Décision go/no-go et retours consignés |

**Acquis :** version 1 fusionnée dans `main` (PR #19). PR #20 en brouillon, [tests Python réussis](https://github.com/micheleClara7772/football-performance-intelligence/actions/runs/43778993298) et [données réelles + navigateur réussis](https://github.com/micheleClara7772/football-performance-intelligence/actions/runs/43778993223). L'utilisateur a vérifié Streamlit via Codespaces et importé 3 381 événements du match Maroc–Portugal.

**Risques à ne pas considérer comme résolus :** droits de démonstration commerciale StatsBomb, droits vidéo FIFA, échec iframe YouTube 153 ; l'extrait officiel reste accessible via le bouton externe. Une IA générative complète n'est pas encore intégrée.

**Priorité P2 :** #17 vues 360 seulement si le chemin critique est sécurisé. Aucune facturation ou abonnement nouveau sans accord.
