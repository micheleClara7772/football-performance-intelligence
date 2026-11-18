> **Historique des cas de recette du 16 novembre** : les descriptions A01–J10 reflètent parfois l'état antérieur à la fusion des PR #21–#24. Les cases effectivement cochées par l'utilisateur sont conservées dans l'[Issue #15](https://github.com/micheleClara7772/football-performance-intelligence/issues/15), qui fait foi. Lire le [bilan du 18](mvp-acceptance-2026-11-18.md) pour les modifications récentes, notamment schéma v2 et replay FIFA+ externe.

# Recette FPI — contrôles historiques, à actualiser le 18 novembre 2026

**Checklist interactive à cocher dans [l'Issue #15](https://github.com/micheleClara7772/football-performance-intelligence/issues/15).**

## Recette de validation exhaustive — campagne du 16 novembre 2026 (avant le chantier du 17)

**Versions :** PR #20 fusionnée dans main ; [PR #21 — annotations](https://github.com/micheleClara7772/football-performance-intelligence/pull/21) **fusionnée** dans main. **Les validations humaines sont à cocher exclusivement par l'utilisateur dans l'Issue #15 (34/125 cochées au dernier contrôle).**

**Mode d'emploi :** cocher une case uniquement après avoir fait le test. Chaque ligne décrit **l'action** et **le résultat attendu**. Pour toute anomalie, commenter avec code de test, SHA/branche, étapes, attendu, observé, capture et gravité. Ne pas supprimer le cache du Codespace pour forcer un cas d'erreur ; réserver les tests destructifs aux copies ou à la CI.

**Préparation Codespaces :** redémarrer le Codespace existant, faire `git status --short` (ne pas perdre les modifications), `git fetch origin`, puis `git switch main` (ne pas répéter si déjà sur `main`), `git pull --ff-only`, `git rev-parse --short HEAD`. Dans le terminal distant : `.venv/bin/python -m pip install -r requirements/py311-linux.lock`, `.venv/bin/python -m pip install --no-deps -e .`, `.venv/bin/python -m pip check`, `.venv/bin/python -m pytest`. Ensuite `.venv/bin/python -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501`. Ouvrir PORTS/Preview in Editor avec port **Private**, puis arrêter avec Ctrl+C et Stop Codespace.

**Base de référence :** Maroc–Portugal 10 décembre 2022 ; match_id 3869486 ; 3 381 événements ; résultat 1–0 ; tirs Maroc 9/Portugal 12 ; passes tentées 249/731 (mi-temps 1 et 2).

### Preuves automatisées déjà acquises

- [x] PR #20 : [tests Python + environnement](https://github.com/micheleClara7772/football-performance-intelligence/actions/runs/43947283070) et [données réelles/navigateur](https://github.com/micheleClara7772/football-performance-intelligence/actions/runs/43947283120) réussis.
- [x] PR #21 : [tests Python](https://github.com/micheleClara7772/football-performance-intelligence/actions/runs/43953436532) et [données réelles + navigateur avec annotation](https://github.com/micheleClara7772/football-performance-intelligence/actions/runs/43953436485) réussis sur commit c4089f8.
- [ ] Après un nouveau commit, recontrôler les CI de la **nouvelle tête**, et examiner les captures de navigateur (dont 02b-annotations-evenements.png).

### Contrôles fonctionnels à cocher

#### A — Préparer GitHub et Codespaces (10 contrôles)

- [ ] **A01** — Confirmer PR #20 fusionnée et PR #21 fusionnée. **Attendu :** Bon statut dans GitHub.
- [ ] **A02** — Redémarrer le Codespace existant. **Attendu :** Pas de nouveau serveur créé.
- [ ] **A03** — Contrôler git status --short avant switch. **Attendu :** Pas de modifications personnelles écrasées.
- [ ] **A04** — Récupérer feat/event-annotations via git fetch origin. **Attendu :** La branche distante existe.
- [ ] **A05** — Basculer sur la branche et git pull --ff-only. **Attendu :** HEAD de PR #21 contrôlé.
- [ ] **A06** — Faire pip check dans .venv. **Attendu :** Aucune dépendance incompatible.
- [ ] **A07** — Faire pytest dans .venv. **Attendu :** Aucun test rouge.
- [ ] **A08** — Démarrer Streamlit port 8501. **Attendu :** Aucun traceback.
- [ ] **A09** — Ouvrir le port privé avec PORTS/Preview in Editor. **Attendu :** Aucune nécessité de rendre public.
- [ ] **A10** — Naviguer cinq rubriques et vérifier le titre du match. **Attendu :** Cinq onglets, pas d'erreur.

#### B — Import StatsBomb et cache (13 contrôles)

- [ ] **B01** — Sans données en cache, ouvrir le tableau de bord. **Attendu :** État vide, aucun chiffre inventé.
- [ ] **B02** — Cliquer Importer depuis StatsBomb. **Attendu :** Téléchargement sur demande seulement.
- [ ] **B03** — Attendre la validation. **Attendu :** Confirmation ou message d'erreur explicite.
- [ ] **B04** — Contrôler match et score. **Attendu :** Maroc 1–0 Portugal, 10/12/2022.
- [ ] **B05** — Contrôler le nombre d'événements. **Attendu :** 3 381 exactement.
- [ ] **B06** — Vérifier identité des sources dans la CI. **Attendu :** match_id 3869486, matches/43/106.json, events/3869486.json.
- [ ] **B07** — Revenir au tableau de bord après import. **Attendu :** Les chiffres apparaissent.
- [ ] **B08** — Changer de rubrique puis revenir. **Attendu :** Pas de nouvel import demandé.
- [ ] **B09** — Arrêter et relancer Streamlit sans supprimer fichiers. **Attendu :** Cache relu automatiquement.
- [ ] **B10** — Inspecter attribution/source/date. **Attendu :** StatsBomb Open Data et droits commerciaux non confirmés.
- [ ] **B11** — Vérifier .gitignore et dépôt. **Attendu :** Cache data/raw non commité.
- [ ] **B12** — Examiner les tests identifiant/score/ID événement erronés. **Attendu :** Données invalides refusées.
- [ ] **B13** — Examiner l'absence ou la corruption du cache dans tests. **Attendu :** Message clair sans métrique inventée.

#### C — Tableau de bord et exactitude (11 contrôles)

- [ ] **C01** — Vérifier titre, équipes et score. **Attendu :** Maroc 1–0 Portugal.
- [ ] **C02** — Additionner tirs périodes 1 et 2. **Attendu :** Maroc 9, Portugal 12.
- [ ] **C03** — Additionner passes tentées périodes 1 et 2. **Attendu :** Maroc 249, Portugal 731.
- [ ] **C04** — Contrôler graphique des tirs par période. **Attendu :** Deux équipes × deux périodes.
- [ ] **C05** — Comparer barres et tableau. **Attendu :** Chiffres cohérents.
- [ ] **C06** — Contrôler colonnes équipe/période/tirs/passes/%/xG. **Attendu :** Lisibles et en français.
- [ ] **C07** — Vérifier passes réussies ≤ tentées et 0 ≤ pourcentage ≤ 100. **Attendu :** Cohérence arithmétique.
- [ ] **C08** — Vérifier xG de chaque période. **Attendu :** Valeur fournisseur ou vide si information incomplète, jamais inventée.
- [ ] **C09** — Lire légendes du tableau. **Attendu :** Les seules périodes 1 et 2 sont exploitées.
- [ ] **C10** — Vérifier étiquette Maroc sans changer données Morocco. **Attendu :** Traduction d'affichage uniquement.
- [ ] **C11** — Vérifier infobulles et fenêtre étroite. **Attendu :** Diagramme lisible, aucun avertissement Streamlit width.

#### D — Analyse tactique (16 contrôles)

- [ ] **D01** — Changer équipe Maroc puis Portugal. **Attendu :** Indicateurs de la bonne équipe.
- [ ] **D02** — Comparaison des mi-temps, indicateur Tirs. **Attendu :** 1re, 2e et écart 2e moins 1re.
- [ ] **D03** — Tester Passes tentées/Passes réussies. **Attendu :** Identiques aux résultats du dashboard.
- [ ] **D04** — Tester Pressions, Récupérations, Interceptions, Entrées dernier tiers. **Attendu :** Graphiques actualisés.
- [ ] **D05** — Lire la réserve sur pression. **Attendu :** Pas d'inférence sur l'efficacité du pressing.
- [ ] **D06** — Lire la définition des entrées dernier tiers. **Attendu :** Passe réussie/conduite franchissant x=80, non exhaustif.
- [ ] **D07** — Contrôler chiffres du tableau tactique. **Attendu :** Cohérence avec le graphe.
- [ ] **D08** — Ouvrir Chronologie pour Tirs. **Attendu :** Six fenêtres de temps.
- [ ] **D09** — Changer Chronologie pour passes, pressions, récupérations. **Attendu :** Série cohérente.
- [ ] **D10** — Lire intervalles 0–14, 15–29, 30+, 45–59, 60–74, 75+. **Attendu :** Temps additionnel inclus, prolongations exclues.
- [ ] **D11** — Ouvrir Emplacements et basculer mi-temps. **Attendu :** Points actualisés.
- [ ] **D12** — Tester Tir, Passe, Pression, Récupération, Interception, Conduite. **Attendu :** Carte ou état vide lisible.
- [ ] **D13** — Survoler les points. **Attendu :** Coordonnées 120×80, joueur et minute si disponibles.
- [ ] **D14** — Lire légende spatiale. **Attendu :** Événements, pas tracking/trajectoire.
- [ ] **D15** — Changer équipe, onglet et revenir. **Attendu :** Pas de chiffres de l'équipe précédente.
- [ ] **D16** — Inspecter tests des coordonnées et filtres. **Attendu :** Valeurs invalides rejetées.

#### E — Vidéos FIFA officielles (10 contrôles)

- [ ] **E01** — Ouvrir Vidéo avec ou sans cache. **Attendu :** Page accessible.
- [ ] **E02** — Sélectionner résumé prolongé 2026. **Attendu :** Lien YouTube 5GVitElttLY.
- [ ] **E03** — Sélectionner résumé original 2022. **Attendu :** Lien YouTube M766FGsv5do.
- [ ] **E04** — Lire une vidéo sur YouTube. **Attendu :** Vraies images de Maroc–Portugal visibles.
- [ ] **E05** — Vérifier absence de l'iframe erreur 153. **Attendu :** Fallback externe clairement présenté.
- [ ] **E06** — Tester le lien FIFA.com. **Attendu :** Succès ou indisponibilité géographique consignée.
- [ ] **E07** — Lire description. **Attendu :** Résumé du match, jamais les 90 minutes promises.
- [ ] **E08** — Lire les avertissements de minutage. **Attendu :** Temps du montage distinct des minutes StatsBomb.
- [ ] **E09** — Vérifier fichiers dépôt et comportement. **Attendu :** Aucun téléchargement/stockage de vidéo FIFA.
- [ ] **E10** — Vérifier issues droits FIFA. **Attendu :** Aucune diffusion, copie ou montage commercial autorisé par défaut.

#### F — Assistant factuel (9 contrôles)

- [ ] **F01** — Ouvrir avant import. **Attendu :** Aucune réponse chiffrée fictive.
- [ ] **F02** — Après import, choisir Maroc puis Portugal. **Attendu :** Réponses contextualisées.
- [ ] **F03** — Question sur tirs des mi-temps. **Attendu :** Nombre, différence, réserve causale.
- [ ] **F04** — Question sur passes tentées/réussies. **Attendu :** Comptes cohérents avec tableau de bord et règle pass.outcome.
- [ ] **F05** — Question sur pressions et récupérations. **Attendu :** Compteurs fournisseur et réserves.
- [ ] **F06** — Question sur limites des indicateurs. **Attendu :** Réponse explicite sur données événementielles et 1re/2e période.
- [ ] **F07** — Lire avertissement IA. **Attendu :** Quatre questions déterministes, aucun LLM connecté.
- [ ] **F08** — Changer question, équipe et onglet. **Attendu :** Pas de mélange entre les contextes.
- [ ] **F09** — Examiner tests d'équipe et question inconnues. **Attendu :** Refus lisible.

#### G — Séances éditables (12 contrôles)

- [ ] **G01** — Sans données, ouvrir Séances. **Attendu :** Demande d'import.
- [ ] **G02** — Générer séance Maroc/Circulation. **Attendu :** Trois exercices.
- [ ] **G03** — Tester quatre objectifs du formulaire. **Attendu :** Exercices différents selon thème.
- [ ] **G04** — Tester 45, 60 et 75 minutes. **Attendu :** Somme initiale = objectif.
- [ ] **G05** — Tester effectifs 6 et 30. **Attendu :** Valeurs bornées et conservées.
- [ ] **G06** — Tester équipe Portugal puis Maroc. **Attendu :** Observations liées à la bonne équipe.
- [ ] **G07** — Lire contenu et réserve staff technique. **Attendu :** Pas de prescription automatique.
- [ ] **G08** — Modifier consigne et point de vigilance. **Attendu :** Modification conservée.
- [ ] **G09** — Modifier une durée pour incohérence. **Attendu :** Avertissement de durée et éventuelle anomalie d'export à signaler.
- [ ] **G10** — Ajouter ou supprimer exercice dans éditeur. **Attendu :** Tableau et total mis à jour.
- [ ] **G11** — Exporter fpi-proposition-seance.json. **Attendu :** Modifications, effectif, durée, approval À valider par l'entraîneur présents.
- [ ] **G12** — Lire note de causalité. **Attendu :** Les statistiques ne démontrent pas la cause tactique.

#### H — Annotations d'événements PR #21 uniquement (22 contrôles)

- [ ] **H01** — Ouvrir 4e onglet Annotations dans Analyse tactique. **Attendu :** Disponible sur feat/event-annotations, pas encore main.
- [ ] **H02** — Ouvrir sans données importées. **Attendu :** Aucun événement inventé.
- [ ] **H03** — Filtrer Maroc/Tir/1re mi-temps. **Attendu :** Vrais événements, minute, joueur, identifiant.
- [ ] **H04** — Changer équipe, période et six types. **Attendu :** Filtres cohérents.
- [ ] **H05** — Limiter intervalle à une zone vide. **Attendu :** Message Aucun événement.
- [ ] **H06** — Sélectionner grande plage >120 actions. **Attendu :** Demande de restreindre, liste plafonnée.
- [ ] **H07** — Choisir action et lire minute/seconde/ID. **Attendu :** Correspondance événement StatsBomb.
- [ ] **H08** — Enregistrer une Observation sans source vidéo. **Attendu :** Note dans tableau.
- [ ] **H09** — Enregistrer une Hypothèse sur autre action. **Attendu :** Deux notes différentes.
- [ ] **H10** — Essayer note vide. **Attendu :** Erreur de validation.
- [ ] **H11** — Essayer texte >2000 caractères. **Attendu :** Longueur limitée.
- [ ] **H12** — Associer résumé FIFA et saisir 02:43. **Attendu :** Repère montage manuel distinct de minute match.
- [ ] **H13** — Saisir 02:43 sans résumé sélectionné. **Attendu :** Erreur indiquant qu'une source est nécessaire.
- [ ] **H14** — Tester formats 2:99, abc, -1:21, 1:1:2. **Attendu :** Horodatage refusé.
- [ ] **H15** — Exporter fichier fpi-annotations-maroc-portugal.json. **Attendu :** Notes et références, aucune vidéo.
- [ ] **H16** — Examiner JSON exporté. **Attendu :** schema_version=2, match_id=3869486, video_sync=manual_player_clock_only (anciens fichiers v1 importables).
- [ ] **H17** — Dans session neuve, réimporter JSON. **Attendu :** Notes restaurées sans sauvegarde serveur automatique.
- [ ] **H18** — Comparer avant/après réimport. **Attendu :** Textes, IDs, minute match et horloge du résumé inchangés.
- [ ] **H19** — Importer copie de JSON avec mauvais match ou event_id. **Attendu :** Rejet sans perdre notes valides.
- [ ] **H20** — Modifier note existante et réexporter. **Attendu :** Une note par ID et dernière modification.
- [ ] **H21** — Contrôler plafonds de 250 notes, 1Mo et URL FIFA. **Attendu :** Limites appliquées.
- [ ] **H22** — Lire nature du module. **Attendu :** Pas de découpage ni de synchronisation vidéo automatique.

#### I — Robustesse, sécurité, conformité (12 contrôles)

- [ ] **I01** — Naviguer plusieurs fois et changer filtres. **Attendu :** Pas d'exception ni de mauvaise équipe.
- [ ] **I02** — Tester fenêtre large/étroite et scrolling. **Attendu :** Boutons accessibles.
- [ ] **I03** — Contrôler accents, termes français, états vides. **Attendu :** Messages clairs.
- [ ] **I04** — Inspecter UI, fichiers exports et commits. **Attendu :** Aucun secret ou clé API.
- [ ] **I05** — Inspecter repo/gitignore. **Attendu :** Pas de JSON StatsBomb brut, fichier FIFA ni .env secret.
- [ ] **I06** — Simuler panne de cache/réseau dans test isolé. **Attendu :** Pas de chiffres fictifs ni faux succès.
- [ ] **I07** — Inspecter tests d'entrées malformées. **Attendu :** Refus propre.
- [ ] **I08** — Consulter Issue #3 StatsBomb. **Attendu :** Licence commerciale et attribution/logo toujours ouverts.
- [ ] **I09** — Consulter #9/#10 FIFA. **Attendu :** YouTube ne vaut pas licence commerciale.
- [ ] **I10** — Vérifier 360, LLM et lecture synchronisée. **Attendu :** Ne sont pas annoncés comme livrés.
- [ ] **I11** — Vérifier quotas et absence d'abonnement imposé. **Attendu :** Aucun coût supplémentaire sans accord.
- [ ] **I12** — Après recette, Ctrl+C puis Stop Codespace. **Attendu :** Pas Delete, fichiers conservés.

#### J — Verdict avant travaux du 17 (10 contrôles)

- [ ] **J01** — Contrôler deux workflows sur tête de PR #21. **Attendu :** Les deux success, aucun nouveau commit non testé.
- [ ] **J02** — Tester manuellement les cinq modules. **Attendu :** Pas de bug P0 non résolu.
- [ ] **J03** — Tester annotations export ET réimport. **Attendu :** Pas de perte de notes.
- [ ] **J04** — Vérifier match de référence. **Attendu :** 3381, 1–0, tirs 9/12, passes 249/731.
- [ ] **J05** — Vérifier vrais résumés FIFA via URL externe. **Attendu :** Pas de lecteur cassé présenté.
- [ ] **J06** — Vérifier gestion cache/erreur. **Attendu :** Pas de données inventées.
- [ ] **J07** — Consigner réserves juridiques. **Attendu :** Développement interne possible sans prétendre usage commercial.
- [ ] **J08** — Écrire verdict GO / GO avec réserves / NO-GO, date, SHA, validateur. **Attendu :** Décision traçable.
- [ ] **J09** — Créer/relier issues pour anomalies avec capture et étapes. **Attendu :** Bugs classés P0/P1/P2.
- [ ] **J10** — Garder PR #21 en brouillon jusqu'à validation propre. **Attendu :** Aucune fusion implicite.

### Décision finale

- [ ] **GO interne** — aucun bug critique, parcours métier validé, versions testées.
- [ ] **GO avec réserves** — anomalies mineures consignées, travaux internes autorisés seulement.
- [ ] **NO-GO** — chiffres faux, perte de notes, fuite de secret, blocage de démarrage ou tests rouges.

**Validateur :** à renseigner. **Date :** à renseigner. **Version/SHA :** à renseigner. **Anomalies :** à renseigner. Un seul verdict à cocher.

**La licence commerciale StatsBomb/FIFA n'est pas confirmée.** Continuer des tests et du développement internes ne signifie pas autorisation de diffusion ou de démonstration commerciale. Les 360, le LLM complet et la synchronisation avec des vidéos autorisées ne sont pas encore livrés.

**Liens :** [PR #21](https://github.com/micheleClara7772/football-performance-intelligence/pull/21) · [Issue #11 — synchronisation vidéo encore bloquée](https://github.com/micheleClara7772/football-performance-intelligence/issues/11).
