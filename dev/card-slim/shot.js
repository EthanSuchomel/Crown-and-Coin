// Not shipped: the cards column on a computer screen: your hand, and a card being played. node shot.js index.html OUT/ w h
const { chromium } = require('playwright'); const path = require('path');
const [, , FILE, OUT, W, H] = process.argv;
(async () => {
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: +W, height: +H } });
  const errs = []; pg.on('pageerror', e => errs.push(e.message));
  await pg.goto('file://' + path.resolve(FILE)); await pg.waitForTimeout(1000);
  for (const fac of ['dinos', 'mythical']) {
    await pg.evaluate(f => { showScreen(null); newGame(f, {}); render(); }, fac); await pg.waitForTimeout(600);
    await pg.screenshot({ path: `${OUT}hand_${fac}_${W}.png` });
    await pg.evaluate(() => { const p = S.players[0]; if (!p.hand.some(c => cardOf(0, c).actions.includes('recruit'))) p.hand[0] = FACTIONS[p.faction].cards.find(c => c.actions.includes('recruit')).id;
      playCard(p.hand.find(c => cardOf(0, c).actions.includes('recruit'))); let n = 0; while (curAction() !== 'recruit' && n++ < 3) nextStep(true); render(); });
    await pg.waitForTimeout(600); await pg.screenshot({ path: `${OUT}play_${fac}_${W}.png` });
  }
  console.log(errs.length ? errs.join('\n') : 'no page errors'); await b.close();
})();
