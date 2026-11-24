// Not shipped: the new cards and the one-time swap. node shot.js index.html OUT/
const { chromium } = require('playwright'); const path = require('path');
const [, , FILE, OUT] = process.argv;
(async () => {
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1280, height: 800 } });
  const errs = []; pg.on('pageerror', e => errs.push(e.message));
  await pg.goto('file://' + path.resolve(FILE)); await pg.waitForTimeout(1000);
  await pg.evaluate(() => { showScreen(null); newGame('robots', {}); render(); }); await pg.waitForTimeout(600);
  await pg.screenshot({ path: OUT + 'hand.png' });
  console.log(await pg.evaluate(() => JSON.stringify(Object.keys(FACTIONS).map(f => [f, FACTIONS[f].cards.map(c => c.actions.join('/'))]))));
  await pg.click('[data-act="swap"]'); await pg.waitForTimeout(300);
  await pg.screenshot({ path: OUT + 'swap1.png' });
  await pg.click('#modal button[data-i="0"]'); await pg.waitForTimeout(300);
  await pg.screenshot({ path: OUT + 'swap2.png' });
  const before = await pg.evaluate(() => JSON.stringify([S.players[0].hand, S.players[0].reserve]));
  await pg.click('#modal button[data-i="0"]'); await pg.waitForTimeout(300);
  console.log('before', before, 'after', await pg.evaluate(() => JSON.stringify([S.players[0].hand, S.players[0].reserve, S.players[0].swapped, canSwap(0), !!document.querySelector('[data-act="swap"]')])));
  await pg.screenshot({ path: OUT + 'after.png' });
  // play a few turns against the computer: every card, no upgrade picker
  const r = await pg.evaluate(async () => { const out = []; for (let k = 0; k < 4; k++) { const c = S.players[0].hand[0]; out.push(upgradeDue(0, c)); playCard(c); let n = 0; while (S.play && n++ < 10) nextStep(true); await new Promise(r => setTimeout(r, 200)); } return out; });
  console.log('upgradeDue', JSON.stringify(r));
  console.log(errs.length ? errs.join('\n') : 'no page errors'); await b.close();
})();
