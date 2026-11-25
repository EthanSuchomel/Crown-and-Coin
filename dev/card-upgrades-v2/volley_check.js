// Not shipped: Volley in the arena. A Robot attack with card 3's Move at level 3 goes to the arena; the defenders are
// hit before anyone moves. node volley_check.js page.html out.png
const {chromium}=require('playwright'); const path=require('path');
(async()=>{
  const b=await chromium.launch(); const pg=await b.newPage({viewport:{width:1400,height:900}}); const errs=[]; pg.on('pageerror',e=>errs.push(e.message));
  await pg.goto('file://'+path.resolve(process.argv[2])); await pg.waitForTimeout(1200);
  const info=await pg.evaluate(()=>{ newGame('robots',{opp:'dinos',quiet:true}); showScreen&&showScreen(null); document.querySelectorAll('.modal').forEach(x=>x.hidden=true);
    S.current=0; const p=S.players[0]; const c=facOf(0).cards[2]; p.up={[c.id]:[0,0,3]}; S.play={card:c.id,step:2,moves:0};
    const h=S.homes[0], to=nbrs(h).find(j=>S.tiles[j].terrain==='plain'&&!S.tiles[j].castle); const A=S.tiles[h], B=S.tiles[to];
    A.army={rarch:16}; A.ready={rarch:16}; syncT(A); B.owner=1; B.army={galli:6,mega:2}; B.ready={}; syncT(B); render();
    humanAttack(h,to,{rarch:16},curLvl()); return {fight:S.fight&&S.fight.mods}; });
  console.log(JSON.stringify(info));
  await pg.waitForTimeout(800); await pg.screenshot({path:process.argv[3].replace('.png','_notice.png')}); console.log(await pg.evaluate(()=>{ const b=document.querySelector('#modal button.primary'); const t=document.querySelector('#modal')&&document.querySelector('#modal').innerText.slice(0,400); if(b) b.click(); return t; }));
  for(let k=0;k<20;k++){ await pg.waitForTimeout(1000); const n=pg.frames().length; const vis=await pg.evaluate(()=>{ const f=document.querySelector("iframe"); return f?getComputedStyle(f.closest("[id]")||f).display+" "+(f.offsetWidth):"none"; }); if(k%5===0) console.log(k,n,vis); if(n>1){ const fr=pg.frames().find(f=>f!==pg.mainFrame()); const c=await fr.evaluate(()=>typeof clock!=="undefined"?clock:-1).catch(()=>-1); if(c>0.3) break; } }
  const fr=pg.frames().find(f=>f!==pg.mainFrame());
  const st=fr?await fr.evaluate(()=>({volley:VOLLEY,done:VOLLEY_DONE,clock,hurt:F.filter(f=>f.team!==VOLLEY).map(f=>Math.round(f.hp*10)/10+"/"+f.T.hp+(f.dead?"x":"")).join(" "),shooters:F.filter(f=>f.team===VOLLEY).length,foes:F.filter(f=>f.team!==VOLLEY).length})).catch(e=>e.message):'no frame';
  console.log(JSON.stringify(st)); console.log(await pg.evaluate(()=>JSON.stringify({fight:!!S.fight,log:S.log.slice(0,4).map(l=>l.t||l.text||l),ar:{ready:AR.ready,loads:AR.loads,errs:AR.errs}})));
  await pg.screenshot({path:process.argv[3]});
  console.log('page errors',errs.length,errs.slice(0,3)); await b.close(); })();
