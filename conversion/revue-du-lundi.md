# Rythme 2 : la revue du lundi

En 5 minutes, l'utilisateur sait où en est son pipeline, quels deals sont en train de mourir et où mettre son énergie cette semaine. Tu ne devines aucune date : le script les calcule.

## Les 5 étapes

### 1. Lis le pipeline

Lance :

```
python3 <dossier du skill>/scripts/pipeline.py pipeline.md --today <la date d'aujourd'hui, aaaa-mm-jj>
```

Le script donne : les deals qui dorment (7 jours ou plus), ceux **sans prochaine étape datée**, ceux **en retard** sur leur prochaine étape, et ce qui est à corriger dans le fichier.

Si l'utilisateur colle un export CSV de son CRM, enregistre-le à la racine du dossier de travail et croise-le : un deal du CSV absent de `pipeline.md` est listé « absent de ton pipeline » (tu ne l'ajoutes qu'avec son accord). Le CSV ne remplace jamais `pipeline.md`. Si l'utilisateur a un CRM (voir « Mon process de vente » de `ma-vente.md`) et n'a pas collé d'export, demande en une ligne : « As-tu modifié des deals dans ton CRM depuis la dernière revue ? Si oui, glisse un export et je mets ton pipeline à jour avant la revue. »

### 2. Ce qui est à corriger passe en premier

Si le script affiche « À corriger dans pipeline.md », montre-le d'abord, une phrase par ligne (« ligne 4 : date illisible, écris-la aaaa-mm-jj »), et propose de corriger toi-même si la bonne valeur est évidente (tu demandes avant de modifier). Continue avec ce qui est lisible : une ligne abîmée ne bloque pas la revue.

### 3. Pipeline vide

S'il n'y a aucun deal ouvert, dis-le en une ligne et propose de traiter un premier call (« colle la transcription de ton dernier call »). Ne fabrique pas de revue vide.

### 4. Écris la revue

Dans `traitements/revue-<aaaa-mm-jj>.md`, et en résumé dans la conversation :

```markdown
# Revue du lundi [aaaa-mm-jj]

## Ce qui a bougé
- [prospect] : [ce qui a changé depuis la dernière revue : nouvelle étape, nouveau contact]
(Source : relis le dernier `traitements/revue-*.md` ; les deals dont le « Dernier contact » est postérieur à sa date, ou qui n'y figuraient pas, ont bougé. Sans revue précédente : « Première revue : rien à comparer. » N'invente jamais un mouvement qui n'est pas dans ces deux sources.)

## Les deals qui dorment (7 jours ou plus)
- [entreprise] ([prospect]), étape [étape], [N] jours sans nouvelle : [la première chose à faire]

## Sans prochaine étape datée
- [entreprise] ([prospect]) : un deal sans prochaine étape datée est un deal qui meurt. [une étape à proposer, avec une date]

## En retard
- [entreprise] : « [action] » prévue le [date].

## Tes 3 priorités de la semaine
1. [entreprise] : [première action], parce que [la raison, en une ligne : montant, étape, risque]
2. …
3. …
```

Les 3 priorités viennent des chiffres du pipeline (le montant, l'étape, le temps sans nouvelle, le risque), pas d'une impression. Dis pourquoi chacune passe avant les autres.

### 5. Une relance pour chaque deal qui dort

Dans le même fichier, une relance courte par deal qui dort, avec les mêmes règles que `apres-un-call.md` (étape 8) : 150 mots au plus, une prochaine étape datée, aucune formule interdite. Si le deal a une transcription dans `calls/`, reprends les mots du prospect ; sinon, n'invente rien : appuie-toi sur la prochaine action écrite dans `pipeline.md`.

## Règles propres à ce rythme

- Les jours sans nouvelle viennent du script. Si Python n'est pas installé, calcule à la main et écris « non vérifié par script ».
- Un deal sans date de dernier contact est signalé comme « date inconnue » : demande-la, ne la devine pas.
- **Une action en retard n'est pas une action « qui n'a pas eu lieu ».** `pipeline.md` dit seulement ce qui était prévu et quand : le deal a pu avancer sans que le fichier soit mis à jour. Écris « prévue le [date], pas mise à jour dans ton pipeline », demande à l'utilisateur ce qui s'est passé, et n'affirme jamais dans une relance qu'un rendez-vous ou un envoi n'a pas eu lieu.
- Les relances suivent la liste des mots interdits de `SKILL.md`.
- Tu ne passes jamais un deal en `perdu` ou `gagné` de toi-même : demande-le.

## Importer un export (« ajoute ces deals à mon pipeline », « mets mon pipeline à jour avec cet export »)

Pour démarrer avec les deals d'un CRM, ou resynchroniser `pipeline.md` après des changements faits dans le CRM :
1. Enregistre l'export CSV à la racine du dossier de travail, et lis-le.
2. Compare avec `pipeline.md` **par entreprise** (une ligne par entreprise) : deals nouveaux, deals dont l'étape ou le montant a changé, deals gagnés ou perdus dans le CRM.
3. Montre la liste des changements (« j'ajoute 12 deals, je passe Nova en Négociation, je marque Weber SAS gagné ») et **attends le « oui »** avant d'écrire quoi que ce soit.
4. Après le « oui », écris. Un deal importé sans prochaine action prend « à fixer » : il apparaîtra « sans prochaine étape datée » tant que l'utilisateur ne l'a pas renseigné, et c'est voulu.
5. Les deals perdus avant l'installation n'ont pas de transcription : l'autopsie les compte, avec une analyse plus faible.

