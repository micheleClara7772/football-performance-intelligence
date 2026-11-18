# FPI — automatisation honnête de la recette historique de 125 cas

La recette initiale est décrite dans `docs/recette-pre17.md` et les cases humaines dans l'[Issue #15](https://github.com/micheleClara7772/football-performance-intelligence/issues/15).

La CI lance **`scripts/auto_acceptance.py` après le contrôle du match réel (3 381 événements) et le test navigateur Chromium**. Elle lit les 125 IDs A01–J10, exécute les assertions de calcul, contrôle la provenance et les exports, vérifie les preuves de navigation déjà produites et génère deux fichiers :

- `outputs/acceptance/rapport-recette-auto.json` : 125 lignes avec statut et preuve.
- `outputs/acceptance/rapport-recette-auto.md` : tableau synthétique lisible par un humain.

Les statuts sont `PASS_AUTOMATIQUE`, `PASS_NAVIGATEUR`, `ECHEC_AUTOMATIQUE` et `A_VALIDER_HUMAINEMENT`. **Une présence de bouton ou d'iframe n'est jamais considérée comme preuve de lecture vidéo.** Les conditions de licence FIFA/StatsBomb, l'OAuth de l'hébergement public, l'ergonomie subjective et l'autorisation de présenter à un partenaire nécessitent des décisions humaines.

**Ne jamais cocher les 125 cases de l'Issue #15 sur la seule base de ce script.** Il fournit un niveau de confiance technique vérifiable, et liste explicitement les cas restant hors automatisation. Les cas en échec font échouer la CI avant fusion.

Chaque CI dépose l'artefact nommé `fpi-auto-acceptance-125` téléchargeable dans GitHub Actions. Aucun média ni fichier fournisseur brut n'est commité.
