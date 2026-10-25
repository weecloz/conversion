import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import verifier_conversion as v  # noqa: E402


def _faux_skill(tmp_path, skill_md=None, extra=None):
    d = tmp_path / "conversion"
    (d / "scripts").mkdir(parents=True)
    for nom in v.REQUIS:
        (d / nom).parent.mkdir(parents=True, exist_ok=True)
        (d / nom).write_text("# x\n", encoding="utf-8")
    (d / "SKILL.md").write_text(skill_md or "---\nname: conversion\ndescription: Un skill.\n---\n# c\n", encoding="utf-8")
    for nom, txt in (extra or {}).items():
        (d / nom).write_text(txt, encoding="utf-8")
    return d


def test_un_skill_correct_passe(tmp_path):
    assert v.check(_faux_skill(tmp_path)) == []


def test_fichier_requis_manquant(tmp_path):
    d = _faux_skill(tmp_path)
    (d / "formats.md").unlink()
    assert any("formats.md" in e for e in v.check(d))


def test_frontmatter_nom_incorrect(tmp_path):
    d = _faux_skill(tmp_path, "---\nname: autre\ndescription: x\n---\n")
    assert any("name" in e for e in v.check(d))


def test_description_trop_longue(tmp_path):
    d = _faux_skill(tmp_path, "---\nname: conversion\ndescription: " + "a" * 1025 + "\n---\n")
    assert any("1024" in e for e in v.check(d))


def test_yaml_invalide(tmp_path):
    d = _faux_skill(tmp_path, "---\nname: conversion\ndescription: un : deux : trois\n---\n")
    assert any("frontmatter" in e for e in v.check(d))


def test_lien_mort_detecte_mais_pas_les_fichiers_de_l_utilisateur(tmp_path):
    d = _faux_skill(tmp_path, extra={"apres-un-call.md": "Lis `inexistant.md` puis écris `pipeline.md` et `ma-vente.md`.\n"})
    erreurs = v.check(d)
    assert any("inexistant.md" in e for e in erreurs)
    assert not any("pipeline.md" in e or "ma-vente.md" in e for e in erreurs)


def test_script_avec_dependance_externe_refuse(tmp_path):
    d = _faux_skill(tmp_path, extra={"scripts/pipeline.py": "import requests\n"})
    assert any("requests" in e for e in v.check(d))


def test_chaine_privee_refusee(tmp_path):
    d = _faux_skill(tmp_path, extra={"formats.md": "écris à accounts@exemple.fr\n"})
    assert any("accounts@" in e for e in v.check(d))


def test_le_vrai_skill_est_conforme():
    assert v.check(RACINE / "conversion") == []
