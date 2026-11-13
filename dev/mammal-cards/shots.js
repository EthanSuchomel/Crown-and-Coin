const {chromium}=require('playwright');
(async()=>{ const out=process.argv[3];
  const b=await chromium.launch(); const pg=await b.newPage({viewport:{width:1280,height:800},deviceScaleFactor:1}); const errs=[]; pg.on('pageerror',e=>errs.push(e.message));
  await pg.goto('file://'+process.argv[2]); await pg.waitForTimeout(1200);
  await pg.click('[data-scr="start"]'); await pg.waitForTimeout(300);
  for(const o of await pg.$$('#fsChoices .fs-opt')) if(/Mammal/.test(await o.innerText())){ await o.click(); break; }
  await pg.waitForTimeout(300); await pg.evaluate(()=>{ const el=document.getElementById('fsInfo'); const h=[...el.querySelectorAll('h3')].find(x=>/Card abilities/.test(x.textContent)); if(h) h.scrollIntoView(); });
  await pg.screenshot({path:out+'/m1_faction.png'});
  await pg.click('[data-scr="go"]'); await pg.waitForTimeout(800);
  await pg.evaluate(()=>{ const p=S.players[0]; p.up={roam:[1,2,1],tusks:[1,3,2]}; p.favor={roam:3}; p.mat=20; p.gold=60; p.hand=['roam','tusks','den'];
    const h=S.tiles[S.homes[0]]; const j=nbrs(h.id).find(i=>S.tiles[i].terrain==='plain'&&!S.tiles[i].castle); const t=S.tiles[j]; t.owner=0; t.barracks=1; t.bk=0; addUnits(t,'ape',3,true); render(); });
  await pg.screenshot({path:out+'/m2_hand.png'});
  await pg.evaluate(()=>{ ui.pick='roam'; render(); }); await pg.screenshot({path:out+'/m3_pick.png'});
  await pg.evaluate(()=>{ ui.pick=null; S.play={card:'roam',step:1}; ui.notes=[]; enterStep(); const t=S.tiles.find(x=>x.owner===0&&x.barracks); ui.sel=t.id; render(); });
  await pg.screenshot({path:out+'/m4_build.png'});
  await pg.evaluate(()=>{ S.play={card:'tusks',step:1}; ui.notes=[]; ui.sel=null; enterStep(); render(); }); await pg.screenshot({path:out+'/m5_adv.png'});
  await pg.evaluate(()=>{ nextStep(true); ui.sel=S.homes[0]; render(); }); await pg.screenshot({path:out+'/m6_roamfree.png'});
  console.log('errs',JSON.stringify(errs)); await b.close(); })();
