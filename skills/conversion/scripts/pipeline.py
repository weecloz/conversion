"""Lit pipeline.md (un tableau Markdown) et répond aux questions de dates.

Usage : python3 pipeline.py <pipeline.md> [--today aaaa-mm-jj] [--days 7] [--mois aaaa-mm]

Colonnes reconnues (dans n'importe quel ordre, accents et majuscules ignorés) :
Prospect, Entreprise, Étape, Montant, Prochaine action, Pour le, Dernier contact, Risque, Statut.
Dates : aaaa-mm-jj ou jj/mm/aaaa. Statut : ouvert, gagné ou perdu.
Une date illisible ou une ligne sans prospect est signalée dans « À corriger », jamais une erreur.
"""
from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from dataclasses import dataclass
from datetime import date, datetime

COLS = {
    "prospect": "prospect", "entreprise": "entreprise", "etape": "etape", "montant": "montant",
    "prochaine action": "action", "prochaine etape": "action", "action": "action",
    "pour le": "pour_le", "date prochaine action": "pour_le", "echeance": "pour_le",
    "dernier contact": "dernier_contact", "dernier echange": "dernier_contact",
    "risque": "risque", "statut": "statut",
}
OUVERTS_CONNUS = ("ouvert", "en cours")
FERMES = ("gagne", "perdu")


@dataclass
class Deal:
    ligne: int
    prospect: str = ""
    entreprise: str = ""
    etape: str = ""
    montant: str = ""
    action: str = ""
    pour_le: date | None = None
    dernier_contact: date | None = None
    risque: str = ""
    statut: str = "ouvert"


def _key(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z]+", " ", s).strip()


def parse_date(s: str) -> date | None:
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d/%m/%y"):
        try:
            return datetime.strptime(s.strip(), fmt).date()
        except ValueError:
            pass
    return None


def _cells(line: str) -> list[str]:
    """Cellules d'une ligne de tableau ; un « \\| » est une barre verticale dans le texte d'une cellule."""
    return [c.replace("\\|", "|").strip() for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]


def _statut(val: str) -> tuple[str, bool]:
    """(statut normalisé, reconnu ?) : « Perdue », « perdu (prix) » → perdu ; « signé », « gagnée » → gagne."""
    k = _key(val)
    if not k:
        return "ouvert", True
    mots = k.split()
    if any(m.startswith("perdu") for m in mots):
        return "perdu", True
    if any(m.startswith("gagn") or m.startswith("sign") for m in mots):
        return "gagne", True
    return "ouvert", k in OUVERTS_CONNUS


def parse(text: str) -> tuple[list[Deal], list[str]]:
    deals, problems, header, vu_tableau = [], [], None, False
    for n, raw in enumerate(text.splitlines(), 1):
        if not raw.strip().startswith("|"):
            header = None  # un nouveau tableau doit avoir sa propre ligne d'en-tête
            continue
        cells = _cells(raw)
        if all(re.fullmatch(r":?-{2,}:?", c) or c == "" for c in cells):
            continue
        if header is None:
            keys = [_key(c) for c in cells]
            if "prospect" in keys:
                header = [COLS.get(k) for k in keys]
                vu_tableau = True
                for c, col in zip(cells, header):
                    if col is None and c:
                        problems.append(f"ligne {n} : colonne « {c} » non reconnue, ignorée")
            continue
        d = Deal(ligne=n)
        if len(cells) > len(header):
            problems.append(f"ligne {n} : plus de cellules que de colonnes (une barre | dans une cellule ? écris \\|)")
        for col, val in zip(header, cells):
            if col is None or not val:
                continue
            if col in ("pour_le", "dernier_contact"):
                dt = parse_date(val)
                if dt is None:
                    problems.append(f"ligne {n} : date « {val} » illisible (écris-la aaaa-mm-jj)")
                setattr(d, col, dt)
            elif col == "statut":
                d.statut, reconnu = _statut(val)
                if not reconnu:
                    problems.append(f"ligne {n} : statut « {val} » non reconnu, lu comme ouvert (écris ouvert, gagné ou perdu)")
            else:
                setattr(d, col, val)
        if not d.prospect:
            problems.append(f"ligne {n} : pas de prospect, ligne ignorée")
            continue
        deals.append(d)
    if not vu_tableau and text.strip():
        problems.append("tableau introuvable : la ligne d'en-tête doit contenir « Prospect »")
    return deals, problems


