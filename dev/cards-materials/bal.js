const {chromium}=require('playwright');
(async()=>{
  const file=process.argv[2], reps=+(process.argv[3]||4), maxT=+(process.argv[4]||40), lvl=process.argv[5]||'medium';
  const b=await chromium.launch(); const pg=await b.newPage({viewport:{width:1280,height:800}});
  const errs=[]; pg.on('pageerror',e=>errs.push('PAGEERR '+e.message));
  await pg.goto('file://'+__dirname+'/'+file); await pg.waitForTimeout(1200);
  const res=await pg.evaluate(async ({reps,maxT,lvl})=>{
    const F=['dinos','robots','mammals','mythical'], W={}, G={}, T=[], E=[];
    F.forEach(f=>{W[f]=0;G[f]=0;});
    for(let r=0;r<reps;r++) for(const a of F) for(const o of F){ if(a===o) continue;
      try{
        newGame(a,{opp:o,quiet:true,level:lvl}); S.players[0].ai=true; S.players[0].diff=lvl;
        while(!S.over&&S.turn<=maxT){ const pid=S.current; const cid=aiChooseCard(pid); S.play={card:cid,step:0}; for(const ev of aiCardGen(pid,cid)){} if(S.over) break; rotateCards(pid); advanceTurn(); if(S.over) break; beginTurn(); }
        let w=null; if(S.over) w=S.winner!=null?S.winner:(S.over==='win'?0:1);
        else { const sc=S.players.map(p=>evalFor(p.id)); w=sc[0]>sc[1]?0:1; }
        G[a]++; G[o]++; W[[a,o][w]]++; T.push(S.turn);
      }catch(e){ E.push(String(e&&e.stack||e).slice(0,300)); }
    }
    return {W,G,avgT:T.reduce((x,y)=>x+y,0)/T.length,E:E.slice(0,3)};
  },{reps,maxT,lvl});
  console.log(file,JSON.stringify(res),'pct',Object.keys(res.W).map(f=>f+' '+Math.round(100*res.W[f]/res.G[f])).join(', '));
  console.log('ERRS',errs.slice(0,5));
  await b.close();
})();
