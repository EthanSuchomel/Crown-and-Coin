// Checks for the new Mammal castle and the board's Mammal numbers. node test.js /path/to/index.html outdir
const {chromium}=require('playwright');
(async()=>{
  const page=process.argv[2], out=process.argv[3];
  const b=await chromium.launch(); const pg=await b.newPage({viewport:{width:1280,height:800},deviceScaleFactor:1});
  const errs=[]; pg.on('pageerror',e=>errs.push('PAGEERR '+e.message)); pg.on('console',m=>{ if(m.type()==='error'&&!/fonts|ERR_|net::/.test(m.text())) errs.push('CONSOLE '+m.text().slice(0,200)); });
  await pg.goto('file://'+page); await pg.waitForTimeout(1500);
  await pg.screenshot({path:out+'/1_title.png'});
  await pg.click('[data-scr="start"]'); await pg.waitForTimeout(400);
  const opts=await pg.$$('#fsChoices .fs-opt'); let picked=false;
  for(const o of opts){ if(/Mammal/.test(await o.innerText())){ await o.click(); picked=true; break; } }
  await pg.waitForTimeout(400); await pg.screenshot({path:out+'/2_faction.png'});
  await pg.click('[data-scr="go"]'); await pg.waitForTimeout(1200);
  await pg.screenshot({path:out+'/3_board.png'});
  // zoom on the Mammal home castle
  const box=await pg.evaluate(()=>{ const h=S.homes[0], svg=document.getElementById('map'), u=[...svg.querySelectorAll('use')].find(e=>e.getAttribute('href')==='#ca-mammals');
    if(!u) return null; const r=u.getBoundingClientRect(); return {x:r.x,y:r.y,w:r.width,h:r.height,fac:S.players[0].faction}; });
  if(box){ await pg.screenshot({path:out+'/4_castle_zoom.png',clip:{x:Math.max(0,box.x-60),y:Math.max(0,box.y-50),width:box.w+120,height:box.h+100}}); }
  // rules checks
  const res=await pg.evaluate(()=>{
    const r={picked:S.players[0].faction, castleBox:null};
    r.porc=UNIT_STATS.porc.hp+'hp thorns '+UNIT_STATS.porc.thorns; r.rhino=UNIT_STATS.rhino.dmg;
    r.barracks=UNITS.mammals.barracks.map(x=>x[0]).join(','); r.lv=barracksLv(0);
    const avg=(a,d,n)=>{ let w=0,aL=0,dL=0; for(let i=0;i<n;i++){ const f=fightBattle(a,d,{}); if(f.won) w++; aL+=cnt(f.attLost); dL+=cnt(f.defLost);} return {win:w/n,attLost:aL/n,defLost:dL/n}; };
    // quills on and off: 10 Gorillas attack 10 Porcupines
    r.apeVsPorc=avg({ape:10},{porc:10},400);
    const th=UNIT_STATS.porc.thorns; UNIT_STATS.porc.thorns=0; r.apeVsPorcNoQuills=avg({ape:10},{porc:10},400); UNIT_STATS.porc.thorns=th;
    // shooters aren't pricked: 10 Archers... (Dinosaur Dilophosaurus) vs 10 Porcupines
    r.diloVsPorc=avg({dilo:10},{porc:10},300); UNIT_STATS.porc.thorns=0; r.diloVsPorcNoQuills=avg({dilo:10},{porc:10},300); UNIT_STATS.porc.thorns=th;
    // a Rhino charge through Porcupines
    const f=fightBattle({rhino:3},{porc:8},{avg:true}); r.rhinoCharge={won:f.won,attLost:f.attLost,defLost:f.defLost,aHp:f.aHp};
    return r; });
  console.log(JSON.stringify(res,null,1));
  // computer-vs-computer games with the Mammals on each side
  const games=await pg.evaluate(()=>{
    const out=[]; const pairs=[['mammals','dinos'],['dinos','mammals'],['mammals','robots'],['robots','mammals'],['mammals','mythical'],['mythical','mammals']];
    for(const [a,o] of pairs){
      try{
        newGame(a,{opp:o,quiet:true,level:'hard'}); S.players[0].ai=true; S.players[0].diff='hard';
        let kanga=0, quillsHit=0;
        while(!S.over&&S.turn<=40){
          const pid=S.current, cid=aiChooseCard(pid); S.play={card:cid,step:0};
          for(const ev of aiCardGen(pid,cid)){}
          S.tiles.forEach(t=>{ if(t.army&&t.army.kanga) kanga++; });
          if(S.over) break; rotateCards(pid); advanceTurn(); if(S.over) break; beginTurn();
        }
        out.push({a,o,winner:S.over?(S.winner!=null?S.winner:S.over):null,turn:S.turn,kanga,units:S.players.map(p=>unitTotal(p.id))});
      }catch(e){ out.push({a,o,err:String(e&&e.stack||e).slice(0,500)}); }
    }
    return out; });
  for(const g of games) console.log(JSON.stringify(g));
  console.log('ERRS',JSON.stringify(errs.slice(0,10)));
  await b.close();
})();
