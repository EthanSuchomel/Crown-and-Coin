const {chromium}=require('playwright');
(async()=>{
  const b=await chromium.launch(); const pg=await b.newPage({viewport:{width:1280,height:800}});
  const errs=[]; pg.on('pageerror',e=>errs.push('PAGEERR '+e.message));
  await pg.goto('file://'+__dirname+'/test.html'); await pg.waitForTimeout(1200);
  const pairs=JSON.parse(process.argv[2]), maxT=+(process.argv[3]||40), lvl=process.argv[4]||'hard';
  const res=await pg.evaluate(async ({pairs,maxT,lvl})=>{
    const out=[]; let REAL=false, C=null;
    const oBuy=buyMat; buyMat=function(pid,n){ const r=oBuy(pid,n); if(REAL&&C) C.mat[pid]+=r; return r; };
    const oPick=aiDoPick; aiDoPick=function(pid,k,later){ if(REAL&&C) C.pick[pid][k]=(C.pick[pid][k]||0)+1; return oPick(pid,k,later); };
    const oReg=aiRegroupGen; aiRegroupGen=function*(pid){ for(const e of oReg(pid)){ if(REAL&&C) C.reg[pid]++; yield e; } };
    for(const [a,o] of pairs){
      const t0=performance.now();
      try{
      newGame(a,{opp:o,quiet:true,level:lvl}); S.players[0].ai=true; S.players[0].diff=lvl;
      C={mat:[0,0],pick:[{},{}],reg:[0,0],fort:[0,0],cards:[0,0],bld:[{},{}]};
      const oB=S; 
      while(!S.over&&S.turn<=maxT){
        const pid=S.current;
        REAL=false; const cid=aiChooseCard(pid), card=cardOf(pid,cid); REAL=true;
        S.play={card:cid,step:0}; C.cards[pid]++; if(card.actions.includes('fortify')) C.fort[pid]++;
        const before=S.tiles.map(t=>[t.market|0,t.fort|0,t.barracks|0,t.bk|0]);
        for(const ev of aiCardGen(pid,cid)){}
        S.tiles.forEach((t,i)=>{ const bb=before[i]; if(t.owner!==pid) return; ['market','fort','barracks','bk'].forEach((k,j)=>{ const d=(t[k]|0)-bb[j]; if(d>0) C.bld[pid][k]=(C.bld[pid][k]||0)+d; }); });
        REAL=false;
        if(S.over) break;
        rotateCards(pid); advanceTurn(); if(S.over) break; beginTurn();
      }
      out.push({a,o,win:S.over?(S.winner!=null?S.winner:(S.over==='win'?0:1)):null,why:S.overWhy,turn:S.turn,ms:Math.round(performance.now()-t0),
        mats:S.players.map(p=>p.mat|0),gold:S.players.map(p=>p.gold),mk:S.players.map(p=>marketsOf(p.id)),units:S.players.map(p=>unitTotal(p.id)),
        hexes:S.players.map(p=>S.tiles.filter(t=>t.owner===p.id).length),...C});
      }catch(e){ out.push({a,o,err:String(e&&e.stack||e).slice(0,600)}); }
    }
    return out;
  },{pairs,maxT,lvl});
  for(const r of res) console.log(JSON.stringify(r));
  console.log('ERRS',errs.slice(0,10));
  await b.close();
})();
