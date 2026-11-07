import sys
from PIL import Image
from anim import build
n=sys.argv[1]; idx=[int(x) for x in sys.argv[2].split(',')]; box=[int(x) for x in sys.argv[3].split(',')] if len(sys.argv)>3 else None
sh,meta,frames=build(n,'blue')
ims=[]
for i in idx:
    im=Image.fromarray(frames[i].astype('uint8'),'RGBA')
    if box: im=im.crop(box)
    bg=Image.new('RGBA',im.size,(70,110,70,255)); bg.alpha_composite(im); ims.append(bg)
w=sum(i.size[0] for i in ims)+10*len(ims); h=max(i.size[1] for i in ims)
C=Image.new('RGB',(w,h),(30,30,30)); x=0
for im in ims: C.paste(im,(x,0)); x+=im.size[0]+10
s=min(1.0,2400/w); C=C.resize((int(w*s),int(h*s)),Image.NEAREST); C.save(f'zoom_{n}.png')
