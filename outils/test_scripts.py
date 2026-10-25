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


# ---- Relecture finale ----
T_LONG = "[01:05:30] Marc: on signe la semaine prochaine\n[01:05:40] You: parfait\n[00:09] Marc: bonjour tout le monde\n"


def test_citation_minutes_equivalentes_hms_et_mmss():
    for t in ("[01:05:30]", "[65:30]", "[1:05:30]"):
        n, manquantes = vc.check(T_LONG, f"{t} « on signe la semaine prochaine »")
        assert (n, manquantes) == (1, []), t


def test_citation_minute_sans_zero_initial():
    n, manquantes = vc.check("[0:09] Marc: bonjour tout le monde\n", "[00:09] « bonjour tout le monde »")
    assert (n, manquantes) == (1, [])


def test_citation_guillemets_droits_verifiee():
    n, manquantes = vc.check(T_MIN, '[00:05] "c\'est trop cher pour nous"')
    assert (n, manquantes) == (1, [])


def test_citation_mal_formatee_signalee_et_non_ignoree():
    n, manquantes = vc.check(T_MIN, "[tout à l'heure] « c'est trop cher pour nous »")
    assert n == 0 and len(manquantes) == 1


def test_tiret_court_traite_comme_sans_minute():
    n, manquantes = vc.check(T_SANS, "[–] « c'est trop cher pour nous »")
    assert (n, manquantes) == (1, [])


def test_cli_messages_ok_et_echec(tmp_path):
    import subprocess
    t = tmp_path / "t.txt"
    t.write_text(T_MIN, encoding="utf-8")
    bon = tmp_path / "bon.md"
    bon.write_text("[00:05] « c'est trop cher pour nous »", encoding="utf-8")
    mauvais = tmp_path / "mauvais.md"
    mauvais.write_text("[00:05] « on signe demain »", encoding="utf-8")
    r = subprocess.run([sys.executable, str(SCRIPTS / "verifier_citations.py"), str(t), str(bon)], capture_output=True, text=True)
    assert r.returncode == 0 and r.stdout.startswith("OK : 1 citations vérifiées, 0 introuvable")
    r = subprocess.run([sys.executable, str(SCRIPTS / "verifier_citations.py"), str(t), str(mauvais)], capture_output=True, text=True)
    assert r.returncode == 1 and r.stdout.startswith("ÉCHEC") and "introuvable" in r.stdout


def test_replique_sur_plusieurs_lignes_est_lue_en_entier():
    t = "[00:05] Marc: je pense que\nle vrai problème c'est le prix\n[00:20] You: d'accord\n"
    import transcript
    lines = transcript.parse(t)
    assert "le vrai problème c'est le prix" in lines[0].text
    n, manquantes = vc.check(t, "[00:05] « le vrai problème c'est le prix »")
    assert (n, manquantes) == (1, [])


def test_format_heure_sans_crochets():
    import transcript
    lines = transcript.parse("00:03 Marc: bonjour\n00:09 You: salut\n")
    assert [(l.t, l.speaker) for l in lines] == [("00:03", "Marc"), ("00:09", "You")]


def test_temps_de_parole_replique_sur_plusieurs_lignes(tmp_path, capsys):
    f = tmp_path / "t.txt"
    f.write_text("[00:05] Marc: un deux trois\nquatre cinq six\n[00:20] You: sept\n", encoding="utf-8")
    tdp.main(str(f), "You")
    out = capsys.readouterr().out
    assert "Marc : 86 % (6 mots)" in out


def test_temps_de_parole_sans_minutes_les_en_tetes_ne_sont_pas_des_interlocuteurs(tmp_path, capsys):
    f = tmp_path / "t.txt"
    f.write_text("Titre : Démo Nova\nDate : 2026-10-19\nDurée : 05:12\nParticipants: You, Marc (Nova)\n\nYou : bonjour tout le monde\n\nMarc : bonjour à toi\nEt aussi : le support\n", encoding="utf-8")
    tdp.main(str(f), "You")
    out = capsys.readouterr().out
    assert "Titre" not in out and "Date" not in out and "Durée" not in out
    assert "Marc : " in out and "(8 mots)" in out
