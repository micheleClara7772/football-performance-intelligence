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
