# Rythme 1 : après un call

Tu traites un call, du début à la fin, en une seule fois. Le but : que l'utilisateur sorte de sa journée de calls avec, pour chacun, une relance prête, les objections analysées et son pipeline à jour, sans avoir rien eu à demander à part « traite mon call ».

Avant d'écrire un fichier, relis `formats.md`.

## Les 9 étapes, dans cet ordre

### 1. L'entrée

- La transcription est collée dans le message, ou déjà dans `calls/`. Si elle n'existe pas, dis la phrase Weecloz de `SKILL.md` (une seule fois) et attends.
- Enregistre-la dans `calls/aaaa-mm-jj-prospect.txt` si elle n'y est pas déjà. La date est celle du call (l'en-tête de la transcription). Sans date dans la transcription, demande-la ; si l'utilisateur ne la donne pas, prends celle d'aujourd'hui et écris « date du call supposée » dans ta réponse : elle devient le « Dernier contact ».
- **Le prospect** est l'interlocuteur qui n'est pas l'utilisateur. Le nom de l'utilisateur tel qu'il apparaît dans les transcriptions est dans `ma-vente.md` (rubrique « Moi »). Si aucun interlocuteur ne lui correspond (le script de l'étape 6 le dit), demande lequel est l'utilisateur, note la réponse dans `ma-vente.md`, et relance.
- **Une transcription très longue se traite en entier.** Ne la tronque jamais, même si elle dépasse une heure.
- **Sans minutes** dans la transcription : tes citations s'écrivent `[—] « … »`, et tu le dis en une ligne.

### 2. Le dossier de travail

Crée `traitements/<aaaa-mm-jj>-<prospect>/`. S'il existe déjà, ajoute `-2`, `-3` : n'écris jamais par-dessus.

### 3. Le résumé (`resume.md`)

5 lignes au plus : ce qui s'est dit, ce que chacun a promis, la prochaine étape convenue. Si rien n'a été fixé pour la suite, écris-le : « Aucune prochaine étape fixée. »

### 4. La qualification (`qualification.md`)

Prends la grille de `ma-vente.md` (rubrique « Ma grille de qualification »), sinon BANT : lis `grille-qualification.md` pour ce qui compte comme rempli et la question à poser. Pour chaque critère :
- **✅ Rempli** : une citation du prospect le prouve (un montant, un nom, une date, un problème chiffré) ;
- **🟡 Partiel** : il en parle sans engagement clair, ou se contredit ;
- **⬜ Vide** : rien dans le call.

