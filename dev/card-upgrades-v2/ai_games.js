// Not shipped: computer-vs-computer games with the new card upgrades. node ai_games.js page.html games [max]
// max: every card starts fully upgraded, so every upgrade gets used.
const {chromium}=require('playwright'); const path=require('path');
(async()=>{
  const b=await chromium.launch(); const pg=await b.newPage(); const errs=[]; pg.on('pageerror',e=>errs.push(e.message));
  await pg.goto('file://'+path.resolve(process.argv[2])); await pg.waitForTimeout(1000);
  const r=await pg.evaluate(([games,max])=>{ const tally={}, fails=[]; const F=['dinos','robots','mammals','mythical'];
    for(const a of F) for(const o of F){ if(a===o) continue; for(let g=0;g<games;g++){
      try{
        newGame(a,{opp:o,quiet:true}); S.players[0].ai=true; S.players.forEach(p=>p.diff='hard');
        if(max) S.players.forEach(p=>{ p.up={}; facOf(p.id).cards.forEach(c=>p.up[c.id]=[3,3,3]); });
        while(!S.over&&S.turn<=40){ const pid=S.current, cid=aiChooseCard(pid); S.play={card:cid,step:0}; for(const ev of aiCardGen(pid,cid)){} if(S.over) break; rotateCards(pid); advanceTurn(); if(S.over) break; beginTurn(); }
        const k=a+'-'+o, t=tally[k]=tally[k]||{w:0,l:0,d:0,turns:0,ups:0};
        if(!S.over) t.d++; else if(S.winner===0) t.w++; else t.l++; t.turns+=S.turn;
        t.ups+=S.players.reduce((s,p)=>s+Object.values(p.up||{}).reduce((x,u)=>x+u.reduce((y,v)=>y+v,0),0),0);
      }catch(e){ fails.push(a+'-'+o+': '+e.message+' '+(e.stack||'').split('\n').slice(1,4).join(' | ')); }
    } }
    return {tally,fails:fails.slice(0,8),nf:fails.length}; }, [+process.argv[3], process.argv[4]==='max']);
  console.log(JSON.stringify(r,null,0)); console.log('page errors',errs.length,errs.slice(0,3)); await b.close(); })();
