import sys
import unicodedata
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "conversion" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import temps_de_parole as tdp  # noqa: E402
import verifier_citations as vc  # noqa: E402

T_MIN = "[00:01] You: Bonjour, ça va ?\n[00:05] Marc Lefort: Oui très bien merci, c'est trop cher pour nous.\n[00:09] You: Parfait, on commence.\n"
T_SANS = "Call with Marc\n\nYou : Bonjour, ça va ?\n\nMarc Lefort : Oui très bien merci, c'est trop cher pour nous.\n"


def test_temps_de_parole_alias_insensible_a_la_casse(tmp_path, capsys):
    f = tmp_path / "t.txt"
    f.write_text(T_MIN, encoding="utf-8")
    tdp.main(str(f), "you")
    assert "You (commercial)" in capsys.readouterr().out


def test_temps_de_parole_sans_minutes(tmp_path, capsys):
    f = tmp_path / "t.txt"
    f.write_text(T_SANS, encoding="utf-8")
    tdp.main(str(f), "You")
    out = capsys.readouterr().out
    assert "You (commercial)" in out and "sans minutes" in out


def test_temps_de_parole_nom_inconnu_liste_les_interlocuteurs(tmp_path, capsys):
    f = tmp_path / "t.txt"
    f.write_text(T_MIN, encoding="utf-8")
    tdp.main(str(f), "Inconnu")
    out = capsys.readouterr().out
    assert "Aucun interlocuteur" in out and "Marc Lefort" in out


def test_temps_de_parole_nom_unicode_decompose(tmp_path, capsys):
    nfd = unicodedata.normalize("NFD", "Zeïlani")
    f = tmp_path / "t.txt"
    f.write_text(T_MIN.replace("You", nfd), encoding="utf-8")
    tdp.main(str(f), "Zeïlani")
    assert "(commercial)" in capsys.readouterr().out


def test_citation_avec_minute_verifiee():
    n, manquantes = vc.check(T_MIN, "[00:05] « c'est trop cher pour nous »")
    assert (n, manquantes) == (1, [])


def test_citation_mauvaise_minute_refusee():
    n, manquantes = vc.check(T_MIN, "[00:09] « c'est trop cher pour nous »")
    assert n == 0 and len(manquantes) == 1


def test_citation_sans_minute_verifiee_sur_tout_le_texte():
    n, manquantes = vc.check(T_SANS, "[—] « c'est trop cher pour nous »")
    assert (n, manquantes) == (1, [])


def test_citation_sans_minute_inventee_refusee():
    n, manquantes = vc.check(T_SANS, "[—] « on signe demain »")
    assert n == 0 and manquantes == ["[—] « on signe demain »"]


def test_phrase_a_dire_sans_crochet_n_est_pas_verifiee():
    n, manquantes = vc.check(T_MIN, "Dis plutôt : « Qu'est-ce qui est trop cher ? »")
    assert (n, manquantes) == (0, [])


def test_citation_coupee_par_des_points_de_suspension():
    n, manquantes = vc.check(T_MIN, "[00:05] « Oui très bien… trop cher pour nous »")
    assert (n, manquantes) == (1, [])


def test_transcription_tres_longue_est_lue_en_entier():
    lignes = [f"[{i // 60:02d}:{i % 60:02d}] {'You' if i % 2 else 'Marc'}: ligne numéro {i} du call" for i in range(5400)]
    texte = "\n".join(lignes)
    n, manquantes = vc.check(texte, "[89:59] « ligne numéro 5399 du call »")
    assert (n, manquantes) == (1, [])
