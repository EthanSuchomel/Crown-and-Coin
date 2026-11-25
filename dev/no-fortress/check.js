// Not shipped: no Fortress map. node check.js
const { chromium } = require('playwright'); const path = require('path');
(async () => {
  const b = await chromium.launch(); const errs = [];
  let pg = await b.newPage({ viewport: { width: 1280, height: 800 } }); pg.on('pageerror', e => errs.push(e.message));
  await pg.goto('file://' + path.resolve('arena.html')); await pg.waitForTimeout(800);
  console.log('arena maps:', await pg.evaluate(() => [...document.querySelectorAll('button[data-map]')].map(x => x.dataset.map).join(',')));
  pg = await b.newPage({ viewport: { width: 1280, height: 800 } }); pg.on('pageerror', e => errs.push(e.message));
  await pg.goto('file://' + path.resolve('index.html')); await pg.waitForTimeout(1000);
  console.log('board:', await pg.evaluate(() => { showScreen(null); newGame('mammals', {});
    const t = S.tiles.find(t => !t.castle); const r = {}; t.fort = 1; for (const [k, v] of [['open', {}], ['mountain', { terrain: 'mountain' }], ['forest', { forest: true }]]) { Object.assign(t, { terrain: v.terrain || t.terrain, forest: !!v.forest }); r[k] = arenaMap(t, 0); } return JSON.stringify(r); }));
  console.log(errs.length ? errs.join('\n') : 'no page errors'); await b.close();
})();
