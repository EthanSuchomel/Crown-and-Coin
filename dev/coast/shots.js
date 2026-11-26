// Not shipped: screenshots of the coast. node shots.js page.html outdir/
const {chromium}=require('playwright'); const path=require('path');
(async()=>{
  const b=await chromium.launch(); const pg=await b.newPage({viewport:{width:1400,height:900}}); const errs=[]; pg.on('pageerror',e=>errs.push(e.message));
  await pg.goto('file://'+path.resolve(process.argv[2])); await pg.waitForTimeout(1200); const O=process.argv[3];
  const t=await pg.evaluate(()=>{ showScreen(null); const t0=performance.now(); newGame('dinos',{opp:'robots'}); const t1=performance.now(); document.querySelectorAll('.modal').forEach(x=>x.hidden=true); render(); return t1-t0; });
  console.log('newGame ms',t.toFixed(0)); await pg.waitForTimeout(500); await pg.screenshot({path:O+'two.png'});
  console.log('page errors',errs.length,errs.slice(0,3)); await b.close(); })();
