# Football Performance Intelligence (FPI)

## À lire en premier

👉 **[Suivi actuel : état réel, priorités et prochaines étapes (16–20 novembre)](docs/suivi-actuel.md)** · [GitHub Project](https://github.com/users/micheleClara7772/projects/1/views/1) · [PR #20](https://github.com/micheleClara7772/football-performance-intelligence/pull/20)


**Statut au 16/11/2026 : version 1 fusionnée dans main ; version 2 en PR #20 (prête pour revue, non fusionnée).**
**Démonstration ciblée : 20 novembre 2026 (rendez-vous à confirmer).**

FPI est un MVP d'analyse de la performance **collective** au football. Le match de référence retenu est **Maroc – Portugal (10 décembre 2022)**. Les droits des données et des vidéos restent à contrôler.

## Modules obligatoires
1. Dashboard de performance collective.
2. Analyse tactique par match et période.
3. Assistant IA contextualisé en français, alimenté par des métriques calculées.
4. Séquences vidéo annotées (**stratégie technique ouverte, décision à prendre**).
5. Générateur de séances d'entraînement révisables et validées par un entraîneur.

**Parcours principal :** dashboard → match → périodes → preuves chiffrées → vidéo → questions IA → séance.

## Principes
- Stack : Python, Streamlit, Pandas, Plotly, stockage local Parquet/JSON, tests pytest.
- Le dépôt est privé ; aucune donnée sous licence incertaine, vidéo protégée ou clé API n'y est publiée.
- Pas d'invention de résultats sportifs ; les conclusions doivent découler de données contrôlées.
- Le périmètre reste celui du MVP, avec cinq modules intégrés plutôt que cinq démos isolées.
- La vidéo n'est pas encore arbitrée ; toute alternative doit être explicitement validée.
- **Le socle de calcul et l'ingestion réelle ont été testés ; l'intégration métier finale, la vidéo et les droits commerciaux ne sont pas encore validés.**

## Organisation
Les Issues GitHub numérotées FPI-I01 à FPI-I18 décrivent les objectifs, critères d'acceptation, dépendances et échéances. Les priorités sont P0 (critique), P1, P2.
Les branches de développement prévues : `feat/*`, `fix/*` ; intégrer par Pull Request après tests. `main` doit rester stable.

## Calendrier
- 15 nov. : cadrage GitHub.
- 16 nov. : environnement et données.
- 17 nov. : indicateurs et tactique.
- 18 nov. : intégration des cinq modules.
- 19 nov. : stabilisation, répétition.
- 20 nov. : présentation, si confirmée.

## État d'avancement vérifié (16 novembre 2026)
- [x] Match Maroc–Portugal du 10/12/2022, identifiant 3869486.
- [x] Architecture Python / Streamlit et dépôt privé.
- [x] Version 1 fusionnée : [PR #19](https://github.com/micheleClara7772/football-performance-intelligence/pull/19).
- [x] Import StatsBomb réel contrôlé par l'utilisateur dans Codespaces : **3 381 événements**.
- [x] Cinq rubriques navigables et contrôles navigateur/CI sur [PR #20](https://github.com/micheleClara7772/football-performance-intelligence/pull/20) — **prête pour revue, non fusionnée**.
- [ ] Finaliser et intégrer la version 2 après revue et tests.
- [ ] Corriger l'expérience vidéo : YouTube fonctionne en externe, **erreur 153 en iframe**.
- [ ] Confirmer les droits commerciaux StatsBomb et FIFA avant tout usage non autorisé.
- [ ] Intégrer et valider le parcours complet de démonstration ; rendez-vous du 20 à confirmer.

## Vérification
L'installation isolée et les commandes de lancement sont décrites dans [DEVELOPMENT.md](DEVELOPMENT.md) ; le suivi opérationnel et ses liens de preuves sont dans [docs/suivi-actuel.md](docs/suivi-actuel.md).

**Le parcours complet en sept étapes n'est pas encore homologué.** La navigation des cinq rubriques et les données réelles ont toutefois été vérifiées. Voir le suivi actuel.
