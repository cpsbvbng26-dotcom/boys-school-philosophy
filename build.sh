#!/bin/sh
# Builds paper/boys-school-philosophy.pdf from the LaTeX source, reproducibly.
# The dates in the PDF are fixed to the date of the paper, 2026-11-23 00:00 UTC (SOURCE_DATE_EPOCH), the optional
# PDF info is suppressed and the trailer ID is fixed in the source, and the paper is typeset three times so that
# references settle. JA_FONT names the font of the Japanese title and abstract (the system package fonts-ipafont-gothic).
# The same TeX Live and fonts give the same bytes; the README records the versions used.
set -eu
cd "$(dirname "$0")/paper"
SOURCE_DATE_EPOCH=1795392000
FORCE_SOURCE_DATE=1
JA_FONT=IPAGothic
export SOURCE_DATE_EPOCH FORCE_SOURCE_DATE JA_FONT
for i in 1 2 3; do
  lualatex -interaction=nonstopmode -halt-on-error boys-school-philosophy.tex > /dev/null
done
rm -f boys-school-philosophy.aux boys-school-philosophy.log boys-school-philosophy.out
sha256sum boys-school-philosophy.pdf
