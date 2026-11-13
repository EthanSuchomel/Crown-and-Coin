"""Ethan's board layout (2026-11-12 sketch): the map takes the whole left side, your numbers sit in a small box in the
map's bottom-left corner (+X coins / turn, X units, X coins, X materials, castles a-b-c), and the cards column's header
holds just the turn line and the Full / ? / Log / New buttons. Usage: python3 patch_hud.py index.html"""
import sys
P = sys.argv[1]
s = open(P).read()
def rep(a, b, n=1):
    global s
    c = s.count(a); assert c == n, (c, a[:100]); s = s.replace(a, b)

# --- markup: the stats box moves inside the map frame
rep('''<div id="bldov" class="bldov" hidden></div></div>
  </section>
  <section class="stats" id="stats" aria-label="Your empire"></section>''',
    '''<div id="bldov" class="bldov" hidden></div><section class="stats" id="stats" aria-label="Your empire"></section></div>
  </section>''')

# --- grid: no stats row any more
rep('''grid-template-rows:minmax(0,1fr) auto var(--maph,70vh) minmax(0,1fr);
  grid-template-areas:". side" "stats side" "board side" ". side"}   /* your numbers sit above the board */''',
    '''grid-template-rows:minmax(0,1fr) var(--maph,70vh) minmax(0,1fr);
  grid-template-areas:". side" "board side" ". side"}   /* your numbers sit in the board's bottom-left corner */''')
rep('''#stage.tall #app{grid-template-columns:minmax(0,1fr);grid-template-rows:auto var(--maph,50vh) minmax(0,1fr);grid-template-areas:"stats" "board" "side";gap:.6em 0}''',
    '''#stage.tall #app{grid-template-columns:minmax(0,1fr);grid-template-rows:var(--maph,50vh) minmax(0,1fr);grid-template-areas:"board" "side";gap:.6em 0}''')
rep('#stage.tall .stats{margin-bottom:0}\n', '')

# --- the stats box: replace the three-box styles
a = s.index('/* your numbers under the board */\n.stats{')
b = s.index('#stage.short #app{padding-top')
s = s[:a] + '''/* your numbers in the board's bottom-left corner (Ethan's sketch): coins a turn, units, coins, materials, castles */
.stats{position:absolute;left:0;bottom:0;z-index:2;display:flex;flex-direction:column;gap:.05em;background:var(--moss);
  border:2px solid var(--edge);border-left:0;border-bottom:0;box-shadow:2px -2px 0 0 var(--outline);border-radius:0 3px 0 0;padding:.3em .6em .35em .45em;
  font-size:.86em;line-height:1.2;pointer-events:none}
.stats .st{display:flex;align-items:center;gap:.35em;white-space:nowrap}
.stats .st b{font-family:var(--font-num);font-weight:800;font-variant-numeric:tabular-nums}
.stats .st small{color:var(--lichen)}
.stats .st .px{width:1.15em!important;height:1.15em!important;flex:none;vertical-align:middle}
.stats .st.inc b{color:var(--gold)}
.stats .st.have b{color:var(--gold)}
.stats button.st{pointer-events:auto;padding:0 .3em 0 0;margin:0;background:transparent;border:0;box-shadow:none;font:inherit;color:inherit;text-align:left;cursor:pointer}
.stats button.st:hover b,.stats button.st:focus-visible b{text-decoration:underline}
.stats .st.cas{font-family:var(--font-num);font-weight:800;margin-top:.1em}
.stats .st.cas small{font-family:var(--font-body);font-weight:500}
''' + s[b:]
for x in ['#stage.short .stats{margin-bottom:.25em}\n',
          '#stage.short .stat{padding:.12em .45em;flex-direction:row;align-items:baseline;gap:.4em}\n',
          '#stage.short .stat .sl{flex:0 1 auto;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}\n',
          '#stage.short .stat .sv{flex:none}\n', '#stage.short .stat .sl{font-size:.6em}\n',
          '#stage.short .stat .sv{font-size:1.02em}\n', '#stage.short .stat .ss{display:none}\n']:
    rep(x, '')
