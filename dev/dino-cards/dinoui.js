const {chromium}=require('playwright');
(async()=>{
  const b=await chromium.launch(); const pg=await b.newPage({viewport:{width:1280,height:800}});
  const errs=[]; pg.on('pageerror',e=>errs.push('PAGEERR '+e.message+' '+(e.stack||'').split('\n').slice(0,3).join('|')));
  await pg.goto('file://'+__dirname+'/test.html'); await pg.waitForTimeout(1200);
  for(const cid of ['stamp','pack','siege','hunt','nest']){
    const r=await pg.evaluate((cid)=>{ const L=[];
      newGame('dinos',{opp:'robots',quiet:false,level:'medium'}); showScreen(null);
      const p=S.players[0]; p.gold=120; p.mat=10; p.up={}; p.up[cid]=[3,3,3];
      p.hand=[cid].concat(facOf(0).cards.map(c=>c.id).filter(c=>c!==cid).slice(0,2)); p.reserve=facOf(0).cards.map(c=>c.id).filter(c=>!p.hand.includes(c));
      const h=S.homes[0], ns=nbrs(h).filter(j=>S.tiles[j].terrain==='plain'&&!S.tiles[j].castle);
      ns.forEach((j,i)=>{ const t=S.tiles[j]; t.owner=0; if(i===0){ t.barracks=1; addUnits(t,'galli',4,true);} if(i===1){ t.market=2; t.barracks=1; } });
      const nc=S.tiles.find(t=>t.castle&&t.owner<0); nc.owner=0; addUnits(nc,'galli',2,true);
      addUnits(S.tiles[h],'galli',6,true); render();
      const snap=()=>({a:curAction(),fx:S.play&&S.play.fx?JSON.stringify(S.play.fx):'',gold:p.gold,mat:p.mat|0,fnest:p.fnest|0,units:unitTotal(0),notes:ui.notes.map(x=>x.replace(/<[^>]+>/g,'')).join(' | ').slice(0,300)});
      startCard(cid); L.push(['start',snap()]);
      for(let k=0;k<12&&S.play&&S.current===0;k++){
        const a=curAction();
        if(a==='move'&&!regrouping()){ const src=S.tiles.filter(t=>t.owner===0&&t.fresh>0); L.push(['moves',movesLimit(0),src.map(t=>t.id+':'+moveTargets(t.id,curLvl()).length).join(',')]); }
        if(a==='move'&&regrouping()){ L.push(['regroup targets', moveTargets(ns[0],0).length, 'pickList', fxPickList().join(',')]); if(S.play.fx.rally){ ui.sel=ns[1]; rallyTo(ns[1]); L.push(['rallied',S.tiles[ns[1]].troops]); } }
        if(a==='fortify'){ L.push(['picks',fxPickList().join(',')]); fxChoose(fxPickList().includes('move')?'move':'build'); L.push(['chose',snap()]); continue; }
        if(a==='build'){ L.push(['market price at ns1',costOf('market',0,S.tiles[ns[1]]),'barracks',costOf('barracks',0),'fort',costOf('fort',0)]); build(ns[2],'market'); L.push(['after market',p.gold, S.tiles[ns[2]].market]); }
        if(a==='recruit'){ L.push(['dpick',JSON.stringify(S.play.dpick||null),'cost home',unitCostAt(S.tiles[h],0,'galli'),'cost nest',unitCostAt(S.tiles[ns[0]],0,'galli')]); if(S.play.dpick) placeDpick(ns[1]); L.push(['after place',S.tiles[ns[1]].troops]); }
        if(a==='advance'){ L.push(['bk cost',bkUpCost(0,0),'guard',guardCost(0)]); const ok=doArmor(0); L.push(['armor',ok,p.armor]); }
        render(); L.push(['step',snap(), document.querySelector('#panel').innerText.replace(/\s+/g,' ').slice(0,160)]);
        nextStep(true);
      }
      return L; },cid);
    console.log('=====',cid); r.forEach(x=>console.log(JSON.stringify(x).slice(0,420)));
  }
  console.log('ERRS',errs.slice(0,6)); await b.close();
})();
