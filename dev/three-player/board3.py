# The 3-player board: an 11 x 11 grid cut down to a hexagon of radius 5 around the centre (91 hexes), less
# the corner hex at each of its six corners and the two hexes beside the corner at the three corners between the
# home castles (12 more) = 79 hexes, about 1.5x the 2-player board's 52. The cut turns with the board, so each
# home castle has exactly the same shape around it. The homes sit one ring in from the other three corners.
import math
N=11
def cube(i):
    r,c=divmod(i,N); x=c; z=r-(c-(c&1))//2; return (x,-x-z,z)
def man(a,b):
    p,q=cube(a),cube(b); return max(abs(p[0]-q[0]),abs(p[1]-q[1]),abs(p[2]-q[2]))
def from_cube(x,y,z):
    c=x; r=z+(c-(c&1))//2
    return r*N+c if 0<=r<N and 0<=c<N else None
C=5*N+5; cx,cy,cz=cube(C)
rel=lambda i:tuple(a-b for a,b in zip(cube(i),(cx,cy,cz)))
inside=[i for i in range(N*N) if man(i,C)<=5]
corners=[(5,-5,0),(5,0,-5),(0,5,-5),(-5,5,0),(-5,0,5),(0,-5,5)]
homeCorners=[corners[0],corners[2],corners[4]]
gapCorners=[corners[1],corners[3],corners[5]]
cut=set()
for k in corners: cut.add(k)
for k in gapCorners:
    # the two edge hexes next to that corner
    for d in [(1,-1,0),(1,0,-1),(0,1,-1),(-1,1,0),(-1,0,1),(0,-1,1)]:
        n=tuple(a+b for a,b in zip(k,d))
        if max(map(abs,n))==5: cut.add(n)
board=[i for i in inside if rel(i) not in cut]
void=[i for i in range(N*N) if i not in board]
homes=[from_cube(*(cx+int(k[0]*.8),cy+int(k[1]*.8),cz+int(k[2]*.8))) for k in homeCorners]
print('hexes',len(board),'cut',len(cut),'homes',homes,'home distances',[man(homes[a],homes[b]) for a,b in ((0,1),(1,2),(0,2))])
print('home ring from centre',[man(h,C) for h in homes])
# the void list as (row,col) pairs, for the game
print('VOID',[divmod(i,N) for i in void])
import json; json.dump({'N':N,'void':void,'homes':homes,'center':C},open('board3.json','w'))
