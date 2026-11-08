"""Make the claude.ai version of Crown & Coin from the iPad site's index.html: drops the home-screen app lines
(icons, manifest, standalone styles, the offline worker). Usage: make_claude_version.py index.html OUT.html
Then publish OUT.html as index.html, arena.html, and every file in myth/ and dino/ to the main Crown & Coin link
(https://claude.ai/artifact/7jbdEk6pGqUo5z36bGR7gj, id 36896898-6a88-4597-9fb5-d8c79c723408)."""
import sys
s=open(sys.argv[1]).read().split('\n')
l1=s[0]; tail='<link rel="manifest" href="manifest.webmanifest">'
assert l1.endswith(tail); l1=l1[:-len(tail)]+'</head><body>'
k=s.index('</head><body>'); txt='\n'.join([l1]+s[k+1:])
sw="<script>\n// offline: keep the game on the iPad so it opens without WiFi (updates download in the background when online)\n"
i=txt.find(sw); assert i>0; j=txt.find('</script>\n',i)+len('</script>\n'); txt=txt[:i]+txt[j:]
assert 'serviceWorker' not in txt and 'manifest.webmanifest' not in txt
open(sys.argv[2],'w').write(txt); print('ok',len(txt))
