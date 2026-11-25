// Not shipped: Triceratops takes a quarter from shots. node check.js
const { chromium } = require('playwright'); const path = require('path');
(async () => {
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1280, height: 800 } });
  const errs = []; pg.on('pageerror', e => errs.push(e.message));
  await pg.goto('file://' + path.resolve('arena.html')); await pg.waitForTimeout(800);
  await pg.click('button[data-ft="0"][data-fac="Dinosaurs"]').catch(() => {}); await pg.click('button[data-ft="1"][data-fac="Robots"]').catch(() => {});
  await pg.evaluate(() => { for (const k of ORDER) { COUNTS[0][k] = 0; COUNTS[1][k] = 0; } COUNTS[0].bow = 3; COUNTS[1].rarch = 20; COUNTS[1].rlong = 4; });
  await pg.click('#again').catch(() => {});
  for (const t of [4000, 6000]) { await pg.waitForTimeout(t);
    console.log(await pg.evaluate(() => JSON.stringify(F.filter(f => f.key === 'bow').map(f => +f.hp.toFixed(2))) + ' longbow targets ' + JSON.stringify(F.filter(f => f.key === 'rlong').map(f => f.target ? f.target.key : null)))); }
  await pg.locator('#arena').screenshot({ path: process.argv[2] || 'trike.png' });
  console.log(errs.length ? errs.join('\n') : 'no page errors'); await b.close();
})();
