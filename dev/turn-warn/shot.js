// Not shipped: the faction briefing, the about-to-win banner, the Robot market factory button. node shot.js index.html OUT/
const { chromium } = require('playwright'); const path = require('path');
const [, , FILE, OUT] = process.argv;
(async () => {
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1280, height: 800 } });
  const errs = []; pg.on('pageerror', e => errs.push(e.message));
  await pg.goto('file://' + path.resolve(FILE)); await pg.waitForTimeout(1000);
  await pg.evaluate(() => { showScreen(null); newGame('robots', {}); startTurn(); }); await pg.waitForTimeout(800);
  await pg.screenshot({ path: OUT + 'brief.png' });
  await pg.evaluate(() => { closeModal();
    const need = winCastles(); const cs = S.tiles.filter(t => t.castle && t.id !== S.homes[0] && t.id !== S.homes[1]);
    cs.slice(0, need).forEach(t => t.owner = 1); S.siege = { pid: 1, left: 2 };
    const h = S.tiles[S.homes[0]]; const j = nbrs(h.id)[0]; S.tiles[j].owner = 1; S.tiles[j].troops = 3; S.tiles[j].army = { bot: 3 };
    render(); showWinWarn(); });
  await pg.waitForTimeout(900); await pg.screenshot({ path: OUT + 'warn.png' });
  console.log(await pg.evaluate(() => JSON.stringify(winWarnings())));
  // Robots: a market, then Advancements on it
  const r = await pg.evaluate(() => { S.siege = null; const me = S.players[0]; me.mat = 20; me.gold = 50;
    const t = S.tiles.find(x => x.owner < 0 && x.terrain === 'plain' && !x.castle && nbrs(x.id).includes(S.homes[0]));
    t.owner = 0; t.market = 1; const cid = FACTIONS.robots.cards[0].id; me.hand[0] = cid;
    S.play = { card: cid, step: cardOf(0, cid).actions.indexOf('advance') };
    ui.sel = t.id; render(); return t.id; });
  await pg.waitForTimeout(600); await pg.screenshot({ path: OUT + 'robo.png' });
  const has = await pg.$('[data-av="rnext"]'); console.log('rnext button', !!has);
  if (has) { await has.click(); await pg.waitForTimeout(300); console.log(await pg.evaluate(i => JSON.stringify({ b: S.tiles[i].barracks, mat: S.players[0].mat }), r)); }
  console.log(errs.length ? errs.join('\n') : 'no page errors'); await b.close();
})();
