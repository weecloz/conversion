import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "conversion" / "scripts"))
import pipeline as p  # noqa: E402

TABLE = """# Pipeline

| Prospect | Entreprise | Étape | Montant | Prochaine action | Pour le | Dernier contact | Risque | Statut |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Marc Lefort | Nova | Démo | 4200 € | Envoyer la proposition | 2026-10-28 | 2026-10-22 | budget flou | ouvert |
| Claire Morel | Cabinet Morel | Proposition | 9000 € | Relancer | 2026-10-20 | 2026-10-12 | | ouvert |
| Paul Weber | Weber SAS | Découverte | 3000 € | | | 2026-10-24 | | ouvert |
| Sonia Diallo | Diallo & Fils | Négo | 12000 € | Appel final | 2026-10-30 | 2026-10-23 | | gagné |
| Hugo Bernard | Bernard Frères | Démo | 6000 € | | | 2026-10-05 | prix | perdu |
"""
AUJOURDHUI = date(2026, 10, 26)


def test_parse_lit_toutes_les_lignes_sans_probleme():
    deals, problemes = p.parse(TABLE)
    assert [d.prospect for d in deals] == ["Marc Lefort", "Claire Morel", "Paul Weber", "Sonia Diallo", "Hugo Bernard"]
    assert problemes == []
    assert deals[0].pour_le == date(2026, 10, 28)
    assert deals[3].statut == "gagne"


def test_dormants_sept_jours_ou_plus_trie_du_plus_ancien():
    deals, _ = p.parse(TABLE)
    out = p.dormants(deals, AUJOURDHUI)
    assert [(d.prospect, age) for d, age in out] == [("Claire Morel", 14)]


def test_dormants_exclut_les_deals_gagnes_et_perdus():
    deals, _ = p.parse(TABLE)
    assert "Hugo Bernard" not in [d.prospect for d, _ in p.dormants(deals, AUJOURDHUI)]


def test_dormants_seuil_configurable():
    deals, _ = p.parse(TABLE)
    assert [d.prospect for d, _ in p.dormants(deals, AUJOURDHUI, days=3)] == ["Claire Morel", "Marc Lefort"]


def test_sans_prochaine_etape_datee():
    deals, _ = p.parse(TABLE)
    assert [d.prospect for d in p.sans_prochaine_etape(deals)] == ["Paul Weber"]


def test_en_retard():
    deals, _ = p.parse(TABLE)
    assert [d.prospect for d in p.en_retard(deals, AUJOURDHUI)] == ["Claire Morel"]


def test_perdus_du_mois_et_perdus_sans_date():
    t = TABLE + "| Ines Roy | Roy SA | Démo | | | | | | perdu |\n"
    deals, _ = p.parse(t)
    dans, sans = p.perdus_du_mois(deals, "2026-10")
    assert [d.prospect for d in dans] == ["Hugo Bernard"]
    assert [d.prospect for d in sans] == ["Ines Roy"]


def test_date_mal_ecrite_est_signalee_sans_planter():
    t = TABLE.replace("2026-10-22", "bientôt")
    deals, problemes = p.parse(t)
    assert deals[0].dernier_contact is None
    assert any("ligne 5" in x and "bientôt" in x for x in problemes)
    assert ("Marc Lefort", None) in [(d.prospect, a) for d, a in p.dormants(deals, AUJOURDHUI)]


def test_date_au_format_francais_acceptee():
    t = TABLE.replace("2026-10-12", "12/10/2026")
    deals, problemes = p.parse(t)
    assert problemes == [] and deals[1].dernier_contact == date(2026, 10, 12)


def test_colonnes_deplacees_et_accents_ignores():
    t = "| statut | PROSPECT | Etape | Dernier contact |\n|---|---|---|---|\n| ouvert | Zoé | Démo | 2026-10-01 |\n"
    deals, problemes = p.parse(t)
    assert problemes == [] and deals[0].prospect == "Zoé" and deals[0].etape == "Démo"


def test_ligne_sans_prospect_signalee_et_ignoree():
    t = TABLE + "| | Orpheline | Démo | | | | 2026-10-01 | | ouvert |\n"
    deals, problemes = p.parse(t)
    assert len(deals) == 5 and any("pas de prospect" in x for x in problemes)


def test_pas_de_tableau_message_clair():
    deals, problemes = p.parse("n'importe quoi\n")
    assert deals == [] and any("tableau introuvable" in x for x in problemes)


def test_fichier_vide_ne_plante_pas():
    assert p.parse("") == ([], [])


def test_cli_affiche_les_trois_sections(tmp_path, capsys):
    f = tmp_path / "pipeline.md"
    f.write_text(TABLE, encoding="utf-8")
    assert p.main([str(f), "--today", "2026-10-26"]) == 0
    out = capsys.readouterr().out
    assert "Claire Morel" in out and "14 jours sans nouvelle" in out
    assert "Sans prochaine étape datée" in out and "Paul Weber" in out
    assert "En retard" in out


def test_cli_date_du_jour_illisible(tmp_path, capsys):
    f = tmp_path / "pipeline.md"
    f.write_text(TABLE, encoding="utf-8")
    assert p.main([str(f), "--today", "demain"]) == 2
    assert "illisible" in capsys.readouterr().out
