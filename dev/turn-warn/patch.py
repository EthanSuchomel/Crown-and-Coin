"""Ethan, 2026-11-24:
- "There also needs to be an indicator at the beginning of each turn that there is someone who is about to win."
  At the start of every turn a banner drops over the map for a few seconds (tap it to close) when a side is about to
  win: it holds enough castles and the countdown is running; it's one castle short of that; or an enemy army stands
  next to a home castle (taking it wins / knocks that side out).
- "At the beginning of the game there needs to be a screen that simply goes over what your current faction is best at."
  Your first turn opens a short briefing for your faction: what it's best at, what it lacks, and how to play it.
Usage: python3 patch.py index.html"""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    c = s.count(a); assert c == n, (c, a[:120]); s = s.replace(a, b)
rep("""function startTurn(){
  beginTurn();""", """// ---- about to win: a banner at the start of every turn (Ethan, 2026-11-24)
function winWarnings(){
  if(!S||S.over) return [];
  const out=[], need=winCastles(), nm=pid=>pid===0?'You':`The ${S.players[pid].name}`, n3=S.players.length>2;
  if(S.siege){ const L=S.siege.left, h=S.siege.pid;
    out.push(h===0?{cls:'mine',t:`You're about to win!`,d:`You hold ${need} castles. Keep them through ${L} more ${n3?'rival':'enemy'} turn${L===1?'':'s'}.`}
      :{cls:'theirs',t:`The ${S.players[h].name} are about to win!`,d:`They hold ${need} castles. ${h===S.current?'':`${n3?'Their rivals have':'You have'} ${L} turn${L===1?'':'s'} to take one back.`}`}); }
  else if(need) S.players.forEach(q=>{ if(!q.out&&winCount(q.id)===need-1) out.push(q.id===0?{cls:'mine',t:'One castle from winning',d:`You hold ${need-1} of ${need} castles. Take one more and hold them.`}
      :{cls:'theirs',t:`The ${q.name} are one castle from winning`,d:`They hold ${need-1} of ${need} castles.`}); });
  S.players.forEach(q=>{ if(q.out) return; const h=S.tiles[S.homes[q.id]]; if(!h||h.owner!==q.id) return;
    const foes=nbrs(h.id).map(j=>S.tiles[j]).filter(t=>t.owner>=0&&t.owner!==q.id&&!S.players[t.owner].out&&t.troops>0);
    if(foes.length){ const f=foes[0].owner;
      out.push(q.id===0?{cls:'theirs',t:'Your home castle is under threat!',d:`Troops from the ${S.players[f].name} are next to it. If they take it, ${n3?"you're out":'they win'}.`}
        :{cls:'mine',t:`The ${q.name}' home castle is in reach`,d:`${f===0?'Your troops are':'Troops from the '+S.players[f].name+' are'} next to it. Take it to ${n3?'knock them out':'win'}.`}); } });
  return out;
}
let _warnT=0;
function showWinWarn(){
  const w=winWarnings(), el=$('#turnwarn'); if(!el) return;
  clearTimeout(_warnT);
  if(!w.length){ el.hidden=true; return; }
  el.innerHTML=w.slice(0,3).map(x=>`<div class="tw ${x.cls}"><b>${x.cls==='theirs'?'⚠ ':'♛ '}${x.t}</b><span>${x.d}</span></div>`).join('');
  el.hidden=false; el.classList.remove('out'); void el.offsetWidth; el.classList.add('in');
  _warnT=setTimeout(()=>{ el.classList.add('out'); _warnT=setTimeout(()=>{ el.hidden=true; },600); },5500);
}
// ---- your faction, at the start of the game (Ethan, 2026-11-24)
const FAC_BRIEF={
  dinos:{best:['The biggest, toughest units: Triceratops, Stegosaurus and Megaraptors win straight-up fights','The Volcano at your home castle rains lava on enemy armies','Nesting grounds and Alamosaurus guards hold the land you take'],
    lack:'No forts or trebuchets: you break castles with brute force.',
    plan:'Build nesting grounds, grow a herd of big units, then smash through.'},
  robots:{best:['Economy: stack markets into resource hexes for more gold and materials','Factories: turn a market into a barracks, then a fortress, right where you need it','Lasers, Archers and Longbows hit hard from range, and trebuchets break walls'],
    lack:'Each hex is one building: a resource hex or a factory, never both.',
    plan:'Build markets early, make a few into factories near the front, then push with ranged units.'},
  mammals:{best:['Numbers and speed: cheap units that spread across the map fast','Rhinos charge, Porcupines prick every attacker with their quills','The Watering Hole and dens keep your army growing'],
    lack:'Single units are weaker than the Dinosaurs\\' giants.',
    plan:'Claim land quickly, build dens, and overwhelm your enemy with a big army.'},
  mythical:{best:['Magic: Mages, Life Trees and magic domes','Minions become Minotaurs, Griffins and Dragons where a Mage stands','Flyers: only flying units can attack your Floating Castle'],
    lack:'No forts, markets, coins or trebuchets: everything runs on magic.',
    plan:'Plant Life Trees, level up your Mages, then turn Minions into Dragons and Griffins.'}
};
function showBriefing(){
  const f=S.players[0].faction, F=FACTIONS[f], b=FAC_BRIEF[f]; if(!b) return;
  openInfo(`You play the ${F.name}`,`<div class="brief"><img src="${ART['castle_'+f].uri}" alt=""><div><p class="bf-h">Best at</p><ul>${b.best.map(x=>`<li>${x}</li>`).join('')}</ul>
    <p class="bf-h">Watch out</p><p>${b.lack}</p><p class="bf-h">How to play them</p><p>${b.plan}</p></div></div>`,[{label:'Let\\'s go',primary:true}]);
}
function startTurn(){
  beginTurn();""")
