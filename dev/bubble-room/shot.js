// Not shipped: screenshots of the round buttons round a hex (recruit at the home castle, build, advancements) on several boards.
// node shot.js index.html OUT/ [w h]
const { chromium } = require('playwright'); const path = require('path');
const [, , FILE, OUT, W, H] = process.argv;
(async () => {
  const b = await chromium.launch();
  const pg = await b.newPage({ viewport: { width: +W || 1280, height: +H || 800 } });
  const errs = []; pg.on('pageerror', e => errs.push(e.message));
  await pg.goto('file://' + path.resolve(FILE)); await pg.waitForTimeout(1200);
  const run = async (name, fac, opts, action, hexOf) => {
    await pg.evaluate(([fac, opts]) => { showScreen(null); newGame(fac, opts); render(); }, [fac, opts]);
    await pg.waitForTimeout(400);
    const ok = await pg.evaluate(([action, hexOf]) => {
      const p = S.players[0];
      if (!p.hand.some(c => cardOf(0, c).actions.includes(action))) p.hand[0] = FACTIONS[p.faction].cards.find(c => c.actions.includes(action)).id;
      const cid = p.hand.find(c => cardOf(0, c).actions.includes(action));
      playCard(cid); let n = 0; while (curAction() !== action && n++ < 3) nextStep(true);
      p.gold = 200; p.mat = 50;
      const id = eval(hexOf); onCell(id); render(); return [curAction(), id];
    }, [action, hexOf]);
    await pg.waitForTimeout(900);
    await pg.screenshot({ path: OUT + name + '.png' }); console.log('shot', name, ok);
  };
  await run('rec_home_random', 'dinos', {}, 'recruit', 'S.homes[0]');
  await run('rec_home_arena', 'robots', { map: 'arena-2p' }, 'recruit', 'S.homes[0]');
  await run('rec_home_3p', 'mammals', { np: 3 }, 'recruit', 'S.homes[0]');
  await run('rec_home_myth', 'mythical', { map: 'arena-2p' }, 'recruit', 'S.homes[0]');
  await run('adv_home', 'dinos', {}, 'advance', 'S.homes[0]');
  await run('adv_home_arena', 'robots', { map: 'arena-2p' }, 'advance', 'S.homes[0]');
  await run('build_home_arena', 'mammals', { map: 'arena-2p' }, 'build', 'S.homes[0]');
  // a hex at the right edge of the map's part of the screen (next to the cards)
  await run('rec_right_edge', 'dinos', {}, 'recruit', '(()=>{ const t=S.tiles.filter(t=>t.castle&&t.terrain!=="void"); let best=null,bx=-1e9; t.forEach(x=>{ const c=hexCenter(x.id); if(c[0]>bx){bx=c[0];best=x;} }); best.owner=0; best.troops=3; syncT&&syncT(best); return best.id; })()');
  console.log(errs.length ? errs.join('\n') : 'no page errors');
  await b.close();
})();
