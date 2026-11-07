import sys
from PIL import Image, ImageDraw
from anim import build
n=sys.argv[1]
sh,meta,frames=build(n,'blue')
# contact sheet at a readable size: frames 2 rows, on grass-ish background with a ground line
fw=420; fh=round(meta['H']*fw/meta['W'])
cols=7; rows=(len(frames)+cols-1)//cols
C=Image.new('RGBA',(cols*fw,rows*(fh+18)),(70,110,70,255)); d=ImageDraw.Draw(C)
for i,f in enumerate(frames):
    im=Image.fromarray(f.astype('uint8'),'RGBA').resize((fw,fh),Image.LANCZOS)
    x=(i%cols)*fw; y=(i//cols)*(fh+18)
    gy=y+round((meta['pad'][2]+meta['H0'])*fh/meta['H']); d.line([(x,gy),(x+fw,gy)],fill=(255,255,0,255))
    C.alpha_composite(im,(x,y)); d.text((x+4,y+fh+2),str(i),fill=(255,255,255,255))
C.convert('RGB').save(f'contact_{n}.png'); print(meta)
