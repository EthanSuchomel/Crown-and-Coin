// Crown & Coin offline worker. Version 48f53f33443b
const V='cc-48f53f33443b';
const FILES=["./", "index.html", "arena.html", "manifest.webmanifest", "icon-180.png", "icon-192.png", "icon-512.png", "myth/minion_blue.png", "myth/minion_red.png", "myth/mage_blue.png", "myth/mage_red.png", "myth/minotaur_blue.png", "myth/minotaur_red.png", "myth/griffin_blue.png", "myth/griffin_red.png", "myth/dragon_blue.png", "myth/dragon_red.png", "myth/griffin_hover_blue.png", "myth/griffin_hover_red.png", "myth/griffin_soar_blue.png", "myth/griffin_soar_red.png", "myth/minotaur_swing_blue.png", "myth/minotaur_swing_red.png", "myth/dragon_stand_blue.png", "myth/dragon_stand_red.png", "myth/griffin_stand_blue.png", "myth/griffin_stand_red.png", "myth/dragon_hover_blue.png", "myth/dragon_hover_red.png", "myth/dragon_soar_blue.png", "myth/dragon_soar_red.png"];
const EXTRA=["https://fonts.googleapis.com/css2?family=Alegreya:wght@800&family=Alegreya+Sans:wght@400;500;700&display=swap", "https://fonts.googleapis.com/css2?family=Oswald:wght@400;500;600;700&display=swap", "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js"];   // fonts and the 3D trebuchet: kept too when there's internet, never required
self.addEventListener('install',e=>{ self.skipWaiting(); e.waitUntil((async()=>{
  const c=await caches.open(V); await c.addAll(FILES);
  for(const u of EXTRA){ try{ const r=await fetch(u,{mode:'cors'}); if(!r.ok) continue; await c.put(u,r.clone());
      if(u.includes('fonts.googleapis')){ const css=await r.text();
        for(const m of css.matchAll(/url\((https:[^)]+)\)/g)){ try{ const f=await fetch(m[1],{mode:'cors'}); if(f.ok) await c.put(m[1],f); }catch(_){} } }
    }catch(_){} }
})()); });
self.addEventListener('activate',e=>{ e.waitUntil((async()=>{ for(const k of await caches.keys()) if(k!==V) await caches.delete(k); await self.clients.claim(); })()); });
self.addEventListener('fetch',e=>{
  const q=e.request; if(q.method!=='GET') return;
  const u=new URL(q.url);
  e.respondWith((async()=>{
    const c=await caches.open(V);
    const hit=await c.match(q,{ignoreSearch:u.origin===location.origin}) || (q.mode==='navigate'&&await c.match('index.html'));
    if(hit) return hit;
    try{ const r=await fetch(q); if(r.ok&&(u.hostname.endsWith('gstatic.com')||u.hostname.endsWith('googleapis.com'))) c.put(q,r.clone()); return r; }
    catch(err){ return Response.error(); }
  })());
});
