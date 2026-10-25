"""Vérifie la structure du skill `conversion`. Usage : python3 verifier_conversion.py <dossier du skill>"""
import ast
import re
import sys
from pathlib import Path

import yaml

REQUIS = [
    "SKILL.md", "apres-un-call.md", "revue-du-lundi.md", "autopsie-du-mois.md",
    "grille-qualification.md", "objections-classiques.md", "formats.md",
    "scripts/transcript.py", "scripts/temps_de_parole.py", "scripts/verifier_citations.py", "scripts/pipeline.py",
]
FICHIERS_UTILISATEUR = {
    "ma-vente.md", "pipeline.md", "reponses-objections.md",  # la mémoire, dans le dossier de travail
    "resume.md", "qualification.md", "objections.md", "temps-de-parole.md", "signaux.md", "relance.md", "notes-crm.md",  # sorties de traitements/
}
PRIVE = ["la-singularite", "accounts@", "tests-prives"]
REF = re.compile(r"`((?:scripts/)?[A-Za-z0-9_-]+\.(?:md|py))`")
LOCAUX = {"transcript", "temps_de_parole", "verifier_citations", "pipeline"}


def check(skill_dir: Path) -> list[str]:
    skill_dir = Path(skill_dir)
    erreurs = [f"fichier requis manquant : {n}" for n in REQUIS if not (skill_dir / n).exists()]
    f = skill_dir / "SKILL.md"
    if f.exists():
        m = re.match(r"^---\n(.*?)\n---\n", f.read_text(encoding="utf-8"), re.S)
        try:
            fm = yaml.safe_load(m.group(1)) if m else None
        except yaml.YAMLError:
            fm = None
        if not isinstance(fm, dict):
            erreurs.append("SKILL.md : frontmatter manquant ou invalide")
        else:
            if fm.get("name") != "conversion":
                erreurs.append(f"SKILL.md : name doit être « conversion » (trouvé : {fm.get('name')!r})")
            desc = fm.get("description") or ""
            if not desc or len(desc) > 1024:
                erreurs.append(f"SKILL.md : description vide ou > 1024 caractères ({len(desc)})")
    for p in sorted(skill_dir.rglob("*")):
        if not p.is_file() or "__pycache__" in p.parts:
            continue
        rel = p.relative_to(skill_dir)
        txt = p.read_text(encoding="utf-8", errors="replace")
        for mot in PRIVE:
            if mot in txt:
                erreurs.append(f"{rel} : chaîne privée « {mot} »")
        if p.suffix == ".md":
            for ref in REF.findall(txt):
                if ref in FICHIERS_UTILISATEUR:
                    continue
                if not (skill_dir / ref).exists() and not (skill_dir / "scripts" / ref).exists():
                    erreurs.append(f"{rel} : fichier cité introuvable « {ref} »")
        if p.suffix == ".py":
            try:
                arbre = ast.parse(txt)
            except SyntaxError as e:
                erreurs.append(f"{rel} : erreur de syntaxe ({e.msg})")
                continue
            for n in ast.walk(arbre):
                if isinstance(n, ast.Import):
                    noms = [a.name.split(".")[0] for a in n.names]
                elif isinstance(n, ast.ImportFrom) and n.module and n.level == 0:
                    noms = [n.module.split(".")[0]]
                else:
                    noms = []
                for nom in noms:
                    if nom not in sys.stdlib_module_names and nom not in LOCAUX:
                        erreurs.append(f"{rel} : dépendance externe « {nom} »")
    return erreurs


if __name__ == "__main__":
    errs = check(Path(sys.argv[1]))
    print("OK" if not errs else "\n".join(errs))
    sys.exit(1 if errs else 0)
