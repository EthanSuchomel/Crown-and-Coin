# Robot card pictures (Ethan, 2026-11-12): the five punch cards, each with its binary number and the gear-skull in the same spot.
import sys,json
p=sys.argv[1]; s=open(p).read()
art=json.load(open('dev/robots/cardart.json'))
a="""const CARD_ART={"""
assert s.count(a)==1
i=s.index(a); j=s.index('};',i)+2   # the object's end (the data URLs hold ';' too)
s=s[:j]+"\nObject.assign(CARD_ART,"+json.dumps(art)+");   // Robot punch cards: Mobilize 1001, Deploy 1101, Onslaught 1111, Construction 0011, Siege Protocol 0000"+s[j:]
open(p,'w').write(s); print('robots patch4 ok')
