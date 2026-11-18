# Assistant à questions libres et coût zéro

L'assistant répond à une **question libre saisie en français** et non à un menu imposé. Son moteur interprète les mots clés, les équipes, la période et les intervalles temporels, puis calcule des réponses uniquement depuis les événements StatsBomb chargés. Il fonctionne sur Streamlit Community Cloud **sans modèle externe, sans token, sans facturation et sans réseau supplémentaire**.

**Mesures couvertes :** tirs, passes (et réussite), buts signalés par Shot/Goal, xG StatsBomb avec complétude, pressions annotées, récupérations, interceptions, progressions franchissant le dernier tiers, conduites, dribbles, fautes et hors-jeu. Classement des joueurs à partir des événements identifiés ; comparaisons d'équipes ; première/deuxième mi-temps ; intervalles de minutes.

Le moteur **n'est pas un LLM** et ne comprend pas toute la langue naturelle. Il reconnaît des reformulations et reconnaît explicitement ce qu'il ne peut pas calculer. Une question hors couverture déclenche une explication et non une statistique inventée. Les formulations causales, schémas, possession, tracking, vitesse, distance et tactique des images ne sont pas déduites de ces données.

Source StatsBomb Open Data / matchs 2022 sous obligations d'attribution, droits commerciaux non confirmés. Les événements temporels ne sont pas automatiquement synchronisés à la rediffusion FIFA+.

Les tests unitaires couvrent questions individuelles, comparaison, période, fenêtre, xG, joueurs, requêtes interdites et saisies malformées ; la CI navigateur doit valider un envoi via `st.chat_input` sur les **3 381 événements** du match réel.
