"""Ethan, 2026-11-22: the screen before a game was too cluttered; split it into three tabs.
 1 You:        your faction, your color, and a button that opens the faction's info page.
 2 Opponent:   players (2/3), the opponent's faction and color (each rival with 3 players), and a Difficulty button.
 3 Map & rules: the map (with a little picture of each) and how to win on it.
Back / Next move between tabs; Start works from any tab. The opponent's color is new: it used to be picked for you.
Usage: python3 patch_tabs.py index.html"""
import sys
P = sys.argv[1]; s = open(P).read()
def rep(a, b, n=1):
    global s; assert s.count(a) == n, (s.count(a), a[:90]); s = s.replace(a, b)

# ---- markup
rep('''<div id="scrFaction" class="screen faction-screen" hidden>
  <div class="fs-grid">
    <div class="fs-choices" id="fsChoices"></div>
    <section class="fs-info" aria-live="polite"><div class="fs-info-body" id="fsInfo"></div><div class="fs-foot"><div class="fs-picks"><div id="fsPlayers"></div><div id="fsMap"></div><div id="fsOpp"></div><div id="fsLevel"></div><div id="fsColors"></div></div><button class="primary fs-go" data-scr="go">Start</button></div></section>
  </div>
</div>''', '''<div id="scrFaction" class="screen faction-screen" hidden>
  <div class="fsx" id="fsx">
    <div class="fsx-tabs" role="tablist" aria-label="Game setup" id="fsxTabs"></div>
    <section class="fsx-body" id="fsxBody" role="tabpanel" aria-live="polite"></section>
    <div class="fsx-foot" id="fsxFoot"></div>
  </div>
</div>''')

