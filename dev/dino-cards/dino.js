const {chromium}=require('playwright');
(async()=>{
  const b=await chromium.launch(); const pg=await b.newPage({viewport:{width:1280,height:800}});
  const errs=[]; pg.on('pageerror',e=>errs.push('PAGEERR '+e.message+' '+(e.stack||'').split('\n').slice(0,3).join('|')));
  await pg.goto('file://'+__dirname+'/test.html'); await pg.waitForTimeout(1200);
  // 1) computer games with every Dinosaur card at level 3, and at mixed levels
  const r=await pg.evaluate(()=>{ const out=[];
    for(const lv of [3,1,2]) for(const o of ['robots','mammals','mythical']) for(const seat of [0,1]){
      try{ const me=seat===0?'dinos':o, op=seat===0?o:'dinos';
        newGame(me,{opp:op,quiet:true,level:'hard'}); S.players[0].ai=true; S.players[0].diff='hard';
        const d=S.players.find(p=>p.faction==='dinos'); d.up={}; facOf(d.id).cards.forEach(c=>d.up[c.id]=[lv,lv,lv]);
        while(!S.over&&S.turn<=25){ const pid=S.current; const cid=aiChooseCard(pid); S.play={card:cid,step:0}; for(const ev of aiCardGen(pid,cid)){} if(S.over) break; rotateCards(pid); advanceTurn(); if(S.over) break; beginTurn(); }
        out.push({lv,o,seat,turn:S.turn,over:S.over,armor:!!d.armor,fnest:d.fnest|0,mat:d.mat|0,units:unitTotal(d.id),opp:unitTotal(1-d.id)});
      }catch(e){ out.push({lv,o,seat,err:String(e.stack).slice(0,500)}); } }
    return out; });
  r.forEach(x=>console.log(JSON.stringify(x)));
  console.log('ERRS',errs.slice(0,5));
  await b.close();
})();
