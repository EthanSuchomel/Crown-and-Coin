"""Ethan, 2026-11-22: the computer's turn speed follows its difficulty. Easy keeps the old pace (about 20-25 s a turn),
Expert takes about 2 s, Medium and Hard sit between (about 12 s and 7 s). Every pause in runAI is scaled; a battle
against you still waits for your OK. Usage: python3 patch_pace.py index.html"""
import sys
P = sys.argv[1]; s = open(P).read()
def rep(a, b, n=1):
    global s; assert s.count(a) == n, (s.count(a), a[:80]); s = s.replace(a, b)
rep("const AI_PACE={lead:1800, act:5200, move:2600, battle:3400};",
    "const AI_PACE={lead:1800, act:5200, move:2600, battle:3400};\nconst AI_SPEED={easy:1, medium:.55, hard:.3, expert:.085};   // how much of the Easy pace each level takes (Ethan, 2026-11-22)")
a = s.index("async function runAI(){"); b = s.index("\n}\n", a)
body = s[a:b]
body = body.replace("  ui.busy=true; const pid=S.current, p=cur();", "  ui.busy=true; const pid=S.current, p=cur();\n  const pace=AI_SPEED[aiLv(pid)]??1, wait=ms=>sleep(ms*pace);")
import re
body = re.sub(r"await sleep\(", "await wait(", body)
body = body.replace("// pacing: each of the computer's actions takes about 6 to 8 seconds, so you can follow what it does", "// pacing: on Easy each action takes about 6 to 8 seconds, so you can follow what it does; harder levels go faster")
s = s[:a] + body + s[b:]
open(P, 'w').write(s); print('ok')