# ---- styles
rep('.fs-grid{width:100%;', '''/* the screen before a game: three tabs (Ethan, 2026-11-22) */
.fsx{width:100%;height:100%;max-width:1060px;display:flex;flex-direction:column;gap:.7em;min-height:0}
.fsx-tabs{display:flex;gap:.5em}
.fsx-tab{flex:1;display:flex;align-items:center;justify-content:center;gap:.55em;padding:.55em .6em;font-size:1.05em;background:var(--moss);color:var(--lichen)}
.fsx-tab .n{display:inline-flex;align-items:center;justify-content:center;width:1.55em;height:1.55em;border-radius:50%;border:2px solid currentColor;font-family:var(--font-num);font-weight:800;font-size:.85em}
.fsx-tab[aria-selected="true"]{background:var(--bone);color:var(--outline);border-color:var(--outline)}
.fsx-tab .sm{display:none}
.fsx-body{flex:1;min-height:0;overflow:auto;background:var(--moss);border:2px solid var(--edge);box-shadow:0 0 0 2px var(--outline);border-radius:3px;padding:1em 1.2em;display:flex;flex-direction:column;gap:1em}
.fsx-sec{display:flex;flex-direction:column;gap:.45em}
.fsx-l{font-family:var(--font-display);font-weight:700;font-size:1.15em;text-shadow:2px 2px 0 var(--outline);display:flex;align-items:baseline;gap:.6em}
.fsx-l small{font-family:var(--font-body);font-weight:500;font-size:.75em;color:var(--lichen);text-shadow:none}
.fsx-facs{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:.7em}
.fsx-fac{display:flex;flex-direction:column;align-items:center;gap:.3em;text-align:center;padding:.7em .5em .6em;background:var(--moss-2);font-family:var(--font-body);font-weight:500;min-width:0}
.fsx-fac .fs-castle{width:100%;max-width:8.5em;height:5.6em;background-size:contain;background-repeat:no-repeat;background-position:center bottom}
.fsx-fac b{font-family:var(--font-display);font-size:1.3em;color:var(--pc)}
.fsx-fac small{color:var(--lichen);font-size:.85em;line-height:1.2}
.fsx-fac[aria-pressed="true"]{border-color:var(--gold);box-shadow:0 0 0 2px var(--outline),0 0 0 4px var(--gold)}
.fsx-fac:disabled{opacity:.35}
.fsx-facs.sm{grid-template-columns:repeat(3,minmax(0,1fr))}
.fsx-facs.sm .fsx-fac{flex-direction:row;justify-content:center;gap:.6em;padding:.45em .6em}
.fsx-facs.sm .fs-castle{width:3.4em;height:2.5em;flex:none}
.fsx-facs.sm b{font-size:1.1em}
.fsx-facs.sm small{display:none}
.fsx-cols{display:flex;align-items:center;gap:.6em;flex-wrap:wrap}
.fsx-cols .cp-sw{width:2.3em;height:2.3em}
.fsx-cols .cp-sw:disabled{opacity:.25}
.fsx-cols .cp-n{font-family:var(--font-display);font-weight:600;min-width:4em}
.fsx-more{align-self:flex-start;display:flex;align-items:center;gap:.5em;font-size:1.05em;padding:.55em 1em}
.fsx-more .ic{display:inline-flex;align-items:center;justify-content:center;width:1.4em;height:1.4em;border-radius:50%;background:var(--gold);color:var(--gold-ink);font-family:var(--font-num);font-weight:800;font-size:.9em}
.fsx-more small{font-family:var(--font-body);font-weight:500;color:var(--lichen)}
.fsx-np{display:flex;align-items:center;gap:.5em}
.fsx-np .op-b{min-width:3em;justify-content:center}
.fsx-rival{display:flex;flex-direction:column;gap:.45em;padding:.7em .8em;background:var(--night);border:2px solid var(--edge);border-radius:3px}
.fsx-maps{display:grid;grid-template-columns:repeat(auto-fill,minmax(8.5em,1fr));gap:.7em;align-items:start}
.fsx-map{display:flex;flex-direction:column;align-items:center;gap:.3em;padding:.5em .4em .45em;background:var(--moss-2);font-family:var(--font-body);font-weight:500;min-width:0}
.fsx-map svg{width:100%;height:5.6em}
.fsx-map b{font-family:var(--font-display);font-size:1.05em}
.fsx-map small{color:var(--lichen);font-size:.8em}
.fsx-map[aria-pressed="true"]{border-color:var(--gold);box-shadow:0 0 0 2px var(--outline),0 0 0 4px var(--gold)}
.fsx-map .rnd{width:100%;height:1.87em;display:flex;align-items:center;justify-content:center;font-family:var(--font-display);font-size:3em;line-height:1;color:var(--gold);text-shadow:2px 2px 0 var(--outline)}
.fsx-rules{background:var(--night);border:2px solid var(--edge);border-radius:3px;padding:.6em .9em;color:var(--lichen)}
.fsx-rules ul{margin:.3em 0;padding-left:1.2em}
.fsx-rules li{margin:.25em 0}
.fsx-rules b{color:var(--bone)}
.fsx-foot{display:flex;align-items:center;gap:.6em}
.fsx-foot .sum{flex:1;min-width:0;font-size:.9em;color:var(--lichen);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;text-align:center}
.fsx-foot .sum b{font-family:var(--font-display)}
.fsx-foot button{padding:.5em 1.2em;font-size:1.05em}
.fsx-foot .fs-go{font-size:1.15em;padding:.5em 1.8em}
.fsx-sheet{max-width:min(820px,94%)!important;padding:0!important;display:flex;flex-direction:column}
.fsx-sheet .fs-info-body{overflow:auto}
.fsx-sheet .btns{padding:.5em 1em .9em}
.fsx-lv{display:grid;gap:.5em;margin:.4em 0}
.fsx-lv button{display:flex;flex-direction:column;align-items:flex-start;gap:.1em;text-align:left;padding:.55em .8em}
.fsx-lv button small{font-family:var(--font-body);font-weight:500;color:var(--lichen);font-size:.88em}
.fsx-lv button[aria-pressed="true"]{border-color:var(--gold);box-shadow:0 0 0 2px var(--outline),0 0 0 4px var(--gold)}
#stage.short .fsx{gap:.4em}
#stage.short .fsx-body{padding:.5em .8em;gap:.55em}
#stage.short .fsx-tab{padding:.3em .5em;font-size:.95em}
#stage.short .fsx-fac{padding:.4em .4em .35em}
#stage.short .fsx-fac .fs-castle{height:3.2em}
#stage.short .fsx-fac small{display:none}
#stage.short .fsx-map svg{height:3.6em}
#stage.short .fsx-map .rnd{height:1.2em}
#stage.short .fsx-maps{grid-template-columns:repeat(auto-fill,minmax(7em,1fr))}
#stage.short .fsx-foot button{padding:.35em .9em}
#stage.short .fsx-foot .sum{font-size:.8em}
#stage.short .fsx-rival{padding:.4em .6em;gap:.3em}
#stage.short .fsx-cols .cp-sw{width:1.9em;height:1.9em}
#stage.narrow .fsx-tab .lg{display:none}
#stage.narrow .fsx-tab .sm{display:inline}
#stage.narrow .fsx-facs:not(.sm){grid-template-columns:repeat(2,minmax(0,1fr))}
#stage.narrow .fsx-facs.sm .fsx-fac{flex-direction:column;gap:.2em}
#stage.narrow .fsx-foot .sum{display:none}
#stage.tall .fsx-facs:not(.sm){grid-template-columns:repeat(2,minmax(0,1fr))}
#stage.short .fsx-facs:not(.sm){grid-template-columns:repeat(4,minmax(0,1fr))}
#stage.short .fsx-fac b{font-size:1.05em}
#stage.short .fsx-l{font-size:1em}
#stage.short .fsx-more{padding:.35em .8em}
.fs-grid{width:100%;''')

