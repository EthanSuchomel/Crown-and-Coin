# Repaint the Alamosaurus body without its tower, riders and saddle cloth (v2).
# The tail, neck and head stay as they were. The torso and the neck base are repainted with the neck's own stripes,
# following the body's shape (a 0..1 'across' coordinate from the back to the belly), fading to the tail's colours at the hips.
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import binary_dilation, distance_transform_edt
D='/tmp/claude-0/-home-claude/112a0b3f-dd28-5943-ad35-c12df06d67ec/scratchpad/'
src=np.array(Image.open(D+'alamo/alamo_blue.png')).astype(np.int32)
H,W=src.shape[:2]
OUT=np.array([14,18,10]); OUT2=np.array([40,33,27])
# fill edges (the outline is drawn 2px outside these)
TOP=[(100,157),(104,154),(110,149),(120,140),(132,131),(146,125),(162,121),(178,120),(190,121),(199,124),(205,126)]
NECKB=[(205,126),(210,125),(214,123),(218,120),(222,116),(225,112),(228,109)]     # the shoulder rising into the neck
FRONT=[(263,109),(262,112),(259,120),(255,132),(249,144),(246,150),(242,157),(237,165),(231,173),(224,181),(218,186),(212,189)]
BELLY=[(212,189),(200,191),(170,192),(140,191),(120,189),(108,187),(104,186),(100,184)]
back=TOP+NECKB[1:]
poly=back+[(263,109)]+FRONT[1:]+BELLY[1:]
m=Image.new('L',(W,H),0); ImageDraw.Draw(m).polygon(poly,fill=255); S=np.array(m)>0
S[:109,:]=False                      # above row 109 the original neck is kept
# rasterise the two sides so we can measure distances
def line_mask(pts):
    im=Image.new('L',(W,H),0); ImageDraw.Draw(im).line(pts,fill=255,width=1); return np.array(im)>0
topL=line_mask(back); botL=line_mask(FRONT+BELLY[1:])
dT=distance_transform_edt(~topL); dB=distance_transform_edt(~botL)
s=dT/np.maximum(dT+dB,1e-6)
# keep: tail (x<100) and the neck/head above row 109 (only the run that starts right of the tower)
A=src[...,3]>0; keep=np.zeros((H,W),bool); keep[:,:100]=A[:,:100]
for yy in range(0,109):
    xs=np.where(A[yy])[0]
    if not len(xs): continue
    br=np.where(np.diff(xs)>1)[0]; starts=np.r_[xs[0],xs[br+1]]; ends=np.r_[xs[br],xs[-1]]
    for a,b in zip(starts,ends):
        if a>=224 or yy<58: keep[yy,a:b+1]=True
# the two colour sources
rows=list(range(97,108))
nsp={}
for r in rows:
    xs=np.where(src[r,:,3]>200)[0]; xs=xs[xs>=224]; nsp[r]=(xs.min()+3,xs.max()-3)
cols=list(range(66,100))
tsp={}
for c in cols:
    ys=np.where(src[:,c,3]>200)[0]; tsp[c]=(ys.min()+2,ys.max()-3)
img=np.zeros((H,W,4),np.int32); img[keep]=src[keep]
rng=np.random.default_rng(3)
from scipy.ndimage import gaussian_filter
noise=gaussian_filter(rng.random((H,W)),2.2); noise=(noise-noise.min())/(noise.max()-noise.min())
rsel=gaussian_filter(rng.random((H,W)),3.0); rsel=(rsel-rsel.min())/(rsel.max()-rsel.min())
Y,X=np.where(S)
for y,x in zip(Y,X):
    sv=float(np.clip(s[y,x],0,1))
    c0,hw=0.495,0.105; h=hw*float(np.clip((x-106)/62,0,1))**0.8     # towards the hips the light flank stripe narrows to a point
    sn=sv
    if abs(sv-c0)<=hw: sn=(c0+(sv-c0)*hw/h) if abs(sv-c0)<h else (0.36 if sv<c0 else 0.66)
    r=rows[min(len(rows)-1,int(rsel[y,x]*len(rows)))]; a,b=nsp[r]; neck=src[r,int(round(a+sn*(b-a))),:3]
    c=cols[int(abs(((x//1)%(2*len(cols)-2))-(len(cols)-1)))]; t0,b0=tsp[c]; tail=src[int(round(t0+sv*(b0-t0))),c,:3]
    wt=np.clip((132-x)/30,0,1)            # 1 at the hips (x<=104), 0 from x=150 on
    img[y,x,:3]=tail if noise[y,x]<wt else neck; img[y,x,3]=255
# knobs along the back, like the tail's
for x in range(106,201,5):
    t=int(np.interp(x,[p[0] for p in TOP],[p[1] for p in TOP]))
    S[t-1,x:x+2]=True; img[t-1,x:x+2,:3]=img[t+1,x:x+2,:3]; img[t-1,x:x+2,3]=255
# the outline: 2 dark pixels outside the new shape, none over kept pixels
ring=binary_dilation(S,iterations=2)&~S; ring[:,:100]=False; ring&=~keep
img[ring,:3]=OUT; img[ring,3]=255
img=np.clip(img,0,255).astype(np.uint8)
Image.fromarray(img).save(D+'alamo2/alamo_plain.png')
bg=Image.new('RGBA',(W,H),(40,90,50,255)); bg.alpha_composite(Image.fromarray(img)); bg.resize((W*3,H*3),Image.NEAREST).save(D+'alamo2/view5.png')
print('ok')
