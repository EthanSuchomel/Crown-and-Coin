from PIL import Image
import numpy as np
from scipy import ndimage
im=np.array(Image.open('/mnt/user-data/attachments/112a0b3f-dd28-5943-ad35-c12df06d67ec/1d925d93-image.png').convert('RGB')).astype(int)
r,g,b=im[...,0],im[...,1],im[...,2]
mag=(r>170)&(b>170)&(g<120)&(abs(r-b)<70)
lab,n=ndimage.label(mag); sz=ndimage.sum(np.ones_like(lab),lab,range(1,n+1))
bg=np.isin(lab,[i for i,s in enumerate(sz,1) if s>20])
near=ndimage.binary_dilation(bg,iterations=2)&~bg
bg|=near&(r>120)&(b>120)&(g<r-40)&(g<b-40)
o=Image.fromarray(np.dstack([im.astype(np.uint8),(~bg).astype(np.uint8)*255]),'RGBA'); o=o.crop(o.getbbox()); print('cut',o.size)
S=max(o.size); sq=Image.new('RGBA',(S,S)); sq.paste(o,((S-o.width)//2,S-o.height))   # same square, bottom-aligned layout as the other building icons
sm=sq.resize((192,192),Image.LANCZOS); A=np.array(sm); A[...,3]=np.where(A[...,3]>128,255,0); sm=Image.fromarray(A)
sm.save('barracks_dinos_nest.png',optimize=True)
a=np.array(sm).astype(int); print('pink left',int(((a[...,3]>0)&(a[...,0]>170)&(a[...,2]>170)&(a[...,1]<120)).sum()))