# ---- the screen's code
a = s.index('function renderFactionScreen(){')
b = s.index('function startNewGame(){', a)
s = s[:a] + r'''// the screen before a game: three tabs (Ethan, 2026-11-22)
let fsTab=0, fsOCol=[null,null];
try{ const v=JSON.parse(localStorage.getItem('cc-ocol')||'null'); if(Array.isArray(v)) fsOCol=[v[0]||null,v[1]||null]; }catch(e){}
function setOppColor(k,c){ if(!COLORS[c]) return; fsOCol[k]=c; try{ localStorage.setItem('cc-ocol',JSON.stringify(fsOCol)); }catch(e){} }
// every side's faction and color as the game will start them (yours wins a clash; a rival's taken pick falls back)
function fsSides(){
  const facs=[fsPick,...(fsNP===3?threeOpps(fsPick,fsOpps):[oppFor(fsPick,fsOpp)])], cols=[myColorFor(fsPick)];
  for(let i=1;i<facs.length;i++){ const w=fsOCol[i-1]; cols.push(w&&COLORS[w]&&!cols.includes(w)?w:otherColor(cols,facs[i])); }
  return {facs,cols};
}
const FSX_TABS=[['You','You'],['Opponent','Rivals'],['Map & rules','Map']];
function fsxSwatches(sel,attr,taken){
  return `<div class="fsx-cols" role="group">${COLOR_ORDER.map(c=>`<button class="cp-sw" ${attr(c)} aria-pressed="${c===sel}" aria-label="${COLORS[c].name}" title="${COLORS[c].name}" style="--sw:${COLORS[c].color}" ${taken.includes(c)?'disabled':''}></button>`).join('')}<span class="cp-n">${COLORS[sel]?COLORS[sel].name:''}</span></div>`;
}
// a little picture of a hand-made map, drawn the way the board shows it
function mapThumb(m,cols){
  const rt=Math.sqrt(3), pts=[], fill={g:'#3f7a3a',f:'#1f4a26',m:'#8f8a7e',w:'#1f5a6e',c:'#cfc8b4'};
  let x0=1e9,x1=-1e9,y0=1e9,y1=-1e9;
  const P=(gx,gy)=>[-gy,-gx];
  m.rows.forEach((row,r)=>[...row].forEach((ch,c)=>{ if(ch==='x') return;
    const gx=c*1.5, gy=r*rt+(c&1)*rt/2, v=[]; for(let k=0;k<6;k++){ const a=k*Math.PI/3; v.push(P(gx+Math.cos(a)*.96,gy+Math.sin(a)*.96)); }
    v.forEach(([x,y])=>{ x0=Math.min(x0,x); x1=Math.max(x1,x); y0=Math.min(y0,y); y1=Math.max(y1,y); });
    const home='123'.includes(ch)?cols[+ch-1]:null;
    pts.push(`<polygon points="${v.map(p=>p.map(n=>n.toFixed(2)).join(',')).join(' ')}" fill="${home?(COLORS[home]||{}).color||'#ccc':fill[ch]||fill.g}"/>`);
    if(ch==='c'||home){ const [x,y]=P(gx,gy); pts.push(`<rect x="${(x-.42).toFixed(2)}" y="${(y-.42).toFixed(2)}" width=".84" height=".84" fill="${home?'#fff':'#5b5547'}" opacity="${home?.9:.8}"/>`); }
  }));
  (m.coins||[]).forEach(([r,c])=>{ const ch=(m.rows[r]||'')[c]; if(ch!=='g') return; const [x,y]=P(c*1.5,r*rt+(c&1)*rt/2); pts.push(`<circle cx="${x.toFixed(2)}" cy="${y.toFixed(2)}" r=".3" fill="#efc15a"/>`); });
  return `<svg viewBox="${(x0-.3).toFixed(2)} ${(y0-.3).toFixed(2)} ${(x1-x0+.6).toFixed(2)} ${(y1-y0+.6).toFixed(2)}" aria-hidden="true">${pts.join('')}</svg>`;
}
function renderFactionScreen(){
  const {facs,cols}=fsSides(), lv=prefLevel;
  $('#fsxTabs').innerHTML=FSX_TABS.map((t,i)=>`<button class="fsx-tab" role="tab" data-fstab="${i}" aria-selected="${i===fsTab}"><span class="n">${i+1}</span><span class="lg">${i===1&&fsNP===3?'Opponents':t[0]}</span><span class="sm">${t[1]}</span></button>`).join('');
  let h='';
  if(fsTab===0){
    const f=FACTIONS[fsPick];
    h=`<div class="fsx-sec"><div class="fsx-l">Your faction</div><div class="fsx-facs">${FACTION_ORDER.map(fid=>{ const F=FACTIONS[fid];
        return `<button class="fsx-fac" data-fs="${fid}" aria-pressed="${fid===fsPick}" style="--pc:${F.ink}"><span class="fs-castle px-c-${fid}" aria-hidden="true"></span><b>${F.name}</b><small>${F.tagline}</small></button>`; }).join('')}</div></div>
      <div class="fsx-sec"><div class="fsx-l">Your color</div>${fsxSwatches(cols[0],c=>`data-col="${c}"`,[])}</div>
      <button class="fsx-more" data-fsx="info"><span class="ic">i</span><span>About the ${f.name} <small>cards, units, abilities</small></span></button>`;
  }else if(fsTab===1){
    const rivals=facs.slice(1);
    h=`<div class="fsx-sec"><div class="fsx-l">Players</div><div class="fsx-np">${[2,3].map(n=>`<button class="op-b" data-np="${n}" aria-pressed="${n===fsNP}" style="--pc:var(--bone)">${n}</button>`).join('')}<span class="hint">${fsNP===3?'You and two rivals':'You and one opponent'}</span></div></div>
      ${rivals.map((rf,k)=>{ const others=cols.filter((c,i)=>i!==k+1);
        return `<div class="fsx-rival"><div class="fsx-l">${fsNP===3?`Rival ${k+1}`:'Opponent'} <small>played by the computer</small></div>
          <div class="fsx-facs sm">${FACTION_ORDER.filter(f=>f!==fsPick).map(fid=>{ const F=FACTIONS[fid];
            return `<button class="fsx-fac" data-ofac="${k}:${fid}" aria-pressed="${fid===rf}" style="--pc:${F.ink}"><span class="fs-castle px-c-${fid}" aria-hidden="true"></span><b>${F.name}</b></button>`; }).join('')}</div>
          ${fsxSwatches(cols[k+1],c=>`data-ocol="${k}:${c}"`,others)}</div>`; }).join('')}
      <button class="fsx-more" data-fsx="level"><span class="ic">!</span><span>Difficulty: ${AI_LEVEL_NAME[lv]} <small>${AI_LEVEL_NOTE[lv]}</small></span></button>`;
  }else{
    const list=CUSTOM_MAPS.filter(m=>m.players===fsNP), sel=list.some(m=>m.id===fsMap)?fsMap:'';
    const win=m=>{ const n=winCastlesFor(fsNP,m?m.id:''); return n?`${n} castles to win`:'last side standing'; };
    h=`<div class="fsx-sec"><div class="fsx-l">Map <small>${fsNP} players</small></div><div class="fsx-maps">
        <button class="fsx-map" data-map="" aria-pressed="${!sel}"><span class="rnd" aria-hidden="true">?</span><b>Random</b><small>a new map each game</small></button>
        ${list.map(m=>`<button class="fsx-map" data-map="${m.id}" aria-pressed="${m.id===sel}">${mapThumb(m,cols)}<b>${escH(m.name)}</b><small>${win(m)}</small></button>`).join('')}</div></div>
      <div class="fsx-sec"><div class="fsx-l">How to win <small>${sel?escH(mapById(sel).name):'Random map'}</small></div><div class="fsx-rules">${winListHtml()}</div></div>`;
  }
  $('#fsxBody').innerHTML=h;
  const side=i=>`<b style="color:${COLORS[cols[i]].ink}">${FACTIONS[facs[i]].name}</b>`;
  const mp=CUSTOM_MAPS.find(m=>m.id===fsMap&&m.players===fsNP);
  $('#fsxFoot').innerHTML=`<button data-fsx="back">${fsTab?'Back':'Title'}</button><span class="sum">${side(0)} vs ${facs.slice(1).map((f,i)=>side(i+1)).join(' and ')} · ${AI_LEVEL_NAME[lv]} · ${mp?escH(mp.name):'Random map'}</span>${fsTab<2?'<button data-fsx="next">Next</button>':''}<button class="primary fs-go" data-scr="go">Start</button>`;
}
function fsxInfo(){
  const m=$('#modal'); m.classList.remove('hidden');
  m.innerHTML=`<div class="sheet fs-info fsx-sheet"><div class="fs-info-body">${factionInfo(fsPick)}</div><div class="btns"><button class="primary" data-fsx="close">Close</button></div></div>`;
}
function fsxLevel(){
  const m=$('#modal'); m.classList.remove('hidden');
  m.innerHTML=`<div class="sheet"><h3>Difficulty</h3><p class="hint">How well the computer plays.</p><div class="fsx-lv">${AI_LEVELS.map(v=>`<button data-fslv="${v}" aria-pressed="${v===prefLevel}"><b>${AI_LEVEL_NAME[v]}</b><small>${AI_LEVEL_NOTE[v]}</small></button>`).join('')}</div><div class="btns"><button data-fsx="close">Close</button></div></div>`;
}
''' + s[b:]
rep("function startNewGame(){ renderFactionScreen(); showScreen('scrFaction'); }", "function startNewGame(){ fsTab=0; renderFactionScreen(); showScreen('scrFaction'); }")

