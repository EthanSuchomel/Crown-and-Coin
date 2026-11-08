"""Fixes applied on top of the current arena.html (after patch_dino.py and the Mythical board patches).
2026-11-07: a Griffin or Dragon that has landed (after its swoop or fire run) counts as on the ground, so ground fighters
can attack it. Before, Rhinos facing only Griffins stood still after the screech: nothing they could hit."""
import sys
p=sys.argv[1]; s=open(p,encoding='utf-8').read()
def R(a,b):
    global s; assert s.count(a)==1,(s.count(a),a[:80]); s=s.replace(a,b)
R("const downed=o=>o.downT>clock;   // a flyer a Dilophosaurus has knocked down",
  "const downed=o=>o.downT>clock||!!o.grounded;   // a flyer on the ground: knocked down by a Dilophosaurus, or a Griffin or Dragon that has landed")
R("They still count as flyers for who can hit them.", "Once landed, ground fighters can attack them too.") if "They still count as flyers for who can hit them." in s else None
open(p,'w',encoding='utf-8').write(s); print('fixed')
# (merged 2026-11-07 from another session's edit on the test link: the Laser Tank's beam does hurt the Triceratops)
# 2026-11-07 (Ethan): Robot Knight 25 health (was 20); shield wall breaks after 50 melee damage (was 30). Edited in arena.html directly.
# 2026-11-08: Laser Tank beam lasts 2.5s (ticks 12) and follows the bunch it was fired at
#   (slides at up to 12 field units/s toward the middle of enemies within 1.5x radius of its spot; scorch mark moves with it)
# 2026-11-08: Robot Longbow no longer misses flyers (missAir 0.15 removed)
# 2026-11-08: merged the main arena link's changes (Procoptodon removed; Porcupine 8hp + quills; Rhino 10 dmg; Brawler 4hp; Archer 1s; Knight 12 dmg 1s bonus{bow:4}) with Knight 25hp
# 2026-11-08: Rhino damage back to 15
# 2026-11-08: Rhino damage 12
