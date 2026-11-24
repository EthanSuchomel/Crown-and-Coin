// Not shipped: the new walls round castles, and which map a castle battle is fought on. node shot.js index.html OUT/
const { chromium } = require('playwright'); const path = require('path');
const [, , FILE, OUT] = process.argv;
(async () => {
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1280, height: 800 }, deviceScaleFactor: 2 });
  const errs = []; pg.on('pageerror', e => errs.push(e.message));
  await pg.goto('file://' + path.resolve(FILE)); await pg.waitForTimeout(1000);
  const r = await pg.evaluate(() => { showScreen(null); newGame('mammals', {}); S.players[0].briefed = true; startTurn(); closeModal();
    const cs = S.tiles.filter(t => t.castle && t.id !== S.homes[0] && t.id !== S.homes[1]);
    cs[0].walls = [3, 3, 3, 3, 3, 3]; cs[1].walls = [3, 2, 1, 0, 3, 3]; cs[2].walls = [0, 0, 3, 3, 0, 0];
    cs[2].owner = 0; cs[2].troops = 1; cs[2].army = { ape: 1 }; cs[2].walls = [3, 3, 0, 3, 3, 3];
    const h = S.tiles[S.homes[0]]; h.walls = [3, 3, 3, 3, 3, 3];
    render();
    const t = cs[0], j = nbrs(t.id)[0], k = nbrs(cs[2].id);
    return { walled: arenaMap(t, wallOn(t.id, j)), open: arenaMap(cs[1], 0), ids: cs.map(c => c.id) }; });
  console.log(JSON.stringify(r));
  await pg.waitForTimeout(500); await pg.evaluate(() => closeModal()); await pg.waitForTimeout(300); await pg.screenshot({ path: OUT + 'walls.png' });
  for (const [k, id] of r.ids.entries()) { const el = await pg.$(`#map [data-i="${id}"]`); }
  console.log(errs.length ? errs.join('\n') : 'no page errors'); await b.close();
})();
