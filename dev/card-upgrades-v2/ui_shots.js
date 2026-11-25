// Not shipped: screenshots of the new card upgrades' buttons and the upgrade picker. node ui_shots.js page.html outdir/
const {chromium}=require('playwright'); const path=require('path');
(async()=>{
  const b=await chromium.launch(); const pg=await b.newPage({viewport:{width:1400,height:900}}); const errs=[]; pg.on('pageerror',e=>errs.push(e.message));
  await pg.goto('file://'+path.resolve(process.argv[2])); await pg.waitForTimeout(1200); const O=process.argv[3];
  const shot=async n=>{ await pg.waitForTimeout(400); await pg.screenshot({path:O+n+'.png'}); };
  // the upgrade picker on a Mythical card
  await pg.evaluate(()=>{ showScreen(null); newGame('mythical',{opp:'dinos',}); document.querySelectorAll('.modal').forEach(x=>x.hidden=true); S.current=0; const c=facOf(0).cards[0]; if(!S.players[0].hand.includes(c.id)) S.players[0].hand[0]=c.id; S.players[0].favor={[c.id]:1}; render(); openUpgrade(c.id); });
  await shot('picker_myth');
  // Advancements with card 4 at level 3 and card 2 at level 2: Rally Cry, Freeze, Border Claim, Early Harvest
  await pg.evaluate(()=>{ closeModal(); showScreen(null); newGame('dinos',{opp:'robots',}); document.querySelectorAll('.modal').forEach(x=>x.hidden=true); S.current=0; const p=S.players[0];
    const c=facOf(0).cards[3]; p.up={[c.id]:[0,0,3]}; p.hand[0]=c.id; S.play={card:c.id,step:2}; ui.notes=[]; ui.notes.push(...nuActionStart(0)); ui.sel=S.homes[0]; render(); });
  await shot('adv_card4');
  await pg.evaluate(()=>{ nuAct('freeze'); });
  await shot('adv_freeze');
  // Build with Relocate
  await pg.evaluate(()=>{ const p=S.players[0]; const c=facOf(0).cards[3]; p.up={[c.id]:[0,3,0]}; S.play={card:c.id,step:1}; ui.notes=[]; ui.nuMode=null; ui.notes.push(...nuActionStart(0)); const h=S.tiles[S.homes[0]]; h.market=1; ui.sel=h.id; render(); });
  await shot('build_relocate');
  // the hand with card upgrades on
  await pg.evaluate(()=>{ S.play=null; ui.sel=null; ui.notes=[]; render(); });
  await shot('hand');
  console.log('page errors',errs.length,errs.slice(0,3)); await b.close(); })();
