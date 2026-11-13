// computer-vs-computer games with the Mammals against each faction, both seats. node bal.js page.html games
const {chromium}=require('playwright');
(async()=>{
  const b=await chromium.launch(); const pg=await b.newPage(); const errs=[]; pg.on('pageerror',e=>errs.push(e.message));
  await pg.goto('file://'+process.argv[2]); await pg.waitForTimeout(1000);
  const r=await pg.evaluate((games)=>{ const tally={};
    for(const o of ['dinos','robots','mythical']) for(const seat of [0,1]) for(let g=0;g<games;g++){
      const facs=seat?[o,'mammals']:['mammals',o]; newGame(facs[0],{opp:facs[1],quiet:true}); S.players[0].ai=true; S.players.forEach(p=>p.diff='medium');
      while(!S.over&&S.turn<=45){ const pid=S.current, cid=aiChooseCard(pid); S.play={card:cid,step:0}; for(const ev of aiCardGen(pid,cid)){} if(S.over) break; rotateCards(pid); advanceTurn(); if(S.over) break; beginTurn(); }
      const mi=seat?1:0, t=tally[o]=tally[o]||{w:0,l:0,d:0,turns:0};
      if(!S.over) t.d++; else if(S.winner===mi) t.w++; else t.l++; t.turns+=S.turn; }
    return tally; }, +process.argv[3]);
  console.log(JSON.stringify(r)); console.log('errs',errs.length,errs.slice(0,3)); await b.close(); })();
