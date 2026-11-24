// Not shipped: no walls to build; the old castle tile; castle battles on the Castle map. node shot3.js index.html OUT/
const { chromium } = require('playwright'); const path = require('path');
const [, , FILE, OUT] = process.argv;
(async () => {
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1280, height: 800 } });
  const errs = []; pg.on('pageerror', e => errs.push(e.message));
  await pg.goto('file://' + path.resolve(FILE)); await pg.waitForTimeout(1000);
  const r = await pg.evaluate(() => { showScreen(null); newGame('mammals', {}); S.players[0].briefed = true; closeModal();
    const me = S.players[0]; me.mat = 30; const h = S.tiles[S.homes[0]];
    const cid = me.hand.find(c => cardOf(0, c).actions.includes('advance')); S.play = { card: cid, step: cardOf(0, cid).actions.indexOf('advance') };
    ui.sel = h.id; render();
    const c = S.tiles.find(t => t.castle && t.owner < 0);
    return { mapCastle: arenaMap(c, 0), canWall: doBuildWall(0, h.id, wallSides(h.id)[0], 0), walls: !!document.querySelector('[data-av="walls"]') }; });
  console.log(JSON.stringify(r));
  await pg.waitForTimeout(500); await pg.screenshot({ path: OUT + 'nowalls.png' });
  // a few computer turns
  const n = await pg.evaluate(async () => { let k = 0; for (const p of S.players) p.ai = true; for (; k < 40 && !S.over; k++) { runAI && await new Promise(r => { try { aiTurnSync ? aiTurnSync() : null } catch (e) {} r(); }); } return S.tiles.filter(t => t.walls.some(w => w > 0)).length; });
  console.log('walled hexes', n, errs.length ? errs.join('\n') : 'no page errors'); await b.close();
})();
