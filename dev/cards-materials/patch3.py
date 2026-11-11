import sys
P='/tmp/claude-0/-home-claude/fb256341-5d08-5e47-8b49-8c9035f9f7b9/scratchpad/cc/'
s=open(P+'cc.html',encoding='utf-8').read()
def rep(old,new,count=1):
    global s
    n=s.count(old)
    if n!=count: print('COUNT',n,'for',old[:140]); sys.exit(1)
    s=s.replace(old,new)
rep("""    else if(a==='move'){ S.play.moves=0; yield* aiMoveGen(pid,lvl); }
  }
}""","""    else if(a==='move'){ S.play.moves=0; yield* aiMoveGen(pid,lvl); }
  }
  if(!S.over) aiStock(pid);   // after its card, spare gold goes into materials for the next build
}
// The markets only sell so many materials a turn, so the computer keeps a store of them for its next Build or Advancements
function aiStock(pid){
  if(!usesMat(pid)) return;
  const p=S.players[pid], want=aiSmart(pid)?14:8; if(matOf(pid)>=want) return;
  const keep=Math.max(6,Math.floor(p.gold*0.35)), n=Math.min(want-matOf(pid),matLeft(pid),Math.floor((p.gold-keep)/MAT_PRICE));
  if(n>0) buyMat(pid,n);
}""")
open(P+'cc.html','w',encoding='utf-8').write(s)
print('ok')
