// Not shipped: close-ups of walls at every damage level. node shot2.js index.html OUT/
const { chromium } = require('playwright'); const path = require('path');
const [, , FILE, OUT] = process.argv;
(async () => {
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1280, height: 800 }, deviceScaleFactor: 4 });
  const errs = []; pg.on('pageerror', e => errs.push(e.message));
  await pg.goto('file://' + path.resolve(FILE)); await pg.waitForTimeout(1000);
  const ids = await pg.evaluate(() => { showScreen(null); newGame('robots', {}); S.players[0].briefed = true; closeModal();
    const cs = S.tiles.filter(t => t.castle && t.id !== S.homes[0] && t.id !== S.homes[1]);
    cs[0].walls = [3, 3, 3, 3, 3, 3]; cs[1].walls = [0, 3, 0, 0, 3, 0]; cs[2].walls = [3, 3, 0, 0, 0, 3];
    render(); return cs.slice(0, 3).map(t => t.id); });
  await pg.waitForTimeout(800); await pg.evaluate(() => closeModal()); await pg.waitForTimeout(300);
  for (const id of ids) {
    const box = await pg.evaluate(i => { const svg = document.getElementById('map'); const vb = svg.viewBox.baseVal, r = svg.getBoundingClientRect();
      const [cx, cy] = hexCenter ? hexCenter(i) : [0, 0]; const k = Math.min(r.width / vb.width, r.height / vb.height);
      const ox = r.left + (r.width - vb.width * k) / 2 - vb.x * k, oy = r.top + (r.height - vb.height * k) / 2 - vb.y * k;
      return { x: ox + cx * k - 70, y: oy + cy * k - 80, width: 140, height: 150 }; }, id).catch(e => null);
    if (box) await pg.screenshot({ path: OUT + 'z' + id + '.png', clip: box });
  }
  console.log(ids, errs.length ? errs.join('\n') : 'no page errors'); await b.close();
})();
