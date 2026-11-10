import json,math,sys
from PIL import Image,ImageDraw
def render(N,void,homes,out,marks=None):
    HR=18; HH=HR*math.sqrt(3); HM=2
    GW=2*HM+HR*(1.5*(N-1)+2); GH=2*HM+HH*(N+.5)
    def ctr(i):
        r,c=divmod(i,N); x=HM+HR+c*1.5*HR; y=HM+HH/2+r*HH+(c&1)*HH/2; return (GH-y,GW-x)
    S=3; ids=[i for i in range(N*N) if i not in void]
    pts=[ctr(i) for i in ids]; xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
    x0,x1,y0,y1=min(xs)-HR,max(xs)+HR,min(ys)-HR,max(ys)+HR
    im=Image.new('RGB',(int((x1-x0)*S),int((y1-y0)*S)),(15,25,18)); d=ImageDraw.Draw(im)
    for i in ids:
        cx,cy=ctr(i); poly=[]
        for k in range(6):
            a=math.pi/180*(60*k)   # flat-top in grid space -> after the swap it is points-up
            gx,gy=HR*math.cos(a),HR*math.sin(a); poly.append(((cx+gy-x0)*S,(cy+gx-y0)*S))
        col=(42,85,41)
        if marks and i in marks: col=marks[i]
        if i in homes: col=(239,193,90)
        d.polygon(poly,fill=col,outline=(6,9,7))
    im.save(out); print(out,im.size,'board w/h',round((x1-x0)/(y1-y0),2))
if __name__=='__main__':
    b=json.load(open('board3.json')); render(b['N'],set(b['void']),b['homes'],'/tmp/claude-0/-home-claude/0542aff7-6b7b-5c4c-9911-25113d3708a3/scratchpad/board3.png')
    N=8; V={r*N+c for r,c in [(0,0),(0,1),(1,0),(0,7),(0,6),(1,7),(7,0),(7,1),(6,0),(7,7),(7,6),(6,7)]}
    render(8,V,[6*N+2,1*N+5],'/tmp/claude-0/-home-claude/0542aff7-6b7b-5c4c-9911-25113d3708a3/scratchpad/board2.png')
