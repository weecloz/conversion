#!/bin/zsh
# usage: ./outils/emballer.sh  ->  skills/conversion/ (copie pour le plugin, jamais éditée à la main)
#                                  ../livrable/conversion.zip (racine du zip : conversion/ et modeles/)
set -e
cd "${0:A:h}/.."
PY=/opt/anaconda3/bin/python3
$PY outils/verifier_conversion.py conversion
$PY -m pytest outils -q
rm -rf skills ../livrable/build ../livrable/conversion.zip
mkdir -p skills ../livrable/build
rsync -a --exclude '__pycache__' --exclude '.DS_Store' conversion/ skills/conversion/
rsync -a --exclude '__pycache__' --exclude '.DS_Store' conversion ../livrable/build/
rsync -a --exclude '.DS_Store' modeles ../livrable/build/
cp ../livrable/LISEZMOI.md ../livrable/build/
(cd ../livrable/build && zip -qrX ../conversion.zip conversion modeles LISEZMOI.md)
rm -rf ../livrable/build
unzip -l ../livrable/conversion.zip | tail -1
