const {chromium}=require('playwright');
(async()=>{
  const fac=process.argv[2]||'dinos';
  const b=await chromium.launch(); const pg=await b.newPage({viewport:{width:1280,height:800}});
  const errs=[]; pg.on('pageerror',e=>errs.push('PAGEERR '+e.message)); pg.on('console',m=>{ if(m.type()==='error'&&!/ERR_TUNNEL|Failed to load/.test(m.text())) errs.push('CONSOLE '+m.text()); });
  await pg.goto('file://'+__dirname+'/test.html'); await pg.waitForTimeout(1200);
  await pg.click('[data-scr="start"]'); await pg.waitForTimeout(300);
  await pg.click(`[data-fs="${fac}"]`); await pg.waitForTimeout(200);
  await pg.screenshot({path:'fs_'+fac+'.png'});
  await pg.click('[data-scr="go"]'); await pg.waitForTimeout(600);
  const cards={dinos:['siege','stamp','pack'],robots:['sprot','cons','mobil'],mammals:['den','forage','roam'],mythical:['grove','march','arcan']}[fac];
  const setup=await pg.evaluate((cards)=>{
    S.players[0].hand=cards.slice(); S.players[0].reserve=cardOf(0,cards[0])?facOf(0).cards.map(c=>c.id).filter(c=>!cards.includes(c)):[];
    S.players[0].gold=40;
    const h=S.homes[0], ns=nbrs(h).filter(j=>S.tiles[j].terrain==='plain'&&!S.tiles[j].castle).slice(0,3);
    ns.forEach((j,i)=>{ const t=S.tiles[j]; t.owner=0; t.army={}; t.ready={}; addUnits(t,basicOf(0),i===0?4:0,true); });
    // one more hex beyond the first neighbour, so a 2-step regroup exists
    const far=nbrs(ns[1]).find(j=>S.tiles[j].terrain==='plain'&&S.tiles[j].owner<0&&!S.tiles[j].castle); if(far!=null) S.tiles[far].owner=0;
    render(); return {h,ns,far};
  },cards);
  console.log('setup',JSON.stringify(setup));
  const panel=async()=>pg.evaluate(()=>document.querySelector('#panel').innerText.replace(/\s+/g,' ').slice(0,400));
  const head=async()=>pg.evaluate(()=>document.querySelector('#sidehead').innerText.replace(/\s+/g,' '));
  console.log('HEAD',await head());
  await pg.click(`[data-act="pick"][data-cid="${cards[0]}"]`); await pg.waitForTimeout(200);
  console.log('PICKED',await panel());
  await pg.click(`[data-act="play"]`); await pg.waitForTimeout(300);
  await pg.evaluate(()=>{ for(let i=0;i<4&&!regrouping();i++) nextStep(true); });
  console.log('PLAY',await panel());
  await pg.screenshot({path:'p1_regroup_'+fac+'.png'});
  // regroup: from the 4-unit hex to the far hex (2 steps through own land)
  const tgt=setup.far!=null?setup.far:setup.ns[2];
  const t1=await pg.evaluate(({a})=>{ onCell(a); return moveTargets(a,curLvl()); },{a:setup.ns[0]});
  console.log('targets',JSON.stringify(t1), 'tgt',tgt, 'curAction',await pg.evaluate(()=>curAction()), 'movesLeft',await pg.evaluate(()=>movesLeft()));
  await pg.evaluate(({b})=>onCell(b),{b:tgt}); await pg.waitForTimeout(200);
  const sheet=await pg.evaluate(()=>{ const m=document.querySelector('#modal'); return m.classList.contains('hidden')?'(no sheet)':m.innerText.replace(/\s+/g,' ').slice(0,200); });
  console.log('SHEET',sheet);
  if(sheet!=='(no sheet)') { await pg.click('#mvall'); await pg.waitForTimeout(200); }
  console.log('after move ready',await pg.evaluate(({b})=>[S.tiles[b].troops,S.tiles[b].fresh],{b:tgt}));
  console.log('REGROUP',await panel());
  await pg.click('#nextBtn'); await pg.waitForTimeout(250);
  console.log('PICK',await panel());
  await pg.screenshot({path:'p2_pick_'+fac+'.png'});
  await pg.click('[data-act="fxpick"][data-k="build"]'); await pg.waitForTimeout(250);
  console.log('BUILD',await panel());
  await pg.evaluate(({b})=>onCell(b),{b:setup.ns[1]}); await pg.waitForTimeout(600);
  await pg.screenshot({path:'p3_build_'+fac+'.png'});
  const bubs=await pg.evaluate(()=>[...document.querySelectorAll('#bldov .bub')].map(x=>x.getAttribute('aria-label')+(x.disabled?' [off]':'')));
  console.log('BUBBLES',JSON.stringify(bubs));
  // buy materials
  if(await pg.$('[data-act="trade"]')){
    await pg.click('[data-act="trade"]'); await pg.waitForTimeout(200);
    console.log('TRADE',await pg.evaluate(()=>document.querySelector('#modal').innerText.replace(/\s+/g,' ')));
    await pg.screenshot({path:'p4_trade_'+fac+'.png'});
    if(await pg.$('#trok')){ await pg.click('#trok'); await pg.waitForTimeout(200); }
    console.log('after trade mat/gold/tr',await pg.evaluate(()=>[matOf(0),S.players[0].gold,S.players[0].tr]));
  }
  // give enough for a barracks and build it
  await pg.evaluate(()=>{ S.players[0].mat=(S.players[0].mat|0)+5; render(); }); await pg.waitForTimeout(500);
  const bb=await pg.$('#bldov .bub[data-bk="barracks"]');
  if(bb){ await bb.click(); await pg.waitForTimeout(250); }
  console.log('after build barracks',await pg.evaluate(({b})=>[S.tiles[b].barracks,matOf(0),S.players[0].gold],{b:setup.ns[1]}));
  console.log('BTN',await pg.evaluate(()=>document.querySelector('#nextBtn').innerText));
  await pg.click('#nextBtn'); await pg.waitForTimeout(300);
  const lw=await pg.evaluate(()=>{ const m=document.querySelector('#modal'); return m.classList.contains('hidden')?'':m.innerText.replace(/\s+/g,' '); });
  if(lw){ console.log('LEFTOVER',lw); await pg.click('#lwg'); await pg.waitForTimeout(300); }
  console.log('NEXT',await panel(), 'action',await pg.evaluate(()=>[curAction(),S.play&&S.play.step,JSON.stringify(S.play&&S.play.fx)]));
  await pg.screenshot({path:'p5_next_'+fac+'.png'});
  console.log('ERRS',errs.slice(0,8));
  await b.close();
})();
