const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage();const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto('file://'+process.cwd()+'/test.html');await p.waitForTimeout(1500);
const r=await p.evaluate(()=>{ const out=[];
 newGame('mythical',{opp:'robots',quiet:true,level:'medium'}); const me=S.players[0]; me.gold=100;
 out.push('start ok? '+mageReqOk(0,0)+' up: '+mythUpMages(0)+' mlv '+mlvOf(0));
 const own=S.tiles.filter(t=>t.owner===0&&!t.castle); const free=S.tiles.filter(t=>t.owner<0&&!t.castle&&t.terrain==='plain');
 const t1=free[0]; t1.owner=0; t1.tree=1; out.push('1 tree: '+mythUpMages(0)+' mlv '+mlvOf(0));
 free[1].owner=0; free[1].tree=1; free[2].owner=0; free[2].tree=1; out.push('3 trees, 0 castles: '+mythUpMages(0)+' mlv '+mlvOf(0));
 const c=S.tiles.find(t=>t.castle&&t.id!==S.homes[0]&&t.id!==S.homes[1]); c.owner=0; out.push('captured '+capCastlesOf(0)+': '+mythUpMages(0)+' mlv '+mlvOf(0));
 c.owner=-1; out.push('castle lost, still level '+mlvOf(0)+'; level 3 ok? '+mageReqOk(0,2));
 out.push(mageReqAll());
 return out.join('\n'); });
console.log(r);
// a few computer games with the Mythical
const r2=await p.evaluate(async()=>{ const lv=[]; for(const o of ['robots','dinos','mammals']){ newGame('mythical',{opp:o,quiet:true,level:'hard'}); S.players[0].ai=true; S.players[0].diff='hard';
  while(!S.over&&S.turn<=50){ const pid=S.current; const cid=aiChooseCard(pid); S.play={card:cid,step:0}; for(const ev of aiCardGen(pid,cid)){} if(S.over) break; rotateCards(pid); advanceTurn(); if(S.over) break; beginTurn(); }
  lv.push(o+': turn '+S.turn+' mage level '+mlvOf(0)+' trees '+treesOf(0)+' castles '+capCastlesOf(0)+' over '+S.over); } return lv.join('\n'); }).catch(e=>'ERR '+e.message);
console.log(r2); console.log('errors:',errs.length?errs.slice(0,3):'none'); await b.close();})();
