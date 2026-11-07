Text edits that add the Mythical units to the arena (made 2026-11-06).
edits-index.html.json: for index.html (the built-in arena string, JSON-escaped).
edits-arena.html.json: for a plain arena.html.
The pictures they point at are in ../../myth/.
edits-fly-*.json: the Griffin and Dragon wing-beat animations, applied after the first edits.
edits-fly2-*.json: Griffin wing joint lowered; Dragon back to its still picture. Apply after edits-fly.
edits-fly3-*.json: Dragon hover wing beats and soaring glide (Ethan's two poses). Apply after edits-fly2.
edits-fly4-*.json: Griffin hover wing beats and soaring glide (Ethan's two poses). Apply after edits-fly3.
edits-fight-*.json: Dragon fire run, Griffin landing + screech, Mage turning Minions into Minotaurs, Minotaur charge + hammer swing. Apply after edits-fly4.
edits-swoop2-*.json: Dragon fire run 3x faster, from its own side across to the enemy edge, then back on from its own edge to land. Apply after edits-fight.
edits-land-*.json: Dragon and Griffin land and stay on the ground with their standing pictures (also removes a stale Dragon style). Apply after edits-swoop2.
edits-mage-*.json: Mage reaches the whole field, lightning every 3s. Apply after edits-land.
edits-walk-*.json: landed Dragon and Griffin use Ethan's folded-wing pictures with walk cycles (replaces the standing pictures). Apply after edits-mage.
edits-front-*.json: Dragon lands at the front line after its fire run; 24-frame wing beats at a steady pace. edits-soar-*.json: no projectile can hit the Dragon while it soars over. Apply after edits-walk, front then soar.
edits-flames-*.json: Dragon fire uses Ethan's flame pictures (flicker drawn by Claude). Apply after edits-soar.
edits-blow-*.json: the soaring flame blows forward; fire lands 14 ahead. edits-dsize-*.json: all Dragon poses the same size (560x480 frames, w 21.35). Apply after edits-flames, blow then dsize.
