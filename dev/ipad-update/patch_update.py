"""iPad app updates (2026-11-13): Ethan's home-screen app kept showing an old version.
- sw.js: install downloads fresh copies (cache:'reload'), not the browser's 10-minute HTTP cache.
- index.html: checks for a new version on every open and whenever the app comes back to the front; when a new
  version takes over it reloads at once if you're on the title screen (or just opened), otherwise it shows an
  'Update now' bar; the title screen shows the version. Usage: python3 patch_update.py index.html sw.js"""
import sys
P, W = sys.argv[1], sys.argv[2]
s = open(P).read()
old = "if('serviceWorker' in navigator && (location.protocol==='https:'||location.hostname==='localhost')) addEventListener('load',()=>navigator.serviceWorker.register('sw.js').catch(()=>{}));"
assert s.count(old) == 1
s = s.replace(old, r"""if('serviceWorker' in navigator && (location.protocol==='https:'||location.hostname==='localhost')){
  const t0=Date.now(), had=!!navigator.serviceWorker.controller;
  const onTitle=()=>{ const t=document.getElementById('scrTitle'); return t&&!t.hidden; };
  // a new version took over: reload now if nothing's being played, otherwise offer it
  navigator.serviceWorker.addEventListener('controllerchange',()=>{
    if(!had) return;   // the very first install: this page is already the newest
    if(onTitle()||Date.now()-t0<15000){ location.reload(); return; }
    if(document.getElementById('updBar')) return;
    const b=document.createElement('div'); b.id='updBar';
    b.style.cssText='position:fixed;left:50%;top:max(.6em,env(safe-area-inset-top,0px));transform:translateX(-50%);z-index:99;display:flex;gap:.6em;align-items:center;background:#16241a;color:#ece4cf;border:2px solid #efc15a;box-shadow:0 0 0 2px #060907;border-radius:3px;padding:.4em .5em .4em .8em;font:600 15px Oswald,sans-serif';
    b.innerHTML='A new version of the game is ready <button class="primary" style="padding:.3em .8em">Update now</button><button class="ghost" style="padding:.3em .6em" aria-label="Later">Later</button>';
    b.children[0].onclick=()=>location.reload(); b.children[1].onclick=()=>b.remove();
    document.body.appendChild(b);
  });
  addEventListener('load',async()=>{
    try{
      const reg=await navigator.serviceWorker.register('sw.js',{updateViaCache:'none'});
      reg.update().catch(()=>{});
      document.addEventListener('visibilitychange',()=>{ if(document.visibilityState==='visible') reg.update().catch(()=>{}); });
    }catch(_){}
    // the version on the title screen, so you can tell which one you have
    try{ const k=(await caches.keys()).find(x=>x.startsWith('cc-')); const v=document.getElementById('tsVer'); if(k&&v) v.textContent='Version '+k.slice(3,11); }catch(_){}
  });
}""")
old = '<button class="ghost ts-full" data-scr="full" data-full aria-pressed="false">⛶ <span class="fl">Full screen</span></button></div>'
assert s.count(old) == 1
s = s.replace(old, old + '<small id="tsVer" class="ts-ver" aria-live="polite"></small>')
old = ".ts-full{font-size:.85em;margin-top:.2em}"
assert s.count(old) == 1
s = s.replace(old, old + "\n.ts-ver{font-size:.75em;color:var(--lichen);opacity:.75;min-height:1em}")
open(P, 'w').write(s)

w = open(W).read()
old = "const c=await caches.open(V); await c.addAll(FILES);"
assert w.count(old) == 1
w = w.replace(old, "const c=await caches.open(V); await c.addAll(FILES.map(f=>new Request(f,{cache:'reload'})));   // fresh copies, not the browser's saved ones")
open(W, 'w').write(w)
print('ok')
