"""Vérifie que chaque citation d'une sortie existe dans la transcription.

Usage : python3 verifier_citations.py <transcription.txt> <sortie.md>

Une citation s'écrit « [mm:ss] « phrase exacte » », ou « [—] « phrase exacte » » quand la
transcription n'a pas de minutes. Les phrases entre « » sans crochet devant (les « dis plutôt »)
ne sont pas des citations et ne sont pas vérifiées. Les « … » dans une citation coupent la phrase.
Code de sortie : 0 si tout est trouvé, 1 sinon.
"""
import re
import sys
import unicodedata

from transcript import parse

CIT = re.compile(r"\[(\d{1,3}:\d{2}(?::\d{2})?|—)\]\s*«\s*(.+?)\s*»", re.S)


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s).lower().replace("’", "'")
    return re.sub(r"[^\w']+", " ", s).strip()


def check(transcript_text: str, output_text: str) -> tuple[int, list[str]]:
    lines = parse(transcript_text)
    whole = norm(transcript_text)
    ok, missing = 0, []
    for t, quote in CIT.findall(output_text):
        parts = [norm(p) for p in re.split(r"…|\.\.\.", quote) if norm(p)]
        if t == "—":
            good = bool(parts) and all(p in whole for p in parts)
        else:
            idx = [i for i, l in enumerate(lines) if l.t == t]
            window = " ".join(norm(l.text) for i in idx[:1] for l in lines[i:i + 3])
            good = bool(idx and parts and all(p in window for p in parts))
        if good:
            ok += 1
        else:
            missing.append(f"[{t}] « {quote} »")
    return ok, missing


if __name__ == "__main__":
    n, miss = check(open(sys.argv[1], encoding="utf-8-sig").read(), open(sys.argv[2], encoding="utf-8").read())
    print(f"OK: {n} citations vérifiées, {len(miss)} introuvable" + ("" if len(miss) < 2 else "s"))
    for m in miss:
        print("  introuvable :", m)
    sys.exit(1 if miss else 0)
