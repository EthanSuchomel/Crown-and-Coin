import sys
P='/tmp/claude-0/-home-claude/fb256341-5d08-5e47-8b49-8c9035f9f7b9/scratchpad/cc/'
s=open(P+'cc.html',encoding='utf-8').read()
def rep(old,new,count=1):
    global s
    n=s.count(old)
    if n!=count: print('COUNT',n,'for',old[:140]); sys.exit(1)
    s=s.replace(old,new)
rep("""    return `<button class="build" data-act="fxpick" data-k="${k}" ${no?'disabled':''}><span class="bi">${ACTIONS[k].icon}</span><span><b>${ACTIONS[k].name}</b><br><small>${did?'Done':fxPickNote(k)}</small></span></button>`; };""",
    """    return `<button class="fxp" data-act="fxpick" data-k="${k}" ${no?'disabled':''}>${ACTIONS[k].icon}<b>${ACTIONS[k].name}</b><small>${did?'Done':fxPickNote(k)}</small></button>`; };""")
rep("""    <div class="builds">${FX_PICKS.map(btn).join('')}</div>
    <p class="hint" style="margin-top:.5em">Each plays like""","""    <div class="fxpicks">${FX_PICKS.map(btn).join('')}</div>
    <p class="hint fxhint" style="margin-top:.5em">Each plays like""")
rep(""".matrow{flex-wrap:wrap;gap:.35em;font-weight:500}""",""".matrow{flex-wrap:wrap;gap:.35em;font-weight:500}
.fxpicks{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:.45em;margin:.2em 0 .3em}
.fxp{display:flex;flex-direction:column;align-items:center;gap:.2em;text-align:center;padding:.5em .3em;font-family:var(--font-body);font-weight:500;line-height:1.15;min-width:0}
.fxp b{font-family:var(--font-display);font-weight:600;font-size:.95em}
.fxp small{color:var(--lichen);font-size:.78em}
#stage.short .fxp small,#stage.short .fxhint,#stage.narrow .fxp small{display:none}""")
open(P+'cc.html','w',encoding='utf-8').write(s); print('ok')
