#!/bin/bash
# rebuilds work/ from base/ with every port step
set -e
cd "$(dirname "$0")"
rm -rf work && cp -r base work
for p in p1_data.py p2_rules.py p3_battle.py p4_ai.py p5_test.py p6_board.py p7_ui.py; do python3 $p work; done
mkdir -p work/art/cards && cp -r newart/art/* work/art/
