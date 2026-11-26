// ---------- The sea and beach round the map (the Godot version's coast, 2026-11-23; browser 2026-11-26) ----------
// Ethan: "a water/beach border so that there is no more dark void around it". The open sea fills everything behind
// the board; a coast picture is made once per board shape: for every point, how far it is from the land's edge,
// blurred so the shore is smooth rather than following each hex's edges, then sand over the land's outer rim, wet
// sand, a line of surf, shallow water and the open sea. It's drawn twice: under the terrain tiles, and over them
// only off the land (so a forest or mountain on the shore doesn't poke out over the beach with its hex corners).
const COAST={px:3, margin:34, sand:[219,196,133], wet:[168,148,99], shallow:[23,145,176], mid:[5,84,143], foam:[230,245,240]};
function coastNoise(seed){   // smooth value noise, wrapping every `per` cells when given
  const h=(x,y)=>{ let n=Math.imul(x*374761393+y*668265263+seed*1442695041,1274126177); n^=n>>>13; n=Math.imul(n,1597334677); return ((n^(n>>>16))>>>0)/4294967296; };
  return (x,y,per)=>{ const xi=Math.floor(x), yi=Math.floor(y), fx=x-xi, fy=y-yi, u=fx*fx*(3-2*fx), v=fy*fy*(3-2*fy), w=a=>per?((a%per)+per)%per:a;
    const a=h(w(xi),w(yi)), b=h(w(xi+1),w(yi)), c=h(w(xi),w(yi+1)), d=h(w(xi+1),w(yi+1));
    return a+(b-a)*u+(c-a)*v+(a-b-c+d)*u*v; };
}
const _cn1=coastNoise(7), _cn2=coastNoise(19);
const cfbm=(n,x,y,per)=>(n(x,y,per)*.6+n(x*2.03+5.1,y*2.03+1.7,per?per*2:0)*.3+n(x*4.1+2.3,y*4.1+7.9,per?per*4:0)*.1);
// the open sea: one tile that repeats seamlessly, about 150 board units across
let _oceanTile=null;
function oceanTile(){
  if(_oceanTile) return _oceanTile;
  const S2=192, cv=document.createElement('canvas'); cv.width=cv.height=S2; const g=cv.getContext('2d'), im=g.createImageData(S2,S2);
  for(let y=0;y<S2;y++) for(let x=0;x<S2;x++){
    const n=cfbm(_cn1,x/S2*4,y/S2*4,4), n2=cfbm(_cn2,x/S2*12,y/S2*12,12), t=Math.min(1,Math.max(0,(n*.6+n2*.4-.3)/.5)), s=t*t*(3-2*t);
    let r=5+(10-5)*s, gg=61+(84-61)*s, b=115+(143-115)*s; const gl=Math.max(0,Math.min(1,(n2-.72)/.1))*Math.max(0,Math.min(1,(n-.45)/.25))*.22;
    r+=(217-r)*gl; gg+=(242-gg)*gl; b+=(255-b)*gl; const o=(y*S2+x)*4; im.data[o]=r; im.data[o+1]=gg; im.data[o+2]=b; im.data[o+3]=255; }
  g.putImageData(im,0,0); return _oceanTile=cv.toDataURL('image/png');
}
// distance to the nearest set pixel (two-pass chamfer), in pixels
function chamfer(mask,W,H){
  const D=new Float32Array(W*H), INF=1e9, a=1, b=1.4142;
  for(let i=0;i<W*H;i++) D[i]=mask[i]?0:INF;
  for(let y=0;y<H;y++) for(let x=0;x<W;x++){ const i=y*W+x; let v=D[i]; if(v===0) continue;
    if(x>0) v=Math.min(v,D[i-1]+a); if(y>0){ v=Math.min(v,D[i-W]+a); if(x>0) v=Math.min(v,D[i-W-1]+b); if(x<W-1) v=Math.min(v,D[i-W+1]+b); } D[i]=v; }
  for(let y=H-1;y>=0;y--) for(let x=W-1;x>=0;x--){ const i=y*W+x; let v=D[i]; if(v===0) continue;
    if(x<W-1) v=Math.min(v,D[i+1]+a); if(y<H-1){ v=Math.min(v,D[i+W]+a); if(x<W-1) v=Math.min(v,D[i+W+1]+b); if(x>0) v=Math.min(v,D[i+W-1]+b); } D[i]=v; }
  return D;
}
function boxBlur(A,W,H,r){
  const T=new Float32Array(W*H), O=new Float32Array(W*H);
  for(let y=0;y<H;y++){ let s=0; const row=y*W; for(let x=-r;x<=r;x++) s+=A[row+Math.min(W-1,Math.max(0,x))];
    for(let x=0;x<W;x++){ T[row+x]=s/(2*r+1); s+=A[row+Math.min(W-1,x+r+1)]-A[row+Math.max(0,x-r)]; } }
  for(let x=0;x<W;x++){ let s=0; for(let y=-r;y<=r;y++) s+=T[Math.min(H-1,Math.max(0,y))*W+x];
    for(let y=0;y<H;y++){ O[y*W+x]=s/(2*r+1); s+=T[Math.min(H-1,y+r+1)*W+x]-T[Math.max(0,y-r)*W+x]; } }
  return O;
}
const sstep=(e0,e1,x)=>{ const t=Math.min(1,Math.max(0,(x-e0)/(e1-e0))); return t*t*(3-2*t); };
let _coastKey='', _coast=null;
// the coast pictures for the current board: {x, y, w, h, lo, hi} (board units; lo/hi are image URLs)
function coastArt(){
  const key=(S&&S.map?'map:'+S.map:'std'+N)+'|'+[...VOID].join(',');
  if(_coast&&_coastKey===key) return _coast;
  const P=COAST.px, M=COAST.margin, x0=VB_X-M, y0=VB_Y-M, W=Math.ceil((VB_W+2*M)*P), H=Math.ceil((VB_H+2*M)*P);
  const cv=document.createElement('canvas'); cv.width=W; cv.height=H; const g=cv.getContext('2d');
  g.fillStyle='#fff'; g.beginPath();
  for(let i=0;i<N*N;i++){ if(VOID.has(i)) continue; const [cx,cy]=hexCenter(i);
    for(let k=0;k<6;k++){ const [x,y]=hexV(cx,cy,HR+.3,k); const X=(x-x0)*P, Y=(y-y0)*P; k?g.lineTo(X,Y):g.moveTo(X,Y); } g.closePath(); }
  g.fill();
  const px=g.getImageData(0,0,W,H).data, land=new Uint8Array(W*H), sea=new Uint8Array(W*H);
  for(let i=0;i<W*H;i++){ const on=px[i*4+3]>127; land[i]=on?1:0; sea[i]=on?0:1; }
  const dl=chamfer(land,W,H), ds=chamfer(sea,W,H), d0=new Float32Array(W*H);
  for(let i=0;i<W*H;i++) d0[i]=(dl[i]-ds[i])/P;   // board units: below 0 on land, above 0 at sea
  const d1=boxBlur(boxBlur(d0,W,H,Math.round(2.4*P)),W,H,Math.round(2.4*P));
  const lo=g.createImageData(W,H), hi=g.createImageData(W,H), [SA,WE,SH,MI,FO]=[COAST.sand,COAST.wet,COAST.shallow,COAST.mid,COAST.foam];
  for(let y=0;y<H;y++) for(let x=0;x<W;x++){
    const i=y*W+x, ux=x/P+x0, uy=y/P+y0, n=(cfbm(_cn1,ux/64,uy/64)-.5)*2, n2=(cfbm(_cn2,ux/19+.37,uy/19+.61)-.5)*2;
    const d=d1[i]+n*2.4+n2*.7;   // a ragged, natural shoreline
    const a=sstep(-5.2,-3.4,d)*(1-sstep(12,24,d)); if(a<=0) continue;
    const mix=(p,q,t)=>[p[0]+(q[0]-p[0])*t,p[1]+(q[1]-p[1])*t,p[2]+(q[2]-p[2])*t];
    let c=SA.map(v=>v*(.95+.07*n2)); c=mix(c,WE,sstep(1.6,3.6,d));
    let w=mix(SH,MI,sstep(4.5,13,d)); let fo=(1-sstep(0,1.3,Math.abs(d-4.6)))*(.55+.45*n2)+(1-sstep(0,.8,Math.abs(d-7.4-n*1.5)))*.22;
    w=mix(w,FO,Math.min(1,Math.max(0,fo))*.75); c=mix(c,w,sstep(3.7,4.4,d));
    const o=i*4; lo.data[o]=c[0]; lo.data[o+1]=c[1]; lo.data[o+2]=c[2]; lo.data[o+3]=a*255;
    const ah=a*sstep(.6,2.2,d); if(ah>0){ hi.data[o]=c[0]; hi.data[o+1]=c[1]; hi.data[o+2]=c[2]; hi.data[o+3]=ah*255; } }
  g.putImageData(lo,0,0); const loU=cv.toDataURL('image/png'); g.clearRect(0,0,W,H); g.putImageData(hi,0,0); const hiU=cv.toDataURL('image/png');
  _coastKey=key; return _coast={x:x0,y:y0,w:W/P,h:H/P,lo:loU,hi:hiU};
}
function coastSvg(which){
  try{ const c=coastArt(); return `<image href="${which==='lo'?c.lo:c.hi}" x="${c.x.toFixed(2)}" y="${c.y.toFixed(2)}" width="${c.w.toFixed(2)}" height="${c.h.toFixed(2)}" preserveAspectRatio="none" style="pointer-events:none"/>`; }
  catch(e){ return ''; }   // (no canvas: no coast, the board as before)
}
