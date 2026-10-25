# Les formats exacts

Tu écris les fichiers de l'utilisateur toujours dans ces formats : le script `pipeline.py` et le skill lui-même les relisent.

## `pipeline.md`

Un tableau Markdown. Les colonnes sont reconnues par leur nom (accents et majuscules ignorés), dans n'importe quel ordre.

```markdown
# Pipeline

| Prospect | Entreprise | Étape | Montant | Prochaine action | Pour le | Dernier contact | Risque | Statut |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Marc Lefort | Nova | Démo | 4200 € | Envoyer la proposition | 2026-10-28 | 2026-10-22 | budget flou | ouvert |
| Claire Morel | Cabinet Morel | Proposition | 9000 € | Relancer | 2026-10-20 | 2026-10-12 | | ouvert |
| Hugo Bernard | Bernard Frères | Démo | 6000 € | | | 2026-10-05 | prix | perdu |
```

Les règles :
- **Dates** : `aaaa-mm-jj` (`jj/mm/aaaa` est aussi lu). Une date illisible est signalée à l'utilisateur, jamais devinée.
- **Statut** : `ouvert`, `gagné` ou `perdu`. La date d'un deal perdu est son « Dernier contact ».
- **Étape** : les noms exacts de la rubrique « Mon process de vente » de `ma-vente.md`.
- **Une ligne par entreprise.** Si l'entreprise existe déjà (même avec un autre interlocuteur), tu **mets à jour** sa ligne : tu n'en ajoutes pas une deuxième. Le contact principal reste dans « Prospect ». Deux deals vraiment distincts dans la même entreprise : demande à l'utilisateur avant d'ajouter une ligne.
- **Statut** : écris exactement `ouvert`, `gagné` ou `perdu` (le script lit aussi « perdue », « signé », « en cours », mais n'écris pas autre chose).
- **Prochaine action et « Pour le »** : toujours remplies pour un deal ouvert. Un deal sans prochaine étape datée est un deal qui meurt : si le call n'en a pas fixé, écris « à fixer » dans « Prochaine action », laisse « Pour le » vide, et dis-le.
- Tu relis ce tableau avec : `python3 <dossier du skill>/scripts/pipeline.py pipeline.md --today aaaa-mm-jj`.

## `reponses-objections.md`

Un bloc par objection, de cette forme exacte :

```markdown
## « C'est trop cher »

- **Réponse écrite** : Demande à quoi il compare. Si c'est un autre outil, reviens sur ce qu'il te fait gagner par mois ; si c'est « rien », chiffre ce que lui coûte le problème.
- **Phrase à dire** : « Trop cher par rapport à quoi ? »
- **Ajoutée le** : 2026-10-26
- **Dernière mise à jour** : 2026-10-26
- **Vue** : 3 fois (Nova 2026-10-20, Morel 2026-10-12, Weber 2026-10-08)
```

« Vue » = le nombre de calls traités où l'objection a été entendue, avec leurs dates.

Le fichier vide ne contient que son titre `# Mes réponses aux objections` et une phrase d'explication. Seul le « oui » de l'utilisateur ajoute ou modifie un bloc.

## Les sorties d'un call traité

Dans `traitements/<aaaa-mm-jj>-<prospect>/` : `resume.md`, `qualification.md`, `objections.md`, `temps-de-parole.md`, `signaux.md`, `relance.md`, `notes-crm.md`. Les gabarits sont dans `apres-un-call.md`. Si le dossier existe déjà, ajoute `-2`, `-3` : n'écris jamais par-dessus.

La revue du lundi s'écrit dans `traitements/revue-<aaaa-mm-jj>.md`, l'autopsie dans `traitements/autopsie-<aaaa-mm>.md`.
