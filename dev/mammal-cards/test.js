// Checks for the Mammal card upgrades (2026-11-13). node test.js /path/to/index.html [games]
const {chromium}=require('playwright');
(async()=>{
  const page=process.argv[2], games=+(process.argv[3]||2);
  const b=await chromium.launch(); const pg=await b.newPage({viewport:{width:1280,height:800}});
  const errs=[]; pg.on('pageerror',e=>errs.push('PAGEERR '+e.message+' '+(e.stack||'').split('\n').slice(0,3).join(' | ')));
  pg.on('console',m=>{ if(m.type()==='error'&&!/fonts|ERR_|net::|Failed to load resource/.test(m.text())) errs.push('CONSOLE '+m.text().slice(0,200)); });
  await pg.goto('file://'+page); await pg.waitForTimeout(1200);
  const res=await pg.evaluate(()=>{
    const out=[]; const ok=(name,cond,info)=>out.push((cond?'PASS ':'FAIL ')+name+(info!==undefined?' :: '+JSON.stringify(info):''));
    const fresh=()=>{ newGame('mammals',{opp:'robots',quiet:true}); S.players[0].ai=false; S.current=0; S.play=null; ui.busy=false; S.players[0].gold=500; S.players[0].mat=50; };
    const setUp=(cid,lv)=>{ S.players[0].up=S.players[0].up||{}; S.players[0].up[cid]=[lv,lv,lv]; };
    const play=(cid,step)=>{ S.play={card:cid,step}; };
    const own=()=>S.tiles.filter(t=>t.owner===0);
    const home=()=>S.tiles[S.homes[0]];
    // give the player a few plain hexes next to home
    const grab=(n)=>{ const ids=[]; const q=[S.homes[0]]; const seen=new Set(q);
      while(q.length&&ids.length<n){ const i=q.shift(); for(const j of nbrs(i)){ if(seen.has(j)) continue; seen.add(j); const t=S.tiles[j]; if(t.terrain==='plain'&&!t.castle&&t.owner<0){ t.owner=0; ids.push(j); } q.push(j); } }
      return ids; };
    fresh();
    ok('cardUps for Mammals', cardUps(0)===true);
    ok('no named upgrades', !hasNamed(0));
    // ---- The Long Roam ----
    const ids=grab(6);
    for(const lv of [0,1,2,3]){ fresh(); setUp('roam',lv); play('roam',0); S.play.moves=0;
      ok(`Long Roam move L${lv}: moves`, movesLimit(0)===2+(lv>=2?2:lv>=1?1:0), movesLimit(0));
      ok(`Long Roam move L${lv}: mountains`, curLvl()===(lv>=3?1:0), curLvl()); }
    fresh(); grab(6); setUp('roam',1); const bk=own().find(t=>!t.castle); bk.barracks=1; bk.bk=0;
    play('roam',1); let notes=dinoActionStart(0); ok('Den Raising note', notes.join(' ').includes('Den Raising'), notes);
    ui.sel=bk.id; mammFreeBkH(); ok('Den Raising: barracks level 1', bk.bk===1, bk.bk); mammFreeBkH(); ok('Den Raising only once', bk.bk===1);
    fresh(); const g2=grab(6); setUp('roam',2); play('roam',1); dinoActionStart(0); const mh=S.tiles[g2[0]]; mh.market=1;
    ok('Second Stall: 2nd market free', costOf('market',0,mh)===0, costOf('market',0,mh)); mh.market=0; ok('Second Stall: 1st market full price', costOf('market',0,mh)===COSTS.market[0]);
    fresh(); grab(6); setUp('roam',3); const m0=matOf(0); play('roam',1); dinoActionStart(0); ok('Land Bounty: +1 material per hex', matOf(0)-m0===own().length, [matOf(0)-m0, own().length]);
    fresh(); setUp('roam',3); play('roam',2); const h0={...home().army}; dinoActionStart(0); const hA=home().army;
    ok('Long Roam recruit L3: ape, rhino, eleph at home', (hA.ape|0)-(h0.ape|0)===1&&(hA.rhino|0)-(h0.rhino|0)===1&&(hA.eleph|0)-(h0.eleph|0)===1, [h0,hA]);
    // ---- Forage ----
    for(const lv of [1,2,3]){ fresh(); const gg=grab(10); S.tiles[gg[0]].market=3; S.tiles[gg[1]].market=3; setUp('forage',lv); play('forage',0);
      const hexes=incomeOf(0).tiles, mk=marketsOf(0), base=harvestGold(0,0,false), g0=S.players[0].gold, mat0=matOf(0);
      resolveInstant(0,'harvest',0,lv); const dg=S.players[0].gold-g0, dm=matOf(0)-mat0;
      const expG=base+(lv>=3?2:1)*hexes-Math.floor(hexes*HARVEST_PER[0]), expM=lv>=3?Math.floor(mk/2):lv>=2?Math.floor(mk/3):0;
      ok(`Forage harvest L${lv}`, dg===expG&&dm===expM, {dg,expG,dm,expM,hexes,mk}); }
    fresh(); grab(6); setUp('forage',3); const fm0=matOf(0); play('forage',1); dinoActionStart(0);
    ok('Forage build L3: +3 mats, free barracks, free fort', matOf(0)-fm0===3&&S.players[0].fnest===1&&S.players[0].ffort===1, [matOf(0)-fm0,S.players[0].fnest,S.players[0].ffort]);
    const fh=own().find(t=>!t.castle&&t.terrain==='plain'); ok('free barracks costs 0', costOf('barracks',0,fh)===0); ok('free fort costs 0', costOf('fort',0,fh)===0);
    ui.sel=fh.id; S.players[0].mat=0; build(fh.id,'barracks'); ok('free barracks built, token used', fh.barracks===1&&S.players[0].fnest===0, [fh.barracks,S.players[0].fnest]);
    build(fh.id,'fort'); ok('free fort built, token used', fh.fort===1&&S.players[0].ffort===0, [fh.fort,S.players[0].ffort]);
    ok('next barracks full price', costOf('barracks',0,fh)===COSTS.barracks[0]);
    fresh(); const fg=grab(6); const A=S.tiles[fg[0]], B=S.tiles[fg[1]]; A.barracks=1; A.fort=1; B.barracks=1; setUp('forage',3); play('forage',2);
    const a0={...A.army}, b0={...B.army}; dinoActionStart(0);
    ok('Forage recruit L3: barracks+fort hex gets 2 apes and a rhino', (A.army.ape|0)-(a0.ape|0)===2&&(A.army.rhino|0)-(a0.rhino|0)===1, A.army);
    ok('Forage recruit L3: barracks-only hex gets 1 ape, no rhino', (B.army.ape|0)-(b0.ape|0)===1&&!(B.army.rhino|0), B.army);
    fresh(); const fg1=grab(6); S.tiles[fg1[0]].barracks=1; S.tiles[fg1[0]].fort=1; setUp('forage',1); play('forage',2); const c0={...S.tiles[fg1[0]].army}; dinoActionStart(0);
    ok('Forage recruit L1: barracks only (not fort)', (S.tiles[fg1[0]].army.ape|0)-(c0.ape|0)===1, S.tiles[fg1[0]].army);
    // ---- Den Season ----
    for(const lv of [1,2,3]){ fresh(); setUp('den',lv); play('den',0); const g0=S.players[0].gold, m0=matOf(0), base=harvestGold(0,0,false);
      resolveInstant(0,'harvest',0,lv); ok(`Den harvest L${lv}`, S.players[0].gold-g0===base+[0,5,10,15][lv]&&matOf(0)-m0===(lv>=3?3:0), [S.players[0].gold-g0-base, matOf(0)-m0]); }
    fresh(); setUp('den',3); play('den',1); const dh0={...home().army}; dinoActionStart(0);
    ok('Den recruit L3: 3 apes + rhino at home', (home().army.ape|0)-(dh0.ape|0)===3&&(home().army.rhino|0)-(dh0.rhino|0)===1, home().army);
    ok('Den Prices: units 1 gold less', unitCostAt(home(),0,'rhino')===UNIT_STATS.rhino.cost-1, unitCostAt(home(),0,'rhino'));
    for(const lv of [1,2,3]){ fresh(); const dg=grab(4); const big=S.tiles[dg[0]]; addUnits(big,'ape',10,true); const small=S.tiles[dg[1]]; addUnits(small,'ape',4,true);
      setUp('den',lv); play('den',2); const note=fortifyStart(0,lv);
      ok(`Den fortify L${lv}: big army`, (big.army.porc|0)===(lv>=2?2:1)&&(big.army.rhino|0)===(lv>=3?1:0), big.army);
      ok(`Den fortify L${lv}: small army untouched`, !(small.army.porc|0), small.army); }
    // ---- Call of the Wild ----
    fresh(); setUp('wild',2); play('wild',0); dinoActionStart(0); const wm0=matOf(0); mammBought(0,'ape',2); mammBought(0,'ape',1); mammBought(0,'eleph',1);
    ok('Hide Trade + Tusk Trade', matOf(0)-wm0===1+5, matOf(0)-wm0);
    fresh(); setUp('wild',3); play('wild',0); ok('Home Calling: home units 2 less', unitCostAt(home(),0,'rhino')===UNIT_STATS.rhino.cost-2, unitCostAt(home(),0,'rhino'));
    for(const lv of [1,2,3]){ fresh(); setUp('wild',lv); play('wild',1); const cs=own().filter(t=>t.castle).length, g0=S.players[0].gold, base=harvestGold(0,0,false);
      resolveInstant(0,'harvest',0,lv); ok(`Wild harvest L${lv}`, S.players[0].gold-g0===base+[0,3,6,10][lv]*cs, S.players[0].gold-g0-base); }
    fresh(); const wg=grab(6); setUp('wild',3); play('wild',2); dinoActionStart(0);
    ok('Wild advance L3: free fort token', S.players[0].ffort===1); ok('Wild advance: fort allowed', S.play.wf===1&&S.play.mb===1);
    const wt=S.tiles[wg[0]]; ui.sel=wt.id; const wm1=matOf(0); mammFortH(); ok('Roost Raising: fort built free with token', wt.fort===1&&matOf(0)===wm1&&S.players[0].ffort===0, [wt.fort,matOf(0)-wm1]);
    mammFortH(); ok('Roost Raising only once', wt.fort===1);
    const wb=S.tiles[wg[1]]; wb.barracks=1; wb.bk=2; const dest=mammBkSpots(0,wb.id).find(i=>i!==wt.id);
    ui.sel=wb.id; ui.mvBk=wb.id; mammMoveBkH(dest); ok('Den Move: barracks moved with its level', !wb.barracks&&!wb.bk&&S.tiles[dest].barracks===1&&S.tiles[dest].bk===2, [wb.barracks,S.tiles[dest].barracks,S.tiles[dest].bk]);
    // ---- Tusks and Thorns ----
    for(const lv of [0,1,2,3]){ fresh(); setUp('tusks',lv); S.play=null; const cs=own().filter(t=>t.castle).length, inc=incomeOf(0);
      ok(`Tusks harvest L${lv}: castles pay every round`, inc.tusk===[0,1,3,5][lv]*cs, inc.tusk);
      const m0=matOf(0); const g0=S.players[0].gold; beginTurn(); ok(`Tusks harvest L${lv}: materials every round`, matOf(0)-m0===[0,0,1,2][lv]*cs, matOf(0)-m0); }
    fresh(); const tg=grab(4); const tb=S.tiles[tg[0]]; tb.barracks=1; tb.bk=1; setUp('tusks',2); play('tusks',1);
    ok('Quick Dens: 1 material less', bkUpCost(0,1,tb)===BARRACKS_UP[1]-1, bkUpCost(0,1,tb));
    const tm0=matOf(0); doUpgradeBarracks(0,tb.id,0); ok('Free Den Upgrade: first upgrade free (any level)', tb.bk===2&&matOf(0)===tm0, [tb.bk,tm0-matOf(0)]);
    doUpgradeBarracks(0,tb.id,0); ok('second upgrade paid', tb.bk===3&&tm0-matOf(0)===BARRACKS_UP[2]-1, tm0-matOf(0));
    for(const lv of [1,2,3]){ fresh(); setUp('tusks',lv); play('tusks',2); S.play.moves=0;
      ok(`Tusks move L${lv}: moves`, movesLimit(0)===2+(lv>=1?1:0)+(lv>=3?1:0), movesLimit(0));
      ok(`Tusks move L${lv}: sneak`, atkOpts(0,0,lv,1).surprise===(lv>=2?1:0)); S.play.moves=movesLimit(0)-1; ok(`Tusks move L${lv}: last move charge-only`, chargeOnly(0)===true); }
    // Roam Free: the regroup after the Advancements
    fresh(); const rg=grab(8); setUp('tusks',3); S.play={card:'tusks',step:0}; S.players[0].hand=['tusks','roam','den'];
    enterStep(); ok('harvest done, now Advancements', curAction()==='advance', curAction());
    nextStep(true); ok('Roam Free: regroup phase', curAction()==='move'&&regrouping()&&rgOn(), [curAction(),S.play.rg]);
    render(); ok('Roam Free panel', document.getElementById('panel').innerHTML.includes('Roam Free'));
    const far=S.tiles[rg[rg.length-1]]; const fromH=home(); const tgts=moveTargets(fromH.id,curLvl()); ok('Roam Free reaches far hexes', tgts.includes(far.id), {n:tgts.length});
    const n0=far.troops; executeMove(fromH.id,far.id,{ape:1},0); ok('Roam Free move made, units stay ready', far.troops===n0+1&&far.fresh>=1, [far.troops,far.fresh]);
    ok('movesLeft unlimited', movesLeft()>50);
    nextStep(true); ok('after Roam Free: next action (Move)', curAction()==='move'&&!rgOn()&&S.play.step===2, [curAction(),S.play.step,S.play.rg]);
    // Watering Hole in any Build
    fresh(); grab(4); setUp('roam',0); play('roam',1); ok('Watering Hole in a basic Build', whOk(0)===true);
    // retired abilities
    fresh(); setUp('den',1); play('den',2); const pairs=grab(2); addUnits(S.tiles[pairs[0]],'rhino',4,true); fortifyStart(0,1); ok('no Mating', (S.tiles[pairs[0]].army.rhino|0)===4);
    // texts render
    fresh(); render(); fsPick='mammals'; renderFactionScreen(); const fi=document.getElementById('fsInfo').innerHTML;
    ok('faction screen lists Mammal card upgrades', fi.includes('Long March')&&fi.includes('Watering Hole'));
    return out;
  });
  const fails=res.filter(x=>x.startsWith('FAIL'));
  console.log(res.join('\n')); console.log(`\n${res.length-fails.length} passed, ${fails.length} failed`);
  // computer games with the Mammals
  const gres=await pg.evaluate((games)=>{
    const out=[]; const pairs=[['mammals','dinos'],['dinos','mammals'],['mammals','robots'],['robots','mammals'],['mammals','mythical'],['mythical','mammals']];
    for(const [a,o] of pairs) for(let gi=0;gi<games;gi++){
      try{
        newGame(a,{opp:o,quiet:true}); S.players[0].ai=true; S.players[0].diff='medium'; S.players[1].diff='medium';
        while(!S.over&&S.turn<=45){
          const pid=S.current, cid=aiChooseCard(pid); S.play={card:cid,step:0};
          for(const ev of aiCardGen(pid,cid)){}
          if(S.over) break; rotateCards(pid); advanceTurn(); if(S.over) break; beginTurn();
        }
        const mi=S.players.findIndex(p=>p.faction==='mammals'), up=S.players[mi].up||{};
        out.push({a,o,winner:S.over?S.players[S.winner!=null?S.winner:0]?.faction:null,turn:S.turn,mammUps:Object.keys(up).map(k=>k+':'+up[k].join('')).join(' '),mat:matOf(mi)});
      }catch(e){ out.push({a,o,err:String(e&&e.stack||e).slice(0,600)}); }
    }
    return out; },games);
  for(const g of gres) console.log(JSON.stringify(g));
  console.log('ERRS',JSON.stringify(errs.slice(0,10)));
  await b.close();
})();
