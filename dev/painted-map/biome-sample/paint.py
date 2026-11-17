import json, base64, io, numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage
from scipy.spatial import cKDTree
rng=np.random.default_rng(7)
d=json.load(open('/home/claude/work/board.json'))
PX=4; x0,y0,vw,vh=[float(v) for v in d['vb'].split()]
W,H=int(vw*PX),int(vh*PX)
T=[t for t in d['tiles'] if t['terrain']!='void']
def kind(t):
    if t['terrain']=='mountain': return 3
    if t['forest']: return 1
    if t['fern']: return 2
    return 0
cen=np.array([[(t['cx']-x0)*PX,(t['cy']-y0)*PX] for t in T]); kinds=np.array([kind(t) for t in T])
def noise(cell,amp,seed):
    r=np.random.default_rng(seed); g=r.uniform(-1,1,(H//cell+3,W//cell+3)).astype(np.float32)
    return amp*np.array(Image.fromarray(g,'F').resize((W+3*cell,H+3*cell),Image.BICUBIC))[:H,:W]
ys,xs=np.mgrid[0:H,0:W].astype(np.float32)
U=PX
wx=noise(int(14*U),7*U,1)+noise(int(5*U),2.2*U,2); wy=noise(int(14*U),7*U,3)+noise(int(5*U),2.2*U,4)
tree=cKDTree(cen)
dist,idx=tree.query(np.stack([(xs+wx).ravel(),(ys+wy).ravel()],1))
idx=idx.reshape(H,W); dist=dist.reshape(H,W)
# inside the board: within a hex radius-ish of some centre (unwarped)
hexm=Image.new('L',(W,H),0); hd=ImageDraw.Draw(hexm)
for (cx,cy) in cen:
    R=d['HR']*PX; hd.polygon([(cx-R*np.sin(a),cy-R*np.cos(a)) for a in np.arange(6)*np.pi/3],fill=255)
lm=ndimage.gaussian_filter(np.array(hexm).astype(float)/255,5*PX)
lm=lm+noise(int(16*U),.16,31)+noise(int(5*U),.07,32)
board=lm>.5
coast=ndimage.distance_transform_edt(board)/PX; sea_d=ndimage.distance_transform_edt(~board)/PX
bio=np.where(board,kinds[idx],-1)
# ground textures
def tex(src,scale_units,crop=None):
    im=Image.open(src).convert('RGB')
    if crop: im=im.crop(crop)
    s=int(scale_units*PX); im=im.resize((s,int(s*im.height/im.width)),Image.LANCZOS)
    out=Image.new('RGB',(W,H))
    for yy in range(0,H,im.height):
        for xx in range(0,W,im.width): out.paste(im,(xx,yy))
    return np.array(out).astype(float)
grass=tex('/home/claude/crown-and-coin/dev/hex-terrain/src/grass_openart.png',72)
n1=noise(int(6*U),1,11)
floor=grass*np.array([.42,.5,.52])+np.dstack([n1*14+14,n1*10+6,n1*6])     # dark, cool forest floor
rock=np.dstack([138+n1*26,138+n1*26,146+n1*24]) + noise(int(2*U),12,12)[...,None]   # grey scree
mud=np.dstack([112+n1*20,70+n1*12,48+n1*8])                                # wet reddish mud
moss=noise(int(3*U),1,13)>.25
mud=np.where(moss[...,None],grass*np.array([.62,.72,.55]),mud)
wt={}
for k in (1,2,3):
    f=ndimage.gaussian_filter((bio==k).astype(float),4.2*PX)
    f=np.clip((f-.18)/.55 + noise(int(4*U),.18,40+k),0,1)
    wt[k]=f*f*(3-2*f)
tot=wt[1]+wt[2]+wt[3]; sc_=np.where(tot>1,1/np.maximum(tot,1e-6),1)
for k in wt: wt[k]=wt[k]*sc_
ground=grass*(1-(wt[1]+wt[2]+wt[3]))[...,None]+floor*wt[1][...,None]+mud*wt[2][...,None]+rock*wt[3][...,None]
# the coast: sand along the shore
sand=np.dstack([214+n1*14,190+n1*12,128+n1*10])
sa=np.clip((3.2-coast)/1.8,0,1)[...,None]
ground=ground*(1-sa)+sand*sa
img=Image.fromarray(np.clip(ground,0,255).astype(np.uint8)).convert('RGBA')
img.putalpha(Image.fromarray((board*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2)))
# the sea: shallow turquoise by the shore, deep blue further out, with ripples
t_=np.clip(sea_d/9,0,1)[...,None]
sea=np.array([70,190,205])*(1-t_)+np.array([12,58,118])*t_
rip=noise(int(2.5*U),1,50); sea=sea+(rip>.55)[...,None]*np.array([40,50,50])*(1-t_*.6)+noise(int(8*U),8,51)[...,None]
foam=(sea_d<1.0)&(sea_d>0); sea[foam]=[235,245,240]
seaimg=Image.fromarray(np.clip(sea,0,255).astype(np.uint8)).convert('RGBA')
seaimg.alpha_composite(img); img=seaimg
# sprites
def uri(u): return Image.open(io.BytesIO(base64.b64decode(u.split(',',1)[1]))).convert('RGBA')
trees=[uri(u) for u in d['forest']]; ferns=[uri(u) for u in d['fern']]
P='/home/claude/crown-and-coin/dev/painted-map/pieces/'
peaks=[Image.open(P+'mountain_s.png'),Image.open(P+'mountain_m.png')]
def trim(im): bb=im.getbbox(); return im.crop(bb)
trees=[trim(t) for t in trees]; ferns=[trim(t) for t in ferns]; peaks=[trim(t) for t in peaks]
items=[]
def scatter(k,spr,spacing,w_lo,w_hi,band,minp=.12,jit=.8):
    s=spacing*PX
    for yy in np.arange(0,H,s*.866):
        off=(int(yy/(s*.866))%2)*s/2
        for xx in np.arange(off,W,s):
            x=int(xx+rng.uniform(-jit,jit)*s/2); y=int(yy+rng.uniform(-jit,jit)*s/2)
            if not(0<=x<W and 0<=y<H) or not board[y,x] or coast[y,x]<2.5: continue
            wv=wt[k][y,x]
            if rng.random()>wv**1.3: continue
            sc=w_lo+(w_hi-w_lo)*wv*rng.uniform(.8,1.1)
            items.append((y,x,spr[rng.integers(len(spr))],sc,rng.random()<.5))
scatter(1,trees,4.2,6,9.5,9)
scatter(2,ferns,3.6,4.2,6.5,6,minp=.2)
scatter(3,peaks,6.5,13,24,8,minp=.55,jit=.6)
items.sort(key=lambda t:t[0])
shadow=Image.new('RGBA',(W,H),(0,0,0,0)); sd=ImageDraw.Draw(shadow)
for y,x,s,sc,fl in items:
    w=sc*PX; sd.ellipse([x-w*.42,y-w*.13,x+w*.48,y+w*.17],fill=(0,0,0,70))
img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(2)))
# lakes and castles (existing tiles), under the sprites so trees can stand in front
TI='/home/claude/crown-and-coin/dev/hex-terrain/tiles/'
for t in T:
    cx,cy=(t['cx']-x0)*PX,(t['cy']-y0)*PX
    f=None
    if t['terrain']=='water': f='water_soft.png'
    elif t['castle']: f='castle_neutral_soft.png' if True else None
    if f:
        im=Image.open(TI+f); sk=1.0; w=int(18.3*1.732*PX*sk); h=int(36.6*PX*sk)
        img.alpha_composite(im.resize((w,h),Image.LANCZOS),(int(cx-w/2),int(cy-h/2)))
for y,x,s,sc,fl in items:
    w=int(sc*PX); h=int(w*s.height/s.width); im=s.resize((w,h),Image.LANCZOS)
    if fl: im=im.transpose(Image.FLIP_LEFT_RIGHT)
    img.alpha_composite(im,(int(x-w/2),int(y-h*.92)))
img.convert('RGB').save('/home/claude/work/painted_proto.png'); print(len(items),W,H)
