import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "conversion" / "scripts"))
import pipeline as p  # noqa: E402
import verifier_citations as vc  # noqa: E402

EX = RACINE / "exemples"


def test_les_citations_des_sorties_d_exemple_sont_exactes():
    call = (EX / "call-nova-1.txt").read_text(encoding="utf-8")
    for f in sorted((EX / "sorties-call-nova-1").glob("*.md")):
        n, manquantes = vc.check(call, f.read_text(encoding="utf-8"))
        assert manquantes == [], f"{f.name} : {manquantes}"


def test_les_sorties_d_exemple_ont_au_moins_dix_citations():
    call = (EX / "call-nova-1.txt").read_text(encoding="utf-8")
    total = sum(vc.check(call, f.read_text(encoding="utf-8"))[0] for f in (EX / "sorties-call-nova-1").glob("*.md"))
    assert total >= 10


def test_les_sept_sorties_existent():
    noms = {f.name for f in (EX / "sorties-call-nova-1").glob("*.md")}
    assert noms == {"resume.md", "qualification.md", "objections.md", "temps-de-parole.md", "signaux.md", "relance.md", "notes-crm.md"}


def test_la_relance_d_exemple_fait_moins_de_150_mots_et_sans_formule_interdite():
    t = (EX / "sorties-call-nova-1" / "relance.md").read_text(encoding="utf-8")
    corps = t.split("```")[1]
    assert len(corps.split()) <= 150
    for interdit in ("je me permets", "n'hésite", "suite à notre échange", "comme convenu", "caler", "se cale", "—"):
        assert interdit not in corps.lower()


def test_pipeline_d_exemple_est_lisible_et_sans_probleme():
    deals, problemes = p.parse((EX / "pipeline.md").read_text(encoding="utf-8"))
    assert problemes == [] and len(deals) >= 6
    assert any(d.statut == "perdu" for d in deals)


def test_aucune_donnee_privee_dans_les_exemples_ni_les_modeles():
    for f in list(EX.rglob("*")) + list((RACINE / "modeles").rglob("*")):
        if f.is_file():
            t = f.read_text(encoding="utf-8")
            for mot in ("la-singularite", "accounts@", "Zeïlani"):
                assert mot not in t, f"{f}: {mot}"
