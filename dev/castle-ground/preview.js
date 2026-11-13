// Screenshots of every castle hex with its ground. node preview.js page.html outdir
const {chromium}=require('playwright');
(async()=>{
  const page=process.argv[2], out=process.argv[3];
  const b=await chromium.launch(); const pg=await b.newPage({viewport:{width:1280,height:800},deviceScaleFactor:2});
  const errs=[]; pg.on('pageerror',e=>errs.push(e.message));
  await pg.goto('file://'+page); await pg.waitForTimeout(1200);
  await pg.click('[data-scr="start"]'); await pg.waitForTimeout(300); await pg.click('[data-scr="go"]'); await pg.waitForTimeout(800);
  const shots=[];
  for(const [fid,opps] of [['mammals',['robots','dinos']],['mythical',['robots','dinos']]]){
    await pg.evaluate(([fid,opps])=>{ newGame(fid,{np:3,opps,quiet:true}); render(); },[fid,opps]); await pg.waitForTimeout(700);
    const n=shots.length; await pg.screenshot({path:`${out}/board_${n}.png`}); shots.push(`board_${n}.png`);
    const boxes=await pg.evaluate(()=>S.homes.map((h,pi)=>{ const g=document.querySelector(`#cells g[data-id="${h}"]`); const r=g.getBoundingClientRect(); return {f:S.players[pi].faction,x:r.x,y:r.y,w:r.width,h:r.height}; }));
    for(const bx of boxes){ await pg.screenshot({path:`${out}/hex_${bx.f}.png`,clip:{x:bx.x-bx.w*.6,y:bx.y-bx.h*.45,width:bx.w*2.2,height:bx.h*1.9}}); }
    // a neutral castle too
    const nb=await pg.evaluate(()=>{ const i=S.tiles.findIndex(t=>t.castle&&!S.homes.includes(t.id)); const r=document.querySelector(`#cells g[data-id="${i}"]`).getBoundingClientRect(); return {x:r.x,y:r.y,w:r.width,h:r.height}; });
    await pg.screenshot({path:`${out}/hex_neutral.png`,clip:{x:nb.x-nb.w*.6,y:nb.y-nb.h*.45,width:nb.w*2.2,height:nb.h*1.9}});
  }
  console.log('errors',JSON.stringify(errs));
  await b.close();
})();
