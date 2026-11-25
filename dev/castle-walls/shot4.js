// Not shipped: the neutral Castle map. node shot4.js arena.html OUT/
const { chromium } = require('playwright'); const path = require('path');
const [, , FILE, OUT] = process.argv;
(async () => {
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1400, height: 900 } });
  const errs = []; pg.on('pageerror', e => errs.push(e.message));
  await pg.goto('file://' + path.resolve(FILE)); await pg.waitForTimeout(800);
  await pg.click('button[data-map="castle"]'); await pg.waitForTimeout(400);
  const fac = await pg.evaluate(() => [...document.querySelectorAll('button[data-fac]')].map(b => b.dataset.ft + ':' + b.dataset.fac));
  console.log(fac.join(' '));
  await pg.click('#again').catch(() => {}); 
  for (const t of [1500, 6000, 15000]) { await pg.waitForTimeout(t); await pg.locator('#arena').screenshot({ path: OUT + 'castle_' + t + '.png' }); }
  const info = await pg.evaluate(() => ({ forts: document.querySelectorAll('#arena img.fort').length, walls: document.querySelectorAll('#arena img.bwallart').length,
    bw: BW.map(L => L.slots.map(s => s.u ? 1 : 0).join('')) }));
  console.log(JSON.stringify(info), errs.length ? errs.join('\n') : 'no page errors'); await b.close();
})();
