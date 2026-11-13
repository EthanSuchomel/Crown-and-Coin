The Robot rework (browser 2026-11-11/12: dev/robots/patch1_factory.py, patch2_resource.py, patch3_cards.py, patch4_cardart.py
and the card layout) ported to the Godot version (Ethan's CrownAndCoin-Godot, Godot 4.7.2), 2026-11-12.

What it brings over
- The war-factory home castle and the three factory pictures (market, market + barracks, full fortress), the five punch-card
  pictures (Mobilize 1001, Deploy 1101, Onslaught 1111, Construction 0011, Siege Protocol 0000), shown on the left of the card
  with no name, like the Dinosaur cards (their wider shape is kept).
- One Robot building per hex: a market that becomes a resource hex (up to 4 markets, Market 2..4 in Build) or a factory
  (Barracks, then Fortress, added in Advancements: tap the home castle, pick Barracks or Fortress, tap the ringed market).
  Captured buildings become one factory (or a resource hex if they were only markets).
- Every Robot card's own upgrades (data/upgrades.json robots_cards, read with dk like the Dinosaurs'): Home Grid, Recompile,
  Cheap Markets, Assembly Line, Rebuild, Refit, Extra Thread, Climb, Offline; Castle Tax/Tolls/Vaults, Drone Line/Air Wing/
  Sky Fleet, Air Lanes, Ridge Hop, Overflight; Full Yield, Market Hubs, Hub Stores, Muster (Archers, Elite), Fresh Units,
  Laser Strike, Double Strike; Scavenger, Brawler Dash, Fresh Ground, Fourth Free, Scrap, Quick Barracks, Quick Fortress,
  Overclock; Border Market, Free Market, Two Free Markets, Factory/Barracks/Fortress Run, Dual Core, Sortie, Home Link.
  Mobilize is Advancements -> Recruit -> Move; Construct is Construction. Update, Efficiency, the old Factory and
  Industrialization are gone.
- The computer: markets on an empty hex or the safest resource hex, factory upgrades in Advancements, Overclock, Laser Strike
  at the start of its Move, Sortie after its Fortify picks, Assembly Line. Like the browser's, it doesn't use the trades.

Apply to a copy of the project: ./build.sh PROJ (p1_data, p2_rules, p3_ai, p4_ui, p5_board, p6_test, then art/ ->
PROJ/art/<folder>/<name>, e.g. art/cards_mobil.png -> art/cards/mobil.png).
check/ (not shipped): ui_robo.gd drives the new screens (SHOTS=dir for screenshots, under xvfb-run with --rendering-driver
opengl3), board_robo.gd every building look and the Laser Strike dialog, soak_robo.gd the Robot computer against each
faction. Results: see godot-port-status.md in the project notes.
