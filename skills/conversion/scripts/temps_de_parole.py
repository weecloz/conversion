"""Temps de parole d'un call de vente.

Usage : python3 compter.py <transcription.txt> "<nom du commercial>[,autre nom]"
Exemple : python3 compter.py call.txt "Alex,You,Vous"

Lit une transcription Weecloz, avec l'heure (« [mm:ss] Nom: texte » ou « [mm:ss] Nom : texte »)
ou sans l'heure (« Nom : texte », un paragraphe par tour de parole), et affiche le % de parole
par interlocuteur, le plus long monologue du commercial, le nombre de « ? » dans ses répliques
et les coupures probables. Les noms sont comparés sans tenir compte des majuscules ni des accents
décomposés.
"""
import re
import sys
import unicodedata

TIMED = re.compile(r"^\[(\d{1,3}):(\d{2})(?::(\d{2}))?\]\s*([^:\[\]]+?)\s*:\s*(.*)$")
UNTIMED = re.compile(r"^([^\s:\[\]][^:\[\]]{0,60}?)\s*:\s+(.+)$")
HEADER = re.compile(r"^(call with|participants|appel avec|participants)\b", re.I)


def key(name):
    return unicodedata.normalize("NFC", name).strip().casefold()


def parse(text):
    """Renvoie (répliques, avec_heures). Une réplique = (t, secondes, nom, texte)."""
    timed, untimed = [], []
    for raw in text.splitlines():
        line = unicodedata.normalize("NFC", raw).strip()
        m = TIMED.match(line)
        if m:
            a, b, c, who, body = m.groups()
            secs = int(a) * 60 + int(b) if c is None else int(a) * 3600 + int(b) * 60 + int(c)
            t = f"{a}:{b}" if c is None else f"{a}:{b}:{c}"
            timed.append((t, secs, who.strip(), body.strip()))
            continue
        m = UNTIMED.match(line)
        if m and not HEADER.match(line):
            untimed.append((None, None, m.group(1).strip(), m.group(2).strip()))
    if timed:
        return timed, True
    return untimed, False


def main(path, aliases):
    with open(path, encoding="utf-8-sig", errors="replace") as f:
        lines, with_times = parse(f.read())
    if not lines:
        print("Aucune réplique trouvée (formats attendus : « [mm:ss] Nom: texte » ou « Nom : texte »).")
        return
    users = {key(a) for a in aliases.split(",") if a.strip()}
    speakers = []
    for _, _, who, _ in lines:
        if who not in speakers:
            speakers.append(who)
    if not any(key(s) in users for s in speakers):
        print("Aucun interlocuteur ne correspond au commercial (" + aliases + ").")
        print("Interlocuteurs trouvés : " + ", ".join(speakers))
        print("Relance le script avec le bon nom.")
        return

    def is_user(who):
        return key(who) in users

    if not with_times:
        print("Transcription sans minutes : pas de durée de monologue ni de minute pour les coupures.")

    words = {}
    for _, _, who, body in lines:
        words[who] = words.get(who, 0) + len(body.split())
    total = sum(words.values()) or 1
    print("Temps de parole (en mots) :")
    for who, n in sorted(words.items(), key=lambda x: -x[1]):
        tag = " (commercial)" if is_user(who) else ""
        print(f"  {who}{tag} : {round(100 * n / total)} % ({n} mots)")

    best = (0, None, None)
    run, start, start_s = 0, None, None
    for i, (t, s, who, body) in enumerate(lines):
        if is_user(who):
            if run == 0:
                start, start_s = t, s
            run += len(body.split())
            if run > best[0]:
                dur = None
                if with_times:
                    nxt = next((l[1] for l in lines[i + 1:] if not is_user(l[2])), None)
                    dur = round((nxt - start_s) / 60, 1) if nxt is not None else None
                best = (run, start, dur)
        else:
            run = 0
    where = f", à partir de [{best[1]}]" if best[1] else ""
    dur = f", environ {best[2]} min" if best[2] is not None else ""
    print(f"Plus long monologue du commercial : {best[0]} mots{where}{dur}")

    q = sum(body.count("?") for _, _, who, body in lines if is_user(who))
    print(f"« ? » dans les répliques du commercial : {q}")

    print("Coupures probables, à vérifier (réplique du prospect qui finit par « … », puis le commercial enchaîne) :")
    found = False
    for prev, cur in zip(lines, lines[1:]):
        if not is_user(prev[2]) and is_user(cur[2]):
            end = prev[3].rstrip()
            if end.endswith("…") or end.endswith("..."):
                found = True
                p = f"[{prev[0]}] " if prev[0] else ""
                c = f"[{cur[0]}] " if cur[0] else ""
                print(f"  {p}« {end[-80:]} » → {c}« {cur[3][:80]} »")
    if not found:
        print("  aucune")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
