// Not shipped: a check of every new card upgrade. node checks.js page.html
const {chromium}=require('playwright'); const path=require('path');
(async()=>{
  const b=await chromium.launch(); const pg=await b.newPage(); const errs=[]; pg.on('pageerror',e=>errs.push(e.message));
  await pg.goto('file://'+path.resolve(process.argv[2])); await pg.waitForTimeout(1000);
  const r=await pg.evaluate(()=>{ const out=[]; const ok=(name,c,info)=>out.push((c?'PASS ':'FAIL ')+name+(info!=null?'  '+JSON.stringify(info):''));
    const setup=(f,o)=>{ newGame(f,{opp:o||(f==='dinos'?'robots':'dinos'),quiet:true}); S.current=0; S.players.forEach(p=>p.ai=false); return S.players[0]; };
    const play=(n,a,lv)=>{ const p=S.players[0], c=facOf(0).cards[n-1]; p.up=p.up||{}; const u=p.up[c.id]=[0,0,0]; const i=c.actions.indexOf(a); u[i]=lv; S.play={card:c.id,step:i}; ui.notes=[]; return c; };
    const home=()=>S.tiles[S.homes[0]];
    const nb=i=>nbrs(i).map(j=>S.tiles[j]);
    try{
    // ----- card 1 Move -----
    let p=setup('dinos'); play(1,'move',1); S.play.moves=0;
    ok('C1 Move L1: 3 moves', movesLimit(0)===3, movesLimit(0));
    { const h=S.homes[0]; const two=moveTargets(h,curLvl()).filter(j=>man(h,j)===2&&S.tiles[j].owner===-1);
      ok('C1 Move L1: can reach an empty hex 2 away', two.length>0, two.length);
      if(two.length){ const to=two[0]; const r=executeMove(h,to,1,curLvl()); ok('C1 Move L1: claims both hexes', r.mid!=null&&S.tiles[r.mid].owner===0&&S.tiles[to].owner===0, {mid:r.mid}); } }
    play(1,'move',2); ok('C1 Move L2: Climb', curLvl()===1);
    play(1,'move',3); S.play.moves=0; ok('C1 Move L3: 4 moves', movesLimit(0)===4); S.play.moves=3; ok('C1 Move L3: the last move is attacks only', chargeOnly(0)===true);
    // ----- card 1 Build -----
    p=setup('dinos'); play(1,'build',3); p.gold=0; const m0=matOf(0); nuActionStart(0);
    ok('C1 Build L3: +3 materials', matOf(0)===m0+3, matOf(0)-m0);
    ok('C1 Build L1: first market free', costOf('market',0,home())===0);
    ok('C1 Build L2: first barracks free', costOf('barracks',0,home())===0);
    nuBuilt(0,'market',0); ok('C1 Build L1: then markets cost again', costOf('market',0,home())>0, costOf('market',0,home()));
    // ----- card 1 Advancements -----
    p=setup('dinos'); play(1,'advance',1); let g0=p.gold, mm=matOf(0); nuActionStart(0); ok('C1 Adv L1: +2 materials', matOf(0)-mm===2&&p.gold===g0);
    play(1,'advance',2); g0=p.gold; mm=matOf(0); nuActionStart(0); ok('C1 Adv L2: +2 materials, +5 gold', matOf(0)-mm===2&&p.gold-g0===5);
    play(1,'advance',3); g0=p.gold; mm=matOf(0); nuActionStart(0); ok('C1 Adv L3: +4 materials, +10 gold', matOf(0)-mm===4&&p.gold-g0===10);
    // ----- card 2 Build -----
    p=setup('dinos'); play(2,'build',2); const base=COSTS.market[0], bb=COSTS.barracks[0];
    ok('C2 Build L1: market 1 gold less', costOf('market',0,home())===base-1, [costOf('market',0,home()),base]);
    ok('C2 Build L2: barracks 1 material less', costOf('barracks',0,home())===bb-1, [costOf('barracks',0,home()),bb]);
    play(2,'build',3); home().market=2; g0=p.gold; nuActionEnd(0); ok('C2 Build L3: Market Day', p.gold-g0===2, p.gold-g0);
    // ----- card 2 Advancements -----
    p=setup('dinos'); play(2,'advance',1); const cl=nuClaimable(0); ok('C2 Adv L1: hexes to claim', cl.length>0, cl.length);
    ok('C2 Adv L1: claim', nuClaim(0,cl[0])&&S.tiles[cl[0]].owner===0); ok('C2 Adv L1: only once', !nuClaim(0,nuClaimable(0)[0]));
    play(2,'advance',2); g0=p.gold; const note=nuEarly(0); ok('C2 Adv L2: early harvest pays', p.gold>g0&&/Early Harvest/.test(note), p.gold-g0);
    S.turn++; S.play={card:facOf(0).cards[3].id,step:0}; g0=p.gold; resolveInstant(0,'harvest',0,0); ok('C2 Adv L2: next Harvest gives nothing', p.gold===g0, p.gold-g0);
    g0=p.gold; resolveInstant(0,'harvest',0,0); ok('C2 Adv L2: the one after pays again', p.gold>g0);
    play(2,'advance',3); { const t=S.tiles.find(t=>t.owner===0&&!t.castle)||cl.map(i=>S.tiles[i])[0]; t.barracks=1; t.bk=0; p.mat=0; ok('C2 Adv L3: free barracks upgrade', doUpgradeBarracks(0,t.id,0)&&t.bk===1); }
    // ----- card 2 Recruit -----
    for(const f of ['dinos','robots','mammals','mythical']){ p=setup(f); const h=home(); const t=S.tiles.find(x=>x.owner===-1&&x.terrain==='plain'&&!x.castle); t.owner=0; t.barracks=1; t.army={}; t.ready={}; syncT(t);
      play(2,'recruit',3); const n0=h.troops, nt=t.troops; nuActionStart(0);
      ok(`C2 Recruit L3 (${f}): home +basic${f==='mythical'?' +Griffin':''}`, h.troops-n0===(f==='mythical'?2:1), h.troops-n0);
      ok(`C2 Recruit L3 (${f}): barracks units`, f==='mythical'?t.troops===nt:(t.army[NU_SET[f]]===1&&t.army[basicOf(0)]===1), t.army); }
    // ----- card 3 Recruit -----
    for(const lv of [1,2,3]){ p=setup('robots'); play(3,'recruit',lv); const n0=home().army.brawler||0; nuActionStart(0); ok(`C3 Recruit L${lv}: ${NU_MUSTER[lv]} basic at home`, (home().army.brawler||0)-n0===NU_MUSTER[lv]); }
    // ----- card 3 Fortify -----
    p=setup('dinos'); { const own=[]; let fr=[S.homes[0]]; const seen=new Set(fr); for(let d=0;d<5;d++){ const nx=[]; for(const c of fr) for(const n of nbrs(c)) if(!seen.has(n)&&S.tiles[n].terrain==='plain'){ seen.add(n); nx.push(n); S.tiles[n].owner=0; } fr=nx; }
      play(3,'fortify',0); S.play.fx={ph:'regroup',n:1,done:[],cur:null}; const r0=moveTargets(S.homes[0],0).length;
      play(3,'fortify',1); S.play.fx={ph:'regroup',n:1,done:[],cur:null}; const r1=moveTargets(S.homes[0],0).length;
      play(3,'fortify',2); S.play.fx={ph:'regroup',n:1,done:[],cur:null}; const r2=moveTargets(S.homes[0],0).length;
      ok('C3 Fortify: home castle reach grows (2, 3, all)', r0<r1&&r1<r2, [r0,r1,r2]); }
    // ----- card 3 Move: sneak, volley -----
    p=setup('robots','dinos'); play(3,'move',2); ok('C3 Move L2: sneak attack', atkOpts(0,0,0,1).surprise===1);
    play(3,'move',3); const ao=atkOpts(0,0,0,1); ok('C3 Move L3: volley', ao.volley===1);
    { const fb0=fightBattle({rarch:20},{galli:10},{avg:true}), fb1=fightBattle({rarch:20},{galli:10},{avg:true,volley:1});
      ok('C3 Move L3: a volley helps the shooters', fb1.ev.volley===1&&fb1.aHp>=fb0.aHp, [Math.round(fb0.aHp),Math.round(fb1.aHp)]); }
    // ----- card 4 Harvest -----
    p=setup('dinos'); const tiles=S.tiles.filter(t=>t.owner===0).length; play(4,'harvest',3); g0=p.gold; mm=matOf(0); resolveInstant(0,'harvest',0,0);
    const plain=harvestGold(0,0); ok('C4 Harvest L3: 2 gold a hex and Quarry', p.gold-g0===plain+2*tiles&&matOf(0)-mm===Math.floor(tiles/3), [p.gold-g0,plain,tiles]);
    p=setup('mythical'); const i0=incomeOf(0).total; p.up={[facOf(0).cards[3].id]:[1,0,0]}; const i1=incomeOf(0).total; p.up[facOf(0).cards[3].id]=[2,0,0]; const i2=incomeOf(0).total;
    ok('C4 Harvest (Mythical): castle magic +1, then +3', i1-i0===1&&i2-i0===3, [i0,i1,i2]);
    // ----- card 4 Build -----
    p=setup('dinos'); play(4,'build',3); g0=p.gold; mm=matOf(0); nuActionStart(0); ok('C4 Build L2+L3: +3 materials, +10 gold', matOf(0)-mm===3&&p.gold-g0===10);
    { const t=S.tiles.find(x=>x.owner===-1&&x.terrain==='plain'&&!x.castle&&nbrs(x.id).some(j=>S.tiles[j].terrain==='plain'&&!S.tiles[j].castle&&S.tiles[j].owner===-1)); t.owner=0; t.market=1; const j=nbrs(t.id).find(j=>S.tiles[j].terrain==='plain'&&!S.tiles[j].castle&&S.tiles[j].owner===-1); S.tiles[j].owner=0;
      ok('C4 Build L1: relocate a market', nuMoveB(0,t.id,'market',j)&&S.tiles[j].market===1&&!t.market); }
    // ----- card 4 Advancements -----
    p=setup('dinos'); ok('C4 Adv: no Scouts, no units shown', !nuSee(0)); play(4,'advance',3); ok('C4 Adv L1: Scouts', nuSee(0));
    { const own=home(); ok('C4 Adv L2: Rally Cry', nuBuff(0,own.id)&&buffOn(own)); const foe=S.tiles[S.homes[1]];
      ok('C4 Adv L3: Freeze', nuFreeze(0,foe.id)&&foe.frz===2); S.current=1; beginTurn(); ok('C4 Adv L3: frozen army has no moves', cnt(foe.ready||{})===0&&foe.frz===1); }
    // ----- card 5 -----
    p=setup('dinos'); { const e=S.tiles.find(t=>t.owner===-1&&t.terrain==='plain'&&!t.castle&&nbrs(t.id).some(j=>S.tiles[j].owner===0)); const fr=nbrs(e.id).find(j=>S.tiles[j].owner===0);
      for(const j of nbrs(e.id)) if(S.tiles[j].owner===-1&&S.tiles[j].terrain==='plain'&&!S.tiles[j].castle){ S.tiles[j].owner=1; break; }
      play(5,'fortify',3); const n0=S.tiles.filter(t=>t.owner===0).reduce((s,t)=>s+t.troops,0); const nt=nuFortify(0); const n1=S.tiles.filter(t=>t.owner===0).reduce((s,t)=>s+t.troops,0);
      S.play.fx={ph:'regroup',n:1,done:[],cur:null}; addUnits(S.tiles[fr],'galli',1,true);
      ok('C5 Fortify L1: Outpost target', moveTargets(fr,0).includes(e.id));
      ok('C5 Fortify L3: border hexes get 2 each', n1>n0&&(n1-n0)%2===0, n1-n0); }
    p=setup('dinos'); play(5,'harvest',3); mm=matOf(0); resolveInstant(0,'harvest',0,0); ok('C5 Harvest L3: +10 materials', matOf(0)-mm===10, matOf(0)-mm);
    p=setup('dinos'); { const c=S.tiles.find(t=>t.castle&&t.owner===-1); c.owner=0; const a0=incomeOf(0).total; p.up={[facOf(0).cards[4].id]:[0,0,3]}; ok('C5 Adv L3: +20 gold a captured castle', incomeOf(0).total-a0===20); }
    // ----- the Mythical's cheaper units -----
    p=setup('mythical'); const t=home(); const mg0=magePrice(0), mn0=convPrice(t,'minotaur'), gr0=convPrice(t,'griffin');
    p.up={[facOf(0).cards[1].id]:[3,0,0]}; ok('Mythical: card 2 Build makes Minotaurs, Griffins and Mages 1 cheaper', convPrice(t,'minotaur')===mn0-1&&convPrice(t,'griffin')===gr0-1&&magePrice(0)===mg0-1);
    // ----- texts -----
    ok('Upgrade texts for every faction card', Object.keys(FACTIONS).every(f=>FACTIONS[f].cards.every(c=>c.actions.every(a=>DCARD[c.id]&&DCARD[c.id][a]&&DCARD[c.id][a].length===3))));
    ok('Mythical cards earn upgrades', (()=>{ setup('mythical'); const c=facOf(0).cards[0]; S.players[0].favor={[c.id]:1}; return upgradeDue(0,c.id); })());
    }catch(e){ out.push('ERROR '+e.message+' '+(e.stack||'').split('\n').slice(1,3).join(' | ')); }
    return out; });
  console.log(r.join('\n')); console.log('page errors',errs.length,errs.slice(0,3)); await b.close(); })();
