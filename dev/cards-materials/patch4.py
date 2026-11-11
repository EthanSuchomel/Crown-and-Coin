import sys
P='/tmp/claude-0/-home-claude/fb256341-5d08-5e47-8b49-8c9035f9f7b9/scratchpad/cc/'
s=open(P+'cc.html',encoding='utf-8').read()
def rep(old,new,count=1):
    global s
    n=s.count(old)
    if n!=count: print('COUNT',n,'for',old[:140]); sys.exit(1)
    s=s.replace(old,new)
rep("""opacity='.8'/></svg>`);""","""opacity='.8'/></svg>`).replace(/'/g,'%27').replace(/\\(/g,'%28').replace(/\\)/g,'%29');   // safe inside an unquoted CSS url()""")
rep("""Materials pay for forts, barracks, barracks upgrades, walls${isDino(0)?'':' and trebuchets'}${isMamm(0)?' and Watering Holes':''}. Units and markets cost gold.""",
    """Materials pay for ${(isDino(0)?['barracks','barracks upgrades','walls']:['forts','barracks','barracks upgrades','walls','trebuchets'].concat(isMamm(0)?['Watering Holes']:[])).join(', ').replace(/, ([^,]*)$/,' and $1')}. Units and markets cost gold.""")
open(P+'cc.html','w',encoding='utf-8').write(s); print('ok')