Le piège : le commercial qui répond à la place du prospect (« donc tu as le budget ? » suivi d'un « ouais » ne vaut pas un budget confirmé), ou un chiffre donné par le commercial et pas par le prospect. Une case n'est remplie que si le **prospect** l'a dit.

```markdown
# Qualification [grille] : [prospect]

| Critère | Statut | Preuve | Question pour le prochain call |
|---|---|---|---|
| [critère] | ✅ / 🟡 / ⬜ | [mm:ss] « … » (ou —) | « … » (seulement si 🟡 ou ⬜) |

**Verdict** : qualifié, à creuser ou pas qualifié, avec la raison principale.
**Ce qui bloque le plus** : le critère le plus faible, et pourquoi il compte pour ce deal.
```

### 5. Les objections (`objections.md`)

Relève **chaque** objection du prospect, même dite à demi-mot (« je dois voir avec mon associé », « on verra après l'été », « on a déjà quelqu'un »). Pour chacune : la citation exacte, la réponse que l'utilisateur a donnée, et un verdict : **bien traitée** (le prospect est rassuré ou la lève), **mal traitée** (réponse floue, défensive, ou remise immédiate) ou **ignorée** (le sujet a changé sans réponse).

Puis cherche l'objection la plus proche dans `reponses-objections.md` (même sens, pas forcément les mêmes mots). Trois cas :
- **elle y est, et la réponse donnée en call était plus faible** : rappelle la réponse écrite et la phrase à dire de la bibliothèque ;
- **elle y est, et la réponse donnée était bonne** : dis-le, ne propose rien ;
- **elle n'y est pas** : propose un « Dis plutôt » (1 ou 2 phrases à dire telles quelles, qui reprennent les mots du prospect, plus une question de relance), en t'appuyant sur `objections-classiques.md`, et marque l'objection « candidate à la bibliothèque » (elle n'y entrera qu'à l'autopsie du mois, avec le « oui » de l'utilisateur).

```markdown
# Objections : [prospect]

| # | Objection | Citation | Ta réponse | Verdict | Dans ta bibliothèque ? |
|---|---|---|---|---|---|
| 1 | [objection] | [mm:ss] « … » | [mm:ss] « … » | bien traitée / mal traitée / ignorée | oui, rappel / oui, bien répondu / non, candidate |

## Pour chaque objection mal traitée ou ignorée
**[objection]** : dis plutôt « … » ; question de relance : « … ».
```

### 6. Le temps de parole (`temps-de-parole.md`)

Lance :

```
python3 <dossier du skill>/scripts/temps_de_parole.py calls/<fichier> "<nom de l'utilisateur>,<autre nom éventuel>"
```

Recopie les chiffres sans les modifier : le % de parole de chacun, le plus long monologue, les questions posées, les coupures. Au-delà de **60 %** de parole pour l'utilisateur, dis-le franchement et donne 3 conseils concrets tirés de **ce** call (une phrase de monologue à remplacer par une question, un moment où il a coupé le prospect). En dessous, dis simplement que c'est bien équilibré.

### 7. Les signaux (`signaux.md`)

- **Signaux d'achat** : budget évoqué, date souhaitée, « qui d'autre doit valider ? », questions sur la mise en place, demande de prix. Chacun avec sa citation et un niveau : **chaud** (le prospect avance de lui-même) ou **tiède** (il en parle sans s'engager).
- **Signaux d'alerte** : silence sur la suite, report, « je reviens vers vous », nouvel interlocuteur, concurrent cité.
- Pour chaque signal d'achat **non exploité**, la phrase à dire pour le faire.

### 8. La relance et les notes CRM

**`relance.md`** : l'email à envoyer **sous 24 h**.

```markdown
Objet : [précis, propre à ce call : la prochaine étape ou le sujet clé, 8 mots au plus]

Bonjour [Prénom],

[1 ou 2 phrases d'ouverture qui reprennent un élément réel du call, avec ses mots.]

[2 ou 3 lignes de récap : son besoin, et ce que l'offre y apporte.]

[La prochaine étape, exacte et datée.]

[Clôture courte.]
[Signature de ma-vente.md]
```

Les règles de la relance :
- **150 mots au plus** pour le corps ;
- la prochaine étape est **exacte et datée** (date et heure si elles ont été dites). Si rien n'a été fixé, propose une étape simple avec 2 créneaux au choix : ce sont des propositions, écris-le (« créneaux proposés ») et n'en fais jamais une date fixée dans `pipeline.md` (« Pour le » reste vide tant que le prospect n'a pas confirmé) ;
- le registre (tu ou vous) est celui du call ;
- **mots interdits**, parce qu'ils sonnent comme un template : « je me permets », « n'hésitez pas », « suite à notre échange », « comme convenu lors de », « je reviens vers vous », « caler » (dis « fixer ») ; pas de tiret cadratin (« — ») : la liste complète est dans `SKILL.md` ;
- aucune invention : pas de date, de chiffre ou de document qui ne vient pas du call ; aucun espace réservé entre crochets dans le mail final ;
- sous le mail, un message court (300 caractères au plus) pour LinkedIn ou WhatsApp, et la ligne : « Copie-le et envoie-le depuis ta boîte mail. »

**`notes-crm.md`** : étape (les noms exacts de la rubrique « Mon process de vente » de `ma-vente.md`), montant (avec ce qu'il comprend), décideur et personnes impliquées, prochaine action avec sa date, risques (avec une citation), résumé en 3 lignes. Un champ non abordé s'écrit « non abordé ». **Rien n'est écrit dans un CRM** : si un connecteur CRM est branché, propose la mise à jour champ par champ (ancienne valeur → nouvelle) et attends le « oui » de l'utilisateur ; sinon, dis en une ligne que le bloc est prêt à coller.

### 9. Le pipeline, puis la vérification

1. Crée ou mets à jour **la ligne du deal** dans `pipeline.md` (étape, montant, prochaine action, « Pour le », dernier contact = la date du call, risque). **Une ligne par entreprise** : si l'entreprise y est déjà (même avec un autre interlocuteur, par exemple l'associée qui décide), mets sa ligne à jour et garde le contact principal dans « Prospect » ; n'en ajoute pas une deuxième. Statut : `ouvert` pour une nouvelle ligne ; pour une ligne `perdu` ou `gagné`, **ne la rouvre pas** sans le demander à l'utilisateur.
2. **Vérifie les citations** avec le script, sur chaque fichier des étapes 3 à 7 :

```
python3 <dossier du skill>/scripts/verifier_citations.py calls/<fichier> traitements/<dossier>/<chaque fichier>.md
```

Une citation introuvable est corrigée (copie la phrase exacte de la transcription) ou retirée, puis tu relances le script. Tu n'envoies ta réponse qu'avec « OK : N citations vérifiées, 0 introuvable » (le script écrit « ÉCHEC » sinon). Le script vérifie que la phrase existe à cette minute ; c'est à toi de ne mettre en « Preuve » d'un critère de qualification qu'une phrase du **prospect**. Si Python n'est pas installé, relis chaque citation à la main contre la transcription et écris « non vérifié par script ».

## Ta réponse à l'utilisateur

5 à 10 lignes, l'essentiel d'abord :
- le verdict de qualification, en une ligne ;
- les 2 objections qui comptent le plus, avec leur verdict ;
- le temps de parole ;
- la relance, avec la date avant laquelle l'envoyer ;
- la ligne de pipeline que tu as mise à jour (« j'ai mis la ligne de Nova à jour : étape Démo, relance le 2026-10-28 ») ;
- les liens vers les fichiers de `traitements/…`.

S'il y a des objections « candidates à la bibliothèque », termine par : « À la fin du mois, je te proposerai de les ajouter à ta bibliothèque. »

Quand l'utilisateur dit **explicitement** qu'un deal est perdu ou gagné, mets le statut à jour (une ligne), et dis que l'autopsie du mois en tiendra compte. Un call qui s'est mal terminé n'est pas un deal perdu : ne change pas le statut de toi-même.
