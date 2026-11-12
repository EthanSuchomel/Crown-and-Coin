# Robot faction art (OpenArt, GPT Image 2.6 Sunburst, magenta background), cut out the same way as the Dinosaur set.
import sys
from PIL import Image
import numpy as np
from scipy import ndimage
A='/mnt/user-data/attachments/3befcac9-cc11-52d0-937a-7b889271868d/'
def cut(src):
    im=np.array(Image.open(src).convert('RGB')).astype(int)
    r,g,b=im[...,0],im[...,1],im[...,2]
    mag=(r>170)&(b>170)&(g<120)&(abs(r-b)<70)
    lab,n=ndimage.label(mag); sz=ndimage.sum(np.ones_like(lab),lab,range(1,n+1))
    bg=np.isin(lab,[i for i,s in enumerate(sz,1) if s>20])
    for _ in range(2):   # the pink fringe along the outlines
        near=ndimage.binary_dilation(bg,iterations=2)&~bg
        bg|=near&(r>110)&(b>110)&(g<r-35)&(g<b-35)
    o=Image.fromarray(np.dstack([im.astype(np.uint8),(~bg).astype(np.uint8)*255]),'RGBA'); return o.crop(o.getbbox())
def pink(im):
    a=np.array(im).astype(int); return int(((a[...,3]>0)&(a[...,0]>170)&(a[...,2]>170)&(a[...,1]<120)).sum())
def hard(im):
    a=np.array(im); a[...,3]=np.where(a[...,3]>128,255,0); return Image.fromarray(a)