rep("""  render();
  if(cur().ai&&(!NET||(cur().cpu&&S.runner===0))) runAI();
}
function rotateCards(pid){""", """  render();
  if(!S.over&&!cur().ai&&!S.players[0].briefed&&!S.announce){ S.players[0].briefed=true; setTimeout(showBriefing,250); }
  else showWinWarn();
  if(cur().ai&&(!NET||(cur().cpu&&S.runner===0))) runAI();
}
function rotateCards(pid){""")
rep("""<svg id="map" viewBox="0 0 269 229" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Game board"></svg>""",
    """<svg id="map" viewBox="0 0 269 229" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Game board"></svg><div id="turnwarn" hidden role="status" aria-live="polite" onclick="this.hidden=true"></div>""")
css = """
/* about to win (2026-11-24) */
#turnwarn{position:absolute;left:50%;top:14px;transform:translateX(-50%);z-index:30;display:flex;flex-direction:column;gap:8px;width:min(560px,calc(100% - 32px));cursor:pointer;opacity:0;transition:opacity .5s, transform .5s}
#turnwarn.in{opacity:1}
#turnwarn.out{opacity:0;transform:translate(-50%,-10px)}
#turnwarn .tw{display:flex;flex-direction:column;gap:2px;padding:10px 16px;border-radius:6px;background:linear-gradient(#2a1d10f2,#160e07f2);border:2px solid #b8893a;box-shadow:0 6px 24px #000a;color:#f0dcaa;text-align:center;font-size:14px}
#turnwarn .tw b{font-family:Cinzel,'Trajan Pro',Georgia,serif;font-size:19px;letter-spacing:.02em}
#turnwarn .tw.theirs{border-color:#c0392b}#turnwarn .tw.theirs b{color:#ff8a70}
#turnwarn .tw.mine b{color:#f3cf6b}
/* your faction (2026-11-24) */
.brief{display:flex;gap:16px;align-items:flex-start}.brief img{width:120px;flex:none;image-rendering:auto}
.brief .bf-h{margin:.6em 0 .2em;font-weight:700;color:#e9c66a;font-family:Cinzel,'Trajan Pro',Georgia,serif}.brief ul{margin:0;padding-left:1.2em}.brief li{margin:.2em 0}
@media (max-width:560px){.brief{flex-direction:column;align-items:center}.brief img{width:90px}}
</style>"""
i = s.index("\n</style>"); s = s[:i] + css[:-len("</style>")] + s[i:]
open(p, 'w', encoding='utf-8').write(s); print('ok')
