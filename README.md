# Football Performance Intelligence (FPI)

**Statut : cadrage et configuration GitHub — application non implémentée.**
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
- **Aucune implémentation métier ni démonstration fonctionnelle n'est encore vérifiée.**

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

## État d'avancement
- [x] Choix du match Maroc–Portugal.
- [x] Choix d'architecture Python/Streamlit.
- [x] Dépôt privé créé.
- [ ] Stratégie vidéo validée.
- [ ] Licence et couverture StatsBomb vérifiées.
- [ ] Données du match ingérées.
- [ ] Modules implémentés et testés.
- [ ] Démonstration de bout en bout validée.

## Vérification
Le socle local préparatoire contient la documentation plus complète, les scripts de cohérence et les modèles GitHub. Les fichiers seront ajoutés au dépôt au fur et à mesure des opérations de publication.

**Statut du produit : 0/7 étapes du parcours vérifiées.**