rep('#stage.short .board .mapwrap{border-width:2px}\n', '#stage.short .board .mapwrap{border-width:2px}\n#stage.short .stats{font-size:.74em;padding:.2em .45em .25em .35em}\n')

# --- the cards header: the turn line and the four buttons
a = s.index("  $('#sidehead').innerHTML=`<span class=\"sh-title\">Cards</span>")
b = s.index('\n', s.index('<span class="sh-btns">', a))
s = s[:a] + '''  $('#sidehead').innerHTML=`<span class="sh-turn">${turn}</span>
    <span class="sh-btns"><button class="ghost" data-head="full" aria-label="${isFull()?'Exit full screen':'Full screen'}" aria-pressed="${isFull()}">⛶ Full</button><button class="ghost" data-head="help" aria-label="How to play">?</button><button class="ghost" data-head="log">Log</button><button class="ghost" data-head="new">${NET?'Leave':'New'}</button></span>${siege}${online}`;''' + s[b:]
# the castle race now lives in the corner box; renderHead no longer needs it
a = s.index('  let race=S.players.length>2?`<span class="sh-castles"')
b = s.index('\n', s.index('<small>of ${CASTLES_TO_WIN}</small></span>`;', a))
s = s[:a] + s[b + 1:]
rep('.sh-turn{font-size:.85em;color:var(--lichen);flex:1;min-width:8em}', '.sh-turn{font-size:.9em;color:var(--lichen);flex:1;min-width:8em;padding:.25em 0}')

# --- renderStats: the five lines
a = s.index('// under the board: coin production')
b = s.index('// details of the tapped hex')
s = s[:a] + '''// in the board's bottom-left corner (Ethan's sketch): +coins a turn, units, coins, materials, and every side's castles
function renderStats(){
  const me=S.players[0], myth=isMyth(0), cur1=myth?'magic':'coin';
  const units=S.tiles.filter(t=>t.owner===0).reduce((n,t)=>n+t.troops,0);
  const cas=S.players.map(p=>`<b style="color:${inkOf(p)}${p.out?';opacity:.4;text-decoration:line-through':''}">${castleCount(p.id)}</b>`).join(' – ');
  $('#stats').innerHTML=`
    <span class="st inc" title="${myth?'Magic':'Coins'} you collect each turn"><b>+${incomeOf(0).total}</b> ${myth?'magic':'coins'} / turn</span>
    <span class="st" title="Your units on the board"><b>${units}</b> unit${units===1?'':'s'}</span>
    <span class="st have" title="${myth?'Magic':'Gold'} you have"><span class="px px-${cur1}" aria-hidden="true"></span><b>${me.gold}</b> ${myth?'magic':'coins'}</span>
    ${usesMat(0)?`<button class="st" data-head="trade" title="Materials: tap to buy more at your markets" aria-label="Materials: ${matOf(0)}. Buy more at your markets">${MAT_IC}<b>${matOf(0)}</b> material${matOf(0)===1?'':'s'}</button>`:''}
    <span class="st cas" title="${S.players.length>2?'Castles held':`Castles held: hold ${CASTLES_TO_WIN} to win`}"><span class="px px-c-neutral" aria-hidden="true"></span>${cas}${S.players.length>2?'':` <small>of ${CASTLES_TO_WIN}</small>`}</span>`;
}
''' + s[b:]
# the materials line opens the buying sheet, like the header button did
rep("$('#sidehead').addEventListener('click',e=>{", "$('#stats').addEventListener('click',e=>{ if(e.target.closest('button[data-head=\"trade\"]')) openTrade(); });\n$('#sidehead').addEventListener('click',e=>{")

# --- sizing: nothing above the board now
rep("statsH=($('#stats').offsetHeight||3.6*fs)+px(getComputedStyle($('#stats')).marginTop)+px(getComputedStyle($('#stats')).marginBottom);",
    "statsH=0;   // your numbers sit inside the board's corner now")
open(P, 'w').write(s)
print('ok')
