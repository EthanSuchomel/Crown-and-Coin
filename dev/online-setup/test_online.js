// Not shipped: two browsers play online against a stand-in for the page's shared store; screenshots to OUT.
// node test_online.js index.html OUT/
const { chromium } = require('playwright');
const path = require('path');
const [, , FILE, OUT] = process.argv;
const store = {};
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1280, height: 800 } });
  await ctx.exposeFunction('__db', (op, p, d) => {
    if (op === 'get') return store[p] === undefined ? null : store[p];
    if (op === 'set') { store[p] = JSON.parse(JSON.stringify(d)); return true; }
    if (op === 'update') { store[p] = Object.assign({}, store[p] || {}, JSON.parse(JSON.stringify(d))); return true; }
    if (op === 'delete') { delete store[p]; return true; }
    if (op === 'query') return Object.keys(store).filter(k => k.startsWith(p + '/') && store[k][d.f] === d.v).map(k => ({ id: k.slice(p.length + 1), data: store[k] }));
  });
  const mock = uid => `(() => {
    window.__uid=${JSON.stringify(uid)};
    const ref=p=>({ get:async()=>{const r=await __db('get',p); return {exists:r!==null,data:()=>r,metadata:{}};},
      set:d=>__db('set',p,d), update:d=>__db('update',p,d), delete:()=>__db('delete',p), acquire:async()=>({acquired:true}),
      onSnapshot(cb){ let last='~'; const t=setInterval(async()=>{ const r=await __db('get',p), j=JSON.stringify(r); if(j!==last){ last=j; cb({exists:r!==null,data:()=>r,metadata:{}}); } },250); return ()=>clearInterval(t); } });
    const DB={ doc:ref, collection:n=>({ doc:id=>ref(n+'/'+id), where:(f,o,v)=>({ onSnapshot(cb){ let last=''; const t=setInterval(async()=>{ const r=await __db('query',n,{f,v}), j=JSON.stringify(r); if(j!==last){ last=j; cb({docs:r.map(x=>({id:x.id,data:()=>x.data}))}); } },300); return ()=>clearInterval(t); } }) }) };
    window.claude={ use: async n => n==='db'?DB:n==='user'?{id:async()=>window.__uid,can:async()=>true,isOwner:()=>true,canEdit:()=>true}:null };
  })();`;
  const url = 'file://' + path.resolve(FILE);
  const A = await ctx.newPage(); await A.addInitScript(mock('userA'));
  const errs = []; A.on('pageerror', e => errs.push('A: ' + e.message));
  await A.goto(url); await A.waitForTimeout(1500);
  const shot = async (pg, n) => { await pg.waitForTimeout(500); await pg.screenshot({ path: OUT + n + '.png' }); console.log('shot', n); };
  await A.click('button[data-scr="online"]'); await A.waitForTimeout(1200);
  await shot(A, 'ol_menu');
  await A.click('button[data-ol="setup"]'); await A.waitForTimeout(500);
  await A.click('button[data-fs="mammals"]');
  await shot(A, 'ol_setup_0');
  await A.click('button[data-fsx="next"]');
  await shot(A, 'ol_setup_1');
  await A.click('button[data-np="3"]');
  await A.click('button[data-okind="1:cpu"]');
  await shot(A, 'ol_setup_1_three');
  await A.click('button[data-np="2"]');
  await A.click('button[data-fsx="next"]');
  await A.click('button[data-map="arena-2p"]');
  await shot(A, 'ol_setup_2');
  await A.click('button[data-fsx="create"]'); await A.waitForTimeout(2500);
  await shot(A, 'ol_wait');
  const code = Object.keys(store)[0].split('/')[1];
  console.log('code', code, 'map in state', JSON.parse(store['games/' + code].state).map);
  const B = await ctx.newPage(); await B.addInitScript(mock('userB'));
  B.on('pageerror', e => errs.push('B: ' + e.message));
  await B.goto(url); await B.waitForTimeout(1500);
  await B.click('button[data-scr="online"]'); await B.waitForTimeout(1200);
  await B.fill('#olCode', code); await B.click('#olJoin button[type="submit"]');
  await B.waitForTimeout(3000);
  await shot(B, 'ol_guest_game');
  await A.waitForTimeout(2000);
  await shot(A, 'ol_host_game');
  console.log('guest map', await B.evaluate(() => [S.map, VOID.size, S.players.map(p => p.faction).join(',')]));
  console.log('host map', await A.evaluate(() => [S && S.map, VOID.size]));
  // local setup still has its own picks
  console.log('local fsOnline', await A.evaluate(() => fsOnline));
  console.log(errs.length ? errs.join('\n') : 'no page errors');
  await b.close();
})();
