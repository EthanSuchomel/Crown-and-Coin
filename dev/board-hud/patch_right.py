"""Ethan, 2026-11-12: the numbers box moves to the map's bottom-right corner (the middle of the screen)."""
import sys
P=sys.argv[1]; s=open(P).read()
def rep(a,b):
    global s; assert s.count(a)==1,a[:80]; s=s.replace(a,b)
rep(".stats{position:absolute;left:0;bottom:0;", ".stats{position:absolute;right:0;bottom:0;")
rep("border:2px solid var(--edge);border-left:0;border-bottom:0;box-shadow:2px -2px 0 0 var(--outline);border-radius:0 3px 0 0;padding:.3em .6em .35em .45em;",
    "border:2px solid var(--edge);border-right:0;border-bottom:0;box-shadow:-2px -2px 0 0 var(--outline);border-radius:3px 0 0 0;padding:.3em .45em .35em .6em;")
rep("#stage.short .stats{font-size:.74em;padding:.2em .45em .25em .35em}", "#stage.short .stats{font-size:.74em;padding:.2em .35em .25em .45em}")
rep("// in the board's bottom-left corner (Ethan's sketch)", "// in the board's bottom-right corner (Ethan, 2026-11-12)")
open(P,'w').write(s); print('ok')
