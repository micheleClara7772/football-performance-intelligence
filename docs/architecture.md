# Architecture cible
**Statut : choix validé ; implémentation non commencée.**

```text
UI Streamlit
 ├─ Dashboard collectif (Plotly)
 ├─ Analyse tactique (métriques + cartes)
 ├─ Vidéo annotée (adaptateur après choix des droits)
 ├─ Assistant IA (indicateurs déterministes)
 └─ Générateur de séances (validation humaine)
              │
     Services / logique métier
              │
     Données locales Parquet/JSON
              │
     Ingestion des sources autorisées
```

**Stack :** Python 3.11+, Streamlit, Pandas, Plotly, pytest ; mplsoccer si approprié ; API LLM configurable ; SQLite seulement si besoin.

## Principes
1. Une équipe configurable, pas de valeur Maroc hardcodée dans toutes les fonctions.
2. Chaque métrique a une définition, unité, source, périmètre, méthode et test.
3. L'IA s'appuie sur des chiffres calculés et cite ses preuves ; pas d'événement inventé.
4. Vidéo et analyse événementielle séparées : timestamp synchronisé seulement après contrôle.
5. Pas de commit de données ou médias non autorisés.
6. En absence d'API/réseau, état explicite et données locales utilisables.

## Structure cible (future)
```text
src/fpi/
  app.py
  config.py
  data/{loaders,validation}.py
  metrics/{collective,periods}.py
  analysis/tactical.py
  video/{models,adapter}.py
  ai/{context,assistant}.py
  training/{models,generator}.py
  ui/{dashboard,tactics,video,assistant,training}.py
tests/
```

## Environnement de développement et transfert

**Préférence obligatoire :** exécuter les installations et les tests dans un environnement **distant**, si compatible avec Cursor et sans facturation non autorisée. La configuration attendue est `.devcontainer/devcontainer.json` (Python 3.11) avec dépendances Python installées dans un `.venv/` interne à l'environnement et fichiers de dépendances reproductibles. Pour un développement local ultérieur, le `.venv` reste isolé mais **ne supprime pas** la nécessité d'une installation Python de base ; un conteneur local nécessiterait Docker ou équivalent. La portabilité résulte des manifestes versionnés et de la reconstruction sur une autre machine : ne pas transférer le dossier `.venv`.

En cas d'incompatibilité Cursor / hébergement distant ou de dépassement des quotas gratuits, **bloquer la mise en place et demander une décision** : ne pas installer automatiquement de composants sur le poste de travail et ne pas engager de frais.
