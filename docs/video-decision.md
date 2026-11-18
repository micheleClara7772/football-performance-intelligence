# Décision vidéo FPI — état du 18 novembre 2026

## Ce qui est implémenté

1. **Match complet authentique Maroc–Portugal 2022** : rediffusion officielle FIFA+ à [ouvrir sur FIFA+](https://www.plus.fifa.com/it/content/marocco-portogallo-quarti-di-finale-coppa-del-mondo-fifa-qatar-2022-match-completo/5f1b5797-25d0-4e10-b723-5072b470bae8). Sa disponibilité, son prix local et sa lecture peuvent varier. **Aucun iframe FIFA+**, car [les conditions de la plateforme](https://inside.fifa.com/terms-of-service-fifaplus) interdisent son insertion dans un site tiers sans permission.
2. **Deux résumés officiels FIFA** : [prolongé](https://www.youtube.com/watch?v=5GVitElttLY) et [original](https://www.youtube.com/watch?v=M766FGsv5do). Le lien externe constitue le chemin fiable. Un lecteur officiel YouTube via `st.iframe` est **facultatif**, non contrôlé en lecture réelle : l'ancienne intégration provoquait **erreur 153** sur Codespaces.
3. **Annotations de l'événement** : event_id StatsBomb, équipe, type, période, minute/seconde du match. Note « Observation » ou « Hypothèse » et repère facultatif au lecteur FIFA+ / YouTube **saisi manuellement**, export/import JSON version 2 (import des v1 préservé). **Aucune correspondance automatique match–vidéo**.

## Ce qui n'est pas livré

- Aucune vidéo **complète** embarquée dans FPI, pas de copie MP4, téléchargement, montage ni redistribution de média FIFA.
- Pas de découpage de séquences, de suivi continu, de tracking, de synchronisation calculée, ni de licence commerciale acquise.
- Une vidéo d'un autre match ne pourra jamais être présentée comme Maroc–Portugal.
- Un véritable lecteur embarqué du match complet nécessite **un fichier original/licencié** autorisé pour cette finalité, les droits associés et des tests réels. L'accès public à FIFA+ ne constitue **pas** cette permission.

## Conséquences produit

- **MVP interne** : accès aux vraies images du match complet **externe** ; analyses et notes dans FPI, avec repères manuels.
- **Présentation à un partenaire** : réévaluer la finalité, droits et obligations avant diffusion des données/vidéos, même si l'URL Streamlit Cloud est publique.
- **Issues #9, #10, #11** restent ouvertes pour les droits, le lecteur vidéo intégral autorisé et l'annotation synchronisée.

**Sources :** [FIFA+ Terms of Service](https://inside.fifa.com/terms-of-service-fifaplus) · [StatsBomb Open Data](https://github.com/hudl/open-data).
