import json, subprocess, sys
R='/home/claude/crown-and-coin/'
src=open(R+'index.html').read()
k='window.ARENA_HTML="'; i=src.find(k)+len(k); j=i
while True:
    j=src.find('"',j); bs=0; q=j-1
    while src[q]=='\\': bs+=1; q-=1
    if bs%2==0: break
    j+=1
board=src[:i]+'@@ARENA@@'+src[j:]
open('out/board_in.html','w').write(board)
arena=open(R+'arena.html').read()
dec=json.loads('"'+src[i:j]+'"')
assert dec==arena, 'embedded arena differs from arena.html'
open('out/arena_in.html','w').write(arena)
subprocess.run(['python3','patch_arena_mages.py','out/arena_in.html','out/arena.html','out/edits-myth-board-arena.html.json'],check=True)
subprocess.run(['python3','patch_board_myth.py','out/board_in.html','out/board_out.html','out/edits-myth-board-board.json','art/myth_board_art.json'],check=True)
b=open('out/board_out.html').read(); a=open('out/arena.html').read()
enc=lambda t: json.dumps(t,ensure_ascii=False)[1:-1].replace('</script','<\\/script')
assert b.count('@@ARENA@@')==1
open('out/index.html','w').write(b.replace('@@ARENA@@',enc(a)))
print('built', len(open('out/index.html').read()))
