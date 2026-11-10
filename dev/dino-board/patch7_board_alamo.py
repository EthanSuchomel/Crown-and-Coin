# Dinosaur board rework, step 7: the board's Alamosaurus picture without the tower and riders (the guard's new look).
import json, base64
R='/home/claude/crown-and-coin/'
s=open(R+'index.html').read()
i=s.index('UNIT_ART={'); j=s.index('}',i)
d=json.loads(s[i+9:j+1]); assert d['alamo'].startswith('data:image/png')
old=d['alamo']; new='data:image/png;base64,'+base64.b64encode(open(R+'dev/dino-board/board_alamo.png','rb').read()).decode()
seg=s[i:j+1]; assert seg.count(old)==1
s=s[:i]+seg.replace(old,new)+s[j+1:]
open(R+'index.html','w').write(s); print('patch7 ok')