def ouverts(deals):
    return [d for d in deals if d.statut not in FERMES]


def dormants(deals, today: date, days: int = 7):
    out = []
    for d in ouverts(deals):
        if d.dernier_contact is None:
            out.append((d, None))
        else:
            age = (today - d.dernier_contact).days
            if age >= days:
                out.append((d, age))
    out.sort(key=lambda x: (x[1] is not None, -(x[1] or 0)))
    return out


def sans_prochaine_etape(deals):
    return [d for d in ouverts(deals) if d.pour_le is None]


def en_retard(deals, today: date):
    return [d for d in ouverts(deals) if d.pour_le is not None and d.pour_le < today]


def perdus_du_mois(deals, mois: str):
    perdus = [d for d in deals if d.statut == "perdu"]
    dans = [d for d in perdus if d.dernier_contact and d.dernier_contact.strftime("%Y-%m") == mois]
    sans = [d for d in perdus if d.dernier_contact is None]
    return dans, sans


def doublons(deals):
    """Entreprises qui ont plusieurs lignes ouvertes (une ligne par entreprise : probablement un doublon)."""
    par = {}
    for d in ouverts(deals):
        if d.entreprise:
            par.setdefault(d.entreprise.strip().casefold(), []).append(d)
    return [v for v in par.values() if len(v) > 1]


def _nom(d: Deal) -> str:
    return f"{d.entreprise} ({d.prospect})" if d.entreprise else d.prospect


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("fichier")
    ap.add_argument("--today")
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--mois")
    a = ap.parse_args(argv)
    today = parse_date(a.today) if a.today else date.today()
    if today is None:
        print(f"--today : date « {a.today} » illisible (écris-la aaaa-mm-jj)")
        return 2
    try:
        brut = open(a.fichier, "rb").read()
    except OSError:
        print(f"Fichier introuvable : {a.fichier}")
        return 2
    try:
        texte = brut.decode("utf-8-sig")
    except UnicodeDecodeError:
        texte = brut.decode("cp1252", errors="replace")
    deals, problems = parse(texte)
    for d in deals:
        if d.dernier_contact and d.dernier_contact > today:
            problems.append(f"ligne {d.ligne} : dernier contact le {d.dernier_contact} est dans le futur")
    for groupe in doublons(deals):
        lignes = ", ".join(str(d.ligne) for d in groupe)
        problems.append(f"doublon possible : {groupe[0].entreprise} a {len(groupe)} lignes ouvertes (lignes {lignes}) : une seule ligne par entreprise")
    print(f"Deals qui dorment ({a.days} jours ou plus) : {len(dormants(deals, today, a.days))}")
    for d, age in dormants(deals, today, a.days):
        quand = f"{age} jours sans nouvelle" if age is not None else "date du dernier contact inconnue"
        print(f"- {_nom(d)}, étape {d.etape or '?'} : {quand}")
    sans = sans_prochaine_etape(deals)
    print(f"\nSans prochaine étape datée : {len(sans)}")
    for d in sans:
        print(f"- {_nom(d)}, étape {d.etape or '?'}")
    retard = en_retard(deals, today)
    print(f"\nEn retard sur la prochaine étape : {len(retard)}")
    for d in retard:
        print(f"- {_nom(d)} : « {d.action or 'action non écrite'} » prévue le {d.pour_le}")
    if a.mois:
        dans, sans_date = perdus_du_mois(deals, a.mois)
        print(f"\nPerdus en {a.mois} : {len(dans)}")
        for d in dans:
            print(f"- {_nom(d)}, étape {d.etape or '?'}, risque : {d.risque or '—'}")
        if sans_date:
            print("Perdus sans date (à dater) : " + ", ".join(_nom(d) for d in sans_date))
    if problems:
        print("\nÀ corriger dans pipeline.md :")
        for x in problems:
            print(f"- {x}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
