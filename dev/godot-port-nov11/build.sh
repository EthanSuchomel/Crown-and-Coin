#!/bin/bash
# rebuilds work/ from base/ with every port step
set -e
cd "$(dirname "$0")"
rm -rf work && cp -r base work
for p in p1_data.py p2_rules.py p3_battle.py p4_ai.py p5_test.py p6_board.py p7_ui.py; do python3 $p work; done
mkdir -p work/art/cards && cp -r newart/art/* work/art/
python3 p8_mage.py work
python3 p9_mage_req.py work
python3 p10_three.py work
python3 p11_ai3.py work
python3 p12_view3.py work
python3 p13_ui3.py work
python3 p14_test3.py work
python3 p15_plant_ui.py work
python3 p16_unit_icons.py work
