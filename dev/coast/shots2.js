// Not shipped: coast on the 3-player board and an iPad-sized screen, with timing. node shots2.js page.html outdir/
const {chromium,devices}=require('playwright'); const path=require('path');
(async()=>{
  const b=await chromium.launch(); const ctx=await b.newContext({...devices['iPad (gen 7) landscape']}); const pg=await ctx.newPage(); const errs=[]; pg.on('pageerror',e=>errs.push(e.message));
  await pg.goto('file://'+path.resolve(process.argv[2])); await pg.waitForTimeout(1200); const O=process.argv[3];
  const t=await pg.evaluate(()=>{ showScreen(null); newGame('mythical',{np:3}); document.querySelectorAll('.modal').forEach(x=>x.hidden=true); const t0=performance.now(); _coastKey=''; coastArt(); const t1=performance.now(); render(); return [t1-t0, typeof MAPS!=='undefined'?Object.keys(MAPS).length:-1]; });
  console.log('coast ms, maps',t); await pg.waitForTimeout(500); await pg.screenshot({path:O+'three_ipad.png'});
  console.log('page errors',errs.length,errs.slice(0,3)); await b.close(); })();
