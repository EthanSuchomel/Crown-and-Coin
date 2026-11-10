# Clean the saddle's armour and straps off the Alamosaurus leg pieces: the hip plate (ro) goes entirely,
# and blue cloth / steel bits on the upper legs are repainted with the surrounding skin.
import numpy as np
from PIL import Image
from scipy.ndimage import binary_dilation
D='/tmp/claude-0/-home-claude/112a0b3f-dd28-5943-ad35-c12df06d67ec/scratchpad/'
def armour(a,top_frac=0.45):
    r,g,b,al=[a[...,i].astype(int) for i in range(4)]
    op=al>40; mx=np.maximum(np.maximum(r,g),b); mn=np.minimum(np.minimum(r,g),b); lum=(r+g+b)/3
    ys=np.where(op.any(1))[0]; y0,y1=ys.min(),ys.max(); upper=np.zeros_like(op); upper[y0:int(y0+(y1-y0)*top_frac)+1]=True
    blue=op&(b>r+20)&(b>g)
    steel=op&upper&((mx-mn)<26)&(lum>95)
    odd=op&upper&(lum>45)&((b>=r-5)|((mx-mn)<18))      # anything not skin-coloured: dark steel, navy cloth
    return blue|steel|odd
def inpaint(a,bad):
    a=a.copy().astype(np.int32); good=(a[...,3]>40)&~bad; bad=bad.copy()
    for _ in range(40):
        if not bad.any(): break
        ring=bad&binary_dilation(good,iterations=1)
        for y,x in zip(*np.where(ring)):
            ys,xs=slice(max(0,y-1),y+2),slice(max(0,x-1),x+2)
            m=good[ys,xs]; 
            if m.any():
                cols=a[ys,xs][m][:,:3]; lum=cols.mean(1); keep=cols[lum>60] if (lum>60).any() else cols   # skin, not outline
                a[y,x,:3]=np.median(keep,0); a[y,x,3]=255
        good|=ring; bad&=~ring
    return a.astype(np.uint8)
out={}
for n in ['leg_nu','leg_fu','leg_rfu','leg_rnu','leg_nl','leg_fl','leg_rnl','leg_rfl']:
    a=np.array(Image.open(D+'alamo/'+n+'.png').convert('RGBA'))
    if n=='leg_fu': a[:180,229:]=0          # the tip of the shoulder plate that stuck out past the chest
    bad=armour(a,0.9 if n=='leg_nu' else 0.6 if n.endswith('u') else 0.3); print(n,'armour px',int(bad.sum()))
    out[n]=inpaint(a,bad) if bad.any() else a
    Image.fromarray(out[n]).save(D+'alamo3/'+n+'.png')
Image.new('RGBA',(314,244),(0,0,0,0)).save(D+'alamo3/leg_ro.png')
body=Image.open(D+'alamo2/alamo_plain.png').convert('RGBA')
c=Image.new('RGBA',body.size,(40,90,50,255))
L=lambda n: Image.open(D+'alamo3/'+n+'.png').convert('RGBA')
for n in ['leg_rfu','leg_rfl','leg_fu','leg_fl']: c.alpha_composite(L(n))
c.alpha_composite(body)
for n in ['leg_rnu','leg_rnl','leg_ro','leg_nu','leg_nl']: c.alpha_composite(L(n))
c.crop((90,100,262,244)).resize((172*5,144*5),Image.NEAREST).save(D+'alamo3/assembled.png')
c.resize((314*3,244*3),Image.NEAREST).save(D+'alamo3/assembled_full.png')
