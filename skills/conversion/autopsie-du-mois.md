# Rythme 3 : l'autopsie du mois (la boucle)

Un deal perdu isolé est une anecdote. Trois deals perdus pour la même raison, c'est un chantier. Une fois par mois, tu cherches les raisons qui **reviennent**, et tu en fais de meilleures réponses pour la bibliothèque : c'est ce qui fait que le système s'améliore.

## Les 8 étapes

### 1. Les deals perdus du mois

Lance :

```
python3 <dossier du skill>/scripts/pipeline.py pipeline.md --today <aujourd'hui, aaaa-mm-jj> --mois <aaaa-mm>
```

Les deals perdus du mois sont ceux de « Perdus en <mois> ». Pour ceux de « Perdus sans date (à dater) » : demande leur date de perte en une question, écris-la dans la colonne « Dernier contact » de `pipeline.md`, et relance le script.

### 2. Lis chaque deal perdu

Pour chaque deal perdu, lis ses transcriptions dans `calls/` (cherche le nom du prospect dans les noms de fichiers). Note :
- l'étape où le deal a basculé (le moment où le prospect décroche, l'objection restée sans réponse, ou la fin d'un call sans prochaine étape) ;
- la raison principale, en quelques mots ;
- une citation du prospect qui la prouve, au format `[mm:ss] « … »` (ou `[—] « … »` sans minutes).

Sans transcription pour un deal, travaille sur la colonne « Risque » de `pipeline.md` et dis que l'analyse de ce deal est plus faible.

### 3. Peu de deals

Moins de 3 deals perdus : fais l'analyse quand même, et dis qu'on ne peut pas encore parler de tendance. Aucun deal perdu : dis-le, félicite sobrement, et propose plutôt de relire la bibliothèque.

### 4. Regroupe

Regroupe les raisons proches sous un même nom (« prix non justifié » regroupe « trop cher » et « pas le budget pour ça »). Garde les 3 plus fréquentes, de la plus fréquente à la moins fréquente.

### 5. Écris l'autopsie

Dans `traitements/autopsie-<aaaa-mm>.md` :

```markdown
# Autopsie [aaaa-mm] : [N] deals perdus

## Les 3 raisons qui reviennent

### 1. [Raison] : [n] deals sur [N]
- Où : [étape]
- Preuves :
  - [Deal] [mm:ss] « … »
  - [Deal] [mm:ss] « … »
- Ce qui s'est passé : une ligne.

### 2. …
### 3. …

## À changer dès ton prochain call
1. [Action concrète] : par exemple, la phrase à dire : « … »
2. …
3. …
```

### 6. La boucle : propose de meilleures réponses

Pour chaque raison qui est une **objection** (prix, timing, concurrent, décideur absent…), écris une meilleure réponse : la réponse écrite, la phrase à dire, et la citation qui la justifie. Compare avec `reponses-objections.md` :
- l'objection y est déjà : propose une **modification** (montre l'ancienne réponse et la nouvelle) ;
- elle n'y est pas : propose un **ajout**.

Numérote les propositions et montre-les avec le format exact de `formats.md`.

### 7. Demande, puis attends

Termine par : « J'ajoute tout à ta bibliothèque ? Réponds "oui", "oui sauf 2" ou "non". » **Ne modifie rien avant la réponse.**

### 8. Exécute la réponse

- **« oui »** : écris toutes les propositions.
- **« oui sauf 2 »** : écris toutes les propositions sauf la 2, qui ne bouge pas.
- **« non »** (ou toute réponse qui refuse tout) : ne touche à rien. `reponses-objections.md` reste **identique au caractère près**, et tu le dis.

Pour chaque proposition validée : la date du jour dans « Ajoutée le » (ajout) ou « Dernière mise à jour » (modification), et « Vue : N fois » avec les deals de l'autopsie. Rends compte ligne par ligne (« ajoutée : "C'est trop cher" », « modifiée : … », « pas touchée : la 2 »).

Termine en rappelant que ces réponses seront reprises au prochain call : au rythme 1 (étape 5), chaque objection est comparée à la bibliothèque.
