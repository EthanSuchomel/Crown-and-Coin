New Mammal home castle and the board's Mammal numbers (2026-11-12)

The castle: Ethan's pick from three OpenArt "out of the box" designs (savanna rock with a ledge, mammoth skeleton hall,
waterfall mesa). He chose the waterfall mesa and asked for it "more defensive and heavy duty"; of three tougher versions
(stone walls, carved and moated, siege-ready) he took the siege-ready one: a boulder-and-iron wall, an iron-plated gate
framed by iron-capped tusks, ballista platforms on the ledges, an armored watchtower on top, the waterfall and pool kept.

  castle_cut.py      cuts it out of the magenta background (also clears the magenta seen through the scaffolding and
                     browns the purple cast in its shadows)
  castle_mammals.png the 256-px game picture (ratio 0.8516), used for castle_mammals: board, title and faction screens
  patch_castle.py    applies it to index.html, and also:
  - Rhino damage 12 on the board, as in the arena (Ethan, 2026-11-08)
  - Porcupine 8 health, and its quills prick back: each melee hit that lands on a Porcupine costs the attacker 1
    (a charging Rhino too; shots, lasers, rockets and magic don't count)
  - no Procoptodon in the Mammal barracks (level 2 unlocks no new unit); its numbers stay for old saved games
  These three were made on the claude.ai link on Nov 7 but lost when the link was replaced by the repo version on
  Nov 9; the arena already had them (commit 540d986), only the board's numbers were behind. Without this, a Mammal
  player could still recruit Procoptodons, which then vanished in arena battles.
  test.js            title, faction and board screenshots, quill checks (10 Gorillas attacking 10 Porcupines lose
                     about 7 instead of about 5; shooters lose the same), and computer games with the Mammals
