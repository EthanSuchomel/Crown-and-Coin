#!/bin/bash
# Rebuilds work/ from base/ (a copy of Ethan's CrownAndCoin-Godot) with every Robot-port step, then copies the new pictures.
set -e
W=${1:?work dir}
D="$(cd "$(dirname "$0")" && pwd)"
for p in p1_data.py p2_rules.py p3_ai.py p4_ui.py p5_board.py p6_test.py; do python3 "$D/$p" "$W"; done
for f in "$D"/art/*.png; do b=$(basename "$f"); dir=${b%%_*}; name=${b#*_}; mkdir -p "$W/art/$dir"; cp "$f" "$W/art/$dir/$name"; done
echo "built $W"
