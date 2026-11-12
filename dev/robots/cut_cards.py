# Robot punch cards (Ethan's OpenArt redraws, 2026-11-12: one template, the gear-skull in the same top-right spot on each).
# Cut from magenta like the other Robot art, fit inside 200x200 like the Dinosaur card art, saved as webp for CARD_ART.
import sys,json,base64,io
sys.path.insert(0,'.')
from PIL import Image
from cut_robots_lib import cut,hard,pink
A='/mnt/user-data/attachments/3befcac9-cc11-52d0-937a-7b889271868d/'
cards={'mobil':'3416c29c-image.png','deploy':'a7b0d455-image.png','onsl':'f359261d-image.png','cons':'9ecd34fd-image.png','sprot':'d3a6b8af-image.png'}
art={}
for cid,f in cards.items():
    o=cut(A+f); k=200/max(o.size); sm=hard(o.resize((round(o.width*k),round(o.height*k)),Image.LANCZOS))
    sm.save(f'card_{cid}.png',optimize=True); b=io.BytesIO(); sm.save(b,'WEBP',quality=88,method=6)
    art[cid]='data:image/webp;base64,'+base64.b64encode(b.getvalue()).decode(); print(cid,o.size,sm.size,'pink',pink(sm),len(art[cid]))
json.dump(art,open('cardart.json','w'))
