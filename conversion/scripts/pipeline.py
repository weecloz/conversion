"""Lit pipeline.md (un tableau Markdown) et répond aux questions de dates.

Usage : python3 pipeline.py <pipeline.md> [--today aaaa-mm-jj] [--days 7] [--mois aaaa-mm]

Colonnes reconnues (dans n'importe quel ordre, accents et majuscules ignorés) :
Prospect, Entreprise, Étape, Montant, Prochaine action, Pour le, Dernier contact, Risque, Statut.
Dates : aaaa-mm-jj ou jj/mm/aaaa. Statut : ouvert, gagné ou perdu.
Une date illisible ou une ligne sans prospect est signalée dans « À corriger », jamais une erreur.
"""
import argparse
import re
import sys
import unicodedata
from dataclasses import dataclass
from datetime import date, datetime

COLS = {
    "prospect": "prospect", "entreprise": "entreprise", "etape": "etape", "montant": "montant",
    "prochaine action": "action", "pour le": "pour_le", "dernier contact": "dernier_contact",
    "risque": "risque", "statut": "statut",
}
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
    return [c.strip() for c in line.strip().strip("|").split("|")]


def parse(text: str) -> tuple[list[Deal], list[str]]:
    deals, problems, header = [], [], None
    for n, raw in enumerate(text.splitlines(), 1):
        if not raw.strip().startswith("|"):
            continue
        cells = _cells(raw)
        if all(re.fullmatch(r":?-{2,}:?", c) or c == "" for c in cells):
            continue
        if header is None:
            keys = [_key(c) for c in cells]
            if "prospect" in keys:
                header = [COLS.get(k) for k in keys]
            continue
        d = Deal(ligne=n)
        for col, val in zip(header, cells):
            if col is None or not val:
                continue
            if col in ("pour_le", "dernier_contact"):
                dt = parse_date(val)
                if dt is None:
                    problems.append(f"ligne {n} : date « {val} » illisible (écris-la aaaa-mm-jj)")
                setattr(d, col, dt)
            elif col == "statut":
                d.statut = _key(val) or "ouvert"
            else:
                setattr(d, col, val)
        if not d.prospect:
            problems.append(f"ligne {n} : pas de prospect, ligne ignorée")
            continue
        deals.append(d)
    if header is None and text.strip():
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
    with open(a.fichier, encoding="utf-8-sig") as f:
        deals, problems = parse(f.read())
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