# ---- taps
rep("""$('#stage').addEventListener('click',e=>{
  const fsb=e.target.closest('button[data-fs]');""", """$('#stage').addEventListener('click',e=>{
  const ft=e.target.closest('button[data-fstab]'); if(ft){ fsTab=+ft.dataset.fstab; renderFactionScreen(); return; }
  const fx=e.target.closest('button[data-fsx]'); if(fx){ const k=fx.dataset.fsx;
    if(k==='close') closeModal(); else if(k==='info') fsxInfo(); else if(k==='level') fsxLevel();
    else if(k==='next'){ fsTab=Math.min(2,fsTab+1); renderFactionScreen(); }
    else if(k==='back'){ if(fsTab) { fsTab--; renderFactionScreen(); } else showScreen('scrTitle'); }
    return; }
  const flv=e.target.closest('button[data-fslv]'); if(flv){ setPrefLevel(flv.dataset.fslv); closeModal(); renderFactionScreen(); return; }
  const fof=e.target.closest('button[data-ofac]'); if(fof){ const [k,f]=fof.dataset.ofac.split(':');
    if(fsNP===3){ const o=threeOpps(fsPick,fsOpps); if(o[1-k]===f) o[1-k]=o[+k]; o[+k]=f; fsOpps=o; } else fsOpp=f;
    renderFactionScreen(); return; }
  const foc=e.target.closest('button[data-ocol]'); if(foc){ const [k,c]=foc.dataset.ocol.split(':'); setOppColor(+k,c); renderFactionScreen(); return; }
  const fsb=e.target.closest('button[data-fs]');""")
rep("else if(k==='go'){ showScreen(null); newGame(fsPick,{np:fsNP,opp:fsOpp,opps:fsOpps,map:(mapById(fsMap)||{}).players===fsNP?fsMap:''}); }",
    "else if(k==='go'){ closeModal(); showScreen(null); newGame(fsPick,{np:fsNP,opp:fsOpp,opps:fsOpps,cols:fsSides().cols,map:(mapById(fsMap)||{}).players===fsNP?fsMap:''}); }")

# ---- the game starts with the picked colors
rep("""  { const mine=myColorFor(facs[0]), taken=[mine]; applyColor(S.players[0],mine);
    for(let i=1;i<np;i++){ const c=otherColor(taken,facs[i]); applyColor(S.players[i],c); taken.push(c); } }""",
    """  { const want=(opts&&opts.cols)||[], mine=myColorFor(facs[0]), taken=[mine]; applyColor(S.players[0],mine);
    for(let i=1;i<np;i++){ const w=want[i], c=w&&COLORS[w]&&!taken.includes(w)?w:otherColor(taken,facs[i]); applyColor(S.players[i],c); taken.push(c); } }""")
open(P, 'w').write(s); print('ok')
